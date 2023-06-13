/**
  ******************************************************************************
  * @file    preproc_dpu.c
  * @author  MCD Application Team
  * @brief   This file is implementing pre-processing functions that are making
  * 		 use of Audio pre-processing libraries
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

/* Includes ------------------------------------------------------------------*/
#include "preproc_dpu.h"

/* External functions --------------------------------------------------------*/
BaseType_t PreProc_DPUInit(AudioProcCtx_t *pxCtx)
{
  assert_param(pxCtx != NULL);
  uint32_t pad;

  assert_param(CTRL_X_CUBE_AI_SPECTROGRAM_NFFT >= CTRL_X_CUBE_AI_SPECTROGRAM_WINDOW_LENGTH );
  assert_param(CTRL_X_CUBE_AI_SPECTROGRAM_NFFT >= CTRL_X_CUBE_AI_SPECTROGRAM_NMEL);

  pxCtx->output_Q_inv_scale = 0.0F;
  pxCtx->output_Q_offset    = 0;

  /* Init RFFT */
  arm_rfft_fast_init_f32(&pxCtx->S_Rfft, CTRL_X_CUBE_AI_SPECTROGRAM_NFFT);

  /* Init Spectrogram */
  pxCtx->S_Spectr.pRfft                    = &pxCtx->S_Rfft;
  pxCtx->S_Spectr.Type                     = CTRL_X_CUBE_AI_SPECTROGRAM_TYPE;
  pxCtx->S_Spectr.pWindow                  = (float32_t *) CTRL_X_CUBE_AI_SPECTROGRAM_WIN;
  pxCtx->S_Spectr.SampRate                 = CTRL_X_CUBE_AI_SENSOR_ODR;
  pxCtx->S_Spectr.FrameLen                 = CTRL_X_CUBE_AI_SPECTROGRAM_WINDOW_LENGTH;
  pxCtx->S_Spectr.FFTLen                   = CTRL_X_CUBE_AI_SPECTROGRAM_NFFT;
  pxCtx->S_Spectr.pScratch1                = pxCtx->pSpectrScratchBuffer1;
  pxCtx->S_Spectr.pScratch2                = pxCtx->pSpectrScratchBuffer2;

  pad                                      = CTRL_X_CUBE_AI_SPECTROGRAM_NFFT - CTRL_X_CUBE_AI_SPECTROGRAM_WINDOW_LENGTH;
  pxCtx->S_Spectr.pad_left                 = pad/2;
  pxCtx->S_Spectr.pad_right                = pad/2 + (pad & 1);

  /* Init mel filterbank */
  pxCtx->S_MelFilter.pStartIndices         = (uint32_t *)  CTRL_X_CUBE_AI_SPECTROGRAM_MEL_START_IDX;
  pxCtx->S_MelFilter.pStopIndices          = (uint32_t *)  CTRL_X_CUBE_AI_SPECTROGRAM_MEL_STOP_IDX;
  pxCtx->S_MelFilter.pCoefficients         = (float32_t *) CTRL_X_CUBE_AI_SPECTROGRAM_MEL_LUT;
  pxCtx->S_MelFilter.NumMels               = CTRL_X_CUBE_AI_SPECTROGRAM_NMEL;
  pxCtx->S_MelFilter.FFTLen                = CTRL_X_CUBE_AI_SPECTROGRAM_NFFT;
  pxCtx->S_MelFilter.SampRate              = (uint32_t) CTRL_X_CUBE_AI_SENSOR_ODR;
  pxCtx->S_MelFilter.FMin                  = (float32_t) CTRL_X_CUBE_AI_SPECTROGRAM_FMIN;
  pxCtx->S_MelFilter.FMax                  = (float32_t) CTRL_X_CUBE_AI_SPECTROGRAM_FMAX;
  pxCtx->S_MelFilter.Formula               = CTRL_X_CUBE_AI_SPECTROGRAM_FORMULA;
  pxCtx->S_MelFilter.Normalize             = CTRL_X_CUBE_AI_SPECTROGRAM_NORMALIZE;
  pxCtx->S_MelFilter.Mel2F                 = 1U;

  /* Init MelSpectrogram */
  pxCtx->S_MelSpectr.SpectrogramConf       = &pxCtx->S_Spectr;
  pxCtx->S_MelSpectr.MelFilter             = &pxCtx->S_MelFilter;

  /* Init LogMelSpectrogram */
  pxCtx->S_LogMelSpectr.MelSpectrogramConf = &pxCtx->S_MelSpectr;
  pxCtx->S_LogMelSpectr.LogFormula         = CTRL_X_CUBE_AI_SPECTROGRAM_LOG_FORMULA;
  pxCtx->S_LogMelSpectr.Ref                = 1.0f;
  pxCtx->S_LogMelSpectr.TopdB              = HUGE_VALF;

  return pdTRUE;
}

BaseType_t PreProc_DPU(AudioProcCtx_t * pxCtx, uint8_t *pDataIn, int8_t *p_spectro)
{
  assert_param(pxCtx != NULL);
  assert_param (pxCtx->type == SPECTROGRAM_LOG_MEL);
  assert_param (pxCtx->S_MelFilter.NumMels == CTRL_X_CUBE_AI_SPECTROGRAM_NMEL);

  int16_t *p_in;
  int8_t  out[CTRL_X_CUBE_AI_SPECTROGRAM_NMEL];

  /* Create a quantized Mel-scaled spectrogram column */
  for (uint32_t i = 0; i < CTRL_X_CUBE_AI_SPECTROGRAM_COL; i++ )
  {
	p_in = (int16_t *)pDataIn + CTRL_X_CUBE_AI_SPECTROGRAM_HOP_LENGTH * i;
	LogMelSpectrogramColumn_q15_Q8(&pxCtx->S_LogMelSpectr, p_in,out,pxCtx->output_Q_offset,pxCtx->output_Q_inv_scale);
	/* transpose */
	for (uint32_t j=0 ; j < pxCtx->S_MelFilter.NumMels ; j++ ){
	  p_spectro[i+CTRL_X_CUBE_AI_SPECTROGRAM_COL*j]= out[j];
	}
  }

  return pdTRUE;
}
