/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    gpdma.c
  * @brief   This file provides code for the configuration
  *          of the GPDMA instances.
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
/* Includes ------------------------------------------------------------------*/
#include "gpdma.h"

/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/* GPDMA1 init function */
void MX_GPDMA1_Init(void)
{

  /* USER CODE BEGIN GPDMA1_Init 0 */

  /* USER CODE END GPDMA1_Init 0 */

  /* Peripheral clock enable */
  __HAL_RCC_GPDMA1_CLK_ENABLE();

  /* GPDMA1 interrupt Init */
//  HAL_NVIC_SetPriority(GPDMA1_Channel0_IRQn, 0, 0);
//  HAL_NVIC_EnableIRQ(GPDMA1_Channel0_IRQn);
//  HAL_NVIC_SetPriority(GPDMA1_Channel1_IRQn, 0, 0);
//  HAL_NVIC_EnableIRQ(GPDMA1_Channel1_IRQn);
  HAL_NVIC_SetPriority(GPDMA1_Channel2_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(GPDMA1_Channel2_IRQn);
  HAL_NVIC_SetPriority(GPDMA1_Channel3_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(GPDMA1_Channel3_IRQn);
//  HAL_NVIC_SetPriority(GPDMA1_Channel4_IRQn, 0, 0);
//  HAL_NVIC_EnableIRQ(GPDMA1_Channel4_IRQn);
  HAL_NVIC_SetPriority(GPDMA1_Channel5_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(GPDMA1_Channel5_IRQn);

  /* USER CODE BEGIN GPDMA1_Init 1 */

  /* USER CODE END GPDMA1_Init 1 */
  /* USER CODE BEGIN GPDMA1_Init 2 */

  /* USER CODE END GPDMA1_Init 2 */

}

/* USER CODE BEGIN 1 */

/* USER CODE END 1 */

void MX_GPDMA1_InitCustom(void)
{
  __HAL_RCC_GPDMA1_CLK_ENABLE();
//  HAL_NVIC_SetPriority(GPDMA1_Channel0_IRQn, 3, 0);
//  HAL_NVIC_SetPriority(GPDMA1_Channel1_IRQn, 3, 0);
  HAL_NVIC_SetPriority(GPDMA1_Channel2_IRQn, 3, 0);
  HAL_NVIC_SetPriority(GPDMA1_Channel3_IRQn, 3, 0);
//  HAL_NVIC_SetPriority(GPDMA1_Channel4_IRQn, 3, 0);
  HAL_NVIC_SetPriority(GPDMA1_Channel5_IRQn, 3, 0);
}
/* USER CODE END 1 */
