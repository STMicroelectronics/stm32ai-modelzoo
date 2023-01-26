/**
 ******************************************************************************
 * @file    SPIBusIF.h
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
#ifndef SPIBUSIF_H_
#define SPIBUSIF_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "ABusIF.h"
#include "FreeRTOS.h"
#include "semphr.h"


/**
 * Create a type name for _SPIBusIF.
 */
typedef struct _SPIBusIF SPIBusIF;

/**
 * Specifies the SPI interface for a generic sensor.
 */
struct _SPIBusIF {
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
   * Slave select GPIO Port
   */
  GPIO_TypeDef* m_pxSSPinPort;

  /**
   * Slave select GPIO Pin.
   */
  uint16_t m_nSSPin;

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
 * @param pxSSPinPort [IN] specifies the port PIN of the Slave Select line.
 * @param nSSPin [IN] specifies the pin number of the Slave Select line.
 * @return SYS_NO_EROR_CODE if success, an error code otherwise.
 */
sys_error_code_t SPIBusIFInit(SPIBusIF *_this, uint8_t nWhoAmI, GPIO_TypeDef* pxSSPinPort, uint16_t nSSPin);

sys_error_code_t SPIBusIFWaitIOComplete(SPIBusIF *_this);
sys_error_code_t SPIBusIFNotifyIOComplete(SPIBusIF *_this);

inline sys_error_code_t SPIBusIFSetWhoAmI(SPIBusIF *_this, uint8_t nWhoAmI);
inline uint8_t SPIBusIFGetWhoAmI(const SPIBusIF *_this);


// Inline function definition
// **************************

SYS_DEFINE_INLINE
sys_error_code_t SPIBusIFSetWhoAmI(SPIBusIF *_this, uint8_t nWhoAmI) {
  assert_param(_this);

  _this->m_nWhoAmI = nWhoAmI;

  return SYS_NO_ERROR_CODE;
}

SYS_DEFINE_INLINE
uint8_t SPIBusIFGetWhoAmI(const SPIBusIF *_this) {
  assert_param(_this);

  return _this->m_nWhoAmI;
}

#ifdef __cplusplus
}
#endif

#endif /* SPIBUSIF_H_ */
