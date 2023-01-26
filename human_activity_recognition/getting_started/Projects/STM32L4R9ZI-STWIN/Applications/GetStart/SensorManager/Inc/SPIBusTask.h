/**
 ******************************************************************************
 * @file    SPIBusTask.h
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
#ifndef SPIBUSTASK_H_
#define SPIBUSTASK_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systp.h"
#include "services/syserror.h"
#include "services/AManagedTaskEx.h"
#include "services/AManagedTaskEx_vtbl.h"
#include "drivers/IIODriver.h"
#include "drivers/IIODriver_vtbl.h"
#include "SPIBusIF.h"
#include "IBus.h"
#include "IBus_vtbl.h"
#include "queue.h"

#include "SMMessageParser.h"


/**
 * Create  type name for _SPIBusTask.
 */
typedef struct _SPIBusTask SPIBusTask;

/**
 *  SPIBusTask internal structure.
 */
struct _SPIBusTask {
  /**
   * Base class object.
   */
  AManagedTaskEx super;

  /* Task variables should be added here. */

  /**
   * Driver object.
   */
  IIODriver *m_pxDriver;

  /**
   * HAL driver configuration parameters.
   */
  const void *p_mx_drv_cfg;

  /**
   * Bus interface used to connect and disconnect devices to this object.
   */
  IBus *m_pBusIF;

  /**
   * Task message queue. Read and write request are wrapped into message posted in this queue.
   */
  QueueHandle_t m_xInQueue;

  /**
   * Count the number of devices connected to the bus. It can be used in further version to
   * de-initialize the SPI IP in some of the PM state.
   */
  uint8_t m_nConnectedDevices;
};


// Public API declaration
//***********************

/**
 * Allocate an instance of SPIBusTask.
 *
 * @param p_mx_drv_cfg [IN] specifies a ::MX_SPIParams_t instance declared in the mx.h file.
 * @return a pointer to the generic object ::AManagedTaskEx if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *SPIBusTaskAlloc(const void *p_mx_drv_cfg);

/**
 * Connect a device to the bus using its interface.
 *
 * @param _this [IN] specifies a task object.
 * @param pxBusIF [IN] specifies the device interface to connect.
 * @return SYS_NO_ERROR_CODE is success, SYS_INVALID_PARAMETER_ERROR_CODE if pxBuff is NULL.
 */
sys_error_code_t SPIBusTaskConnectDevice(SPIBusTask *_this, SPIBusIF *pxBusIF);

/**
 * Disconnect a device from the bus using its interface.
 *
 * @param _this [IN] specifies a task object.
 * @param pxBusIF [IN] specifies the device interface to connect.
 * @return SYS_NO_ERROR_CODE is success, SYS_INVALID_PARAMETER_ERROR_CODE if pxBuff is NULL.
 */
sys_error_code_t SPIBusTaskDisconnectDevice(SPIBusTask *_this, SPIBusIF *pxBusIF);

/**
 * Get the ::IBus interface of teh task.
 *
 * @param _this [IN] specifies a task object.
 * @return the ::IBus interface of the task.
 */
IBus *SPIBusTaskGetBusIF(SPIBusTask *_this);



// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* SPIBUSTASK_H_ */
