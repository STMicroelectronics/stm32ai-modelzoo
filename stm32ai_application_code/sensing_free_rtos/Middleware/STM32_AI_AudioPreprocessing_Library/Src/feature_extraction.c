/**
 ******************************************************************************
 * @file    feature_extraction.c
 * @author  MCD Application Team
 * @brief   Spectral feature extraction functions
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
#include "feature_extraction.h"

#ifndef M_PI
#define M_PI    3.14159265358979323846264338327950288 /*!< pi */
#endif

#define NORM_Q15  (1.0F/32768.0F)

/**
 * @defgroup groupFeature Feature Extraction
 * @brief Spectral feature extraction functions
 * @{
 */

/**
 * @brief      Convert 16-bit PCM into floating point values
 *
 * @param      *pInSignal  points to input signal buffer
 * @param      *pOutSignal points to output signal buffer
 * @param      len         signal length
 */
void buf_to_float(int16_t *pInSignal, float32_t *pOutSignal, uint32_t len)
{
  for (uint32_t i = 0; i < len; i++)
  {
    pOutSignal[i] = (float32_t) pInSignal[i];
  }
}

/**
 * @brief      Convert 16-bit PCM into normalized floating point values
 *
 * @param      *pInSignal   points to input signal buffer
 * @param      *pOutSignal  points to output signal buffer
 * @param      len          signal length
 */
void buf_to_float_normed(int16_t *pInSignal, float32_t *pOutSignal, uint32_t len)
{
  for (uint32_t i = 0; i < len; i++)
  {
    pOutSignal[i] = (float32_t) pInSignal[i] / (1 << 15);
  }
}

/**
 * @brief      Power Spectrogram column
 *
 * @param      *S          points to an instance of the floating-point Spectrogram structure.
 * @param      *pInSignal  points to the in-place input signal frame of length FFTLen.
 * @param      *pOutCol    points to  output Spectrogram column.
 * @return     None
 */
void SpectrogramColumn(SpectrogramTypeDef *S, float32_t *pInSignal, float32_t *pOutCol)
{
  uint32_t frame_len = S->FrameLen;
  uint32_t n_fft = S->FFTLen;
  float32_t *scratch_buffer = S->pScratch1;

  float32_t first_energy;
  float32_t last_energy;

  /* In-place window application (on signal length, not entire n_fft) */
  /* @note: OK to typecast because hannWin content is not modified */
  arm_mult_f32(pInSignal, S->pWindow, pInSignal, frame_len);

  /* Zero pad if signal frame length is shorter than n_fft */
  memset(&pInSignal[frame_len], 0, (n_fft - frame_len)*sizeof(*pInSignal));

  /* FFT */
  arm_rfft_fast_f32(S->pRfft, pInSignal, scratch_buffer, 0);

  /* Power spectrum */
  first_energy = scratch_buffer[0] * scratch_buffer[0];
  last_energy = scratch_buffer[1] * scratch_buffer[1];
  pOutCol[0] = first_energy;
  arm_cmplx_mag_squared_f32(&scratch_buffer[2], &pOutCol[1], (n_fft / 2) - 1);
  pOutCol[n_fft / 2] = last_energy;

  /* Magnitude spectrum */
  if (S->Type == SPECTRUM_TYPE_MAGNITUDE)
  {
    for (uint32_t i = 0; i < (n_fft / 2) + 1; i++)
    {
      arm_sqrt_f32(pOutCol[i], &pOutCol[i]);
    }
  }
}

void SpectrogramColumn_pad(SpectrogramTypeDef *S, float32_t *pInSignal, float32_t *pOutCol)
{
  uint32_t n_fft = S->FFTLen;
  float32_t first_energy;
  float32_t last_energy;
  float32_t *p_sum = &S->spectro_sum;
  float32_t *p_out = S->pScratch2;

  /* In-place window application (on signal length, not entire n_fft) */
  /* @note: OK to typecast because hannWin content is not modified */
  arm_mult_f32(pInSignal+S->pad_left, S->pWindow, pInSignal+S->pad_left, S->FrameLen);
  /* FFT */
  arm_rfft_fast_f32(S->pRfft, pInSignal, p_out, 0);

  /* Power spectrum */
  first_energy = p_out[0] * p_out[0];
  last_energy  = p_out[1] * p_out[1];
  pOutCol[0] = first_energy;
  arm_cmplx_mag_squared_f32(&p_out[2], &pOutCol[1], (n_fft / 2) - 1);
  pOutCol[n_fft/2] = last_energy;

  /* Magnitude spectrum */
  if (S->Type == SPECTRUM_TYPE_MAGNITUDE)
  {
    for (uint32_t i = 0; i < (n_fft / 2) + 1; i++)
    {
      arm_sqrt_f32(pOutCol[i], &pOutCol[i]);
      *p_sum += pOutCol[i];
    }
  }
}

/**
 * @brief      Mel Spectrogram column
 *
 * @param      *S          points to an instance of the floating-point Mel structure.
 * @param      *pInSignal  points to input signal frame of length FFTLen.
 * @param      *pOutCol    points to  output Mel Spectrogram column.
 * @return     None
 */
void MelSpectrogramColumn(MelSpectrogramTypeDef *S, float32_t *pInSignal, float32_t *pOutCol)
{
  float32_t *tmp_buffer = S->SpectrogramConf->pScratch1;

  /* Power Spectrogram */
  SpectrogramColumn(S->SpectrogramConf, pInSignal, tmp_buffer);

  /* Mel Filter Banks Application */
  MelFilterbank(S->MelFilter, tmp_buffer, pOutCol);
}

