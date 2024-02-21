 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_camera_spi.h
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

#ifndef __NUCLEO_H743ZI2_CAMERA_SPI_H
#define __NUCLEO_H743ZI2_CAMERA_SPI_H

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "nucleo_h743zi2_camera.h"
#include "nucleo_h743zi2_errno.h"

/* Macros --------------------------------------------------------------------*/

/* Exported types ------------------------------------------------------------*/

/* Local variables -----------------------------------------------------------*/

/* Public functions ----------------------------------------------------------*/
void MX_SPI1_Init();
void SPI_Cam_Init_Begin(uint8_t *p_camera_capture_buffer);
void SPI_Cam_Take_Picture();
void SPI_Cam_Swap_Bytes();
void SPI_Cam_Fetch_Data();
void delayInit(void);
void delayMs(uint16_t nms);
void delayUs(uint32_t nus);
void spiBegin(void);
uint8_t spiReadWriteByte(uint8_t TxData);
void spiCsLow(int pin);
void spiCsHigh(int pin);
void spiCsOutputMode(int pin);

#endif /* __NUCLEO_H743ZI2_CAMERA_SPI_H */