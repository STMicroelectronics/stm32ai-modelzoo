 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_display_spi.c
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

/* Includes ------------------------------------------------------------------*/
#include "ILI9341_STM32_Driver.h"

/* Functions definition ------------------------------------------------------*/
int32_t BSP_DISPLAY_SPI_Init(void)
{
  return ILI9341_Init(SCREEN_HORIZONTAL_1);
}

void BSP_DISPLAY_SPI_DrawImage(const char* Image_Array)
{
  ILI9341_Draw_Image(Image_Array, SCREEN_HORIZONTAL_1);
}
