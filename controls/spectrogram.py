import flet as ft
import numpy as np
import matplotlib as mpl

from utils import np_to_base64
from config import Config
import const

class Spectrogram(ft.UserControl):
    def __init__(self) -> None:
        super().__init__()
        self._repeat_times = 0
    
    def build(self):
        self._content = ft.Image(
            src_base64=const.BASE64_IMAGE_EMPTY,
            fit=ft.ImageFit.FILL,
            left=0,
            top=0,
            right=0,
            bottom=0,
        )
        return self._content
    
    def update_image(self, spec: np.ndarray) -> None:
        image = mpl.colormaps[Config.spectrogram_color_map](spec)
        image = (image * np.iinfo(np.uint8).max).astype(np.uint8)
        image = image.repeat(self._repeat_times, axis=0)
        self._content.src_base64 = np_to_base64(image)
        self._content.update()

    def on_resize(self, _: None, height: ft.OptionalNumber) -> None:
        self._repeat_times = height / Config.n_bins