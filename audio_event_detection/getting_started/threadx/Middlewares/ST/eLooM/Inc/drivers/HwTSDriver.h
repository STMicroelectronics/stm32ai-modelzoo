/**
 ******************************************************************************
 * @file    HwTSDriver.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 4.0.0
 * @date    Mar 15, 2022
 *
 * @brief   Driver for the timestamp service that use an hardware timer.
 *
 * This driver uses an hardware timer to generate the tick for the timestamp
 * service. To use this driver the configuration parameter
 * SYS_TS_CFG_TSDRIVER_FREQ_HZ must be set to the address of a timer
 * configuration structure compatible with ::SYS_TIMParams_t, and the
 * SYS_TS_CFG_TSDRIVER_PARAMS parameter must be set to the clock frequency in
 * Hz of the hardware timer.
 *
 * This driver needs a dedicated hardware resource,
 * but on the other side its resolution is not limited by the RTOS tick.
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
#ifndef ELOOM_INC_DRIVERS_HWTSDRIVER_H_
#define ELOOM_INC_DRIVERS_HWTSDRIVER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "drivers/ITSDriver.h"
#include "drivers/ITSDriver_vtbl.h"


/**
 * Create  type name for _HwTSDriver_t.
 */
typedef struct _HwTSDriverParams_t HwTSDriverParams_t;

/**
 * Create  type name for _HwTSDriver_t.
 */
typedef struct _HwTSDriver_t HwTSDriver_t;

/**
 * HW Timer configuration parameters.
 */
typedef struct _SYS_TIMParams_t
{
  TIM_HandleTypeDef *pxTim; /*!< HAL TIM handle */
  IRQn_Type nIrq; /*!< External interrupt number. */
  void (*pMxInitF)(void); /*!< MX TIM initialization function */
} SYS_TIMParams_t;

/**
 * Initialization parameters for the driver.
 */
struct _HwTSDriverParams_t
{
  SYS_TIMParams_t *pxTimParams;
};

/**
 *  HwTSDriver_t internal structure.
 */
struct _HwTSDriver_t
{
  /**
   * Base class object.
   */
  ITSDriver_t super;

  /* Driver variables should be added here. */

  /**
   * Specifies the handle of the HW TIM used by the driver.
   */
  HwTSDriverParams_t m_xHwHandle;
};

/** Public API declaration */
/***************************/

/**
 * Allocate an instance of HwTSDriver_t. The driver is allocated
 * in the FreeRTOS heap.
 *
 * @return a pointer to the generic interface ::IDriver if success,
 * or SYS_OUT_OF_MEMORY_ERROR_CODE otherwise.
 */
IDriver *HwTSDriverAlloc(void);


/** Inline functions definition */
/********************************/


#ifdef __cplusplus
}
#endif

#endif /* ELOOM_INC_DRIVERS_HWTSDRIVER_H_ */
