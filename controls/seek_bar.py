from typing import Callable

import flet as ft

from config import Config

class SeekBar(ft.Container):
    def __init__(self, on_update_position: Callable[[float], None]) -> None:
        super().__init__(
            content=ft.VerticalDivider(
                width=Config.seek_bar_thickness,
                thickness=Config.seek_bar_thickness,
                opacity=Config.seek_bar_opacity,
                color=ft.colors.RED,
            ),
            alignment=ft.alignment.center_left,
        )
        self._on_update_position = on_update_position
        
    @property
    def pos(self) -> float:
        return (self.alignment.x + 1) / 2
    
    @pos.setter
    def pos(self, pos: float) -> None:
        self.alignment.x = (pos * 2) - 1
        self.update()
        self._on_update_position(pos)