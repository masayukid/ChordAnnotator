from copy import deepcopy
from collections.abc import Generator
from typing import List, TYPE_CHECKING

import flet as ft
import flet.canvas as cv
from flet_core.canvas.shape import Shape
import keyboard

if TYPE_CHECKING:
    from app import App
from controls.seek_bar import SeekBar
from controls.pitch_row import PitchRow
from musics.chord_info import ChordInfo
from utils import pitch_row_state_to_hex, hex_to_pitch_row_state
from commander import Command
from config import Config

class InfoOverlay(ft.UserControl):
    def __init__(self, app: 'App') -> None:
        super().__init__()
        self._app = app
        self._width = None
        self._first_info = None
        self._current_info = None
        self._selection_pivot = None
        self._is_editing = False
        self._clipboard = []

    def build(self):
        self._info_canvas = cv.Canvas()
        self._seek_bar = SeekBar(
            on_update_position=self._on_update_seek_bar_pos
        )
        self._pitch_rows = ft.Column(
            controls=[
                PitchRow(ft.colors.TRANSPARENT, ft.colors.WHITE) for _ in range(Config.n_bins)
            ],
            spacing=0,
        )
        self._pitch_rows_container = ft.Container(
            content=self._pitch_rows,
            margin=ft.margin.only(top=Config.info_bar_height),
            visible=False,
        )
        return ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Container(
                        height=Config.info_bar_height,
                        bgcolor=ft.colors.GREY_800,
                    ),
                    self._pitch_rows_container,
                    ft.Container(
                        content=self._info_canvas,
                        left=0,
                        top=0,
                        right=0,
                        bottom=0,
                        opacity=Config.chord_info_opacity,
                    ),
                    self._seek_bar,
                ]
            ),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
    
    @property
    def current_info(self) -> ChordInfo:
        return self._current_info
    
    @property
    def seek_bar(self) -> SeekBar:
        return self._seek_bar

    def _on_update_seek_bar_pos(self, pos: float) -> None:
        info = self.get_info(pos)

        if info != self._current_info:
            if self._is_editing:
                self.finish_edit_current_info()

            if keyboard.is_pressed('shift'):
                if self._selection_pivot is None:
                    self._start_select_info(self._current_info)
                selected_infos = self._get_infos_between(self._selection_pivot, info)
                self._update_pitch_row_range(selected_infos[0].start_pos, selected_infos[-1].end_pos)
            else:
                self._finish_select_info()

            self._current_info = info
            self._update_dropdown_options()
        self._update_menu_buttons()

    def _start_select_info(self, info: ChordInfo) -> None:
        self._selection_pivot = info
        self._pitch_rows_container.visible = True
        self._pitch_rows_container.bgcolor = ft.colors.with_opacity(Config.background_opacity, ft.colors.WHITE)
        self._pitch_rows_container.update()
        
        self._update_pitch_row_state([False] * Config.n_bins)

    def _finish_select_info(self) -> None:
        self._selection_pivot = None
        self._pitch_rows_container.visible = False
        self._pitch_rows_container.update()

    def _get_selected_infos(self) -> List[ChordInfo]:
        if self._selection_pivot is None:
            return [self._current_info]
        else:
            return self._get_infos_between(self._selection_pivot, self._current_info)

    def _get_infos_between(self, info1: ChordInfo, info2: ChordInfo) -> List[ChordInfo]:
        start_pos, end_pos = info1.start_pos, info2.start_pos
        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos
        infos = []
        info = self._first_info
        while info is not None:
            if info.start_pos < start_pos:
                info = info.next
                continue
            if info.start_pos > end_pos:
                break
            infos.append(info)
            info = info.next
        return infos

    def _update_dropdown_options(self) -> None:
        key_options = [ft.dropdown.Option(text=key_name) for key_name in self._current_info.key_name_suggestions]
        chord_options = [ft.dropdown.Option(text=chord_name) for chord_name in self._current_info.chord_name_suggestions]

        self._app.view.menu.update_key_name_dropdown_options(key_options)
        self._app.view.menu.update_chord_name_dropdown_options(chord_options)

    def _update_menu_buttons(self) -> None:
        addable = self.get_selectable_info(self._seek_bar.pos) is None
        deletable = self._current_info.index > 0 and (self._selection_pivot is None or self._selection_pivot.index > 0)
        can_skip_start = self._seek_bar.pos > 0
        can_skip_prev = self._seek_bar.pos > self._current_info.start_pos or self._current_info.prev is not None
        can_pause_resume = self._seek_bar.pos < 1
        can_skip_next = self._seek_bar.pos < self._current_info.end_pos or self._current_info.next is not None
        can_skip_end = self._seek_bar.pos < 1

        self._app.view.menu.update_add_info_button_enabled(addable)
        self._app.view.menu.update_delete_info_button_enabled(deletable)
        self._app.view.menu.update_skip_start_button_enabled(can_skip_start)
        self._app.view.menu.update_skip_prev_button_enabled(can_skip_prev)
        self._app.view.menu.update_pause_resume_button_enabled(can_pause_resume)
        self._app.view.menu.update_skip_next_button_enabled(can_skip_next)
        self._app.view.menu.update_skip_end_button_enabled(can_skip_end)

    def initialize(self) -> None:
        self._first_info = ChordInfo(0)
        self._current_info = None
        self._is_editing = False
        self._selection_pivot = None
        self._clipboard = []
        self._seek_bar.pos = 0

        self._app.view.menu.update_copy_info_button_enabled(True)
        self._app.view.menu.update_paste_info_button_enabled(False)

    def get_content(self) -> dict:
        content = []
        duration = self._app.audio_player.duration / 1e3
        for info in self._get_infos():
            time_stamp = info.start_pos * duration
            key_name = info.key_name
            chord_name = info.chord_name
            pitch_row_hex = pitch_row_state_to_hex(info.pitch_row_state)

            content.append({
                'time_stamp': time_stamp,
                'key_name': key_name,
                'chord_name': chord_name,
                'pitch_row_hex': pitch_row_hex
            })
        return content

    def update_content(self, content: List[dict]) -> None:
        duration = self._app.audio_player.duration / 1e3
        for info_data in content:
            pos = info_data['time_stamp'] / duration
            key_name = info_data['key_name']
            chord_name = info_data['chord_name']
            pitch_row_state = hex_to_pitch_row_state(info_data['pitch_row_hex'])

            if pos > 0:
                info = ChordInfo(pos)
                self.get_info(pos).insert(info)
            else:
                info = self._first_info
            info.load(key_name, chord_name, pitch_row_state)
        self._update_info_canvas()

    def send_add_info_command(self) -> None:
        info = ChordInfo(self._seek_bar.pos)
        info.set_key_name(self.current_info.key_name)
        self._app.commander.send(
            Command(
                do=lambda: self._add_infos([info]),
                undo=lambda: self._delete_infos([info]),
            )
        )

    def send_delete_info_command(self) -> None:
        infos = self._get_selected_infos()
        self._app.commander.send(
            Command(
                do=lambda: self._delete_infos(infos),
                undo=lambda: self._add_infos(infos),
            )
        )

    def send_paste_info_command(self) -> None:
        info = self._current_info
        infos = []
        for _ in range(len(self._clipboard)):
            if info is None:
                break
            infos.append(info)
            info = info.next
        clipboard_backup = deepcopy(self._clipboard)
        infos_backup = deepcopy(infos)
        self._app.commander.send(
            Command(
                do=lambda: self._copy_paste(clipboard_backup, infos),
                undo=lambda: self._copy_paste(infos_backup, infos),
            )
        )

    def send_select_key_name_command(self, key_name: str) -> None:
        info = self._current_info
        key_name_backup = info.key_name
        self._app.commander.send(
            Command(
                do=lambda: self._on_select_key_name(info, key_name),
                undo=lambda: self._on_select_key_name(info, key_name_backup),
            )
        )

    def send_select_chord_name_command(self, chord_name: str) -> None:
        info = self._current_info
        chord_name_backup = info.chord_name
        self._app.commander.send(
            Command(
                do=lambda: self._on_select_chord_name(info, chord_name),
                undo=lambda: self._on_select_chord_name(info, chord_name_backup),
            )
        )

    def _send_toggle_pitch_row_command(self, idx: int) -> None:
        info = self._current_info
        info_backup = deepcopy(info)
        self._app.commander.send(
            Command(
                do=lambda: self._toggle_pitch_row(info, idx),
                undo=lambda: self._copy_paste([info_backup], [info]),
            )
        )
    
    def _add_infos(self, infos: List[ChordInfo]) -> None:
        prev = self.get_info(infos[0].start_pos)
        for info in infos:
            prev.insert(info)
            self._info_canvas.shapes[info.index * 2:0] = self._create_info_shapes(info)
            prev = info
        self._info_canvas.update()
        
        target = infos[0].prev
        if self._is_info_editing(target):
            self._update_pitch_row_range(target.start_pos, target.end_pos)

        self._on_update_seek_bar_pos(self._seek_bar.pos)

    def _delete_infos(self, infos: List[ChordInfo]) -> None:
        target = infos[0].prev

        if self._current_info in infos and self._is_editing:
            self.finish_edit_current_info()
        for info in infos:
            del self._info_canvas.shapes[info.index * 2:info.index * 2 + 2]
            info.delete()
        self._info_canvas.update()

        if self._is_info_editing(target):
            self._update_pitch_row_range(target.start_pos, target.end_pos)

        self._on_update_seek_bar_pos(self._seek_bar.pos)

    def copy_to_clipboard(self) -> None:
        self._clipboard = self._get_selected_infos()
        self._app.view.menu.update_paste_info_button_enabled(True)

    def _copy_paste(self, sources: List[ChordInfo], targets: List[ChordInfo]) -> None:
        for source, target in zip(sources, targets):
            target.load(source.key_name, source.chord_name, source.pitch_row_state)
            self._on_info_modified(target)
            
        if self._is_info_editing(target):
            self._update_pitch_row_state(target.pitch_row_state)
        else:
            self._seek_bar.pos = target.start_pos
            self.start_edit_current_info()

    def _on_select_key_name(self, info: ChordInfo, key_name: str) -> None:
        while info is not None:
            info.set_key_name(key_name)
            self._on_info_modified(info)
            info = info.next

    def _on_select_chord_name(self, info: ChordInfo, chord_name: str) -> None:
        info.set_chord_name(chord_name)
        self._on_info_modified(info)

    def on_secondary_click_info(self, info: ChordInfo, idx: int) -> None:
        if self._is_info_editing(info):
            if idx >= 0:
                self._send_toggle_pitch_row_command(idx)
        else:
            self._seek_bar.pos = info.start_pos
            self.start_edit_current_info()

    def _toggle_pitch_row(self, info: ChordInfo, idx: int) -> None:
        info.pitch_row_state[idx] = not info.pitch_row_state[idx]
        if self._is_info_editing(info):
            self._pitch_rows.controls[idx].is_highlighted = info.pitch_row_state[idx]
        else:
            self._seek_bar.pos = info.start_pos
            self.start_edit_current_info()
        self._on_info_modified(info)

    def _is_info_editing(self, info: ChordInfo) -> bool:
        return info == self._current_info and self._is_editing

    def _on_info_modified(self, info: ChordInfo) -> None:
        info.update_chord_name_suggestions()
        info.update_key_name_suggestions()
        self._update_chord_name_in_canvas(info)

        if info == self._current_info:
            self._update_dropdown_options()

    def _update_chord_name_in_canvas(self, info: ChordInfo) -> None:
        self._info_canvas.shapes[info.index * 2 + 1].text = info.chord_name
        self._info_canvas.update()

    def start_edit_current_info(self) -> None:
        self._is_editing = True
        self._pitch_rows_container.visible = True
        self._pitch_rows_container.bgcolor = ft.colors.with_opacity(Config.background_opacity, ft.colors.BLACK)
        self._pitch_rows_container.update()

        self._update_pitch_row_state(self._current_info.pitch_row_state)
        self._update_pitch_row_range(self._current_info.start_pos, self._current_info.end_pos)

        self._app.view.menu.update_key_name_dropdown_enabled(True)
        self._app.view.menu.update_chord_name_dropdown_enabled(True)

    def finish_edit_current_info(self) -> None:
        self._is_editing = False
        self._pitch_rows_container.visible = False
        self._pitch_rows_container.update()

        self._app.view.menu.update_key_name_dropdown_enabled(False)
        self._app.view.menu.update_chord_name_dropdown_enabled(False)
    
    def get_selectable_info(self, pos: float) -> ChordInfo:
        info = self.get_info(pos)
        duration = self._app.audio_player.duration
        if (pos - info.start_pos) * duration < Config.info_min_interval:
            return info
        if (info.end_pos - pos) * duration < Config.info_min_interval:
            if info.end_pos < 1:
                return info.next
        return None

    def get_info(self, pos: float) -> ChordInfo:
        for info in self._get_infos():
            if pos < info.end_pos:
                return info
        return info

    def _get_infos(self) -> Generator[ChordInfo]:
        info = self._first_info
        while info is not None:
            yield info
            info = info.next

    def _update_pitch_row_state(self, pitch_row_state: List[bool]) -> None:
        for i in range(Config.n_bins):
            self._pitch_rows.controls[i].is_highlighted = pitch_row_state[i]

    def _update_pitch_row_range(self, start_pos: float, end_pos: float) -> None:
        self._pitch_rows_container.margin.left = start_pos * self._width
        self._pitch_rows_container.margin.right = (1 - end_pos) * self._width
        self._pitch_rows_container.update()

    def on_update_width(self, width: ft.OptionalNumber) -> None:
        self._width = width - Config.seek_bar_thickness
        if self._is_editing:
            self._update_pitch_row_range(self._current_info.start_pos, self._current_info.end_pos)
        self._update_info_canvas()

    def _update_info_canvas(self) -> None:
        shapes = []
        for info in self._get_infos():
            shapes += self._create_info_shapes(info)
        self._info_canvas.shapes = shapes
        self._info_canvas.update()

    def _create_info_shapes(self, info: ChordInfo) -> List[Shape]:
        pos_pixel = info.start_pos * self._width
        return [
            cv.Rect(
                x=pos_pixel,
                y=0,
                width=Config.chord_info_thickness,
                height=Config.window_max_height,
                paint=ft.Paint(
                    color=ft.colors.WHITE
                ),
            ),
            cv.Text(
                x=pos_pixel + Config.chord_info_text_margin,
                y=0,
                text=info.chord_name,
                style=ft.TextStyle(
                    size=Config.chord_info_font_size,
                    color=ft.colors.WHITE,
                ),
            )
        ]