import re
from typing import List, Self

from musics.pitch import Pitch, get_pitch_suggestions
from musics.chord_parser import chord_tone_from_text, text_from_chord_tone

class Chord:
    def __init__(
        self,
        root: Pitch | None = None,
        chord_tone: List[bool] | None = None,
        bass: Pitch | None = None,
    ) -> None:
        self._root = root
        self._chord_tone = chord_tone
        self._bass = bass

    @classmethod
    def from_text(cls, text: str) -> Self:
        if text == 'N.C.':
            return cls()
        
        pattern = r'(?P<root>[A-G](#{1,2}|b{1,2})?)'
        pattern += r'(?P<others>.*?)'
        pattern += r'(?P<bass>/[A-G](#{1,2}|b{1,2})?)?'
        m = re.fullmatch(pattern, text)

        if m is None:
            raise Exception('ERROR: Invalid string')
        
        root = m.group('root')
        others = m.group('others')
        bass = m.group('bass')

        if bass is None:
            bass = root
        else:
            bass = bass[1:]

        chord_tone = chord_tone_from_text(others)

        return cls(
            root=Pitch.from_text(root),
            chord_tone=chord_tone,
            bass=Pitch.from_text(bass),
        )
    
    @property
    def is_non_chord(self) -> bool:
        return self._root is None

    @property
    def root(self) -> Pitch:
        return self._root

    @property
    def chord_tone(self) -> List[bool]:
        return list(self._chord_tone)
    
    @property
    def bass(self) -> Pitch:
        return self._bass
    
    def equals(self, other: Self) -> bool:
        return self.to_string() == other.to_string()
    
    def to_string(self, key: str | None = None) -> str:
        if self.is_non_chord:
            return 'N.C.'
        
        text = self._root.to_string(key)
        text += text_from_chord_tone(list(self._chord_tone))

        if not self._bass.equals(self._root):
            text += f'/{self._bass.to_string(key)}'

        return text

def get_chord_suggestions(pitches: List[bool], bass_idx: int, key: str) -> List[Chord]:
    chords_dict = dict()
    for root_idx in range(12):
        if not pitches[root_idx]:
            continue

        chord_tone = pitches[root_idx:] + pitches[:root_idx]
        for root in get_pitch_suggestions(root_idx, key):
            for bass in get_pitch_suggestions(bass_idx, key):
                if root_idx == bass_idx and not root.equals(bass):
                    continue

                chord = Chord(
                    root=root,
                    chord_tone=chord_tone,
                    bass=bass,
                )
                
                try:
                    degree_name = chord.to_string(key)
                    degree_name = re.sub('\(omit.*\)', '', degree_name)
                    chords_dict[degree_name] = chord
                except Exception as e:
                    continue
    
    chords_sorted = []
    with open('appearance.txt', 'r') as file:
        for line in file.readlines():
            line = line.rstrip('\n')
            if line in chords_dict:
                chord = chords_dict.pop(line)
                chords_sorted.append(chord)
    for chord in chords_dict.values():
        chords_sorted.append(chord)
    return chords_sorted