/**
 * @brief      Log-Mel Spectrogram column
 *
 * @param      *S          points to an instance of the floating-point Log-Mel structure.
 * @param      *pInSignal  points to input signal frame of length FFTLen.
 * @param      *pOutCol    points to  output Log-Mel Spectrogram column.
 * @return     None
 */
void LogMelSpectrogramColumn(LogMelSpectrogramTypeDef *S, float32_t *pInSignal, float32_t *pOutCol)
{
  uint32_t n_mels = S->MelSpectrogramConf->MelFilter->NumMels;
  float32_t top_dB = S->TopdB;
  float32_t ref = S->Ref;
  float32_t *tmp_buffer = S->MelSpectrogramConf->SpectrogramConf->pScratch1;

  SpectrogramColumn(S->MelSpectrogramConf->SpectrogramConf, pInSignal, tmp_buffer);

  /* Mel Filter Banks Application to power spectrum column */
  MelFilterbank(S->MelSpectrogramConf->MelFilter, tmp_buffer, pOutCol);

  /* Scaling */
  for (uint32_t i = 0; i < n_mels; i++) {
    pOutCol[i] /= ref;
  }

  /* Avoid log of zero or a negative number */
  for (uint32_t i = 0; i < n_mels; i++) {
    if (pOutCol[i] <= 0.0f) {
      pOutCol[i] = FLT_MIN;
    }
  }
  if (S->LogFormula == LOGMELSPECTROGRAM_SCALE_DB)
  {
    /* Convert power spectrogram to decibel */
    for (uint32_t i = 0; i < n_mels; i++) {
      pOutCol[i] = 10.0f * log10f(pOutCol[i]);
    }

    /* Threshold output to -top_dB dB */
    for (uint32_t i = 0; i < n_mels; i++) {
      pOutCol[i] = (pOutCol[i] < -top_dB) ? (-top_dB) : (pOutCol[i]);
    }
  }
  else
  {
    /* Convert power spectrogram to log scale */
    for (uint32_t i = 0; i < n_mels; i++) {
      pOutCol[i] = logf(pOutCol[i]);
    }
  }
}

void LogMelSpectrogramColumn_q15_Q8(LogMelSpectrogramTypeDef *S, int16_t *pInSignal, int8_t *pOutCol,int8_t offset,float32_t inv_scale)
{
  float32_t *p_in, *p_out;

  float32_t top_dB              = S->TopdB;
  float32_t ref                 = S->Ref;
  SpectrogramTypeDef *p_spectro = S->MelSpectrogramConf->SpectrogramConf;
  uint32_t n_mels               = S->MelSpectrogramConf->MelFilter->NumMels;
  uint32_t frame_len            = p_spectro->FrameLen;
  uint32_t pad_left             = p_spectro->pad_left;
  uint32_t pad_right            = p_spectro->pad_right;

  /* use first scratch buffer as input buffer */
  p_in  = p_spectro->pScratch1;

  /* Zero pad left and right */
  memset(p_in, 0, pad_left*sizeof(*p_in));
  memset(p_in+pad_left+frame_len, 0, pad_right*sizeof(*p_in));

  /* scale input signal */
  p_in +=  pad_left;
  for (int i= 0 ; i<frame_len; i++ )
  {
    p_in[i]  = (float)(*pInSignal++) * NORM_Q15;
  }

  /* compute spectrogram  with first scratch buffer as input*/
  p_in  = p_spectro->pScratch1;
  p_out = p_spectro->pScratch2;

  SpectrogramColumn_pad(p_spectro, p_in, p_out);

  /* swap input & output buffers*/
  p_in  = p_spectro->pScratch2;
  p_out = p_spectro->pScratch1;

  /* Mel Filter Banks Application to power spectrum column */
  MelFilterbank(S->MelSpectrogramConf->MelFilter,p_in, p_out);

  /* Scaling */
  for (uint32_t i = 0; i < n_mels; i++) {
    p_out[i] /= ref;
  }

  /* Avoid log of zero or a negative number */
  for (uint32_t i = 0; i < n_mels; i++) {
    if (p_out[i] <= 0.0f) {
      p_out[i] = FLT_MIN;
    }
  }

  if (S->LogFormula == LOGMELSPECTROGRAM_SCALE_DB)
  {
    /* Convert power spectrogram to decibel */
    for (uint32_t i = 0; i < n_mels; i++) {
      p_out[i] = 10.0f * log10f(p_out[i]);
    }

    /* Threshold output to -top_dB dB */
    for (uint32_t i = 0; i < n_mels; i++) {
      p_out[i] = (p_out[i] < -top_dB) ? (-top_dB) : (p_out[i]);
    }
  }
  else
  {
    /* Convert power spectrogram to log scale */
    for (uint32_t i = 0; i < n_mels; i++) {
      p_out[i] = logf(p_out[i]);
    }
  }

  /*  Quantization */
  for (uint32_t i=0 ; i < n_mels ; i++ ){
    pOutCol[i]= (int8_t)__SSAT((int32_t)roundf(p_out[i]*inv_scale + (float) offset), 8);
  }
}

/**
 * @brief      Mel-Frequency Cepstral Coefficients (MFCCs) column
 *
 * @param      *S          points to an instance of the floating-point MFCC structure.
 * @param      *pInSignal  points to input signal frame of length FFTLen.
 * @param      *pOutCol    points to  output MFCC spectrogram column.
 * @return     None
 */
void MfccColumn(MfccTypeDef *S, float32_t *pInSignal, float32_t *pOutCol)
{
  float32_t *tmp_buffer = S->pScratch;

  LogMelSpectrogramColumn(S->LogMelConf, pInSignal, tmp_buffer);

  /* DCT for computing MFCCs from spectrogram slice. */
  DCT(S->pDCT, tmp_buffer, pOutCol);
}

/**
 * @} end of groupFeature
 */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
