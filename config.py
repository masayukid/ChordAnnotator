import os
import configparser
from typing import Any, Callable, Generic, TypeVar

DEBUG = True

T = TypeVar("T")
R = TypeVar("R")

class classproperty(Generic[T, R]):
    def __init__(self, func: Callable[[type[T]], R]) -> None:
        self.func = func

    def __get__(self, obj: Any, cls: type[T]) -> R:
        return self.func(cls)
    
class Config:
    _config = configparser.ConfigParser()

    @classmethod
    def load_config_file(cls, path: str = 'config.ini') -> None:
        if DEBUG:
            cls._create_config_file()
        else:
            if os.path.exists(path):
                with open(path) as f:
                    Config._config.read_file(f)
            else:
                cls._create_config_file()

    @classmethod
    def save_config_file(cls, path: str = 'config.ini') -> None:
        with open(path, 'w') as file:
            cls._config.write(file)

    @classmethod
    def _create_config_file(cls) -> None:
        cls._config.add_section('app')
        cls._config.set('app', 'title', 'ChordAnnotator')
        cls._config.set('app', 'window_min_width', '1280')
        cls._config.set('app', 'window_min_height', '720')
        cls._config.set('app', 'window_max_height', '4320')
        cls._config.set('app', 'padding', '10')
        cls._config.set('app', 'spacing', '10')

        cls._config.add_section('progress_bar')
        cls._config.set('progress_bar', 'width', '400')
        
        cls._config.add_section('menu')
        cls._config.set('menu', 'height', '70')
        cls._config.set('menu', 'spacing', '40')
        cls._config.set('menu', 'popup_menu_button_size', '50')
        cls._config.set('menu', 'key_name_dropdown_width', '100')
        cls._config.set('menu', 'chord_name_dropdown_width', '220')

        cls._config.set('menu', 'sensitivity_slider_width', '120')
        cls._config.set('menu', 'sensitivity_default', '3.5')
        cls._config.set('menu', 'sensitivity_min', '2')
        cls._config.set('menu', 'sensitivity_max', '5')
        cls._config.set('menu', 'sensitivity_divisions', '6')
        
        cls._config.set('menu', 'zoom_power_slider_width', '120')
        cls._config.set('menu', 'zoom_power_default', '0')
        cls._config.set('menu', 'zoom_power_min', '-3')
        cls._config.set('menu', 'zoom_power_max', '3')
        cls._config.set('menu', 'zoom_power_divisions', '6')

        cls._config.add_section('keyboard')
        cls._config.set('keyboard', 'width', '54')

        cls._config.add_section('piano_roll')
        cls._config.set('piano_roll', 'update_interval', '0.02')
        cls._config.set('piano_roll', 'scroll_bar_height', '12')
        cls._config.set('piano_roll', 'scroll_duration', '1000')

        cls._config.add_section('spec_view')
        cls._config.set('spec_view', 'pitch_row_opacity', '0.5')

        cls._config.add_section('spectrogram')
        cls._config.set('spectrogram', 'color_map', 'jet')

        cls._config.add_section('info_overlay')
        cls._config.set('info_overlay', 'bar_height', '20')
        cls._config.set('info_overlay', 'min_interval', '100')
        cls._config.set('info_overlay', 'background_opacity', '0.4')

        cls._config.add_section('chord_info')
        cls._config.set('chord_info', 'thickness', '2')
        cls._config.set('chord_info', 'opacity', '0.8')
        cls._config.set('chord_info', 'font_size', '15')
        cls._config.set('chord_info', 'text_margin', '6')

        cls._config.add_section('seek_bar')
        cls._config.set('seek_bar', 'thickness', '2')
        cls._config.set('seek_bar', 'opacity', '1')

        cls._config.add_section('cqt')
        cls._config.set('cqt', 'n_bins', '88')
        cls._config.set('cqt', 'bins_per_octave', '12')
        cls._config.set('cqt', 'hop_length', '1024')
        cls._config.set('cqt', 'midi_min', '21')
        cls._config.set('cqt', 'num_divisions', '3')

    @classproperty
    def title(cls) -> str:
        return cls._config.get('app', 'title')
    @classproperty
    def window_min_width(cls) -> int:
        return cls._config.getint('app', 'window_min_width')
    @classproperty
    def window_min_height(cls) -> int:
        return cls._config.getint('app', 'window_min_height')
    @classproperty
    def window_max_height(cls) -> int:
        return cls._config.getint('app', 'window_max_height')
    @classproperty
    def padding(cls) -> int:
        return cls._config.getint('app', 'padding')
    @classproperty
    def spacing(cls) -> int:
        return cls._config.getint('app', 'spacing')
    
    @classproperty
    def progress_bar_width(cls) -> int:
        return cls._config.getint('progress_bar', 'width')
    
    @classproperty
    def menu_height(cls) -> int:
        return cls._config.getint('menu', 'height')
    @classproperty
    def menu_spacing(cls) -> int:
        return cls._config.getint('menu', 'spacing')
    @classproperty
    def popup_menu_button_size(cls) -> int:
        return cls._config.getint('menu', 'popup_menu_button_size')
    @classproperty
    def key_name_dropdown_width(cls) -> int:
        return cls._config.getint('menu', 'key_name_dropdown_width')
    @classproperty
    def chord_name_dropdown_width(cls) -> int:
        return cls._config.getint('menu', 'chord_name_dropdown_width')
    
    @classproperty
    def sensitivity_slider_width(cls) -> int:
        return cls._config.getint('menu', 'sensitivity_slider_width')
    @classproperty
    def sensitivity_default(cls) -> float:
        return cls._config.getfloat('menu', 'sensitivity_default')
    @classproperty
    def sensitivity_min(cls) -> float:
        return cls._config.getfloat('menu', 'sensitivity_min')
    @classproperty
    def sensitivity_max(cls) -> float:
        return cls._config.getfloat('menu', 'sensitivity_max')
    @classproperty
    def sensitivity_divisions(cls) -> int:
        return cls._config.getint('menu', 'sensitivity_divisions')
    
    @classproperty
    def zoom_power_slider_width(cls) -> int:
        return cls._config.getint('menu', 'zoom_power_slider_width')
    @classproperty
    def zoom_power_default(cls) -> float:
        return cls._config.getfloat('menu', 'zoom_power_default')
    @classproperty
    def zoom_power_min(cls) -> float:
        return cls._config.getfloat('menu', 'zoom_power_min')
    @classproperty
    def zoom_power_max(cls) -> float:
        return cls._config.getfloat('menu', 'zoom_power_max')
    @classproperty
    def zoom_power_divisions(cls) -> int:
        return cls._config.getint('menu', 'zoom_power_divisions')
    
    @classproperty
    def keyboard_width(cls) -> int:
        return cls._config.getint('keyboard', 'width')
    
    @classproperty
    def update_interval(cls) -> float:
        return cls._config.getfloat('piano_roll', 'update_interval')
    @classproperty
    def scroll_bar_height(cls) -> int:
        return cls._config.getint('piano_roll', 'scroll_bar_height')
    @classproperty
    def scroll_duration(cls) -> int:
        return cls._config.getint('piano_roll', 'scroll_duration')
    
    @classproperty
    def pitch_row_opacity(cls) -> float:
        return cls._config.getfloat('spec_view', 'pitch_row_opacity')
    
    @classproperty
    def spectrogram_color_map(cls) -> str:
        return cls._config.get('spectrogram', 'color_map')
    
    @classproperty
    def info_bar_height(cls) -> int:
        return cls._config.getint('info_overlay', 'bar_height')
    @classproperty
    def info_min_interval(cls) -> int:
        return cls._config.getint('info_overlay', 'min_interval')
    @classproperty
    def background_opacity(cls) -> float:
        return cls._config.getfloat('info_overlay', 'background_opacity')
    
    @classproperty
    def chord_info_thickness(cls) -> int:
        return cls._config.getint('chord_info', 'thickness')
    @classproperty
    def chord_info_opacity(cls) -> float:
        return cls._config.getfloat('chord_info', 'opacity')
    @classproperty
    def chord_info_font_size(cls) -> int:
        return cls._config.getint('chord_info', 'font_size')
    @classproperty
    def chord_info_text_margin(cls) -> float:
        return cls._config.getfloat('chord_info', 'text_margin')
    
    @classproperty
    def seek_bar_thickness(cls) -> int:
        return cls._config.getint('seek_bar', 'thickness')
    @classproperty
    def seek_bar_opacity(cls) -> float:
        return cls._config.getfloat('seek_bar', 'opacity')
    
    @classproperty
    def n_bins(cls) -> int:
        return cls._config.getint('cqt', 'n_bins')
    @classproperty
    def bins_per_octave(cls) -> int:
        return cls._config.getint('cqt', 'bins_per_octave')
    @classproperty
    def hop_length(cls) -> int:
        return cls._config.getint('cqt', 'hop_length')
    @classproperty
    def midi_min(cls) -> int:
        return cls._config.getint('cqt', 'midi_min')
    @classproperty
    def num_divisions(cls) -> int:
        return cls._config.getint('cqt', 'num_divisions')