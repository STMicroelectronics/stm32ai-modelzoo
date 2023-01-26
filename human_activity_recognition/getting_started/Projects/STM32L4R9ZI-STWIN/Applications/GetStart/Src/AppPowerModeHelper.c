/**
 ******************************************************************************
 * @file    AppPowerModeHelper.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
 *
 * @brief   Define the Power Mode State Machine for this application.
 *
 * Implement the interface ::IAppPowerModeHelper.
 *
 *********************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *********************************************************************************
 */

#include "AppPowerModeHelper.h"
#include "AppPowerModeHelper_vtbl.h"
#include "FreeRTOS.h"
#include "services/sysinit.h"
#include "services/sysdebug.h"


#define SYS_DEBUGF(level, message)      SYS_DEBUGF3(SYS_DBG_APMH, level, message)


/**
 * Application Power Mode Helper virtual table.
 */
static const IAppPowerModeHelper_vtbl s_xAppPowerModeHelper_vtbl = {
    AppPowerModeHelper_vtblInit,
    AppPowerModeHelper_vtblComputeNewPowerMode,
    AppPowerModeHelper_vtblCheckPowerModeTransaction,
    AppPowerModeHelper_vtblDidEnterPowerMode,
    AppPowerModeHelper_vtblGetActivePowerMode,
    AppPowerModeHelper_vtblGetPowerStatus,
    AppPowerModeHelper_vtblIsLowPowerMode
};

/**
 * Internal state of the Application Power Mode Helper.
 */
struct _AppPowerModeHelper
{

  /**
   * Base class object.
   */
  IAppPowerModeHelper *super;

  /**
   * Specifies the system power mode status.
   */
  SysPowerStatus status;

  /**
   * Used to buffer the the previous RUN state during the transaction from RUN_x to SLEEP_x.
   * The buffered state is use to compute the correct transaction from SLEEP_x to RUN_x.
   */
  EPowerMode previous_run_state;
};

/* Private member function declaration */
/***************************************/

extern void SystemClock_Backup(void);

extern void SystemClock_Restore(void);

/* Public API definition */
/*************************/

IAppPowerModeHelper *AppPowerModeHelperAlloc(void)
{
  IAppPowerModeHelper *p_new_obj = (IAppPowerModeHelper*)pvPortMalloc(sizeof(AppPowerModeHelper));

  if (p_new_obj == NULL)
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
  }
  else
  {
    p_new_obj->vptr = &s_xAppPowerModeHelper_vtbl;
  }

  return p_new_obj;
}


/* Virtual functions definition */
/********************************/

sys_error_code_t AppPowerModeHelper_vtblInit(IAppPowerModeHelper *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppPowerModeHelper *p_obj = (AppPowerModeHelper*)_this;

  p_obj->status.active_power_mode = E_POWER_MODE_STATE1;
  p_obj->previous_run_state = E_POWER_MODE_STATE1;

  return res;
}

EPowerMode AppPowerModeHelper_vtblComputeNewPowerMode(IAppPowerModeHelper *_this, const SysEvent event)
{
  assert_param(_this != NULL);
  AppPowerModeHelper *p_obj = (AppPowerModeHelper*)_this;

  EPowerMode power_mode = p_obj->status.active_power_mode;

  switch (event.xEvent.nSource)
  {
  case SYS_PM_EVT_SRC_CTRL:
    if (power_mode == E_POWER_MODE_STATE1)
    {
      if (event.xEvent.nParam == SYS_PM_EVENT_PARAM_START_ML)
      {
        power_mode = E_POWER_MODE_X_CUBE_AI_ACTIVE;
      }
    }
    else if ((power_mode == E_POWER_MODE_X_CUBE_AI_ACTIVE))
    {
      if (event.xEvent.nParam == SYS_PM_EVENT_PARAM_STOP_PROCESSING)
      {
        power_mode = E_POWER_MODE_STATE1;
      }
    }
    break;

  case SYS_PM_EVT_SRC_LP_TIMER:
    if (power_mode == E_POWER_MODE_STATE1)
    {
      power_mode = E_POWER_MODE_SLEEP_1;
    }
    break;

  default:

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: wrong SysEvent.\r\n"));

    sys_error_handler();
    break;
  }

#ifdef SYS_DEBUG
  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: new PM:%u-%u.\r\n", p_obj->status.active_power_mode, power_mode));
#endif

  return power_mode;
}

