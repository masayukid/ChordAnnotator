from os import environ
from typing import List

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame.midi as midi

VOLUME = 127

class Piano:
    def __init__(self) -> None:
        midi.init()
        self._output = midi.Output(0)
        self._output.set_instrument(0)
        self._sounding_notes = []

    def notes_on(self, notes: List[int]) -> None:
        self.notes_off()
        for note in notes:
            self._output.note_on(note, VOLUME)
            if note not in self._sounding_notes:
                self._sounding_notes.append(note)
        
    def notes_off(self) -> None:
        for note in self._sounding_notes:
            self._output.note_off(note, VOLUME)