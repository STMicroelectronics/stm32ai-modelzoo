/**
 ******************************************************************************
 * @file    SysDefPowerModeHelper.c
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Oct 31, 2018
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2018 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#include "services/SysDefPowerModeHelper.h"
#include "services/SysDefPowerModeHelper_vtbl.h"
#include "services/sysinit.h"
#include "services/sysdebug.h"


#if (SYS_CFG_USE_DEFAULT_PM_HELPER==1)

#ifndef SYS_CFG_DEF_PM_HELPER_STANDBY
#defien SYS_CFG_DEF_PM_HELPER_STANDBY   0  ///< if defined to 1 then the MCU goes in STANDBY mode when the system enters in SLEEP_1.
#endif

#define SYS_DEBUGF(level, message)      SYS_DEBUGF3(SYS_DBG_APMH, level, message)


/**
 * Application Power Mode Helper virtual table.
 */
static const IAppPowerModeHelper_vtbl s_xSysDefPowerModeHelper_vtbl = {
    SysDefPowerModeHelper_vtblInit,
    SysDefPowerModeHelper_vtblComputeNewPowerMode,
    SysDefPowerModeHelper_vtblCheckPowerModeTransaction,
    SysDefPowerModeHelper_vtblDidEnterPowerMode,
    SysDefPowerModeHelper_vtblGetActivePowerMode,
    SysDefPowerModeHelper_vtblGetPowerStatus,
    SysDefPowerModeHelper_vtblIsLowPowerMode
};


/* Private member function declaration */
/***************************************/

/* defined in sys_init_mx.c*/
extern void SystemClock_Backup(void);

/* defined in sys_init_mx.c*/
extern void SystemClock_Restore(void);


/* Public API definition */
/*************************/

IAppPowerModeHelper *SysDefPowerModeHelperAlloc() {
  IAppPowerModeHelper *pNewObj = (IAppPowerModeHelper*)SysAlloc(sizeof(SysDefPowerModeHelper));

  if (pNewObj == NULL) {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
  }
  else {
    pNewObj->vptr = &s_xSysDefPowerModeHelper_vtbl;
  }

  return pNewObj;
}


/* Private function definition */
/*******************************/

sys_error_code_t SysDefPowerModeHelper_vtblInit(IAppPowerModeHelper *this) {
  assert_param(this);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  SysDefPowerModeHelper *pObj = (SysDefPowerModeHelper*)this;

  pObj->m_xStatus.m_eActivePowerMode = E_POWER_MODE_STATE1;

  return xRes;
}

EPowerMode SysDefPowerModeHelper_vtblComputeNewPowerMode(IAppPowerModeHelper *this, const SysEvent xEvent) {
  assert_param(this);
  SysDefPowerModeHelper *pObj = (SysDefPowerModeHelper*)this;

  EPowerMode ePowerMode = pObj->m_xStatus.m_eActivePowerMode;

  switch (xEvent.xEvent.nSource) {

  case SYS_PM_EVT_SRC_SW:
    if ((xEvent.xEvent.nParam == SYS_PM_EVT_PARAM_ENTER_LP) && (ePowerMode == E_POWER_MODE_STATE1)) {
      ePowerMode = E_POWER_MODE_SLEEP_1;
    }
    else if ((xEvent.xEvent.nParam == SYS_PM_EVT_PARAM_EXIT_LP) && (ePowerMode == E_POWER_MODE_SLEEP_1)) {
      ePowerMode = E_POWER_MODE_STATE1;
    }
    break;

  default:
    sys_error_handler();
    break;
  }

  return ePowerMode;
}

