/**
 ******************************************************************************
 * @file    I2CBusIF.h
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
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
 *
 ******************************************************************************
 */
#ifndef I2CBUSIF_H_
#define I2CBUSIF_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "ABusIF.h"
#include "FreeRTOS.h"
#include "semphr.h"


/**
 * Create a type name for _I2CBusIF.
 */
typedef struct _I2CBusIF I2CBusIF;

/**
 * Specifies the I2C interface for a generic sensor.
 */
struct _I2CBusIF {
  /**
   * The bus connector encapsulates the function pointer to read and write in the bus,
   * and it is compatible with the the ST universal sensor driver.
   */
  ABusIF super;

  /**
   * Sensor ID.
   */
  uint8_t m_nWhoAmI;

  /**
   * Slave address.
   */
  uint8_t m_nAddress;

  /**
   * Synchronization object used to synchronize the sensor with the bus.
   */
  SemaphoreHandle_t m_xSyncObj;
};


// Public API declaration
// **********************

/**
 * Initialize a sensor object. It must be called once before using the sensor.
 *
 * @param _this [IN] specifies a sensor object.
 * @param nWhoAmI [IN] specifies the sensor ID. It can be zero.
 * @param nAddress [IN] specifies the I2C address of teh device.
 * @return SYS_NO_EROR_CODE if success, an error code otherwise.
 */
sys_error_code_t I2CBusIFInit(I2CBusIF *_this, uint8_t nWhoAmI, uint8_t nAddress);

sys_error_code_t I2CBusIFWaitIOComplete(I2CBusIF *_this);
sys_error_code_t I2CBusIFNotifyIOComplete(I2CBusIF *_this);

inline sys_error_code_t I2CBusIFSetWhoAmI(I2CBusIF *_this, uint8_t nWhoAmI);
inline uint8_t I2CBusIFGetWhoAmI(const I2CBusIF *_this);

int32_t I2CBusNullRW(void *pxSensor, uint8_t nRegAddr, uint8_t* pnData, uint16_t nSize);

// Inline function definition
// **************************

SYS_DEFINE_INLINE
sys_error_code_t I2CBusIFSetWhoAmI(I2CBusIF *_this, uint8_t nWhoAmI) {
  assert_param(_this);

  _this->m_nWhoAmI = nWhoAmI;

  return SYS_NO_ERROR_CODE;
}

SYS_DEFINE_INLINE
uint8_t I2CBusIFGetWhoAmI(const I2CBusIF *_this) {
  assert_param(_this);

  return _this->m_nWhoAmI;
}

#ifdef __cplusplus
}
#endif

#endif /* I2CBUSIF_H_ */
