from typing import Any, TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from app import App
from controls.menu import Menu
from controls.piano_roll import PianoRoll, ScrollOption
from utils import get_spectrogram
from config import Config

class View(ft.UserControl):
    def __init__(self, app: 'App') -> None:
        super().__init__(expand=True)
        self._app = app

    def build(self) -> ft.Control:
        self._menu = Menu(self._app)
        self._piano_roll = PianoRoll(self._app)
        return ft.Column(
            controls=[
                self._menu,
                self._piano_roll,
            ],
            spacing=Config.spacing,
        )
    
    @property
    def menu(self) -> Menu:
        return self._menu
    
    @property
    def piano_roll(self) -> PianoRoll:
        return self._piano_roll

    def show_dialog(self, dialog: ft.AlertDialog) -> None:
        self.page.show_dialog(dialog)

    def close_dialog(self) -> None:
        self.page.close_dialog()
    
    def load(self, path: str) -> None:
        spec = get_spectrogram(path)
        self._piano_roll.spec_view.load_spec(spec)
        self._piano_roll.scroll_to(
            ScrollOption(
                destination=ScrollOption.Destination.SEEK_BAR_POS,
                immediate=True,
                forced=True,
            )
        )
        self._menu.update_popup_menu_state(Menu.PopupMenuState.SAVABLE)

    def on_resize(self, _: Any = None) -> None:
        width = self.page.width - Config.padding * 2
        height = self.page.height - Config.padding * 2
        self._piano_roll.on_resize(width, height - Config.menu_height - Config.spacing)