boolean_t SysDefPowerModeHelper_vtblCheckPowerModeTransaction(IAppPowerModeHelper *this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode) {
  UNUSED(this);
  boolean_t xRes = FALSE;

  switch (eActivePowerMode) {
  case E_POWER_MODE_STATE1:
    if (eNewPowerMode == E_POWER_MODE_SLEEP_1) {
      xRes = TRUE;
    }
    break;
  case E_POWER_MODE_SLEEP_1:
    if (eNewPowerMode == E_POWER_MODE_STATE1) {
      xRes = TRUE;
    }
    break;
  default:
    xRes = FALSE;
  }

  if (xRes == FALSE) {
    sys_error_handler();
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: PM transaction %u -> %u\r\n", (uint8_t)eActivePowerMode, (uint8_t)eNewPowerMode));

  return xRes;
}

#if (SYS_CFG_DEF_PM_HELPER_STANDBY != 1)

//Put the system in STOP1
sys_error_code_t SysDefPowerModeHelper_vtblDidEnterPowerMode(IAppPowerModeHelper *this, EPowerMode ePowerMode) {
  assert_param(this);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  SysDefPowerModeHelper *pObj = (SysDefPowerModeHelper*)this;

  pObj->m_xStatus.m_eActivePowerMode = ePowerMode;

  switch (ePowerMode) {
  case E_POWER_MODE_SLEEP_1:

    /* before put the MCU in STOP check if there are event pending in the system queue*/

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: try SLEEPx:%u\r\n", ePowerMode));

    /* disable the IRQ*/
    __asm volatile ("cpsid i");

    /* reset the WWDG*/
    SysResetAEDCounter();

    if (!SysEventsPending()) {
      /* there are no other message waiting so I can put the MCU in stop
       Enable Power Control clock*/
      __HAL_RCC_PWR_CLK_ENABLE();

      /* Enter Stop Mode
       see bugstabs4 #5265 comment #35*/
      __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
      /*PWR->SCR = SKP_PRWR_SCR_CWUF_1_5;*/

      SystemClock_Backup();
      HAL_PWREx_EnterSTOP1Mode(PWR_STOPENTRY_WFI);

      /* The MCU has exited the STOP mode
       reset the WWDG*/
      SysResetAEDCounter();

      /* Configures system clock after wake-up from STOP*/
      SystemClock_Restore();

      /* generate a software event to go in STATE1.*/
      SysEvent xEvent;
      xEvent.nRawEvent = SYS_PM_MAKE_EVENT(SYS_PM_EVT_SRC_SW, SYS_PM_EVT_PARAM_EXIT_LP);
      SysPostPowerModeEvent(xEvent);
    }

    /* enable the IRQ*/
    __asm volatile ("cpsie i");
    break;

  case E_POWER_MODE_STATE1:

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: RUN\r\n"));
    break;

  default:
    break;
  }

  return xRes;
}

#else

/* Put the system in STANDBY*/

extern void SysPowerConfig();

sys_error_code_t SysDefPowerModeHelper_vtblDidEnterPowerMode(IAppPowerModeHelper *this, EPowerMode ePowerMode) {
  assert_param(this);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  SysDefPowerModeHelper *pObj = (SysDefPowerModeHelper*)this;

  pObj->m_xStatus.m_eActivePowerMode = ePowerMode;

  switch (ePowerMode) {
  case E_POWER_MODE_SLEEP_1:

    /* before put the MCU in STOP check if there are event pending in the system queue*/

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: try SLEEPx:%u\r\n", ePowerMode));

    /* disable the IRQ*/
    __asm volatile ("cpsid i");

    /* reset the WWDG*/
    SysResetAEDCounter();

    if (!SysEventsPending()) {
      /* there are no other message waiting so I can put the MCU in stop
       Enable Power Control clock*/
      __HAL_RCC_PWR_CLK_ENABLE();

      /* Enter Stop Mode*/

      /* Disable all used wakeup sources: WKUP pin*/
      HAL_PWR_DisableWakeUpPin(PWR_WAKEUP_PIN2);

      /* see bugstabs4 #5265 comment #35*/
      __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
      /*PWR->SCR = SKP_PRWR_SCR_CWUF_1_5;*/

      /* Enable wakeup pin WKUP2*/
      HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN2_LOW);

      /* Request to enter STANDBY mode*/
      HAL_PWR_EnterSTANDBYMode();

      /* The MCU has exited the STANDBY mode. Generate a system reset.*/
      HAL_NVIC_SystemReset();
    }

    /* enable the IRQ*/
    __asm volatile ("cpsie i");
    break;

  case E_POWER_MODE_STATE1:

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PMH: RUN\r\n"));
    break;

  default:
    break;
  }

  return xRes;
}
#endif

EPowerMode SysDefPowerModeHelper_vtblGetActivePowerMode(IAppPowerModeHelper *this) {
  assert_param(this);
  SysDefPowerModeHelper *pObj = (SysDefPowerModeHelper*)this;

  return pObj->m_xStatus.m_eActivePowerMode;
}

SysPowerStatus SysDefPowerModeHelper_vtblGetPowerStatus(IAppPowerModeHelper *this) {
  assert_param(this);
  SysDefPowerModeHelper *pObj = (SysDefPowerModeHelper*)this;

  return pObj->m_xStatus;
}

boolean_t SysDefPowerModeHelper_vtblIsLowPowerMode(IAppPowerModeHelper *this, const EPowerMode ePowerMode) {
  UNUSED(this);

  return ePowerMode == E_POWER_MODE_SLEEP_1;
}

#else /* (SYS_CFG_USE_DEFAULT_PM_HELPER==1) */

IAppPowerModeHelper *SysDefPowerModeHelperAlloc(void) {

  return NULL;
}

#endif /* (SYS_CFG_USE_DEFAULT_PM_HELPER==1) */
