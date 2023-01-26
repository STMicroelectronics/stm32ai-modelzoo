/**
 ******************************************************************************
 * @file    SMUtilTask.h
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief   Utility API for the Sensor Manager module.
 *
 * This utility module of the Sensor Manager is in charge of:
 * - Generate the timestamp
 *
 * It uses an hardware timer.
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
#ifndef UTILTASK_H_
#define UTILTASK_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systp.h"
#include "services/syserror.h"
#include "drivers/SMUtilityDriver.h"


/* Public API declaration */
/**************************/

/**
 * The same as SMUtilTaskGetTimeStamp() but without a task object. It implicitly uses the only
 * instance of ::SMUtilTask.
 *
 * @return the system time stamp in tick.
 */
uint32_t SMUtilGetTimeStamp(void);

/**
 * Get the instance of ::SMUtilityDriver.
 *
 * @return a pointer to the application ::SMUtilityDriver
 */
__weak SMUtilityDriver_t *GetSMUtilityDriver(void);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* UTILTASK_H_ */
