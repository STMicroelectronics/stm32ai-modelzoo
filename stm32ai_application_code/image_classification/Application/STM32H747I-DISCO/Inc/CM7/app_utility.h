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
void Utility_Dma2d_Memcpy(uint32_t *, uint32_t *, uint16_t , uint16_t , uint16_t , uint16_t ,
                     uint32_t , uint32_t , uint32_t , int , int );
void Utility_DCache_Coherency_Maintenance(uint32_t *, int32_t , DCache_Coherency_TypeDef );
void Utility_Bubblesort(float *, int *, int);
uint32_t Utility_GetTimeStamp(void);

#ifdef __cplusplus
}
#endif

#endif /*__APP_UTILITY_H */

