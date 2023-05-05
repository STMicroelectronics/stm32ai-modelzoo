/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    gpdma.h
  * @brief   This file contains all the function prototypes for
  *          the gpdma.c file
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __GPDMA_H__
#define __GPDMA_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* USER CODE BEGIN Includes */

/* USER CODE END Includes */



extern DMA_HandleTypeDef handle_GPDMA1_Channel3;

extern DMA_HandleTypeDef handle_GPDMA1_Channel2;


/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

void MX_GPDMA1_Init(void);

/* USER CODE BEGIN Prototypes */
void MX_GPDMA1_InitCustom(void);
/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif

#endif /* __GPDMA_H__ */

