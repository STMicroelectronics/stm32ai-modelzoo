
/*
 * This file is part of the Arducam SPI Camera project.
 *
 * Copyright 2021 Arducam Technology co., Ltd. All Rights Reserved.
 *
 * This work is licensed under the MIT license, see the file LICENSE for details.
 *
 */



#ifndef  __STM32HAL_H
#define  __STM32HAL_H

#include "nucleo_h743zi2_camera_spi.h"

#define arducamSpiBegin()                    spiBegin()
#define arducamSpiTransfer(val)              spiReadWriteByte(val)    //  SPI communication sends a byte
#define arducamSpiCsPinHigh(pin)             spiCsHigh(pin)    //Set the CS pin of SPI to high level
#define arducamSpiCsPinLow(pin)              spiCsLow(pin)  //Set the CS pin of SPI to low level
#define arducamCsOutputMode(pin)             spiCsOutputMode(pin)
#define arducamDelayMs(val)                  delayMs(val)           //  Delay Ms
#define arducamDelayUs(val)                  delayUs(val) //Delay Us

#endif /*__STM32HAL_H*/

