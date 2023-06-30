/**
  ******************************************************************************
  * @file    SPIBusIF.c
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

#include "SPIBusIF.h"
#include "services/sysmem.h"

// Private functions declaration
// *****************************

// Private variables
// *****************

// Public API implementation.
// **************************

ABusIF *SPIBusIFAlloc(uint8_t who_am_i, GPIO_TypeDef *p_port, uint16_t pin, uint8_t auto_inc)
{
  SPIBusIF *_this = NULL;

  _this = SysAlloc(sizeof(SPIBusIF));
  if (_this != NULL)
  {
    ABusIFInit(&_this->super, who_am_i);

    _this->p_cs_gpio_port = p_port;
    _this->cs_gpio_pin = pin;
    _this->auto_inc = auto_inc;

    // initialize the software resources
    if (TX_SUCCESS != tx_semaphore_create(&_this->sync_obj, "SPI_IP_S", 0))
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

sys_error_code_t SPIBusIFWaitIOComplete(SPIBusIF *_this)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (TX_SUCCESS != tx_semaphore_get(&_this->sync_obj, TX_WAIT_FOREVER))
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }

  return res;
}

sys_error_code_t SPIBusIFNotifyIOComplete(SPIBusIF *_this)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (TX_SUCCESS != tx_semaphore_put(&_this->sync_obj))
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    res = SYS_UNDEFINED_ERROR_CODE;
  }

  return res;
}

// Private functions definition
// ****************************

