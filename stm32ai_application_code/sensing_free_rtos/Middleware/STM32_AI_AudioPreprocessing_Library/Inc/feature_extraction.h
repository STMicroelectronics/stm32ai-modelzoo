/**
 ******************************************************************************
 * @file    feature_extraction.h
 * @author  MCD Application Team
 * @brief   Header for feature_extraction.c module
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
#ifndef _FEATURE_EXTRACTION_H
#define _FEATURE_EXTRACTION_H

#ifdef __cplusplus
 extern "C" {
#endif

#include "arm_math.h"
#include "common_tables.h"
#include "float.h"
#include "dct.h"
#include "mel_filterbank.h"
#include "window.h"

/**
 *\mainpage STM32 Audio Preprocessing Library
 *
 * Introduction
 * ------------
 * This STM32_AI_AudioPreprocessing_Library is a C Library for
 * audio preprocessing in Artificial Intelligence applications optimized for
 * STM32 devices. It provides the building blocks for spectral analysis and
 * feature extraction, such as:
 * - Spectrogram computation
 * - Mel-scaled and LogMel-scaled spectrogram computation
 * - Mel-frequency cepstral coefficients (MFCCs) computation
 *
 *
 * Toolchain Support
 * ------------
 *
 * The library has been developed and tested with IAR version 8.20
 *
 *
 */

/**
 * @addtogroup groupFeature
 * @{
 */

/**
 * @brief Spectrum types
 */
typedef enum
{
  SPECTRUM_TYPE_MAGNITUDE,  /*!< magnitude spectrum */
  SPECTRUM_TYPE_POWER       /*!< squared magnitude spectrum */
} Spectrogram_TypeTypedef;

/**
 * @brief LogMel Spectrum decibel conversion formula
 */
typedef enum
{
  LOGMELSPECTROGRAM_SCALE_DB,  /*!< return mel energies using decibel scale (librosa) */
  LOGMELSPECTROGRAM_SCALE_LOG  /*!< return mel energies using natural log scale (TensorFlow) */
} LogMelSpectrogram_ScaleTypedef;

/**
 * @brief Instance structure for the floating-point Spectrogram function.
 */
typedef struct
{
  arm_rfft_fast_instance_f32 *pRfft;         /*!< points to the real FFT instance */
  Spectrogram_TypeTypedef Type;              /*!< spectrum type */
  float32_t *pWindow;                        /*!< points to the window function. The length must be equal to FrameLen. */
  uint32_t SampRate;                         /*!< sampling rate of the input signal. */
  uint32_t FrameLen;                         /*!< length of the input signal. */
  uint32_t FFTLen;                           /*!< length of the real FFT. */
  uint32_t pad_left;                         /*!< zero padding on the left of the window . */
  uint32_t pad_right;                        /*!< zero padding on the right of the window . */
  float32_t spectro_sum;                     /*!< sum of spectrogram components */
  float32_t *pScratch1;                      /*!< point to the first temporary calculation buffer of length FFTLen */
  float32_t *pScratch2;                      /*!< point to the second temporary calculation buffer of length FFTLen */
} SpectrogramTypeDef;

/**
 * @brief Instance structure for the floating-point MelSpectrogram function.
 */
typedef struct
{
  SpectrogramTypeDef *SpectrogramConf;       /*!< points to the Spectrogram instance */
  MelFilterTypeDef *MelFilter;               /*!< points to the MelFilter instance */
} MelSpectrogramTypeDef;

/**
 * @brief Instance structure for the floating-point Log-MelSpectrogram function.
 */
typedef struct
{
  MelSpectrogramTypeDef *MelSpectrogramConf; /*!< points to the Mel-Spectrogram instance */
  LogMelSpectrogram_ScaleTypedef LogFormula; /*!< returned mel energy scale (dB or Log) */
  float32_t Ref;                             /*!< scaling for the input signal (typ 1.0).
                                                  Input signal is scaled by 1.0 / Ref. */
  float32_t TopdB;                           /*!< threshold the ouput to -TopdB when dB scaled is used (typ. 80.0 dB) */
} LogMelSpectrogramTypeDef;

/**
 * @brief Instance structure for the floating-point Mfcc function.
 */
typedef struct
{
  LogMelSpectrogramTypeDef *LogMelConf;      /*!< points to the LogMel instance */
  DCT_InstanceTypeDef *pDCT;                 /*!< points to the DCT instance. */
  uint32_t NumMfccCoefs;                     /*!< number of mel coefficients to return. */
  float32_t *pScratch;                       /*!< points to the temporary calculation buffer of length NumMels */
} MfccTypeDef;

/* Utilities */
void buf_to_float(int16_t *pInSignal, float32_t *pOutSignal, uint32_t len);
void buf_to_float_normed(int16_t *pInSignal, float32_t *pOutSignal, uint32_t len);

/* Column calculation functions */
void SpectrogramColumn(SpectrogramTypeDef *S, float32_t *pInSignal, float32_t *pOutCol);
void MelSpectrogramColumn(MelSpectrogramTypeDef *S, float32_t *pInSignal, float32_t *pOutCol);
void LogMelSpectrogramColumn(LogMelSpectrogramTypeDef *S, float32_t *pInSignal, float32_t *pOutCol);
void LogMelSpectrogramColumn_q15_Q8(LogMelSpectrogramTypeDef *S, int16_t *pInSignal, int8_t *pOutCol,int8_t offset,float32_t inv_scale);
void MfccColumn(MfccTypeDef *S, float32_t *pInSignal, float32_t *pOutCol);

/**
 * @} end of groupFeature
 */

#ifdef __cplusplus
}
#endif

#endif /* _FEATURE_EXTRACTION_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/

