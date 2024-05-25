from typing import List

import flet as ft

from controls.pitch_row import PitchRow
from config import Config

class Key(PitchRow):
    def __init__(self, bgcolor: str) -> None:
        super().__init__(bgcolor, ft.colors.RED)

class WhiteKey(Key):
    def __init__(self) -> None:
        super().__init__(ft.colors.WHITE)

    def build(self) -> ft.Control:
        super().build()
        self._content.border = ft.border.all(0.5, ft.colors.GREY_500)
        return self._content

class BlackKey(Key):
    def __init__(self) -> None:
        super().__init__(ft.colors.BLACK)
        self.expand = 2

class Keyboard(ft.UserControl):
    def __init__(self) -> None:
        super().__init__(width=Config.keyboard_width)
        self._keys = []
        
    def build(self) -> ft.Control:
        self._white_keys = ft.Column(spacing=0)
        self._black_keys = ft.Column(width=Config.keyboard_width * 2 / 3, spacing=0)

        self._black_keys.controls.append(ft.Container(expand=2))
        for i in reversed(range(Config.n_bins)):
            midi_idx = Config.midi_min + i
            pitch_class = midi_idx % 12
            if pitch_class in [0, 2, 4, 5, 7, 9, 11]:
                key = WhiteKey()
                self._white_keys.controls.append(key)
            else:
                if pitch_class in [3, 10]:
                    self._black_keys.controls.append(ft.Container(expand=3))
                key = BlackKey()
                self._black_keys.controls.append(key)
                self._black_keys.controls.append(ft.Container(expand=1))
            self._keys.append(key)
        self._black_keys.controls.append(ft.Container(expand=1))

        self._content = [
            self._white_keys,
            self._black_keys,
        ]
        return self._content
    
    def highlight_keys(self, idxs: List[int]) -> None:
        for idx in idxs:
            self._keys[idx].is_highlighted = True

    def unhighlight_keys(self, idxs: List[int]) -> None:
        for idx in idxs:
            self._keys[idx].is_highlighted = False