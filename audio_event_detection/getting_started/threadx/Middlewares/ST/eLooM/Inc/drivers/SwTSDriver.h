/**
 ******************************************************************************
 * @file    SwTSDriver.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 4.0.0
 * @date    Mar 21, 2022
 *
 * @brief  Software driver for the timestamp service.
 *
 * This driver reuses the RTOS tick, so the configuration parameter
 * SYS_TS_CFG_TSDRIVER_FREQ_HZ must be set to onfigTICK_RATE_HZ for the
 * FreeRTOS version of eLooM, and the SYS_TS_CFG_TSDRIVER_PARAMS parameter
 * must be set to SYS_TS_USE_SW_TSDRIVER.
 *
 * This driver has the advantage to do not use any dedicated hardware resource,
 * but on the other side its resolution is limited to the by the RTOS tick.
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
#ifndef ELOOM_INC_DRIVERS_SWTSDRIVER_H_
#define ELOOM_INC_DRIVERS_SWTSDRIVER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "drivers/ITSDriver.h"
#include "drivers/ITSDriver_vtbl.h"
/* MISRA messages linked to ThreadX include are ignored */
/*cstat -MISRAC2012-* */
#include "tx_api.h"
  /*cstat +MISRAC2012-* */

/**
 * Create  type name for _HwTSDriver_t.
 */
typedef struct _SwTSDriverParams_t SwTSDriverParams_t;

/**
 * Create  type name for _SwTSDriver_t.
 */
typedef struct _SwTSDriver_t SwTSDriver_t;

/**
 *  SwTSDriver_t internal structure.
 */
struct _SwTSDriver_t
{
  /**
   * Base class object.
   */
  ITSDriver_t super;

  /* Driver variables should be added here. */

  /**
   * RTOS tick counter when the timestamp service is started.
   */
  ULONG m_nStartTick;
};

/** Public API declaration */
/***************************/

/**
 * Allocate an instance of SwTSDriver_t. The driver is allocated
 * in the FreeRTOS heap.
 *
 * @return a pointer to the generic interface ::IDriver if success,
 * or SYS_OUT_OF_MEMORY_ERROR_CODE otherwise.
 */
IDriver *SwTSDriverAlloc(void);


/** Inline functions definition */
/********************************/


#ifdef __cplusplus
}
#endif

#endif /* ELOOM_INC_DRIVERS_SWTSDRIVER_H_ */
