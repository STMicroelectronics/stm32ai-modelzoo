# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

'''Generates LUTs for on-target preprocessing'''
import numpy as np
import librosa 
import os
import sys
from hydra.core.hydra_config import HydraConfig


def generate_mel_LUTs(sr: int,
                      n_fft: int,
                      n_mels: int,
                      fmax: int,
                      fmin: int,
                      norm: str,
                      htk: bool):
    '''
    Generates mel filterbank look-up tables for use in the Getting Started C application.
    The resulting mel filter weight matrix is sparse, so it is transformed to a non-zero weight array,
    a starting index array, and a stopping index array.

    Inputs
    ------
    sr : int, sampling rate
    n_fft : int, length of FFT 
    n_mels : int, number of mel bands
    fmax : int, highest frequency in mel filterbank
    fmin : int, lowest frequency in mel filterbank
    norm : str, normalization used for mel weights
    htk : bool, set to True to use the htk formula for mel scale.

    Outputs
    -------
    melFilterLut : np.ndarray, array containing non-zero mel weights
    melFilterStartIndices : np.ndarray, array containing start indexes 
    for non-zero parts of the sparse mel filter weight array
    melFilterStopIndices : np.ndarray, array containing start indexes 
    for non-zero parts of the sparse mel filter weight array
    '''
    if norm == "None":
        norm = None
    # Create mel filter matrix
    mel_fb = librosa.filters.mel(sr=sr,
                                 n_fft=n_fft,
                                 n_mels=n_mels,
                                 fmax=fmax,
                                 fmin=fmin,
                                 norm=norm,
                                 htk=htk)
    melFilterStartIndices = np.zeros(n_mels)
    melFilterStopIndices = np.zeros(n_mels)

    for i in range(mel_fb.shape[0]):
        nonzero_idx = np.nonzero(mel_fb[i])[0]
        if len(nonzero_idx) == 0:
            print("Mel filter matrix : \n")
            print(mel_fb)
            raise ValueError(
                "At least one line in mel filter matrix has no nonzero coefficients. \
                 \n This is incompatible with the on target pre-processing")
        else:
            melFilterStartIndices[i] = nonzero_idx[0]
            melFilterStopIndices[i] = nonzero_idx[-1]

    melFilterLut = mel_fb[np.nonzero(mel_fb)]

    # Check we have the right amount of coeffs
    assert int(np.sum((melFilterStopIndices - melFilterStartIndices) + 1) == len(melFilterLut)), \
    "ERROR : Mismatch between n° of coeffs and start/stop indices"

    return melFilterLut, melFilterStartIndices.astype('int'), melFilterStopIndices.astype('int')

def generate_hann_window_LUT(window, win_length):
    '''
    Generates hanning window look-up table for use in the Getting Started C application.
    Raises an exception if attempting to generate another window type 
    as it's not supported in the C application currently.

    Inputs
    ------
    window : str, window type. Must be "hann", else an exception is raised
    win_length : int, window length

    Outputs
    -------
    hann_window : np.ndarray, array containing hanning window weights.
    '''
    if window != 'hann':
        raise ValueError("The only available window type for on target pre-processing is Hanning \n \
                         Please set the feature_extraction.window parameter in your config file to 'hann'")

    hann_window = librosa.filters.get_window('hann', win_length)

    return hann_window

def generate_LUTs_header_file(path,
                              melFilterLut,
                              melFilterStartIndices,
                              melFilterStopIndices,
                              hannWin):
    '''
    Generates the header file for the look-up tables used in the Getting Started C application
    Writes directly to path/user_mel_tables.h
    Inputs
    ------
    path : str or Posixpath, path to write the header file to.
    melFilterLut : np.ndarray, array of non-zero mel filter weights
    melFilterStartIndices : np.ndarray, array containing start indexes 
    for non-zero parts of the sparse mel filter weight array
    melFilterStopIndices : np.ndarray, array containing start indexes 
    for non-zero parts of the sparse mel filter weight array
    hannWin : np.ndarray, array containing hanning window weights.

    Outputs
    -------
    None
    '''

    # Write .h file
    with open(os.path.join(path, "user_mel_tables.h"), "wt") as f:
        f.write('/**\n')
        f.write('******************************************************************************\n')
        f.write('* @file    user_mel_tables.h\n')
        f.write('* @author  MCD Application Team\n')
        f.write('* @brief   Header for mel_user_tables.c module')
        f.write('******************************************************************************\n')
        f.write('* @attention\n')
        f.write('*\n')
        f.write('* Copyright (c) 2022 STMicroelectronics.\n')
        f.write('* All rights reserved.\n')
        f.write('*\n')
        f.write('* This software is licensed under terms that can be found in the LICENSE file\n')
        f.write('* in the root directory of this software component.\n')
        f.write('* If no LICENSE file comes with this software, it is provided AS-IS.\n')
        f.write('*\n')
        f.write('******************************************************************************\n')
        f.write('*/\n')
        f.write('#ifndef _MEL_USER_TABLES_H\n')
        f.write('#define _MEL_USER_TABLES_H\n')
        f.write('#include "arm_math.h"\n')
        f.write('extern const float32_t userWin[{}];\n'.format(len(hannWin)))
        f.write('extern const uint32_t  user_melFiltersStartIndices[{}];\n'.format(len(melFilterStartIndices)))
        f.write('extern const uint32_t  user_melFiltersStopIndices[{}];\n'.format(len(melFilterStopIndices)))
        f.write('extern const float32_t user_melFilterLut[{}];\n'.format(len(melFilterLut)))
        f.write('\n')
        f.write('#endif /* _MEL_USER_TABLES_H */\n')

