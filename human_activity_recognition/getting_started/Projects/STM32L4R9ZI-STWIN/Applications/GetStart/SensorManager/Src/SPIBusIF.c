/**
 ******************************************************************************
 * @file    SPIBusIF.c
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

#include "SPIBusIF.h"

// Private functions declaration
// *****************************


// Private variables
// *****************


// Public API implementation.
// **************************

// GCC requires one function forward declaration in only one .c source
// in order to manage the inline.
// See also http://stackoverflow.com/questions/26503235/c-inline-function-and-gcc
#if defined (__GNUC__) || defined (__ICCARM__)
extern sys_error_code_t SPIBusIFSetWhoAmI(SPIBusIF *_this, uint8_t nWhoAmI);
extern uint8_t SPIBusIFGetWhoAmI(const SPIBusIF *_this);
#endif

sys_error_code_t SPIBusIFInit(SPIBusIF *_this, uint8_t nWhoAmI, GPIO_TypeDef* pxSSPinPort, uint16_t nSSPin) {
  assert_param(_this);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  ABusIFInit(&_this->super);

  _this->m_nWhoAmI = nWhoAmI;
  _this->m_pxSSPinPort = pxSSPinPort;
  _this->m_nSSPin = nSSPin;

  // initialize the software resources
  _this->m_xSyncObj = xSemaphoreCreateBinary();
  if (_this->m_xSyncObj == NULL){
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
    xRes = SYS_OUT_OF_MEMORY_ERROR_CODE;
  }
#ifdef DEBUG
  else {
    vQueueAddToRegistry(_this->m_xSyncObj, "SPI_IP_S");
  }
#endif

  return xRes;
}

sys_error_code_t SPIBusIFWaitIOComplete(SPIBusIF *_this) {
  assert_param(_this);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  if (_this->m_xSyncObj != NULL){
    if (pdTRUE != xSemaphoreTake(_this->m_xSyncObj, portMAX_DELAY)) {
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
      xRes = SYS_UNDEFINED_ERROR_CODE;
    }
  }
  else {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_FUNC_CALL_ERROR_CODE);
    xRes = SYS_INVALID_FUNC_CALL_ERROR_CODE;
  }

  return xRes;
}

sys_error_code_t SPIBusIFNotifyIOComplete(SPIBusIF *_this) {
  assert_param(_this);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  if (_this->m_xSyncObj != NULL){
    if (pdTRUE != xSemaphoreGive(_this->m_xSyncObj)) {
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
      xRes = SYS_UNDEFINED_ERROR_CODE;
    }
  }
  else {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_FUNC_CALL_ERROR_CODE);
    xRes = SYS_INVALID_FUNC_CALL_ERROR_CODE;
  }

  return xRes;
}


// Private functions definition
// ****************************


