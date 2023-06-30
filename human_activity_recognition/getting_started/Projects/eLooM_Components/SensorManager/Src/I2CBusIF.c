/**
  ******************************************************************************
  * @file    I2CBusIF.c
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

#include "I2CBusIF.h"
#include "services/sysmem.h"

// Private functions declaration
// *****************************

// Private variables
// *****************

// Public API implementation.
// **************************

ABusIF *I2CBusIFAlloc(uint8_t who_am_i, uint8_t address, uint8_t auto_inc)
{
  I2CBusIF *_this = NULL;

  _this = (I2CBusIF *)SysAlloc(sizeof(I2CBusIF));
  if (_this != NULL)
  {
    ABusIFInit(&_this->super, who_am_i);

    _this->address = address;
    _this->auto_inc = auto_inc;

    // initialize the software resources
    if (TX_SUCCESS != tx_semaphore_create(&_this->sync_obj, "I2C_IP_S", 0))
    {
      SysFree(_this);
      _this = NULL;
    }
    else
    {
      ABusIFSetHandle(&_this->super, _this);
    }
  }
  return (ABusIF *)_this;
}

sys_error_code_t I2CBusIFWaitIOComplete(I2CBusIF *_this)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  // if (_this->m_xSyncObj != NULL){//TODO: STF.Port - how to check the sem is initialized ??
  if (TX_SUCCESS != tx_semaphore_get(&_this->sync_obj, TX_WAIT_FOREVER))
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }
  // }

  return res;
}

sys_error_code_t I2CBusIFNotifyIOComplete(I2CBusIF *_this)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  // if (_this->m_xSyncObj != NULL){//TODO: STF.Port - how to check the sem is initialized ??
  if (TX_SUCCESS != tx_semaphore_put(&_this->sync_obj))
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }
//  }

  return res;
}

// Private functions definition
// ****************************

int32_t I2CBusNullRW(void *p_sensor, uint8_t reg, uint8_t *p_data, uint16_t size)
{
  UNUSED(p_sensor);
  UNUSED(reg);
  UNUSED(p_data);
  UNUSED(size);

  return 0;
}
