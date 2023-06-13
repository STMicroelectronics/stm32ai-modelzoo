/**
 ******************************************************************************
 * @file    window.h
 * @author  MCD Application Team
 * @brief   Header for window.c module
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
#ifndef __WINDOW_H
#define __WINDOW_H

#ifdef __cplusplus
 extern "C" {
#endif

#include "arm_math.h"

/**
 * @addtogroup groupWindow
 * @{
 */

/**
 * @brief Window function types
 */
typedef enum
{
  WINDOW_HANN,      /*!< Hann (Hanning) window */
  WINDOW_HAMMING,   /*!< Hamming window */
  WINDOW_BLACKMAN   /*!< Blackman window */
} WindowTypedef;

int32_t Window_Init(float32_t *pDst, uint32_t len, WindowTypedef type);

/**
 * @} end of groupWindow
 */

#ifdef __cplusplus
}
#endif

#endif /* __WINDOW_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