def generate_LUTs_c_file(path,
                         melFilterLut,
                         melFilterStartIndices,
                         melFilterStopIndices,
                         hannWin):
    
    '''
    Generates the C code file for the look-up tables used in the Getting Started C application
    Writes directly to path/user_mel_tables.c
    Inputs
    ------
    path : str or Posixpath, path to write the header file to.
    melFilterLut : np.ndarray, array of non-zero mel filter weights
    melFilterStartIndices : np.ndarray, array containing start indexes 
    for non-zero parts of the sparse mel filter weight array
    melFilterStopIndices : np.ndarray, array containing start indexes 
    for non-zero parts of the sparse mel filter weight array
    hannWin : np.ndarray, array containing hanning window weights.

    Outputs
    -------
    None
    '''
    # path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")
    # Convert LUTs to str to be able to write to file
    melFilterLut_str = np.array2string(melFilterLut,
                                       separator='F ,',
                                       formatter={'float': lambda x : np.format_float_scientific(x,
                                                  precision=10, unique=False)},
                                       threshold=sys.maxsize)
    melFilterLut_str = '{' + melFilterLut_str[1:-1] + 'F}'

    melFilterStartIndices_str = np.array2string(melFilterStartIndices, separator=',', threshold=sys.maxsize)
    melFilterStopIndices_str = np.array2string(melFilterStopIndices, separator=',', threshold=sys.maxsize)
    melFilterStartIndices_str = '{' + melFilterStartIndices_str[1:-1] + '}'
    melFilterStopIndices_str = '{' + melFilterStopIndices_str[1:-1] + '}'

    hannWin_str = np.array2string(hannWin,
                                  separator='F ,',
                                  formatter={'float': lambda x : np.format_float_scientific(x,
                                             precision=10, unique=False)},
                                  threshold=sys.maxsize)
    

    hannWin_str = '{' + hannWin_str[1:-1] + 'F}'


    # Write file

    with open(os.path.join(path, "user_mel_tables.c"), "wt") as f:
        f.write('/**\n')
        f.write('******************************************************************************\n')
        f.write('* @file    user_mel_tables.c\n')
        f.write('* @author  MCD Application Team\n')
        f.write('* @brief   This file has lookup tables for user-defined windows and mel filter banks')
        f.write('******************************************************************************\n')
        f.write('* @attention\n')
        f.write('*\n')
        f.write('* Copyright (c) 2022 STMicroelectronics.\n')
        f.write('* All rights reserved.\n')
        f.write('*\n')
        f.write('* This software is licensed under terms that can be found in the LICENSE file\n')
        f.write('* in the root directory of this software component.\n')
        f.write('* If no LICENSE file comes with this software, it is provided AS-IS.\n')
        f.write('*\n')
        f.write('******************************************************************************\n')
        f.write('*/\n')
        f.write('\n')
        f.write('#include "user_mel_tables.h"\n')
        f.write('\n')
        f.write('const float32_t userWin[{}] = {};\n'.format(len(hannWin), hannWin_str))
        f.write('const uint32_t user_melFiltersStartIndices[{}] = {};\n'.format(
                len(melFilterStartIndices), melFilterStartIndices_str))
        f.write('const uint32_t user_melFiltersStopIndices[{}] = {};\n'.format(
                len(melFilterStopIndices), melFilterStopIndices_str))
        f.write('const float32_t user_melFilterLut[{}] = {};\n'.format(
            len(melFilterLut), melFilterLut_str))
        f.write('\n')

def generate_mel_LUT_files(config):
    '''
    Wrapper function to compute LUTs and write the appropriate files
    
    Inputs
    ------
    config : dict, configuration dictionary

    Outputs
    -------
    None
    '''

    # I don't really like hardcoding the path here but it's done like this everywhere else
    
    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")
    melFilterLut, melFilterStartIndices, melFilterStopIndices = generate_mel_LUTs(
        sr=config.preprocessing.target_rate,
        n_fft=config.feature_extraction.n_fft,
        n_mels=config.feature_extraction.n_mels,
        fmax=config.feature_extraction.fmax,
        fmin=config.feature_extraction.fmin,
        norm=config.feature_extraction.norm,
        htk=config.feature_extraction.htk)

    hannWin = generate_hann_window_LUT(window=config.feature_extraction.window,
                                       win_length=config.feature_extraction.window_length)
    print("[INFO] Generating LUT header file")
    generate_LUTs_header_file(path,
                              melFilterLut, 
                              melFilterStartIndices,
                              melFilterStopIndices,
                              hannWin)
    print("[INFO] Done generating LUT header file")
    print("[INFO] Generating LUT C file")
    generate_LUTs_c_file(path,
                         melFilterLut,
                         melFilterStartIndices,
                         melFilterStopIndices,
                         hannWin)
    print('[INFO] : Done generating LUT C file')
