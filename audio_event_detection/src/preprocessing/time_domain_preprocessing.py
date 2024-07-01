# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

'''Contains functions for preprocessing of audio input in the temporal domain'''
import librosa
import numpy as np


def load_and_reformat(wave_path: str,
                      min_length: int = 1, 
                      max_length: int = 10, 
                      target_rate: int = 44100,
                      top_db: int = 30,
                      frame_length: int = 2048,
                      hop_length: int = 512,
                      trim_last_second: int = False,
                      lengthen: str = 'after'):
     '''Reformats a waveform to have length at least min_length and at most max_length.
       Padding is done by repeating the waveform, and reducing is done by cutting the wavelength from the end.
       (e.g. last seconds are discarded.)
       Also resamples waveform to target_rate, and removes silence.
       
       Inputs
       ------
       wave_path : str or PosixPath, path to waveform file
       min_length : int,  Minimum length of output waveform in seconds. 
            If input waveform is below this duration, it will be repeated to reach min_length.
       max_length : int, Maximum length of output waveform in seconds.
            If input waveform is longer, it will be cut from the end.
       target_rate : int, Sample rate of output waveform
       top_db : int, Passed to librosa.split. Frames below -top_db will be considered as silence and cut.
            Higher values induce more tolerance to silence.
       frame_length : int, frame length used for silence removal
       hop_length : int, hop length used for silence removal
       trim_last_second : bool. Set to True to cut the output waveform to an integer number of seconds.
            For example, if the output waveform is 7s and 350 ms long, this option will cut the last 350 ms.
        
        Outputs
        -------
        wave : ndarray, output waveform
        sr : int, sample rate of output waveform.'''

     wave, sr = librosa.load(wave_path, sr=target_rate, duration=max_length)
     if len(wave) < sr * min_length and lengthen == 'before':
          print("[INFO] : Sound wave shorter than min_length, repeating")
          n_repeats = sr * min_length // len(wave)
          print('[INFO] : Sound wave repeated {} times'.format(n_repeats))
          wave = np.tile(wave, n_repeats + 1)
          wave = wave[:min_length*target_rate]

     # Remove silence in clips

     intervals = librosa.effects.split(wave, top_db=top_db,
                                        frame_length=frame_length, hop_length=hop_length)

     wave = np.concatenate([wave[interval[0]:interval[1]] for interval in intervals])

     n_seconds = len(wave) // sr
     
     if trim_last_second and n_seconds >= 1:
          wave = wave[:n_seconds * sr]

     if len(wave) < sr * min_length and lengthen == 'after':
          print("[INFO] : Sound wave shorter than min_length, repeating")
          n_repeats = sr * min_length // len(wave)
          print('[INFO] : Sound wave repeated {} times'.format(n_repeats))
          wave = np.tile(wave, n_repeats + 1)
          wave = wave[:min_length*target_rate]

     return wave, sr