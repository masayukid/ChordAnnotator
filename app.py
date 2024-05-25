import os
import json
from typing import Callable

import flet as ft

from controls.view import View
from controls.audio_player import AudioPlayer
from controls.custom_dialog import MessageDialog, ProgressDialog, ConfirmDialog
from commander import Commander
from config import Config
import const

class App:
    def __init__(self) -> None:
        Config.load_config_file()
        
    def run(self) -> None:
        ft.app(self._main)

    def _main(self, page: ft.Page) -> None:
        self.commander = Commander()

        page.title = Config.title
        page.window_prevent_close = True
        page.window_min_width = Config.window_min_width
        page.window_min_height = Config.window_min_height
        page.window_max_height = Config.window_max_height
        page.theme = ft.Theme(
            scrollbar_theme=ft.ScrollbarTheme(
                thumb_color=None,
                interactive=True,
            )
        )

        self.file_picker = ft.FilePicker(
            on_result=self._on_pick_file
        )
        page.overlay.append(self.file_picker)

        self.audio_player = AudioPlayer()
        page.overlay.append(self.audio_player)

        self.view = View(self)
        page.controls.append(self.view)

        page.on_keyboard_event = self._on_keyboard
        page.on_window_event = self._on_window_event
        page.on_resize = self.view.on_resize
        page.update()

        self.view.on_resize()

    def _on_keyboard(self, e: ft.KeyboardEvent) -> None:
        if e.page.dialog is not None and e.page.dialog.open:
            return
        if self.view.menu.is_dropdown_expanded:
            return
        
        match e.key:
            case ' ':
                self.view.menu.on_click_pause_resume()
            case 'C':
                if e.ctrl:
                    self.view.menu.on_click_copy_info()
                else:
                    self.view.menu.on_click_add_info()
            case 'V':
                if e.ctrl:
                    self.view.menu.on_click_paste_info()
            case 'O':
                if e.ctrl:
                    self.view.menu.on_click_open()
            case 'S':
                if e.ctrl:
                    self.view.menu.on_click_save()
            case 'Z':
                if e.ctrl:
                    if e.shift:
                        self.commander.redo()
                    else:
                        self.commander.undo()
            case 'Arrow Left':
                if e.ctrl:
                    self.view.menu.on_click_skip_start()
                else:
                    self.view.menu.on_click_skip_prev()
            case 'Arrow Right':
                if e.ctrl:
                    self.view.menu.on_click_skip_end()
                else:
                    self.view.menu.on_click_skip_next()
            case 'Delete':
                self.view.menu.on_click_delete_info()

    def _on_window_event(self, e: ft.ControlEvent) -> None:
        if e.data == 'close':
            self._with_save_confirmation(lambda: e.page.window_destroy())

    def _on_pick_file(self, e: ft.FilePickerResultEvent) -> None:
        if e.files is None:
            return
        
        path = e.files[0].path
        root, ext = os.path.splitext(path)
        if len(ext) == 0 or ext[1:] not in const.AUDIO_EXTENTIONS:
            self.view.show_dialog(
                MessageDialog(
                    title='ERROR',
                    message='Format not supported.',
                    message_type=MessageDialog.MessageType.ERROR,
                )
            )
            return

        json_path = root + '.json'
        self._with_save_confirmation(lambda: self._load(path, json_path))

    def _with_save_confirmation(self, action: Callable[[], None]) -> None:
        if self.commander.has_been_changed:
            self.view.show_dialog(
                ConfirmDialog(
                    message='Changes will not be saved. Are you sure you want to exit?',
                    on_confirm=action,
                )
            )
        else:
            action()

    def _load(self, path: str, json_path: str) -> None:
        self.commander.initialize()

        self.view.show_dialog(ProgressDialog())
        self.audio_player.load(path)
        self.view.load(path)
        self.view.close_dialog()
        
        if os.path.exists(json_path):
            self.view.show_dialog(
                ConfirmDialog(
                    message='Editing data found. Would you like to load it?',
                    on_confirm=lambda: self._load_json(json_path),
                )
            )

    def _load_json(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            duration = data['metadata']['duration']
            if duration != self.audio_player.duration / 1e3:
                self.view.show_dialog(
                    MessageDialog(
                        title='ERROR',
                        message='Audio duration has been changed.',
                        message_type=MessageDialog.MessageType.ERROR,
                    )
                )
                return
            self.view.piano_roll.spec_view.info_overlay.update_content(data['content'])

    def save(self) -> None:
        root = os.path.splitext(self.audio_player.src)[0]
        json_path = root + '.json'

        if os.path.exists(json_path):
            self.view.show_dialog(
                ConfirmDialog(
                    message='Edit file already exists. Are you sure you want to overwrite it?',
                    on_confirm=lambda: self._save_json(json_path),
                )
            )
        else:
            self._save_json(json_path)
        
    def _save_json(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as file:
            duration = self.audio_player.duration / 1e3
            content = self.view.piano_roll.spec_view.info_overlay.get_content()
            data = {
                'metadata': {
                    'duration': duration,
                },
                'content': content,
            }
            json.dump(data, file, indent=4)
        self.commander.clear_num_change()

if __name__ == '__main__':
    App().run()