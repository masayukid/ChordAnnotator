import re
from typing import List, Self

PITCH_SYMBOLS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
DEGREE_SYMBOLS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
INTERVALS = [2, 2, 1, 2, 2, 2, 1]
KEY_DICT = {
    'Am': 'C',
    'A#m': 'C#',
    'Bbm': 'Db',
    'Bm': 'D',
    'Cm': 'Eb',
    'C#m': 'E',
    'Dm': 'F',
    'D#m': 'F#',
    'Ebm': 'Gb',
    'Em': 'G',
    'Fm': 'Ab',
    'F#m': 'A',
    'Gm': 'Bb',
    'G#m': 'B',
    'Abm': 'Cb',
}

class Pitch:
    def __init__(self, symbol: str, accidental: str) -> None:
        self._symbol = symbol
        self._accidental = accidental

    @classmethod
    def from_text(cls, text: str) -> Self:
        m = re.fullmatch(r'(?P<symbol>[A-G])(?P<accidental>#{,2}|b{,2})', text)
        if m is None:
            raise Exception('ERROR: Invalid string')
        return cls(m.group('symbol'), m.group('accidental'))
    
    def equals(self, other: Self) -> bool:
        return self._symbol == other._symbol and self._accidental == other._accidental

    def calc_interval(self, other: Self) -> int:
        return (self.get_pitch_idx() - other.get_pitch_idx() + 6) % 12 - 6
    
    def sharp(self) -> None:
        if len(self._accidental) > 0 and self._accidental[0] == 'b':
            self._accidental = self._accidental[:-1]
        else:
            self._accidental += '#'

    def flat(self) -> None:
        if len(self._accidental) > 0 and self._accidental[0] == '#':
            self._accidental = self._accidental[:-1]
        else:
            self._accidental += 'b'
    
    def get_pitch_idx(self) -> int:
        pitch_idx = 0
        idx = PITCH_SYMBOLS.index(self._symbol)
        for i in range(idx):
            pitch_idx += INTERVALS[i]
        if len(self._accidental) > 0:
            if self._accidental[0] == '#':
                pitch_idx += len(self._accidental)
            else:
                pitch_idx -= len(self._accidental)
        return pitch_idx % 12
            
    def to_string(self, key: str | None = None) -> str:
        if key is None:
            return self._symbol + self._accidental
        scale = get_major_scale(key)
        for i in range(7):
            if self._symbol == scale[i]._symbol:
                diff = self.calc_interval(scale[i])
                if diff < 0:
                    repl_text = 'b' * abs(diff)
                else:
                    repl_text = '#' * diff
                repl_text += DEGREE_SYMBOLS[i]
                return repl_text

def get_major_scale(key: str) -> List[Pitch]:
    scale = []
    key = KEY_DICT.get(key, key)
    idx = PITCH_SYMBOLS.index(key[0])
    interval = Pitch.from_text(key[0]).calc_interval(Pitch.from_text(key))
    for i in range(7):
        symbol = PITCH_SYMBOLS[(idx + i) % 7]
        diff = sum(INTERVALS[:i]) - interval
        if diff > 0:
            scale.append(Pitch(symbol, '#' * diff))
        else:
            scale.append(Pitch(symbol, 'b' * abs(diff)))
        interval += INTERVALS[(idx + i) % 7]
    return scale

def get_pitch_suggestions(pitch_idx: int, key: str) -> List[Pitch]:
    pitches = []
    scale = get_major_scale(key)
    for pitch in scale:
        if pitch.get_pitch_idx() == pitch_idx:
            return [pitch]
        interval = (pitch_idx - pitch.get_pitch_idx() + 6) % 12 - 6
        if interval == -1:
            pitch.flat()
            pitches.append(pitch)
        if interval == 1:
            pitch.sharp()
            pitches.append(pitch)
    return pitches