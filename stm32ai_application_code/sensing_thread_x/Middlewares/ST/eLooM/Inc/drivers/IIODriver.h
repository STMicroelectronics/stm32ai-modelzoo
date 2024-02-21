/**
 ******************************************************************************
 * @file    IIODriver.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Aug 6, 2019
 *
 * @brief   I/O Driver interface.
 *
 * I/O driver interface extends the basic ::IDriver interface with read and
 * write operation.
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2017 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef INCLUDE_DRIVERS_IIODRIVER_H_
#define INCLUDE_DRIVERS_IIODRIVER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "IDriver.h"
//#include "IDriver_vtbl.h"


/**
 * Create  type name for _IIODriver.
 */
typedef struct _IIODriver IIODriver;


// Public API declaration
//***********************

/**
 *
 * @param _this [IN] specifies a pointer to a IIODriver object.
 * @param pDataBuffer [IN] specifies the buffer with the data to be written by the driver.
 * @param nDataSize [IN] specified the size in byte of the buffer.
 * @param nChannel [IN] specifies the channel where to write the data.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IIODrvWrite(IIODriver *_this, uint8_t *pDataBuffer, uint16_t nDataSize, uint16_t nChannel);

/**
 *
 * @param _this [IN] specifies a pointer to a IIODriver object.
 * @param pDataBuffer [OUT] specifies the buffer used to store the received data.
 * @param nDataSize [IN] specified the size in byte of the buffer.
 * @param nChannel [IN] specifies the channel from where to read the data.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IIODrvRead(IIODriver *_this, uint8_t *pDataBuffer, uint16_t nDataSize, uint16_t nChannel);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_DRIVERS_IIODRIVER_H_ */
