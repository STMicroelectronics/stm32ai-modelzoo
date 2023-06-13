'''Generates LUTs for on-target preprocessing'''
import numpy as np
import librosa 
import os
import sys
from hydra.core.hydra_config import HydraConfig


def generate_mel_LUTs(config):
    sr = config.pre_processing.target_rate
    n_fft = config.feature_extraction.n_fft
    n_mels = config.feature_extraction.n_mels
    fmax = config.feature_extraction.fmax
    fmin = config.feature_extraction.fmin
    norm = config.feature_extraction.norm
    if norm == "None":
        norm = None
    htk = config.feature_extraction.htk
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
                "At least one line in mel filter matrix has no nonzero coefficients. \n This is incompatible with the on target pre-processing")
        else:
            melFilterStartIndices[i] = nonzero_idx[0]
            melFilterStopIndices[i] = nonzero_idx[-1]

    melFilterLut = mel_fb[np.nonzero(mel_fb)]

    # Check we have the right amount of coeffs
    assert int(np.sum((melFilterStopIndices - melFilterStartIndices) + 1) == len(melFilterLut)), \
    "ERROR : Mismatch between n° of coeffs and start/stop indices"

    return melFilterLut, melFilterStartIndices.astype('int'), melFilterStopIndices.astype('int')

def generate_hann_window_LUT(config):
    if config.feature_extraction.window != 'hann':
        raise ValueError("The only available window type for on target pre-processing is Hanning")

    win_length = config.feature_extraction.window_length
    hann_window = librosa.filters.get_window('hann', win_length)

    return hann_window

def generate_LUTs_header_file(melFilterLut,
                              melFilterStartIndices,
                              melFilterStopIndices,
                              hannWin):

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")

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

def generate_LUTs_c_file(melFilterLut,
                         melFilterStartIndices,
                         melFilterStopIndices,
                         hannWin):
    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")
    # Convert LUTs to str to be able to write to file
    melFilterLut_str = np.array2string(melFilterLut,
                                       separator='F ,',
                                       formatter={'float': lambda x : np.format_float_scientific(x,
                                                  precision=10, unique=False)},
                                       threshold=sys.maxsize)
    melFilterLut_str = '{' + melFilterLut_str[1:-1] + '}'

    melFilterStartIndices_str = np.array2string(melFilterStartIndices, separator=',', threshold=sys.maxsize)
    melFilterStopIndices_str = np.array2string(melFilterStopIndices, separator=',', threshold=sys.maxsize)
    melFilterStartIndices_str = '{' + melFilterStartIndices_str[1:-1] + '}'
    melFilterStopIndices_str = '{' + melFilterStopIndices_str[1:-1] + '}'

    hannWin_str = np.array2string(hannWin,
                                  separator='F ,',
                                  formatter={'float': lambda x : np.format_float_scientific(x,
                                             precision=10, unique=False)},
                                  threshold=sys.maxsize)
    

    hannWin_str = '{' + hannWin_str[1:-1] + '}'


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
    '''Wrapper function to compute LUTs and write the appropriate files'''
    melFilterLut, melFilterStartIndices, melFilterStopIndices = generate_mel_LUTs(config)
    hannWin = generate_hann_window_LUT(config)
    print("[INFO] Generating LUT header file")
    generate_LUTs_header_file(melFilterLut, 
                              melFilterStartIndices,
                              melFilterStopIndices,
                              hannWin)
    print("[INFO] Done generating LUT header file")
    print("[INFO] Generating LUT C file")
    generate_LUTs_c_file(melFilterLut,
                         melFilterStartIndices,
                         melFilterStopIndices,
                         hannWin)
    print('[INFO] : Done generating LUT C file')
