 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_display_spi.h
 * @author  MDG Application Team
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

#ifndef NUCLEO_H743ZI2_DISPLAY_SPI_H
#define NUCLEO_H743ZI2_DISPLAY_SPI_H

/* Includes ------------------------------------------------------------------*/
#include "lcd.h"

/* Functions prototype -------------------------------------------------------*/
int32_t BSP_DISPLAY_SPI_Init(void);
void BSP_DISPLAY_SPI_DrawImage(const char* Image_Array);

#endif 