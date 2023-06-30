/**
  ******************************************************************************
  * @file    SMMessageParser.c
  * @author  SRA - MCD
  * @brief   Definition of the HID REport PArser API.
  *
  * Definition of the HID REport PArser API.
  *
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  *
  ******************************************************************************
  */

#include "SMMessageParser.h"

uint16_t SMMessageGetSize(uint8_t message_id)
{
  uint16_t nSize;
  switch (message_id)
  {
    case SM_MESSAGE_ID_DATA_READY:
      nSize = sizeof(struct sensorDataReadyMessage_t);
      break;

    case SM_MESSAGE_ID_FORCE_STEP:
      nSize = sizeof(struct internalMessageFE_t);
      break;

    case SM_MESSAGE_ID_SD_CMD:
      nSize = sizeof(struct sdMessage_t);
      break;

    case SM_MESSAGE_ID_SENSOR_CMD:
      nSize = sizeof(struct sensorMessage_t);
      break;

    case SM_MESSAGE_ID_SPI_BUS_READ:
    case SM_MESSAGE_ID_SPI_BUS_WRITE:
      nSize = sizeof(struct spiIOMessage_t);
      break;

    case SM_MESSAGE_ID_I2C_BUS_READ:
    case SM_MESSAGE_ID_I2C_BUS_WRITE:
      nSize = sizeof(struct i2cIOMessage_t);
      break;

    default:
      nSize = sizeof(struct internalMessageFE_t);
  }

  return nSize;
}
