from typing import TYPE_CHECKING, List, Any

import flet as ft

if TYPE_CHECKING:
    from app import App
from controls.custom_dialog import ProgressDialog
from controls.piano_roll import ScrollOption
from config import Config
import const

class Menu(ft.UserControl):
    class PopupMenuState:
        UNLOADED = 0
        SAVABLE = 1

    def __init__(self, app: 'App') -> None:
        super().__init__(height=Config.menu_height)
        self._app = app
        self._is_dropdown_expanded = False
        self._popup_menu_state = Menu.PopupMenuState.UNLOADED

    def build(self) -> ft.Control:
        self._popup_menu_item_list = [
            (0, ft.PopupMenuItem(
                icon=ft.icons.AUDIO_FILE_OUTLINED,
                text='Open',
                on_click=self.on_click_open)),
            (1, ft.PopupMenuItem(
                icon=ft.icons.SAVE_OUTLINED,
                text='Save',
                on_click=self.on_click_save)),
            (0, ft.PopupMenuItem()),
            (0, ft.PopupMenuItem(
                icon=ft.icons.EXIT_TO_APP,
                text='Exit',
                on_click=lambda _: self.page.window_close())),
        ]
        self._popup_menu = ft.PopupMenuButton(
            width=Config.popup_menu_button_size,
            items=self._get_popup_menu_items(),
        )

        self._skip_start_button = ft.IconButton(
            icon=ft.icons.SKIP_PREVIOUS,
            on_click=self.on_click_skip_start,
            disabled=True,
        )
        self._skip_prev_button = ft.IconButton(
            icon=ft.icons.FAST_REWIND,
            on_click=self.on_click_skip_prev,
            disabled=True,
        )
        self._pause_resume_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            on_click=self.on_click_pause_resume,
            disabled=True,
        )
        self._skip_next_button = ft.IconButton(
            icon=ft.icons.FAST_FORWARD,
            on_click=self.on_click_skip_next,
            disabled=True,
        )
        self._skip_end_button = ft.IconButton(
            icon=ft.icons.SKIP_NEXT,
            on_click=self.on_click_skip_end,
            disabled=True,
        )

        self._add_info_button = ft.IconButton(
            icon=ft.icons.ADD_OUTLINED,
            icon_color=ft.colors.GREY,
            on_click=self.on_click_add_info,
            disabled=True,
        )
        self._delete_info_button = ft.IconButton(
            icon=ft.icons.DELETE_OUTLINED,
            icon_color=ft.colors.GREY,
            on_click=self.on_click_delete_info,
            disabled=True,
        )
        self._copy_info_button = ft.IconButton(
            icon=ft.icons.COPY,
            on_click=self.on_click_copy_info,
            disabled=True,
        )
        self._paste_info_button = ft.IconButton(
            icon=ft.icons.PASTE,
            on_click=self.on_click_paste_info,
            disabled=True,
        )

        self._key_name_dropdown = ft.Dropdown(
            width=Config.key_name_dropdown_width,
            on_focus=self._on_focus_dropdown,
            on_change=self._on_key_name_selected,
            disabled=True,
        )
        self._dummy_button = ft.ElevatedButton(
            width=Config.spacing,
            opacity=0,
        )
        self._chord_name_dropdown = ft.Dropdown(
            width=Config.chord_name_dropdown_width,
            on_focus=self._on_focus_dropdown,
            on_change=self._on_chord_name_selected,
            disabled=True,
        )

        self._sensitivity_slider = ft.Slider(
            value=Config.sensitivity_default,
            width=Config.sensitivity_slider_width,
            min=Config.sensitivity_min,
            max=Config.sensitivity_max,
            divisions=Config.sensitivity_divisions,
            on_change_end=self._on_sensitivity_changed,
        )
        self._zoom_out_button = ft.IconButton(
            icon=ft.icons.ZOOM_OUT,
            on_click=self.on_click_zoom_out,
        )
        self._zoom_power_slider = ft.Slider(
            value=Config.zoom_power_default,
            width=Config.zoom_power_slider_width,
            min=Config.zoom_power_min,
            max=Config.zoom_power_max,
            divisions=Config.zoom_power_divisions,
            on_change_end=self._on_zoom_power_changed,
        )
        self._zoom_in_button = ft.IconButton(
            icon=ft.icons.ZOOM_IN,
            on_click=self.on_click_zoom_in,
        )

        left_controls = ft.Row(
            controls=[
                self._skip_start_button,
                self._skip_prev_button,
                self._pause_resume_button,
                self._skip_next_button,
                self._skip_end_button,
                ft.VerticalDivider(width=Config.menu_spacing),
                self._add_info_button,
                self._delete_info_button,
                self._copy_info_button,
                self._paste_info_button,
                ft.VerticalDivider(width=Config.menu_spacing),
                self._key_name_dropdown,
                self._dummy_button,
                self._chord_name_dropdown,
            ],
            spacing=0,
        )
        right_controls = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.icons.REMOVE_RED_EYE_OUTLINED,
                    color=ft.colors.GREY_800,
                ),
                self._sensitivity_slider,
                ft.VerticalDivider(width=Config.menu_spacing),
                self._zoom_out_button,
                self._zoom_power_slider,
                self._zoom_in_button,
            ],
            spacing=0,
        )
        controls = ft.Row(
            controls=[
                left_controls,
                right_controls,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
        )
        return ft.Row(
            controls=[
                self._popup_menu,
                controls,
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=Config.spacing,
        )
    
    @property
    def is_dropdown_expanded(self) -> bool:
        return self._is_dropdown_expanded
    
    @property
    def sensitivity(self) -> float:
        slider = self._sensitivity_slider
        return slider.min + slider.max - slider.value
    
    @property
    def zoom_power(self) -> float:
        return self._zoom_power_slider.value

    def update_popup_menu_state(self, popup_menu_state: int) -> None:
        self._popup_menu_state = popup_menu_state
        self._popup_menu.items = self._get_popup_menu_items()
        self._popup_menu.update()
    
    def _get_popup_menu_items(self) -> List[ft.Control]:
        items = []
        for state, item in self._popup_menu_item_list:
            if state <= self._popup_menu_state:
                items.append(item)
        return items
    
    def update_skip_start_button_enabled(self, enabled: bool) -> None:
        self._skip_start_button.disabled = not enabled
        self._skip_start_button.update()

    def update_skip_prev_button_enabled(self, enabled: bool) -> None:
        self._skip_prev_button.disabled = not enabled
        self._skip_prev_button.update()

    def update_pause_resume_button_enabled(self, enabled: bool) -> None:
        self._pause_resume_button.disabled = not enabled
        self._pause_resume_button.update()

    def toggle_pause_resume_button(self, is_playing: bool) -> None:
        if is_playing:
            self._pause_resume_button.icon = ft.icons.STOP
        else:
            self._pause_resume_button.icon = ft.icons.PLAY_ARROW
        self._pause_resume_button.update()

    def update_skip_next_button_enabled(self, enabled: bool) -> None:
        self._skip_next_button.disabled = not enabled
        self._skip_next_button.update()

    def update_skip_end_button_enabled(self, enabled: bool) -> None:
        self._skip_end_button.disabled = not enabled
        self._skip_end_button.update()

    def update_add_info_button_enabled(self, enabled: bool) -> None:
        self._add_info_button.disabled = not enabled
        if enabled:
            self._add_info_button.icon = ft.icons.ADD_BOX_OUTLINED
            self._add_info_button.icon_color = ft.colors.BLUE
        else:
            self._add_info_button.icon = ft.icons.ADD
            self._add_info_button.icon_color = ft.colors.GREY
        self._add_info_button.update()

    def update_delete_info_button_enabled(self, enabled: bool) -> None:
        self._delete_info_button.disabled = not enabled
        if enabled:
            self._delete_info_button.icon = ft.icons.DELETE
            self._delete_info_button.icon_color = ft.colors.RED
        else:
            self._delete_info_button.icon = ft.icons.DELETE_OUTLINED
            self._delete_info_button.icon_color = ft.colors.GREY
        self._delete_info_button.update()

    def update_copy_info_button_enabled(self, enabled: bool) -> None:
        self._copy_info_button.disabled = not enabled
        self._copy_info_button.update()

    def update_paste_info_button_enabled(self, enabled: bool) -> None:
        self._paste_info_button.disabled = not enabled
        self._paste_info_button.update()

    def update_key_name_dropdown_enabled(self, enabled: bool) -> None:
        self._key_name_dropdown.disabled = not enabled
        self._key_name_dropdown.update()

    def update_chord_name_dropdown_enabled(self, enabled: bool) -> None:
        self._chord_name_dropdown.disabled = not enabled
        self._chord_name_dropdown.update()

    def update_key_name_dropdown_options(self, options: List[ft.dropdown.Option]) -> None:
        self._key_name_dropdown.options = options
        self._key_name_dropdown.value = options[0].text
        self._key_name_dropdown.update()

    def update_chord_name_dropdown_options(self, options: List[ft.dropdown.Option]) -> None:
        self._chord_name_dropdown.options = options
        self._chord_name_dropdown.value = options[0].text
        self._chord_name_dropdown.update()
    
    def on_click_open(self, _: Any = None) -> None:
        self._app.file_picker.pick_files(
            allowed_extensions=const.AUDIO_EXTENTIONS,
            allow_multiple=False,
        )

    def on_click_save(self, _: Any = None) -> None:
        if self._popup_menu_state != Menu.PopupMenuState.SAVABLE:
            return
        
        self._app.save()
    
    def on_click_skip_start(self, _: Any = None) -> None:
        if self._skip_start_button.disabled:
            return
        
        self._app.view.piano_roll.skip_to_start()
    
    def on_click_skip_prev(self, _: Any = None) -> None:
        self._dummy_button.focus()
        if self._skip_prev_button.disabled:
            return
        
        self._app.view.piano_roll.skip_to_prev()
    
    def on_click_pause_resume(self, _: Any = None) -> None:
        if self._pause_resume_button.disabled:
            return
        
        self._app.view.piano_roll.pause_resume()
    
    def on_click_skip_next(self, _: Any = None) -> None:
        self._dummy_button.focus()
        if self._skip_next_button.disabled:
            return
        
        self._app.view.piano_roll.skip_to_next()
    
    def on_click_skip_end(self, _: Any = None) -> None:
        if self._skip_end_button.disabled:
            return
        
        self._app.view.piano_roll.skip_to_end()
    
    def on_click_add_info(self, _: Any = None) -> None:
        if self._add_info_button.disabled:
            return
               
        self._app.view.piano_roll.spec_view.info_overlay.send_add_info_command()
        
    def on_click_delete_info(self, _: Any = None) -> None:
        if self._delete_info_button.disabled:
            return
        
        self._app.view.piano_roll.spec_view.info_overlay.send_delete_info_command()
        
    def on_click_copy_info(self, _: Any = None) -> None:
        if self._copy_info_button.disabled:
            return
        
        self._app.view.piano_roll.spec_view.info_overlay.copy_to_clipboard()
        
    def on_click_paste_info(self, _: Any = None) -> None:
        if self._paste_info_button.disabled:
            return
        
        self._app.view.piano_roll.spec_view.info_overlay.send_paste_info_command()
    
    def _on_focus_dropdown(self, _: Any) -> None:
        if not self._is_dropdown_expanded:
            self._is_dropdown_expanded = True
        else:
            self._is_dropdown_expanded = False
            self._dummy_button.focus()
            
    def _on_key_name_selected(self, _: Any) -> None:
        key_name = self._key_name_dropdown.value
        self._app.view.piano_roll.spec_view.info_overlay.send_select_key_name_command(key_name)

    def _on_chord_name_selected(self, _: Any) -> None:
        chord_name = self._chord_name_dropdown.value
        self._app.view.piano_roll.spec_view.info_overlay.send_select_chord_name_command(chord_name)

    def _on_sensitivity_changed(self, _: Any = None) -> None:
        if self._app.view.piano_roll.spec_view.is_loaded:
            self._app.view.show_dialog(ProgressDialog())
            self._app.view.piano_roll.spec_view.update_spec_image()
            self._app.view.close_dialog()

    def on_click_zoom_out(self, _: Any = None) -> None:
        if self._zoom_out_button.disabled:
            return
        
        step = (Config.zoom_power_max - Config.zoom_power_min) / Config.zoom_power_divisions
        self._zoom_power_slider.value -= step
        self._zoom_power_slider.update()
        self._on_zoom_power_changed()

    def on_click_zoom_in(self, _: Any = None) -> None:
        if self._zoom_in_button.disabled:
            return
        
        step = (Config.zoom_power_max - Config.zoom_power_min) / Config.zoom_power_divisions
        self._zoom_power_slider.value += step
        self._zoom_power_slider.update()
        self._on_zoom_power_changed()

    def _on_zoom_power_changed(self, _: Any = None) -> None:
        self._update_zoom_buttons()
        if self._app.view.piano_roll.spec_view.is_loaded:
            self._app.view.piano_roll.spec_view.update_spec_width()
            self._app.view.piano_roll.scroll_to(
                ScrollOption(
                    destination=ScrollOption.Destination.SEEK_BAR_CENTERED,
                    immediate=True,
                    forced=True,
                )
            )

    def _update_zoom_buttons(self) -> None:
        can_zoom_in = self._zoom_power_slider.value < self._zoom_power_slider.max
        self._zoom_in_button.disabled = not can_zoom_in
        self._zoom_in_button.update()
        can_zoom_out = self._zoom_power_slider.value > self._zoom_power_slider.min
        self._zoom_out_button.disabled = not can_zoom_out
        self._zoom_out_button.update()