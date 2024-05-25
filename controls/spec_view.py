from typing import List, TYPE_CHECKING

import flet as ft
import numpy as np
import librosa

if TYPE_CHECKING:
    from app import App
from controls.pitch_row import PitchRow
from controls.spectrogram import Spectrogram
from controls.info_overlay import InfoOverlay
from utils import min_max_normalized
from config import Config

class SpecView(ft.UserControl):
    def __init__(self, app: 'App') -> None:
        super().__init__()
        self._app = app
        self._spec = None

    def build(self):
        self._spectrogram = Spectrogram()
        self._info_overlay = InfoOverlay(self._app)
        self._pitch_rows = ft.Column(
            controls=[
                PitchRow(ft.colors.TRANSPARENT, ft.colors.WHITE) for _ in range(Config.n_bins)
            ],
            opacity=Config.pitch_row_opacity,
            spacing=0,
        )
        return ft.Stack(
            controls=[
                ft.Container(
                    content=self._spectrogram,
                    margin=ft.margin.only(top=Config.info_bar_height),
                ),
                self._info_overlay,
                ft.Container(
                    content=self._pitch_rows,
                    margin=ft.margin.only(top=Config.info_bar_height),
                ),
            ]
        )
    
    @property
    def info_overlay(self) -> InfoOverlay:
        return self._info_overlay
    
    @property
    def is_loaded(self) -> bool:
        return self._spec is not None
    
    @property
    def spec_width(self) -> ft.OptionalNumber:
        return self.width
    
    @property
    def spec_height(self) -> ft.OptionalNumber:
        return self._spec_height
    
    def load_spec(self, spec: np.ndarray) -> None:
        self._info_overlay.initialize()
        self._spec = spec
        self.update_spec_image()
        self.update_spec_width()
        
    def update_spec_image(self) -> None:
        spec = librosa.power_to_db(self._spec ** self._app.view.menu.sensitivity)
        spec = min_max_normalized(spec)
        self._spectrogram.update_image(spec)

    def update_spec_width(self) -> None:
        self.width = self._spec.shape[1] * 2 ** self._app.view.menu.zoom_power
        self.update()
        self._info_overlay.on_update_width(self.width)

    def highlight_rows(self, idxs: List[int]) -> None:
        for idx in idxs:
            self._pitch_rows.controls[idx].is_highlighted = True

    def unhighlight_rows(self, idxs: List[int]) -> None:
        for idx in idxs:
            self._pitch_rows.controls[idx].is_highlighted = False
    
    def on_resize(self, _: None, height: ft.OptionalNumber) -> None:
        self._spec_height = height - Config.info_bar_height
        self._spectrogram.on_resize(None, self._spec_height)
        if self.is_loaded:
            self.update_spec_image()