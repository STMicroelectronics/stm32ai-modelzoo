/**
 ******************************************************************************
 * @file    SMUtilityDriver.c
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief   Sensor Manager Utility driver.
 *
 * This driver is in charge of the timer used for the timestamp.
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

#include "drivers/SMUtilityDriver.h"
#include "drivers/SMUtilityDriver_vtbl.h"
#include "FreeRTOS.h"
#include "services/sysdebug.h"


#define SYS_DEBUGF(level, message)      SYS_DEBUGF3(SYS_DBG_DRIVERS, level, message)

/**
 * SMUtilityDriver_t Driver virtual table.
 */
static const IDriver_vtbl sUtilityDriver_vtbl = {
    SMUtilityDriver_vtblInit,
    SMUtilityDriver_vtblStart,
    SMUtilityDriver_vtblStop,
    SMUtilityDriver_vtblDoEnterPowerMode,
    SMUtilityDriver_vtblReset
};

/*
 GCC requires one function forward declaration in only one .c source
 in order to manage the inline.
 See also http://stackoverflow.com/questions/26503235/c-inline-function-and-gcc
 */
#if defined (__GNUC__) || defined (__ICCARM__)
extern uint32_t SMUtilityDrvGetTimeStamp(SMUtilityDriver_t *_this);
#endif

/* Private member function declaration */
/***************************************/

/* Public API definition */
/*************************/

IDriver* SMUtilityDriverAlloc(void)
{
  IDriver *p_new_obj = (IDriver*) pvPortMalloc(sizeof(SMUtilityDriver_t));

  if(p_new_obj == NULL)
  {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("UtilityDriver - alloc failed.\r\n"));
  }
  else
  {
    p_new_obj->vptr = &sUtilityDriver_vtbl;
  }

  return p_new_obj;
}

sys_error_code_t SMUtilityDriver_vtblInit(IDriver *_this, void *p_params)
{
  assert_param(_this != NULL);
//  assert_param(p_params);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SMUtilityDriver_t *p_obj = (SMUtilityDriver_t*) _this;
  SMUtilityDriverParams_t *p_init_param = (SMUtilityDriverParams_t*)p_params;
  p_obj->mx_handle.p_mx_tim_cfg = p_init_param->p_mx_tim_cfg;
  /*TIM_HandleTypeDef p_tim = p_obj->mx_handle.p_mx_tim_cfg->p_tim;*/

  /* Initialize the timer for the timestamp  */
  p_obj->mx_handle.p_mx_tim_cfg->p_mx_init_f();

  return res;
}

sys_error_code_t SMUtilityDriver_vtblStart(IDriver *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SMUtilityDriver_t *p_obj = (SMUtilityDriver_t*) _this;
  TIM_HandleTypeDef *p_tim = p_obj->mx_handle.p_mx_tim_cfg->p_tim;

  if(HAL_TIM_Base_Start(p_tim) != HAL_OK)
  {
    res = SYS_UNDEFINED_ERROR_CODE;
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    sys_error_handler();
  }

  return res;
}

sys_error_code_t SMUtilityDriver_vtblStop(IDriver *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SMUtilityDriver_t *p_obj = (SMUtilityDriver_t*) _this;
  TIM_HandleTypeDef *p_tim = p_obj->mx_handle.p_mx_tim_cfg->p_tim;

  if(HAL_TIM_Base_Stop(p_tim) != HAL_OK)
  {
    res = SYS_UNDEFINED_ERROR_CODE;
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    sys_error_handler();
  }
  p_tim->Instance->CNT = 0;

  return res;
}

sys_error_code_t SMUtilityDriver_vtblDoEnterPowerMode(IDriver *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  /*UtilityDriver *p_obj = (UtilityDriver*)_this;*/

  if(new_power_mode == E_POWER_MODE_SENSORS_ACTIVE)
  {
    SMUtilityDriver_vtblStart(_this);
  }
  else
  {
    SMUtilityDriver_vtblStop(_this);
  }

  return res;
}

sys_error_code_t SMUtilityDriver_vtblReset(IDriver *_this, void *p_params)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  /*UtilityDriver *p_obj = (UtilityDriver*)_this;*/

  return res;
}

/* Private function definition */
/*******************************/
