from io import BytesIO
from base64 import b64encode
from typing import List

import librosa
import numpy as np
from PIL import Image
from pydub import AudioSegment

from config import Config

def idx_to_midi(idx: int) -> int:
    return Config.midi_min + Config.n_bins - idx - 1

def np_to_base64(array: np.ndarray) -> str:
    buffer = BytesIO()
    img = Image.fromarray(array)
    img.save(buffer, 'png')
    return b64encode(buffer.getvalue()).decode('utf-8')

def min_max_normalized(spec: np.ndarray) -> np.ndarray:
    min_val = spec.min()
    val_range = spec.max() - min_val
    if val_range == 0:
        return spec - min_val
    return (spec - min_val) / val_range

def get_spectrogram(path: str) -> np.ndarray:
    audio: AudioSegment = AudioSegment.from_file(path)
    wav = audio.get_array_of_samples()
    y = np.array(wav, dtype=np.float32) / np.iinfo(wav.typecode).max
    spec = np.abs(
        librosa.cqt(
            y=y,
            sr=audio.frame_rate,
            hop_length=Config.hop_length,
            fmin=librosa.midi_to_hz(Config.midi_min),
            n_bins=Config.n_bins * Config.num_divisions,
            bins_per_octave=Config.bins_per_octave * Config.num_divisions,
        )
    )
    spec = spec[::Config.num_divisions, :]
    return np.flipud(min_max_normalized(spec))

def hex_to_pitch_row_state(hex: str) -> List[bool]:
    return [bool(int(e)) for e in format(int(hex, 16), f'0{Config.n_bins}b')]

def pitch_row_state_to_hex(pitch_row_state: List[bool]) -> str:
    return hex(int(''.join([str(int(e)) for e in pitch_row_state]), 2))