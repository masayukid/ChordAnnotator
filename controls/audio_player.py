from typing import Any
from threading import Thread

import flet as ft

import const

class AudioPlayer(ft.Audio):
    class State:
        UNLOADED = 'unloaded'
        SEEKING = 'seeking'
        PLAYING = 'playing'
        PAUSED = 'paused'

    def __init__(self) -> None:
        super().__init__(
            src_base64=const.BASE64_AUDIO_EMPTY,
            on_loaded=self._on_loaded,
            on_seek_complete=self._on_seek_complete,
        )
        self._duration = 0
        self._playback_pos = 0
        self._state = AudioPlayer.State.UNLOADED

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def playback_pos(self) -> float:
        return self._playback_pos
    
    @property
    def is_playing(self) -> bool:
        return self._state == AudioPlayer.State.PLAYING
    
    @property
    def is_paused(self) -> bool:
        return self._state == AudioPlayer.State.PAUSED
    
    def load(self, path: str) -> None:
        self._state = AudioPlayer.State.UNLOADED
        if path != self.src:
            self.src = path
            self.update()
        else:
            self._on_loaded()

    def _on_loaded(self, _: Any = None) -> None:
        if self.src is None:
            return
        
        self._duration = self.get_duration()
        self._state = AudioPlayer.State.PAUSED

    def play(self, pos: float) -> None:
        self._state = AudioPlayer.State.SEEKING
        self.seek(pos)

    def seek(self, pos: float) -> None:
        self._playback_pos = pos
        position_milliseconds = int(pos * self._duration)
        super().seek(position_milliseconds)

    def _on_seek_complete(self, _: Any = None) -> None:
        if self._state == AudioPlayer.State.SEEKING:
            self._state = AudioPlayer.State.PLAYING
            Thread(target=self._on_playing).start()
            self.resume()

    def _on_playing(self) -> None:
        while self.is_playing:
            playback_pos = min(max(self.get_current_position() / self._duration, 0), 1)
            if self._playback_pos - playback_pos > 0.99999:
                break
            self._playback_pos = playback_pos
        self.pause()

    def pause(self) -> None:
        self._state = AudioPlayer.State.PAUSED
        super().pause()