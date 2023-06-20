/********************************************************************************
* @file    ai_model_config.h
* @author  STMicroelectronics - AIS - MCD Team
* @version 1.0.0
* @date    2023-Jun-19
* @brief   Configure the getting started functionality
*
*  Each logic module of the application should define a DEBUG control byte
* used to turn on/off the log for the module.
*
*********************************************************************************
* @attention
*
* Copyright (c) 2022 STMicroelectronics
* All rights reserved.
*
* This software is licensed under terms that can be found in the LICENSE file in
* the root directory of this software component.
* If no LICENSE file comes with this software, it is provided AS-IS.
*********************************************************************************
*/
/* ---------------    Generated code    ----------------- */
#ifndef AI_MODEL_CONFIG_H
#define AI_MODEL_CONFIG_H

#ifdef __cplusplus
extern "C" {
#endif

#define CTRL_X_CUBE_AI_MODE_NAME                 "X-CUBE-AI AED"
#define CTRL_X_CUBE_AI_MODE_NB_OUTPUT            (1U)
#define CTRL_X_CUBE_AI_MODE_OUTPUT_1             (CTRL_AI_CLASS_DISTRIBUTION)
#define CTRL_X_CUBE_AI_MODE_CLASS_NUMBER         (10U)
#define CTRL_X_CUBE_AI_MODE_CLASS_LIST           {"chainsaw","clock_tick","crackling_fire","crying_baby","dog","helicopter","rain","rooster","sea_waves","sneezing"}
#define CTRL_X_CUBE_AI_SENSOR_TYPE               COM_TYPE_MIC
#define CTRL_X_CUBE_AI_SENSOR_NAME               "imp34dt05"
#define CTRL_X_CUBE_AI_SENSOR_ODR                (16000.0F)
#define CTRL_X_CUBE_AI_SENSOR_FS                 (112.5F)
#define CTRL_X_CUBE_AI_NB_SAMPLES                (0U)
#define CTRL_X_CUBE_AI_PREPROC                   (CTRL_AI_SPECTROGRAM_LOG_MEL)
#define CTRL_X_CUBE_AI_SPECTROGRAM_NMEL          (64U)
#define CTRL_X_CUBE_AI_SPECTROGRAM_COL           (96U)
#define CTRL_X_CUBE_AI_SPECTROGRAM_HOP_LENGTH    (160U)
#define CTRL_X_CUBE_AI_SPECTROGRAM_NFFT          (512U)
#define CTRL_X_CUBE_AI_SPECTROGRAM_WINDOW_LENGTH (400U)
#define CTRL_X_CUBE_AI_SPECTROGRAM_NORMALIZE     (0U) // (1U)
#define CTRL_X_CUBE_AI_SPECTROGRAM_FORMULA       (MEL_HTK) //MEL_SLANEY
#define CTRL_X_CUBE_AI_SPECTROGRAM_FMIN          (125U)
#define CTRL_X_CUBE_AI_SPECTROGRAM_FMAX          (7500U)
#define CTRL_X_CUBE_AI_SPECTROGRAM_TYPE          (SPECTRUM_TYPE_MAGNITUDE) // ,  /*!< magnitude spectrum */
#define CTRL_X_CUBE_AI_SPECTROGRAM_LOG_FORMULA   (LOGMELSPECTROGRAM_SCALE_LOG) //LOGMELSPECTROGRAM_SCALE_DB
#define CTRL_X_CUBE_AI_SPECTROGRAM_SILENCE_THR   (100) // 0 means disabled
#define CTRL_X_CUBE_AI_SPECTROGRAM_WIN           (userWin)
#define CTRL_X_CUBE_AI_SPECTROGRAM_MEL_LUT       (user_melFilterLut)
#define CTRL_X_CUBE_AI_SPECTROGRAM_MEL_START_IDX (user_melFiltersStartIndices)
#define CTRL_X_CUBE_AI_SPECTROGRAM_MEL_STOP_IDX  (user_melFiltersStopIndices)
#define CTRL_X_CUBE_AI_OOD_THR                   (0.0F)
#define CTRL_SEQUENCE                            {CTRL_CMD_PARAM_AI,0}

#ifdef __cplusplus
}
#endif

#endif /* AI_MODEL_CONFIG_H */
