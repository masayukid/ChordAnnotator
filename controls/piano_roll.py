import time
from threading import Thread
from typing import List, Optional, TYPE_CHECKING

import keyboard
import flet as ft
import numpy as np

if TYPE_CHECKING:
    from app import App
from controls.keyboard import Keyboard
from controls.spec_view import SpecView
from musics.piano import Piano
from utils import idx_to_midi
from config import Config

class ScrollOption:
    class Destination:
        SEEK_BAR_POS = 'seek_bar_pos'
        SEEK_BAR_CENTERED = 'seek_bar_centered'

    def __init__(
            self,
            destination: Destination,
            immediate: Optional[bool] = False,
            forced: Optional[bool] = False,
        ):
        self.destination = destination
        self.immediate = immediate
        self.forced = forced

class PianoRoll(ft.UserControl):
    def __init__(self, app: 'App') -> None:
        super().__init__(expand=True)
        self._app = app
        self._mouse_pos = None
        self._scroll_offset = 0
        self._is_scrolling = False
        self._highlighted_idxs = []

    def build(self):
        self._piano = Piano()
        self._keyboard = Keyboard()
        self._spec_view = SpecView(self._app)
        self._scroll_view = ft.Row(
            controls=[
                ft.Container(
                    content=self._spec_view,
                    margin=ft.margin.only(bottom=Config.scroll_bar_height),
                )
            ],
            scroll=ft.ScrollMode.ALWAYS,
            on_scroll=self._on_scroll,
            on_scroll_interval=1,
        )
        self._gesture_detector_container = ft.Container(
            content=ft.GestureDetector(
                on_hover=self._on_hover,
                on_tap_down=self._on_tap_down,
                on_tap_up=self._on_tap_up,
                on_secondary_tap_down=self._on_secondary_tap_down,
                on_scroll=self._on_scroll_mouse_wheel,
                on_exit=self._on_exit,
            ),
            margin=ft.margin.only(bottom=Config.scroll_bar_height),
        )
        return [
            ft.Container(
                content=self._keyboard,
                margin=ft.margin.only(
                    top=Config.info_bar_height,
                    bottom=Config.scroll_bar_height,
                ),
            ),
            ft.Container(
                content=self._scroll_view,
                margin=ft.margin.only(left=Config.keyboard_width),
            ),
            self._gesture_detector_container,
        ]
    
    def did_mount(self) -> None:
        Thread(target=self._fixed_update).start()
    
    @property
    def spec_view(self) -> SpecView:
        return self._spec_view
    
    def skip_to_start(self) -> None:
        self._skip_seek_bar_pos(0)

    def skip_to_prev(self) -> None:
        info = self._spec_view.info_overlay.current_info
        seek_bar_pos = self._spec_view.info_overlay.seek_bar.pos
        if abs(seek_bar_pos - info.start_pos) < 0.00001 and info.prev is not None:
            info = info.prev
        self._skip_seek_bar_pos(info.start_pos)

    def pause_resume(self) -> None:
        if self._app.audio_player.is_paused:
            pos = self._spec_view.info_overlay.seek_bar.pos
            self._app.audio_player.play(pos)
        elif self._app.audio_player.is_playing:
            self._app.audio_player.pause()

    def skip_to_next(self) -> None:
        info = self._spec_view.info_overlay.current_info
        self._skip_seek_bar_pos(info.end_pos)

    def skip_to_end(self) -> None:
        self._skip_seek_bar_pos(1)

    def _skip_seek_bar_pos(self, pos: float) -> None:
        if self._app.audio_player.is_playing:
            self._app.audio_player.seek(pos)
        else:
            self._spec_view.info_overlay.seek_bar.pos = pos
            self.scroll_to(
                ScrollOption(
                    destination=ScrollOption.Destination.SEEK_BAR_CENTERED,
                    forced=True,
                )
            )

    def scroll_to(self, option: ScrollOption) -> None:
        if self._is_scrolling and not option.forced:
            return
        
        pos_pixel = self._spec_view.info_overlay.seek_bar.pos * self._spec_view.spec_width
        match option.destination:
            case ScrollOption.Destination.SEEK_BAR_POS:
                offset = pos_pixel
            case ScrollOption.Destination.SEEK_BAR_CENTERED:
                offset = pos_pixel - self._scroll_view_width / 2
                offset = min(max(offset, 0), self._spec_view.spec_width - self._scroll_view_width)

        if self._scroll_offset == offset:
            return
        
        if option.immediate:
            duration = 1
        else:
            duration = Config.scroll_duration

        self._is_scrolling = True
        self._scroll_view.scroll_to(
            offset=offset,
            duration=duration,
        )
    
    def _on_scroll(self, e: ft.OnScrollEvent) -> None:
        self._scroll_offset = e.pixels
        if e.event_type == 'end':
            self._on_scroll_end()

    def _on_scroll_end(self) -> None:
        self._is_scrolling = False

    def _on_hover(self, e: ft.HoverEvent) -> None:
        self._mouse_pos = (e.local_x, e.local_y)

    def _on_tap_down(self, e: ft.TapEvent) -> None:
        self._on_update_mouse_pos(e.local_x, e.local_y)

        if self._app.audio_player.is_paused:
            pos = self._calc_pos(e.local_x)
            info = self._spec_view.info_overlay.get_selectable_info(pos)
            if info is not None:
                pos = info.start_pos
            self._spec_view.info_overlay.seek_bar.pos = pos
            
        notes = [idx_to_midi(idx) for idx in self._highlighted_idxs]
        self._piano.notes_on(notes)

    def _on_tap_up(self, e: ft.TapEvent) -> None:
        self._piano.notes_off()

    def _on_secondary_tap_down(self, e: ft.TapEvent) -> None:
        self._on_update_mouse_pos(e.local_x, e.local_y)

        if self._app.audio_player.is_paused:
            pos = self._calc_pos(e.local_x)
            info = self._spec_view.info_overlay.get_info(pos)
            idx = self._calc_idx(e.local_y)
            self._spec_view.info_overlay.on_secondary_click_info(info, idx)

    def _on_scroll_mouse_wheel(self, e: ft.ScrollEvent) -> None:
        delta = np.sign(e.scroll_delta_y)
        if keyboard.is_pressed('ctrl'):
            if delta > 0:
                self._app.view.menu.on_click_zoom_out()
            else:
                self._app.view.menu.on_click_zoom_in()
        elif self._app.audio_player.is_paused:
            pos = min(max(self._spec_view.info_overlay.seek_bar.pos + (delta / self._spec_view.spec_width), 0), 1)
            self._spec_view.info_overlay.seek_bar.pos = pos

            pos_pixel = self._spec_view.info_overlay.seek_bar.pos * self._spec_view.spec_width
            if self._is_out_of_drawing_area(pos_pixel):
                self.scroll_to(ScrollOption(ScrollOption.Destination.SEEK_BAR_CENTERED))

    def _on_exit(self, e: ft.HoverEvent) -> None:
        self._mouse_pos = (None, None)
    
    def _calc_pos(self, local_x: float) -> float:
        if local_x < Config.keyboard_width:
            return 0
        pixel = local_x + self._scroll_offset - Config.keyboard_width
        return min(max(pixel / self._spec_view.spec_width, 0), 1)

    def _calc_idx(self, local_y: float) -> int:
        if local_y < Config.info_bar_height:
            return -1
        local_y -= Config.info_bar_height
        row_height = self._spec_view.spec_height / Config.n_bins
        return min(max(int(local_y / row_height), 0), Config.n_bins - 1)

    def _is_out_of_drawing_area(self, pos_pixel: float) -> bool:
        if pos_pixel < self._scroll_offset:
            return True
        if pos_pixel > self._scroll_offset + self._scroll_view_width:
            return True
        return False

    def _fixed_update(self) -> None:
        start_pos = None

        def on_start_play() -> None:
            self._piano.notes_off()
            self._spec_view.info_overlay.finish_edit_current_info()
            update_scrollbar_interactive(False)
            self._app.view.menu.toggle_pause_resume_button(True)

        def on_playing() -> None:
            self._spec_view.info_overlay.seek_bar.pos = self._app.audio_player.playback_pos
            pos_pixel = self._spec_view.info_overlay.seek_bar.pos * self._spec_view.spec_width
            if self._is_out_of_drawing_area(pos_pixel):
                self.scroll_to(ScrollOption(ScrollOption.Destination.SEEK_BAR_CENTERED))

        def on_finish_play() -> None:
            update_scrollbar_interactive(True)
            self._app.view.menu.toggle_pause_resume_button(False)
                        
        def update_scrollbar_interactive(interactive: bool) -> None:
            self.page.theme.scrollbar_theme.interactive = interactive
            if interactive:
                self.page.theme.scrollbar_theme.thumb_color = None
            else:
                self.page.theme.scrollbar_theme.thumb_color = ft.colors.RED
            self.page.update()

        while True:
            if self._mouse_pos is not None:
                if self._mouse_pos[0] is not None:
                    self._on_update_mouse_pos(*self._mouse_pos)
                else:
                    self._unhighlight_idxs()
                self._mouse_pos = None

            if self._app.audio_player.is_playing:
                if start_pos is None:
                    start_pos = self._spec_view.info_overlay.seek_bar.pos
                    on_start_play()
                on_playing()
            elif start_pos is not None:
                self._spec_view.info_overlay.seek_bar.pos = start_pos
                start_pos = None
                on_finish_play()
                
            time.sleep(Config.update_interval)

    def _on_update_mouse_pos(self, local_x: float, local_y: float) -> None:
        if self._spec_view.is_loaded:
            pos = self._calc_pos(local_x)
            info = self._spec_view.info_overlay.get_selectable_info(pos)
            clickable = info is not None
            self._update_mouse_cursor_clickable(clickable)

        idx = self._calc_idx(local_y)
        if idx < 0:
            if self._spec_view.is_loaded:
                if info is None:
                    info = self._spec_view.info_overlay.get_info(pos)
                idxs = [idx for idx in range(Config.n_bins) if info.pitch_row_state[idx]]
            else:
                idxs = []
        else:
            idxs = [idx]

        if idxs != self._highlighted_idxs:
            self._highlight_idxs(idxs)

    def _update_mouse_cursor_clickable(self, clickable: bool) -> None:
        if clickable:
            self._gesture_detector_container.content.mouse_cursor = ft.MouseCursor.CLICK
        else:
            self._gesture_detector_container.content.mouse_cursor = ft.MouseCursor.BASIC
        self._gesture_detector_container.content.update()

    def _highlight_idxs(self, idxs: List[int]) -> None:
        self._unhighlight_idxs()
        self._keyboard.highlight_keys(idxs)
        self._spec_view.highlight_rows(idxs)
        self._highlighted_idxs = idxs

    def _unhighlight_idxs(self) -> None:
        self._keyboard.unhighlight_keys(self._highlighted_idxs)
        self._spec_view.unhighlight_rows(self._highlighted_idxs)
        self._highlighted_idxs = []

    def on_resize(self, width: ft.OptionalNumber, height: ft.OptionalNumber) -> None:
        self._scroll_view_width = width - Config.keyboard_width
        self._spec_view.on_resize(None, height - Config.scroll_bar_height)