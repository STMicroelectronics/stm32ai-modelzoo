/**
 ******************************************************************************
 * @file    syscs.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 3.0.4
 * @date    May 27, 2022
 *
 * @brief   System critical section
 *
 * This header export a ROTS independent macro to enter and exit a critical
 * section:
 * - SYS_DECLARE_CS(cs)
 * - SYS_ENTER_CRTITICA(cs)
 * - SYS_EXIT_CRTITICA(cs)
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
#ifndef ELOOM_INC_SERVICES_SYSCS_H_
#define ELOOM_INC_SERVICES_SYSCS_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "systp.h"

/*  SYS_DECLARE_CS(cs) */
/*  SYS_ENTER_CRTITICAL(cs) */
/*  SYS_EXIT_CRTITICAL(cs)  */

#if defined(SYS_TP_RTOS_FREERTOS)
#include "syscs_freertos.h"
#elif defined(SYS_TP_RTOS_THREADX)
#include "syscs_threadx.h"
#endif

/* Public API declaration */
/**************************/



/* Inline functions definition */
/*******************************/



#ifdef __cplusplus
}
#endif

#endif /* ELOOM_INC_SERVICES_SYSCS_H_ */
