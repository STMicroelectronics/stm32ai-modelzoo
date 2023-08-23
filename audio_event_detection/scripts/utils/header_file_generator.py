import os
import ssl
from datetime import datetime

from hydra.core.hydra_config import HydraConfig

ssl._create_default_https_context = ssl._create_unverified_context


def _is_power_of_two(n):
    return (n != 0) and (n & (n - 1) == 0)


def gen_h_user_file(config):


    # Bunch of checks to see if parameters are valid
    assert config.pre_processing.target_rate in [16000, 48000], (
        "Target rate should match one of the available ODR rates of digital microphone, e.g. 16000 or 48000")
    assert _is_power_of_two(config.feature_extraction.n_fft), (
        "n_fft must be power of 2 due to ARM CMSIS-DSP implementation constraints"
    )
    assert config.feature_extraction.window_length <= config.feature_extraction.n_fft, (
        "Window length must be lower or equal to n_fft"
    )
    # Sort names from config as was done when training model
    class_names = config.dataset.class_names
    n_classes = len(class_names)
    if config.dataset.use_other_class:
        n_classes += 1
        class_names.append("other")
    class_names = sorted(class_names)
    # input_shape = params.model.input_shape

    classes = '{' + ','.join(['"' + x + '"' for x in class_names]) + '}'
    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    with open(os.path.join(path, "ai_model_config.h"), "wt") as f:
        f.write('/**')
        f.write('******************************************************************************\n')
        f.write('* @file    ai_model_config.h\n')
        f.write('* @author  STMicroelectronics - AIS - MCD Team\n')
        f.write('* @version 1.0.0\n')
        f.write(f'* @date    {datetime.now().strftime("%Y-%b-%d")}\n')
        f.write('* @brief   Configure the getting started functionality\n')
        f.write('*\n')
        f.write('*  Each logic module of the application should define a DEBUG control byte\n')
        f.write('* used to turn on/off the log for the module.\n')
        f.write('*\n')
        f.write('*********************************************************************************\n')
        f.write('* @attention\n')
        f.write('*\n')
        f.write('* Copyright (c) 2022 STMicroelectronics\n')
        f.write('* All rights reserved.\n')
        f.write('*\n')
        f.write('* This software is licensed under terms that can be found in the LICENSE file in\n')
        f.write('* the root directory of this software component.\n')
        f.write('* If no LICENSE file comes with this software, it is provided AS-IS.\n')
        f.write('*********************************************************************************\n')
        f.write('*/\n')

        f.write("/* ---------------    Generated code    ----------------- */\n")
        f.write('#ifndef AI_MODEL_CONFIG_H\n')
        f.write('#define AI_MODEL_CONFIG_H\n')
        f.write('\n')
        f.write('#ifdef __cplusplus\n')
        f.write('extern "C" {\n')
        f.write('#endif\n')
        f.write('\n')
        f.write('#define CTRL_X_CUBE_AI_MODE_NAME                 "X-CUBE-AI AED"\n')
        f.write('#define CTRL_X_CUBE_AI_MODE_NB_OUTPUT            (1U)\n')
        f.write('#define CTRL_X_CUBE_AI_MODE_OUTPUT_1             (CTRL_AI_CLASS_DISTRIBUTION)\n')
        f.write('#define CTRL_X_CUBE_AI_MODE_CLASS_NUMBER         ({}U)\n'.format(n_classes))
        f.write('#define CTRL_X_CUBE_AI_MODE_CLASS_LIST           {}\n'.format(classes))
        f.write('#define CTRL_X_CUBE_AI_SENSOR_TYPE               COM_TYPE_MIC\n')
        f.write('#define CTRL_X_CUBE_AI_SENSOR_NAME               "imp34dt05"\n')
        # NOTE : Letting user choose mic ODR.
        f.write('#define CTRL_X_CUBE_AI_SENSOR_ODR                ({}.0F)\n'.format(config.pre_processing.target_rate))
        f.write('#define CTRL_X_CUBE_AI_SENSOR_FS                 (112.5F)\n')
        f.write('#define CTRL_X_CUBE_AI_NB_SAMPLES                (0U)\n')
        # NOTE : Update this when we support additional preprocessing types
        f.write('#define CTRL_X_CUBE_AI_PREPROC                   (CTRL_AI_SPECTROGRAM_LOG_MEL)\n')
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_NMEL          ({}U)\n'.format(config.feature_extraction.n_mels))
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_COL           ({}U)\n'.format(config.feature_extraction.patch_length))
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_HOP_LENGTH    ({}U)\n'.format(config.feature_extraction.hop_length))
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_NFFT          ({}U)\n'.format(config.feature_extraction.n_fft))
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_WINDOW_LENGTH ({}U)\n'.format(config.feature_extraction.window_length))
        if config.feature_extraction.norm is None or config.feature_extraction.norm == "None":
                f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_NORMALIZE     (0U) // (1U)\n')
        elif config.feature_extraction.norm == "slaney":
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_NORMALIZE     (1U) // (0U)\n')
        else:
            raise ValueError("feature_extraction.norm must either be None or 'slaney' for Getting Started")
        
        if config.feature_extraction.htk:
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_FORMULA       (MEL_HTK) //MEL_SLANEY\n')
        else:
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_FORMULA       (MEL_SLANEY) //MEL_HTK\n')
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_FMIN          ({}U)\n'.format(config.feature_extraction.fmin))
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_FMAX          ({}U)\n'.format(config.feature_extraction.fmax))
        if int(config.feature_extraction.power) == 1:
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_TYPE          (SPECTRUM_TYPE_MAGNITUDE) // ,  /*!< magnitude spectrum */\n')
        elif int(config.feature_extraction.power) == 2:
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_TYPE          (SPECTRUM_TYPE_POWER) // ,  /*!< squared magnitude spectrum */\n')
        else:
            raise ValueError("Higher powers than 2 for spectrogram not supported in Getting Started.")
        if config.feature_extraction.to_db:
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_LOG_FORMULA   (LOGMELSPECTROGRAM_SCALE_DB) //LOGMELSPECTROGRAM_SCALE_LOG\n')
        else:
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_LOG_FORMULA   (LOGMELSPECTROGRAM_SCALE_LOG) //LOGMELSPECTROGRAM_SCALE_DB\n')
        # NOTE : Make this a deployment parameter
        # For now, just disable it if spec is db scale
        if config.feature_extraction.to_db:
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_SILENCE_THR   (0) // 0 means disabled\n')
        else:
            f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_SILENCE_THR   (100) // 0 means disabled\n')
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_WIN           (userWin)\n')
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_MEL_LUT       (user_melFilterLut)\n')
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_MEL_START_IDX (user_melFiltersStartIndices)\n')
        f.write('#define CTRL_X_CUBE_AI_SPECTROGRAM_MEL_STOP_IDX  (user_melFiltersStopIndices)\n')
        f.write('#define CTRL_X_CUBE_AI_OOD_THR                   ({}F)\n'.format(config.model.unknown_class_threshold))
        f.write('#define CTRL_SEQUENCE                            {CTRL_CMD_PARAM_AI,0}\n')
        f.write('\n')
        f.write('#ifdef __cplusplus\n')
        f.write('}\n')
        f.write('#endif\n')
        f.write('\n')
        f.write('#endif /* AI_MODEL_CONFIG_H */\n')