boolean_t AppPowerModeHelper_vtblCheckPowerModeTransaction(IAppPowerModeHelper *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode) {
  UNUSED(_this);
  boolean_t res = FALSE;

  switch (active_power_mode) {
  case E_POWER_MODE_STATE1:
    if (new_power_mode == E_POWER_MODE_X_CUBE_AI_ACTIVE) {
      res = TRUE;
    }
    break;
  case E_POWER_MODE_X_CUBE_AI_ACTIVE:
    if (new_power_mode == E_POWER_MODE_STATE1) {
      res = TRUE;
    }
    break;
  case E_POWER_MODE_SLEEP_1:
    if (new_power_mode == E_POWER_MODE_STATE1) {
      res = TRUE;
    }
    break;
  default:
    res = FALSE;
  }

  if (res == FALSE) {

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: ERR PM transaction %u -> %u\r\n", (uint8_t)active_power_mode, (uint8_t)new_power_mode));

    sys_error_handler();
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: PM transaction %u -> %u\r\n", (uint8_t)active_power_mode, (uint8_t)new_power_mode));

  return res;
}

sys_error_code_t AppPowerModeHelper_vtblDidEnterPowerMode(IAppPowerModeHelper *_this, EPowerMode power_mode) {
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppPowerModeHelper *p_obj = (AppPowerModeHelper*)_this;

  p_obj->status.active_power_mode = power_mode;

  switch (power_mode) {
  case E_POWER_MODE_SLEEP_1:

    /* before put the MCU in STOP check if there are event pending in the system queue*/

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: try SLEEP_1\r\n"));

    /* disable the IRQ*/
    __asm volatile ("cpsid i");

    /* reset the WWDG*/
    SysResetAEDCounter();

    if (!SysEventsPending()) {
      HAL_SuspendTick();
      /* there are no other message waiting so I can put the MCU in stop
       Enable Power Control clock*/
      __HAL_RCC_PWR_CLK_ENABLE();

      /* Enter Stop Mode*/

      /* Disable all used wakeup sources: WKUP pin*/
      HAL_PWR_DisableWakeUpPin(PWR_WAKEUP_PIN2);

      __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);

      SystemClock_Backup();
      HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);

      /* The MCU has exited the STOP mode
       reset the WWDG*/
      SysResetAEDCounter();

      /* Configures system clock after wake-up from STOP*/
      SystemClock_Restore();
      HAL_ResumeTick();
    }

    /* enable the IRQ*/
    __asm volatile ("cpsie i");
    break;

  case E_POWER_MODE_STATE1:

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: STATE1\r\n"));

#if defined(DEBUG) || defined(SYS_DEBUG)
    {
      size_t nFreeHeapSize = xPortGetFreeHeapSize();
      SYS_DEBUGF(SYS_DBG_LEVEL_SL, ("PMH: free heap = %i.\r\n", nFreeHeapSize));
    }
#endif
    break;

  case E_POWER_MODE_X_CUBE_AI_ACTIVE:

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: X_CUBE_AI_ACTIVE\r\n"));

#if defined(DEBUG) || defined(SYS_DEBUG)
    {
      size_t nFreeHeapSize = xPortGetFreeHeapSize();
      SYS_DEBUGF(SYS_DBG_LEVEL_SL, ("PMH: free heap = %i.\r\n", nFreeHeapSize));
    }
#endif
    break;

  default:
    sys_error_handler();
    break;
  }

  return res;
}

EPowerMode AppPowerModeHelper_vtblGetActivePowerMode(IAppPowerModeHelper *_this) {
  assert_param(_this);
  AppPowerModeHelper *p_obj = (AppPowerModeHelper*)_this;

  return p_obj->status.active_power_mode;
}

SysPowerStatus AppPowerModeHelper_vtblGetPowerStatus(IAppPowerModeHelper *_this) {
  assert_param(_this);
  AppPowerModeHelper *p_obj = (AppPowerModeHelper*)_this;

  return p_obj->status;
}

boolean_t AppPowerModeHelper_vtblIsLowPowerMode(IAppPowerModeHelper *_this, const EPowerMode power_mode) {
  UNUSED(_this);

  return power_mode == E_POWER_MODE_SLEEP_1 ? TRUE : FALSE;
}
