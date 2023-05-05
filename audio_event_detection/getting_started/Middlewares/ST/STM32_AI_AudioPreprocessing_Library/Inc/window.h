/**
 ******************************************************************************
 * @file    window.h
 * @author  MCD Application Team
 * @brief   Header for window.c module
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
