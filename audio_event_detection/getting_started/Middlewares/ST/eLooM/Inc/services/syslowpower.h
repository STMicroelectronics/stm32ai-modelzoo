/**
 ******************************************************************************
 * @file    syslowpower.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Jun 2, 2017
 *
 * @brief This file declares the public API related to the power management.
 *
 * This header file declares the public API and the data structures used by the
 * application tasks in order to:
 * - Inform the system INIT task about the the status of the events that can
 * trigger a power mode change.
 * - Request to switch to a power mode.
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2017 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef SYSLOWPOWER_H_
#define SYSLOWPOWER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/systypes.h"
#include "services/syserror.h"
#include "events/sysevent.h"


#ifndef SYS_CFG_USE_DEFAULT_PM_HELPER
#error Missing definition: SYS_CFG_USE_DEFAULT_PM_HELPER must be defined in sysconfig.h
#endif

#if (SYS_CFG_USE_DEFAULT_PM_HELPER==1)
#include "sysdeflowpower.h"
#else
#include "applowpower.h"
#endif

/**
 * Macro to make system power mode event.
 *
 * @param src [IN] specifies the source of the event
 * @param params [IN] specifies a parameter. Its value depend on the event source.
 */
#define SYS_PM_MAKE_EVENT(src, params)      ((((src) & 0X7U) | (((params)<<3) & 0xF8U)) & 0x000000FF)

/**
 * Check if the current code is inside an ISR or not.
 */
#define SYS_IS_CALLED_FROM_ISR() (((SCB->ICSR) & (SCB_ICSR_VECTACTIVE_Msk)) != 0 ? TRUE : FALSE)

#ifndef SysPostEvent
#define SysPostPowerModeEvent SysPostEvent
#endif


/* Public API declaration */
/**************************/

/**
 * Get a copy of the system status related to the power management.
 *
 * @return copy of the system status related to the power management.
 */
SysPowerStatus SysGetPowerStatus(void);

/**
 * Get the current system power mode.
 *
 * @return the current system power mode.
 */
EPowerMode SysGetPowerMode(void);

/**
 * Notify the system about an event related to the power mode management.
 * This function can be called also from an ISR.
 *
 * @param xEvent [IN] specifies a power mode event.
 * @return SYS_NO_ERROR_CODE if the event has been posted in the system queue with success,
 *         an error code otherwise.
 */
sys_error_code_t SysPostPowerModeEvent(SysEvent xEvent);

/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* SYSLOWPOWER_H_ */
