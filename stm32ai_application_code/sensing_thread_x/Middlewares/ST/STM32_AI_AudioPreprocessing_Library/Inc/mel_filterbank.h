/**
 ******************************************************************************
 * @file    mel_filterbank.h
 * @author  MCD Application Team
 * @brief   Header for mel_filterbank.c module
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; Copyright (c) 2019 STMicroelectronics.
 * All rights reserved.</center></h2>
 *
 * This software component is licensed by ST under Software License Agreement
 * SLA0055, the "License"; You may not use this file except in compliance with
 * the License. You may obtain a copy of the License at:
 *        www.st.com/resource/en/license_agreement/dm00251784.pdf
 *
 ******************************************************************************
 */
#ifndef __MEL_FILTERBANK_H
#define __MEL_FILTERBANK_H

#ifdef __cplusplus
 extern "C" {
#endif

#include "arm_math.h"

/**
 * @addtogroup groupMelFilterbank
 * @{
 */

/**
 * @brief Mel-Hz conversion formula types
 */
typedef enum
{
  MEL_HTK,    /*!< HTK Formula */
  MEL_SLANEY  /*!< Malcolm Slaney's Formula */
} MelFormulaTypedef;

/**
 * @brief Instance structure for the floating-point MelFilterbank function.
 */
typedef struct
{
  uint32_t  *pStartIndices;    /*!< points to the mel filter pCoefficients start indexes */
  uint32_t  *pStopIndices;     /*!< points to the mel filter pCoefficients stop indexes */
  float32_t *pCoefficients;    /*!< points to the mel filter weights of length CoefficientsLength */
  uint32_t CoefficientsLength; /*!< (Set by Init) number pCoefficients elements */
  uint32_t NumMels;            /*!< number of Mel bands to generate. */
  uint32_t FFTLen;             /*!< number of input FFT points. */
  uint32_t SampRate;           /*!< input signal sampling rate. */
  float32_t FMin;              /*!< lowest frequency in Hz (typ. 0). */
  float32_t FMax;              /*!< highest frequency in Hz (typ. sr / 2.0). */
  MelFormulaTypedef Formula;   /*!< Mel-Hz conversion formula type. */
  uint32_t Normalize;          /*!< if 0, leave all the triangles. Otherwise divide the triangular mel weights by the
                                    width of the mel band (area normalization) */
  uint32_t Mel2F; /*!< if 0, create bins in mel domain (TensorFlow). Otherwise, create bins in Hz domain (librosa) */
} MelFilterTypeDef;


void MelFilterbank_Init(MelFilterTypeDef *MelFilterStruct);
void MelFilterbank(MelFilterTypeDef *M, float32_t *pSpectrCol, float32_t *pMelCol);

/**
 * @} end of groupMelFilterbank
 */

#ifdef __cplusplus
}
#endif

#endif /* __MEL_FILTERBANK_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
