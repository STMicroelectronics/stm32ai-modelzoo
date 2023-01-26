/**
 ******************************************************************************
 * @file    SMUtilTask.c
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief   Implementation of the SMUTIL task of the Sensor Manager module.
 *
 * This file define the SMUtilTask class.
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

#include "SMUtilTask.h"
#include "services/sysdebug.h"


#define SYS_DEBUGF(level, message)             SYS_DEBUGF3(SYS_DBG_SMUTIL, level, message)


/* Private member function declaration */
/***************************************/


/* Inline function forward declaration */
/***************************************/

#if defined (__GNUC__)
/* Inline function defined inline in the header file UtilTask.h must be declared here as extern function. */
#endif


/* Public API definition */
/*************************/


uint32_t SMUtilGetTimeStamp(void)
{
  uint32_t timestamp = 0;
  SMUtilityDriver_t *p_drv = GetSMUtilityDriver();
  if (p_drv != NULL)
  {
    timestamp = SMUtilityDrvGetTimeStamp(p_drv);
  }

  return timestamp;
}

__weak SMUtilityDriver_t *GetSMUtilityDriver(void)
{
  return NULL;
}


/* Private function definition */
/*******************************/

