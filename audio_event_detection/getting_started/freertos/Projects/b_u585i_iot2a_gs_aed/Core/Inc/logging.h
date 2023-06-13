/**
  ******************************************************************************
  * @file           : Logging.h
  * @brief          : This file contains a stub for a logger
  * 
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


/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __LOGGING_H
#define __LOGGING_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include <stdio.h>

/* Exported macro ------------------------------------------------------------*/
#define LogError  printf
#define LogInfo   printf
#define LogSys    printf
#define LogDebug  printf
#define LogAssert printf
#define LogWarn   printf

#ifdef __cplusplus
}
#endif

#endif /*  __LOGGING_ */
