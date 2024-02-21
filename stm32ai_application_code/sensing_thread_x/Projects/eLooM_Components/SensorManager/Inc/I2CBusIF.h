/**
  ******************************************************************************
  * @file    I2CBusIF.h
  * @author  SRA - MCD
  * @brief
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
#ifndef I2CBUSIF_H_
#define I2CBUSIF_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "ABusIF.h"
#include "tx_api.h"


/**
  * Create a type name for _I2CBusIF.
  */
typedef struct _I2CBusIF I2CBusIF;

/**
  * Specifies the I2C interface for a generic sensor.
  */
struct _I2CBusIF
{
  /**
    * The bus connector encapsulates the function pointer to read and write in the bus,
    * and it is compatible with the the ST universal sensor driver.
    */
  ABusIF super;

  /**
    * Slave address.
    */
  uint8_t address;

  /**
    * Address auto-increment (Multi-byte read/write).
    */
  uint8_t auto_inc;

  /**
    * Synchronization object used to synchronize the sensor with the bus.
    */
  TX_SEMAPHORE sync_obj;
};


// Public API declaration
// **********************

/**
  * Initialize a sensor object. It must be called once before using the sensor.
  *
  * @param _this [IN] specifies a sensor object.
  * @param nWhoAmI [IN] specifies the sensor ID. It can be zero.
  * @param nAddress [IN] specifies the I2C address of the device.
  * @param nAutoInc [IN] specifies the I2C address auto-increment to allow multiple data read/write.
  * @return SYS_NO_EROR_CODE if success, an error code otherwise.
  */
ABusIF *I2CBusIFAlloc(uint8_t who_am_i, uint8_t address, uint8_t auto_inc);

sys_error_code_t I2CBusIFWaitIOComplete(I2CBusIF *_this);
sys_error_code_t I2CBusIFNotifyIOComplete(I2CBusIF *_this);

int32_t I2CBusNullRW(void *p_sensor, uint8_t reg, uint8_t *p_data, uint16_t size);

// Inline function definition
// **************************

#ifdef __cplusplus
}
#endif

#endif /* I2CBUSIF_H_ */
