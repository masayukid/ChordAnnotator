from typing import List, Self

from musics.chord import get_chord_suggestions
from utils import idx_to_midi
from config import Config

class ChordInfo:
    def __init__(self, pos: float) -> None:
        self._pos = pos
        self._prev: Self = None
        self._next: Self = None
        self._key_name_suggestions = []
        self._chord_name_suggestions = []
        self.load('C/Am', 'N.C.', [False] * Config.n_bins)

    @property
    def prev(self) -> Self:
        return self._prev
    
    @property
    def next(self) -> Self:
        return self._next
    
    @property
    def index(self) -> int:
        if self._prev is None:
            return 0
        return self._prev.index + 1

    @property
    def start_pos(self) -> float:
        return self._pos
    
    @property
    def end_pos(self) -> float:
        if self._next is None:
            return 1
        return self._next._pos
    
    @property
    def key_name_suggestions(self) -> List[str]:
        return self._key_name_suggestions
    
    @property
    def chord_name_suggestions(self) -> List[str]:
        return self._chord_name_suggestions
    
    @property
    def chord_name(self) -> str:
        return self._chord_name_suggestions[0]
    
    @property
    def key_name(self) -> str:
        return self._key_name_suggestions[0]
    
    @property
    def pitch_row_state(self) -> List[bool]:
        return self._pitch_row_state
    
    def insert(self, info: Self) -> None:
        info._prev = self
        info._next = self._next
        if self._next is not None:
            self._next._prev = info
        self._next = info
        
    def delete(self) -> None:
        if self._prev is None:
            return
        self._prev._next = self._next
        if self._next is not None:
            self._next._prev = self._prev

    def load(self, key_name: str, chord_name: str, pitch_row_state: List[bool]) -> None:
        self.set_key_name(key_name)
        self.set_chord_name(chord_name)
        self._pitch_row_state = list(pitch_row_state)
        self.update_key_name_suggestions()
        self.update_chord_name_suggestions()

    def set_key_name(self, key_name: str) -> None:
        if key_name in self._key_name_suggestions:
            self._key_name_suggestions.remove(key_name)
        self._key_name_suggestions = [key_name] + self._key_name_suggestions

    def set_chord_name(self, chord_name: str) -> None:
        if chord_name in self._chord_name_suggestions:
            self._chord_name_suggestions.remove(chord_name)
        self._chord_name_suggestions = [chord_name] + self._chord_name_suggestions

    # ==================================
    #  和音名推定アルゴリズム
    # ==================================
    def update_key_name_suggestions(self) -> None:
        suggestions = [
            'C/Am',
            'C#/A#m',
            'Db/Bbm',
            'D/Bm',
            'Eb/Cm',
            'E/C#m',
            'F/Dm',
            'F#/D#m',
            'Gb/Ebm',
            'G/Em',
            'Ab/Fm',
            'A/F#m',
            'Bb/Gm',
            'B/G#m',
            'Cb/Abm',
        ]

        if self.key_name in suggestions:
            suggestions.remove(self.key_name)
            suggestions = [self.key_name] + suggestions
        self._key_name_suggestions = suggestions

    def update_chord_name_suggestions(self) -> None:
        bass_idx = None
        pitches = [False] * 12
        for i in range(Config.n_bins):
            if self._pitch_row_state[i]:
                pitch = idx_to_midi(i) % 12
                pitches[pitch] = True
                bass_idx = pitch

        if bass_idx is None:
            self._chord_name_suggestions = ['N.C.']
        else:
            key = self.key_name.split('/')[0]
            suggestions = [chord.to_string() for chord in get_chord_suggestions(pitches, bass_idx, key)]
            if self.chord_name in suggestions:
                suggestions.remove(self.chord_name)
                suggestions = [self.chord_name] + suggestions
            self._chord_name_suggestions = suggestions