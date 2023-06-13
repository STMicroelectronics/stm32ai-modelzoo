/**
  ******************************************************************************
  * @file    preproc_dpu.h
  * @author  MCD Application Team
  * @brief   Header for preproc_dpu.c module
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef _PREPROC_DPU_H
#define _PREPROC_DPU_H

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "dpu_config.h"
#include "feature_extraction.h"
#include "mel_filterbank.h"
#include "user_mel_tables.h"

/* Exported constants --------------------------------------------------------*/
#define AUDIO_HALF_BUFF_SIZE (CTRL_X_CUBE_AI_SPECTROGRAM_PATCH_LENGTH*2)
#define AUDIO_BUFF_SIZE      (AUDIO_HALF_BUFF_SIZE*2)

/* Exported types ------------------------------------------------------------*/
typedef enum {
  SPECTROGRAM_BYPASS,
  SPECTROGRAM_MEL,
  SPECTROGRAM_LOG_MEL,
  SPECTROGRAM_MFCC
}spectrogram_type_t;

typedef struct {
  spectrogram_type_t         type;

  arm_rfft_fast_instance_f32 S_Rfft;
  MelFilterTypeDef           S_MelFilter;
  SpectrogramTypeDef         S_Spectr;
  MelSpectrogramTypeDef      S_MelSpectr;
  LogMelSpectrogramTypeDef   S_LogMelSpectr;
  DCT_InstanceTypeDef        S_DCT;
  MfccTypeDef                S_Mfcc;

  float32_t pSpectrScratchBuffer1[CTRL_X_CUBE_AI_SPECTROGRAM_NFFT];
  float32_t pSpectrScratchBuffer2[CTRL_X_CUBE_AI_SPECTROGRAM_NFFT];

  /**
   * Specifies the quantization parameters of the unique output preprocessing
   */
  float32_t output_Q_inv_scale;
  int8_t    output_Q_offset;
}AudioProcCtx_t;

/* Exported functions --------------------------------------------------------*/
extern BaseType_t PreProc_DPUInit(AudioProcCtx_t *pxCtx);
extern BaseType_t PreProc_DPU(AudioProcCtx_t *pxCtx, uint8_t *pDataIn, int8_t *p_spectro);

#endif /* _PREPROC_DPU_H*/
