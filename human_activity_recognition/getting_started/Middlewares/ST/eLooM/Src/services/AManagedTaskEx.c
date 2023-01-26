/**
 ******************************************************************************
 * @file    AManagedTaskEx.c
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Oct 25, 2018
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

#include "services/AManagedTaskEx.h"
#include "services/AManagedTaskEx_vtbl.h"


/* Public API definition */
/*************************/

void AMTExRun(void *pParams) {
  sys_error_code_t xRes;
  AManagedTaskEx *_this = (AManagedTaskEx*)pParams;
  pExecuteStepFunc_t pExecuteStepFunc = NULL;

  /* At this point all system has been initialized.
     Execute task specific delayed one time initialization. */
  xRes = AMTOnEnterTaskControlLoop((AManagedTask*)_this);
  if (SYS_IS_ERROR_CODE(xRes)) {
    /* stop the system execution */
    sys_error_handler();
  }

  for (;;) {
    if(_this->m_pfPMState2FuncMap == NULL) {
      sys_error_handler();
    }

    /* check if there is a pending power mode switch request */
    if (_this->m_xStatus.nPowerModeSwitchPending == 1U) {
      /* clear the power mode switch delay because the task is ready to switch.*/
      taskENTER_CRITICAL();
      _this->m_xStatus.nDelayPowerModeSwitch = 0;
      taskEXIT_CRITICAL();
      vTaskSuspend(NULL);
    }
    else {
      /* find the execute step function  */
      uint8_t nPMState = (uint8_t)AMTGetTaskPowerMode((AManagedTask*)_this);
      pExecuteStepFunc = _this->m_pfPMState2FuncMap[nPMState];

      if (pExecuteStepFunc != NULL) {
        taskENTER_CRITICAL();
        _this->m_xStatus.nDelayPowerModeSwitch = 1;
        taskEXIT_CRITICAL();
        xRes = pExecuteStepFunc((AManagedTask*)_this);
        taskENTER_CRITICAL();
        _this->m_xStatus.nDelayPowerModeSwitch = 0;
        taskEXIT_CRITICAL();
      }
      else {
        /* there is no function so, we suspend the task.*/
        (void)AMTExSetInactiveState(_this, TRUE);
        vTaskSuspend(_this->m_xThaskHandle);
        (void)AMTExSetInactiveState(_this, FALSE);
      }

      /* notify the system that the task is working fine.*/
      (void)AMTNotifyIsStillRunning((AManagedTask*)_this, xRes);

#if (SYS_TRACE > 1)
      if (res != SYS_NO_ERROR_CODE) {
        sys_check_error_code(xRes);
        sys_error_handler();
      }
#endif

    }
  }
}
