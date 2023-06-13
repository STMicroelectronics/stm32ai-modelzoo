/**
 ******************************************************************************
 * @file    window.c
 * @author  MCD Application Team
 * @brief   Window functions generation
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
#include "window.h"

#ifndef M_PI
#define M_PI    3.14159265358979323846264338327950288 /*!< pi */
#endif

/**
 * @defgroup groupWindow Window functions
 * @brief Window functions generation
 *
 * A lot of different window have been developed and tested in DSP,
 * but common choice is between Hanning, Hamming, Blackman and Flat-Top (even if many others are available).
 * - https://github.com/ARM-software/CMSIS_5/issues/217
 *
 * @{
 */

void cosine_sum_window_create(float32_t *pDst, uint32_t len, float64_t a0, float64_t a1, float64_t a2);

/**
 * @brief      Generate a window function.
 *
 * @param      *pDst  points to the output buffer.
 * @param      len    window length.
 * @param      type   window type.
 * @return     0 if successful or -1 if there is an error.
 */
int32_t Window_Init(float32_t *pDst, uint32_t len, WindowTypedef type)
{
  int32_t status = 0;

  switch (type)
  {
    case WINDOW_HANN:
      cosine_sum_window_create(pDst, len, 0.5, 0.5, 0.0);
      break;
    case WINDOW_HAMMING:
      cosine_sum_window_create(pDst, len, 0.54, 0.46, 0.0);
      break;
    case WINDOW_BLACKMAN:
      cosine_sum_window_create(pDst, len, 0.42, 0.5, 0.08);
      break;
    default:
      /* Window type is not implemented */
      status = -1;
      break;
  }

  return status;
}

/**
 * @brief Helper function to create cosine-sum windows
 */
void cosine_sum_window_create(float32_t *pDst, uint32_t len, float64_t a0, float64_t a1, float64_t a2)
{

  for (uint32_t i = 0; i < len; i++)
  {
    *pDst++ = a0
            - a1 * cos(2.0 * M_PI * (float64_t) i / (float64_t) len)
            + a2 * cos(4.0 * M_PI * (float64_t) i / (float64_t) len);
  }
}

/**
 * @} end of groupWindow
 */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
