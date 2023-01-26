/**
 ******************************************************************************
 * @file    jdata_conf.h
 * @author  MCD Application Team
 * @brief   jdata_conf file template header file using FatFs API
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#include "stm32ipl_conf.h"

#ifdef STM32IPL_ENABLE_JPEG

/* Includes ------------------------------------------------------------------*/
#include "ff.h"
#include "stm32ipl_mem_alloc.h"

/* Private typedef -----------------------------------------------------------*/  
/* Private define ------------------------------------------------------------*/
#define JFILE     FIL
#define JMALLOC   xalloc
#define JFREE     xfree

#else /* STM32IPL_ENABLE_JPEG */

/* Includes ------------------------------------------------------------------*/
#include <stdint.h>
#include <stddef.h>

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
#define JFILE     void
#define JMALLOC   malloc
#define JFREE     free

#endif /* STM32IPL_ENABLE_JPEG */

#define JFREAD(file, buf, sizeofbuf)  \
   read_file(file, buf, sizeofbuf)

#define JFWRITE(file, buf, sizeofbuf)  \
   write_file(file, buf, sizeofbuf)

/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Private function prototypes -----------------------------------------------*/
/* Private functions ---------------------------------------------------------*/
size_t read_file(JFILE *file, uint8_t *buf, uint32_t sizeofbuf);
size_t write_file(JFILE *file, uint8_t *buf, uint32_t sizeofbuf);
