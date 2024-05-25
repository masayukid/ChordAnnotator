import flet as ft

from typing import Callable

from config import Config

class ProgressDialog(ft.AlertDialog):
    def __init__(self) -> None:
        super().__init__(
            modal=True,
            title=ft.Text('Loading...'),
            content=ft.ProgressBar(
                width=Config.progress_bar_width,
            ),
        )

class MessageDialog(ft.AlertDialog):
    class MessageType:
        INFOMATION = 'infomation'
        SUCCESS = 'success'
        WARNING = 'warning'
        ERROR = 'error'

    def __init__(self, title: str, message: str, message_type: str) -> None:
        super().__init__(
            modal=True,
            title=ft.Row (
                controls=[
                    self._get_icon(message_type),
                    ft.Text(title),
                ]
            ),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Close", on_click=self._on_click_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _get_icon(self, message_type: str) -> ft.Icon:
        match message_type:
            case MessageDialog.MessageType.INFOMATION:
                return ft.Icon(ft.icons.INFO_OUTLINED, color=ft.colors.GREY)
            case MessageDialog.MessageType.SUCCESS:
                return ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINED, color=ft.colors.GREEN)
            case MessageDialog.MessageType.WARNING:
                return ft.Icon(ft.icons.WARNING_AMBER, color=ft.colors.YELLOW)
            case MessageDialog.MessageType.ERROR:
                return ft.Icon(ft.icons.ERROR_OUTLINED, color=ft.colors.RED)

    def _on_click_close(self, e: ft.ControlEvent) -> None:
        self.open = False
        self.update()

class ConfirmDialog(ft.AlertDialog):
    def __init__(self, message: str, on_confirm: Callable[[], None]) -> None:
        super().__init__(
            modal=True,
            title=ft.Text('Confirmation'),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=self._on_click_ok),
                ft.TextButton("Cancel", on_click=self._on_click_cancel),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._on_confirm = on_confirm

    def _on_click_ok(self, e: ft.ControlEvent) -> None:
        self.open = False
        self.update()
        self._on_confirm()
        
    def _on_click_cancel(self, e: ft.ControlEvent) -> None:
        self.open = False
        self.update()