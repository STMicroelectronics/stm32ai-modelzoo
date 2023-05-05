/**
 ******************************************************************************
 * @file    dct.h
 * @author  MCD Application Team
 * @brief   Header for dct.c module
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
#ifndef __DCT_H
#define __DCT_H

#ifdef __cplusplus
 extern "C" {
#endif

#include "arm_math.h"

/**
 * @addtogroup groupDCT
 * @{
 */

/**
 * @brief DCT types and normalization mode.
 */
typedef enum
{
  DCT_TYPE_I,          /*!< DCT type-I */
  DCT_TYPE_II,         /*!< DCT type-II */
  DCT_TYPE_II_ORTHO,   /*!< DCT type-II orthogonal */
  DCT_TYPE_II_SCALED,  /*!< DCT type-II scaled */
  DCT_TYPE_III,        /*!< DCT type-III */
  DCT_TYPE_III_ORTHO,  /*!< DCT type-III orthogonal */
} DCT_TypeTypeDef;

/**
 * @brief Instance structure for the floating-point DCT functions.
 */
typedef struct
{
  uint32_t NumFilters;     /*!< output length (e.g. number of MFCCs). */
  uint32_t NumInputs;      /*!< input signal length (e.g. number of mel bands). */
  DCT_TypeTypeDef Type;    /*!< DCT type and normalization mode. */
  uint32_t RemoveDCTZero;  /*!< compute DCT of length NumFilters + 1 and return the last NumFilters points. */
  float32_t *pDCTCoefs;    /*!< points to the cosFactor table of length (NumFilters * NumInputs) elements. */
} DCT_InstanceTypeDef;

int32_t DCT_Init(DCT_InstanceTypeDef *S);
void DCT(DCT_InstanceTypeDef *S, float32_t *pIn, float32_t *pOut);

/**
 * @} end of groupDCT
 */

#ifdef __cplusplus
}
#endif

#endif /* __DCT_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
