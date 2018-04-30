import librosa
import numpy as np
from tqdm import tqdm

def wav2mfcc(file_path, max_pad_len=100, rate=16000):
    wave, sr = librosa.load(file_path, mono=True, sr=None)
    wave = wave[::3]
    mfcc = librosa.feature.mfcc(wave, sr=rate)
    pad_width = max_pad_len - mfcc.shape[1]
    print(mfcc.shape)
    if pad_width < 0:
        mfcc = np.zeros((mfcc.shape[0], max_pad_len))
    else:
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
    return mfcc
