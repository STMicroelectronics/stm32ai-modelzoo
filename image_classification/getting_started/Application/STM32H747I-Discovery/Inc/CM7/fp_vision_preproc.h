/**
 ******************************************************************************
 * @file    fp_vision_preproc.h
 * @author  MCD Application Team
 * @brief   Header for fp_vision_preproc.c module
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
#ifndef __FP_VISION_PREPROC_H
#define __FP_VISION_PREPROC_H

#ifdef __cplusplus
extern "C"
{
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32ipl.h"

/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/
/* External variables --------------------------------------------------------*/


/* Exported functions ------------------------------------------------------- */
void PREPROC_ImageResize(AppConfig_TypeDef*);
void PREPROC_PixelFormatConversion(AppConfig_TypeDef*);
void PREPROC_Pixel_RB_Swap(void *, void *, uint32_t );
void PREPROC_Init(AppConfig_TypeDef * );

#ifdef __cplusplus
}
#endif

#endif /*__FP_VISION_PREPROC_H */

