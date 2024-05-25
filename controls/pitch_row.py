import flet as ft

class PitchRow(ft.UserControl):
    def __init__(self, default_bgcolor, highlighted_bgcolor) -> None:
        super().__init__(expand=True)
        self._default_bgcolor = default_bgcolor
        self._highlighted_bgcolor = highlighted_bgcolor
        self._is_highlighted = False
        
    def build(self) -> ft.Control:
        self._content = ft.Container(
            bgcolor=self._default_bgcolor,
        )
        return self._content
    
    @property
    def is_highlighted(self) -> bool:
        return self._is_highlighted
    
    @is_highlighted.setter
    def is_highlighted(self, is_highlighted: bool) -> None:
        if self._is_highlighted != is_highlighted:
            self._is_highlighted = is_highlighted
            if is_highlighted:
                self._content.bgcolor = self._highlighted_bgcolor
            else:
                self._content.bgcolor = self._default_bgcolor
            self._content.update()