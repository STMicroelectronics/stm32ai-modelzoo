# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

'''Contains functions to extract spectral features from an audio signal'''

import librosa
import numpy as np
import warnings

def compute_mel_spectrogram(wave,
                            sr, 
                            n_fft, 
                            hop_length,
                            win_length=None,
                            window='hann',
                            center=True,
                            pad_mode='constant',
                            power=2.0,
                            n_mels=64,
                            fmin=20,
                            fmax=20000,
                            power_to_db_ref = np.max,
                            norm="slaney",
                            htk=False,
                            to_db=True,
                            **kwargs):

    '''Wrapped around the librosa melspectrogram function. Computes power or amplitude mel spectrograms.
        For more information on arguments which are passed to librosa.feature.melspectrogram, 
        consult its documentation here https://librosa.org/doc/0.9.2/generated/librosa.feature.melspectrogram.html#librosa.feature.melspectrogram
        
        
        Inputs
        ------
        wave : 1D ndarray : Waveform to be converted to spectrogram
        sr : int, sampling rate of wave,
        n_fft : int, length of FFT window, passed to librosa.feature.melspectrogram
        hop_length : int, hop length between FFTs, passed to librosa.feature.melspectrogram
        win_length : int, passed to librosa.feature.melspectrogram. If None default to n_fft
        window : str, passed to librosa.feature.melspectrogram
        center : bool, passed to librosa.feature.melspectrogram 
        pad_mode : str, passed to librosa.feature.melspectrogram
        power : float, 1.0 or 2.0 only are allowed. Set to 2.O for power melspectrogram, 
            and 1.0 for amplitude melspectrogram
        n_mels : int, number of mel filters. passed to librosa.feature.melspectrogram
        fmin : int, min freq of spectrogram, passed to librosa.feature.melspectrogram
        fmax : int, max freq of spectrogram, passed to librosa.feature.melspectrogram
        power_to_db_ref, : func, used to convert linear scale mel spectrogram to db scale. 
                Passed to passed to librosa.power_to_db or librosa.amplitude_to_db
        
        Outputs
        -------
        db_melspec : 2D array of shape (n_mels, n_frames). 
            Decibel-scale mel spectrogram of input waveform.
        '''

    melspec = librosa.feature.melspectrogram(y=wave, 
                                            sr=sr, 
                                            n_fft=n_fft,
                                            hop_length=hop_length,
                                            win_length=win_length,
                                            window=window,
                                            center=center,
                                            pad_mode=pad_mode,
                                            power=power,
                                            n_mels=n_mels,
                                            fmin=fmin,
                                            fmax=fmax,
                                            norm=norm,
                                            htk=htk,
                                            **kwargs)
    if to_db:
        if power == 2.0:
            db_melspec = librosa.power_to_db(melspec, ref=power_to_db_ref)
        elif power == 1.0:
            db_melspec = librosa.amplitude_to_db(melspec, ref=power_to_db_ref)
        else:
            raise ValueError('Power must be either 2.0 or 1.0')
        return db_melspec
    else:
        return np.log(melspec + 1e-4)


def get_patches(wave,
                sr,
                patch_length,
                overlap,
                n_fft, 
                hop_length,
                include_last_patch=False,
                win_length=None,
                window='hann',
                center=True,
                pad_mode='constant',
                power=2.0,
                n_mels=64,
                fmin=20,
                fmax=20000,
                power_to_db_ref = np.max,
                norm="slaney",
                htk=False,
                to_db=True,
                **kwargs):
    ''' Converts a waveform into several dB-scale mel-spectrogram patches of specified length.
        Patches can overlap as specified by the user.

        Inputs
        ------
        wave : 1D ndarray : Waveform to be converted to spectrogram
        sr : int, sampling rate of wave,
        patch_length : int, number of spectrogram frames per patch.
                       Note that the length is specified in frames, e.g. if each frame in 
                       the spectrogram represents 50 ms, a patch of 1s would need 20 frames. 

        overlap : float between 0 and 1.0, proportion of overlap between consecutive spectrograms.
                    For example, with an overlap of 0.25 and a patch length of 20, 
                    patch number n would share its 5 first frames with patch (n-1),
                    and its 5 last frames with patch (n+1). 

        n_fft : int, length of FFT window, passed to librosa.feature.melspectrogram
        hop_length : int, hop length between FFTs, passed to librosa.feature.melspectrogram
        include_last_patch : bool. If set to False, the last spectrogram frames 
            will be discarded if they are not enough to build a new patch with.
            If set to True, they will be kept in a new patch which will more heavily overlap with the previous one.
            For example, with a patch length of 20 frames, and overlap of 0.25 (thus 5 frames),
            and an overall clip length of 127 frames, the last 7 frames would not be enough to build a new patch,
            since we'd need 20 - 5 = 15 new frames. If include_last_patch is set to False,
            these last 7 frames will be discarded. If it is set to True, 
            they will be included in a new patch along with the 13 previous frames.

        win_length : int, passed to librosa.feature.melspectrogram. If None default to n_fft
        window : str, passed to librosa.feature.melspectrogram
        center : bool, passed to librosa.feature.melspectrogram 
        pad_mode : str, passed to librosa.feature.melspectrogram
        power : float, 1.0 or 2.0 only are allowed. Set to 2.O for power melspectrogram, 
            and 1.0 for amplitude melspectrogram
        n_mels : int, number of mel filters. passed to librosa.feature.melspectrogram
        fmin : int, min freq of spectrogram, passed to librosa.feature.melspectrogram
        fmax : int, max freq of spectrogram, passed to librosa.feature.melspectrogram
        power_to_db_ref, : func, used to convert linear scale mel spectrogram to db scale. 
                Passed to passed to librosa.power_to_db or librosa.amplitude_to_db

        Outputs 
        -------
        Patches : list of 2D ndarrays of shape (n_mels, patch_length). List of output patches.
    '''

    db_melspec = compute_mel_spectrogram(wave=wave,
                                         sr=sr, 
                                         n_fft=n_fft, 
                                         hop_length=hop_length,
                                         win_length=win_length,
                                         window=window,
                                         center=center,
                                         pad_mode=pad_mode,
                                         power=power,
                                         n_mels=n_mels,
                                         fmin=fmin,
                                         fmax=fmax,
                                         power_to_db_ref = power_to_db_ref,
                                         norm=norm,
                                         htk=htk,
                                         to_db=to_db,
                                         **kwargs)

    num_frames = db_melspec.shape[1]
    # Cut up db_melspec

    overlap_frames = int(np.floor(patch_length * overlap))
    if num_frames < patch_length:
        print("NOT ENOUGH FRAMES", num_frames)
        print("WAVE HAD {} SAMPLES".format(len(wave)))
        warnings.warn("WARNING : Not enough frames to form a full patch")
        num_patches = 0
    else:
        num_patches = 1 + ((num_frames - patch_length)  // (patch_length - overlap_frames))
    patches = [db_melspec[:, (patch_length - overlap_frames) * i : patch_length * (i+1) - overlap_frames * i] for i in range(num_patches)]

    if include_last_patch:
        patches.append(db_melspec[:, num_frames - patch_length : num_frames])

    return patches