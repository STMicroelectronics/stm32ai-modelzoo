/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    mdf.h
  * @brief   This file contains all the function prototypes for
  *          the mdf.c file
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
#ifndef __MDF_H__
#define __MDF_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

extern MDF_HandleTypeDef AdfHandle0;

extern MDF_FilterConfigTypeDef AdfFilterConfig0;

extern MDF_HandleTypeDef MdfHandle0;

extern MDF_FilterConfigTypeDef MdfFilterConfig0;

/* USER CODE BEGIN Private defines */
extern MDF_DmaConfigTypeDef AdfDmaConfig;
extern MDF_DmaConfigTypeDef MdfDmaConfig;
/* USER CODE END Private defines */

void MX_ADF1_Init(void);
void MX_MDF1_Init(void);

/* USER CODE BEGIN Prototypes */

/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif

#endif /* __MDF_H__ */

