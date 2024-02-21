/**
 ******************************************************************************
 * @file    app_utility.h
 * @author  MCD Application Team
 * @brief   Header for app_utility.c module
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2019 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __APP_UTILITY_H
#define __APP_UTILITY_H

#ifdef __cplusplus
extern "C"
{
#endif

/* Includes ------------------------------------------------------------------*/
#include "camera.h"
#include "main.h"

typedef enum
{
  INVALIDATE           = 0x01,   
  CLEAN                = 0x02  
}DCache_Coherency_TypeDef;


/* Exported constants --------------------------------------------------------*/

/* External variables --------------------------------------------------------*/

/* Exported functions ------------------------------------------------------- */
void Utility_Dma2d_Memcpy(uint32_t *pSrc, uint32_t *pDst, uint16_t x, uint16_t y, uint16_t xsize, uint16_t ysize,
                        uint32_t rowStride, uint32_t input_color_format, uint32_t output_color_format, int pfc,
                        int red_blue_swap);
void Utility_DCache_Coherency_Maintenance(uint32_t *mem_addr, int32_t mem_size, DCache_Coherency_TypeDef Maintenance_operation);
void Utility_Bubblesort(float *prob, int *classes, int size);
uint32_t Utility_GetTimeStamp(void);

#ifdef __cplusplus
}
#endif

#endif /*__APP_UTILITY_H */

