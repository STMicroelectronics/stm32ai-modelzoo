/**
  ******************************************************************************
  * @file    IBus.h
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
#ifndef IBUS_H_
#define IBUS_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "ABusIF.h"


/**
  * Creates a type name for _IBus.
  */
typedef struct _IBus IBus;


static inline sys_error_code_t IBusCtrl(IBus *_this, EBusCtrlCmd eCtrlCmd, uint32_t nParams);

/**
  * Connect a device to the bus using its interface.
  *
  * @param _this [IN] specifies a bus object.
  * @param pxBusIF [IN] specifies the device interface to connect.
  * @return SYS_NO_ERROR_CODE is success, SYS_INVALID_PARAMETER_ERROR_CODE if pxBuff is NULL.
  */
static inline sys_error_code_t IBusConnectDevice(IBus *_this, ABusIF *pxBusIF);

/**
  * Disconnect a device from the bus using its interface.
  *
  * @param _this [IN] specifies a bus object.
  * @param pxBusIF [IN] specifies the device interface to connect.
  * @return SYS_NO_ERROR_CODE is success, SYS_INVALID_PARAMETER_ERROR_CODE if pxBuff is NULL.
  */
static inline sys_error_code_t IBusDisconnectDevice(IBus *_this, ABusIF *pxBusIF);

#ifdef __cplusplus
}
#endif

#endif /* IBUS_H_ */
