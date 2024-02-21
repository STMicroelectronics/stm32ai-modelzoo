/**
 ******************************************************************************
 * @file    SwTSDriver.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 4.0.0
 * @date    Mar 21, 2022
 *
 * @brief   Definition of the software driver used by the framework for the
 * timestamp service.
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights xReserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#include "drivers/SwTSDriver.h"
#include "drivers/SwTSDriver_vtbl.h"
/* MISRA messages linked to ThreadX include are ignored */
/*cstat -MISRAC2012-* */
#include "tx_api.h"
/*cstat +MISRAC2012-* */
#include "services/sysdebug.h"


#define SYS_DEBUGF(level, message)      SYS_DEBUGF3(SYS_DBG_DRIVERS, level, message)


/**
 * SwTSDriver Driver virtual table.
 */
static const ITSDriver_vtbl sSwTSDriver_vtbl = {
    SwTSDriver_vtblInit,
    SwTSDriver_vtblStart,
    SwTSDriver_vtblStop,
    SwTSDriver_vtblDoEnterPowerMode,
    SwTSDriver_vtblReset,
    SwTSDriver_vtblGetTimestamp
};


/* Private member function declaration */
/***************************************/


/* Public API definition */
/*************************/


/* IDriver virtual functions definition */
/****************************************/

IDriver *SwTSDriverAlloc(void) {
  ITSDriver_t *pxNewObj = (ITSDriver_t*)SysAlloc(sizeof(SwTSDriver_t));

  if (pxNewObj == NULL) {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SwTSDriver - alloc failed.\r\n"));
  }
  else {
    pxNewObj->vptr = &sSwTSDriver_vtbl;
  }

  return (IDriver*)pxNewObj;
}

sys_error_code_t SwTSDriver_vtblInit(IDriver *_this, void *pxParams) {
  assert_param(_this != NULL);
  UNUSED(pxParams);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  SwTSDriver_t *pxObj = (SwTSDriver_t*)_this;

  pxObj->m_nStartTick = 0;

  return xRes;
}

sys_error_code_t SwTSDriver_vtblStart(IDriver *_this) {
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  /*SwTSDriver_t *pxObj = (SwTSDriver_t*)_this;*/

  SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SwTsDrv: start driver.\r\n"));

  return xRes;
}

sys_error_code_t SwTSDriver_vtblStop(IDriver *_this) {
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  /*SwTSDriver_t *pxObj = (SwTSDriver_t*)_this;*/

  SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SwTsDrv: stop driver.\r\n"));

  return xRes;
}

sys_error_code_t SwTSDriver_vtblDoEnterPowerMode(IDriver *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
/*  SwTSDriver_t *pxObj = (SwTSDriver_t*)_this; */

  SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SwTsDrv: not implemented\r\n"));

  return xRes;
}

sys_error_code_t SwTSDriver_vtblReset(IDriver *_this, void *pxParams)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  SwTSDriver_t *pxObj = (SwTSDriver_t*)_this;
  UINT nPosture = TX_INT_ENABLE;

  nPosture = tx_interrupt_control(TX_INT_DISABLE);
  pxObj->m_nStartTick = tx_time_get();
  tx_interrupt_control(nPosture);

  return xRes;
}

uint64_t SwTSDriver_vtblGetTimestamp(ITSDriver_t *_this)
{
  assert_param(_this != NULL);
  SwTSDriver_t *pxObj = (SwTSDriver_t*)_this;
  ULONG nRtosTick;
  UINT nPosture = TX_INT_ENABLE;
  uint64_t nTimestamp;

  /* Read the rtos tick*/
  nRtosTick = tx_time_get();

  /* compute the timestamp in critical section */
  nPosture = tx_interrupt_control(TX_INT_DISABLE);
  nTimestamp = (uint64_t)nRtosTick - pxObj->m_nStartTick;
  tx_interrupt_control(nPosture);

  return nTimestamp;
}


/* Private function definition */
/*******************************/

