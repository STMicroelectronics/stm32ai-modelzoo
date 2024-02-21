#!/usr/bin/env python
# coding: utf-8

#   This software component is licensed by ST under BSD 3-Clause license,
#   the "License"; You may not use this file except in compliance with the
#   License. You may obtain a copy of the License at:
#                        https://opensource.org/licenses/BSD-3-Clause


"""ASC Feature Extraction example."""

import matplotlib.pyplot as plt
import numpy as np
import sys
import librosa
import librosa.display
import scipy.fftpack as fft

SR = 16000
N_FFT = 1024
N_MELS = 30


def create_col(y):
    assert y.shape == (1024,)

    # Create time-series window
    fft_window = librosa.filters.get_window('hann', N_FFT, fftbins=True)
    assert fft_window.shape == (1024,), fft_window.shape

    # Hann window
    y_windowed = fft_window * y
    assert y_windowed.shape == (1024,), y_windowed.shape

    # FFT
    fft_out = fft.fft(y_windowed, axis=0)[:513]
    assert fft_out.shape == (513,), fft_out.shape

    # Power spectrum
    S_pwr = np.abs(fft_out)**2

    assert S_pwr.shape == (513,)

    # Generation of Mel Filter Banks
    mel_basis = librosa.filters.mel(SR, n_fft=N_FFT, n_mels=N_MELS, htk=False)
    assert mel_basis.shape == (30, 513)

    # Apply Mel Filter Banks
    S_mel = np.dot(mel_basis, S_pwr)
    S_mel.astype(np.float32)
    assert S_mel.shape == (30,)

    return S_mel


def feature_extraction(y):
    assert y.shape == (1024, 32)

    S_mel = np.empty((30, 32), dtype=np.float32, order='C')
    for col_index in range(0, 32):
        S_mel[:, col_index] = create_col(y[:, col_index])

    # Scale according to reference power
    S_mel = S_mel / S_mel.max()
    # Convert to dB
    S_log_mel = librosa.power_to_db(S_mel, top_db=80.0)
    assert S_log_mel.shape == (30, 32)

    return S_log_mel


if __name__ == '__main__':

    wav_filename = sys.argv[1]
    if len(sys.argv) < 1:
        print('Filename not specified')
        exit(1)

    # Load audio file as a floating point time series
    y, _ = librosa.load(wav_filename, sr=SR, mono=True, dtype=np.float32)

    # Slice into overlapping frames
    frames = librosa.util.frame(y, frame_length=N_FFT, hop_length=512)

    # Extract features from overlapping frames (drop end-of-file samples)
    # S_log_Mel[0] = first feature (30x32) matrix
    # S_log_Mel[1] = second feature (30x32) matrix
    # ...
    nb_features = int(frames.shape[1] / 32)
    S_log_mel = np.empty((nb_features, 30, 32), dtype=np.float32, order='C')
    for i in range(0, nb_features):
        frame = frames[:, 0 + i:32 + i]
        S_log_mel[i] = feature_extraction(frame)

    # Plot first feature/spectrogram
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(S_log_mel[0], sr=SR, y_axis='mel', fmax=8000,
                             x_axis='time', cmap='viridis')
    # plt.pcolormesh(S_log_Mel[0])
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel spectrogram')
    plt.tight_layout()

    plt.show()
