/**
 ******************************************************************************
 * @file    SysTimestamp.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 4.0.0
 * @date    Mar 17, 2022
 *
 * @brief  Definition of the eLooM timestamp service.
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#include "services/SysTimestamp.h"
/* MISRA messages linked to ThreadX include are ignored */
/*cstat -MISRAC2012-* */
#include "tx_api.h"
/*cstat +MISRAC2012-* */
#include "services/sysdebug.h"

#if (SYS_TS_CFG_ENABLE_SERVICE == 1)

#define SYS_DEBUGF(level, message)                SYS_DEBUGF3(SYS_DBG_SYSTS, level, message)


/* Private member function declaration */
/***************************************/

/**
 * Initialize the system timestamp service. This function, even if it is not static, is not declared in the header file
 * because it should be used only by the INIT task.
 *
 * @param _this  [IN] specifies a system timestamp object.
 * @param pxDrvCfg [IN] specify the configuration structure of an hardware timer or SYS_TS_USE_SW_TSDRIVER to use the RTOS tick.
 * @return SYS_NO_ERROR_CODE if success, SYS_TS_SERVICE_ISSUE_ERROR_CODE otherwise.
 */
sys_error_code_t SysTsInit(SysTimestamp_t *_this, const void *pxDrvCfg);


/* Public API definition */
/*************************/

sys_error_code_t SysTsInit(SysTimestamp_t *_this, const void *pxDrvCfg) {
  assert_param(_this != NULL);
  sys_error_code_t xRes;

  /* initialize the low level driver.*/
  if (pxDrvCfg != SYS_TS_USE_SW_TSDRIVER) {
    _this->m_pxDriver = (ITSDriver_t*)HwTSDriverAlloc();
    if (_this->m_pxDriver == NULL)
    {
      SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("SysTS: unable to alloc driver object.\r\n"));
      xRes = SYS_GET_LAST_LOW_LEVEL_ERROR_CODE();
    }
    else {
      HwTSDriverParams_t xParams = {
          .pxTimParams = (SYS_TIMParams_t*)pxDrvCfg
      };
      xRes = IDrvInit((IDriver*)_this->m_pxDriver, &xParams);
      if (SYS_IS_ERROR_CODE(xRes)) {
        SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("SysTS: error during driver initialization.\r\n"));
      }
    }
  }
  else {
    _this->m_pxDriver = (ITSDriver_t*)SwTSDriverAlloc();
    if (_this->m_pxDriver == NULL)
    {
      SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("SysTS: unable to alloc driver object.\r\n"));
      xRes = SYS_GET_LAST_LOW_LEVEL_ERROR_CODE();
    }
    else {
      xRes = IDrvInit((IDriver*)_this->m_pxDriver, NULL);
      if (SYS_IS_ERROR_CODE(xRes)) {
        SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("SysTS: error during driver initialization.\r\n"));
      }
    }
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("SysTS: System timestamp service ready.\r\n"));

  return xRes;
}

sys_error_code_t SysTsStart(SysTimestamp_t *_this, bool bReset) {
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  if (bReset) {
    xRes = IDrvReset((IDriver*)_this->m_pxDriver, NULL);
  }

  if (!SYS_IS_ERROR_CODE(xRes)) {
    xRes = IDrvStart((IDriver*)_this->m_pxDriver);

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("SysTS: System timestamp service started.\r\n"));
  }
  else {
    __NOP();
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SysTS: System timestamp error during driver reset.\r\n"));
  }

  return xRes;
}

sys_error_code_t SysTsStop(SysTimestamp_t *_this) {
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  xRes = IDrvStop((IDriver*)_this->m_pxDriver);

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("SysTS: System timestamp service stopped.\r\n"));

  return xRes;
}

double SysTsGetTimestampF(SysTimestamp_t *_this) {
  assert_param(_this != NULL);

  uint64_t nTimeStampTick = ITSDrvGetTimeStamp(_this->m_pxDriver);
  double fTimestamp = (double)nTimeStampTick / (double)(SYS_TS_CFG_TSDRIVER_FREQ_HZ);

  return fTimestamp;
}

uint64_t SysTsGetTimestampN(SysTimestamp_t *_this) {
  assert_param(_this != NULL);

  uint64_t nTimeStampTick = ITSDrvGetTimeStamp(_this->m_pxDriver);

  return nTimeStampTick;
}

#endif // (SYS_TS_CFG_ENABLE_SERVICE == 1)
