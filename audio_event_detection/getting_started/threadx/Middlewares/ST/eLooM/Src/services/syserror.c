/**
 ******************************************************************************
 * @file    syserror.c
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Sep 5, 2016
 * @brief   Implement the global error management API
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2016 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#include "services/systp.h"
#include "services/syserror.h"


sys_error_t g_nSysError = {0};

#define COUNTOF(A)        (sizeof(A)/sizeof(*A))

#define FREERTOS_CONFIG_ASSERT_MUST_BLOCK

#ifndef SYS_IS_CALLED_FROM_ISR
#define SYS_IS_CALLED_FROM_ISR() ((SCB->ICSR & SCB_ICSR_VECTACTIVE_Msk) != 0 ? TRUE : FALSE)
#endif


void sys_error_handler(void)
{
#if defined(DEBUG)
	__asm volatile ("bkpt 0");
#else
  __disable_irq();
	while(1) {
      __asm volatile( "NOP" );
	}
#endif
}

#if (SYS_TRACE > 1)
void sys_check_error_code(sys_error_code_t xError) {
	// first check if it is a general error code
	switch (xError) {
	  default:
	    break;
	}
}
#endif
