/**
 ******************************************************************************
 * @file    SysTimestamp.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 4.0.0
 * @date    Mar 15, 2022
 *
 * @brief   Timestamp service.
 *
 * The framework timestamp service provides an efficient way to get a common
 * timestamp across the whole application. The service is configured with three
 * parameter in the global sysgonfig.h file:
 *
 * - SYS_TS_CFG_ENABLE_SERVICE: enable (1) or disable (0) the service.
 * - SYS_TS_CFG_TSDRIVER_PARAMS: specifies the low level driver used by the
 *                               service.
 * - SYS_TS_CFG_TSDRIVER_FREQ_HZ: specifies the clock frequency in Hz of the
 *                                hardware timer.
 *
 * When the service is not enabled, it does not increase the memory footprint
 * of eLooM. The timestamp service can use a software driver base on the RTOS
 * tick or a dedicated hardware timer as showed in the class diagram in Fig.1
 *
 * \anchor timestamo_fig1 \image html 26_SysTimestampSrv_class.png "Fig.1 - SysTimestampSRV class diagram"
 *
 * Valid value are for SYS_TS_CFG_TSDRIVER_PARAMS are:
 * - SYS_TS_USE_SW_TSDRIVER to use the RTOS tick (see ::SwTSDriver_t).
 * - The configuration structure for an hardware timer.
 *   It must be compatible with ::SysTimestamp_t type (see ::SwTSDriver_t).
 *
 *   To use the service the application call the SysTsStart() first, then
 *   it can use SysTsGetTimestampF() or SysTsGetTimestampN() to get the current
 *   value of the timestamp in second as a double , or in tick as 64 bit
 *   integer. These functions can be used both in the code of a task and in an
 *   ISR.
 *
 *   This is an example code:
 *   \code{.c}
 *   sys_error_code_t HelloWorldTask_vtblOnEnterTaskControlLoop(AManagedTask *_this)
 *   {
 *     assert_param(_this);
 *     sys_error_code_t xRes = SYS_NO_ERROR_CODE;
 *     HelloWorldTask *pObj = (HelloWorldTask*)_this;
 *
 *     SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("HW: start.\r\n"));
 *
 *     IDrvStart(pObj->m_pxDriver);
 *
 *     SysTsStart(SysGetTimestampSrv(), true);
 *
 *     return xRes;
 *   }
 *
 *
 *   static sys_error_code_t HelloWorldTaskExecuteStepState1(AManagedTask *_this)
 *   {
 *     assert_param(_this != NULL);
 *     sys_error_code_t xRes = SYS_NO_ERROR_CODE;
 *
 *     vTaskDelay(pdMS_TO_TICKS(1000));
 *
 *     double fTimestamp = SysTsGetTimestampF(SysGetTimestampSrv());
 *     SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("Hello STWINCSV1!! ts=%f\r\n", fTimestamp));
 *     __NOP();
 *     __NOP();
 *
 *     return xRes;
 *   }
 *   \endcode
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
#ifndef ELOOM_INC_SERVICES_SYSTIMESTAMP_H_
#define ELOOM_INC_SERVICES_SYSTIMESTAMP_H_

#include "drivers/HwTSDriver.h"
#include "drivers/HwTSDriver_vtbl.h"
#include "drivers/SwTSDriver.h"
#include "drivers/SwTSDriver_vtbl.h"

#ifndef SYS_TS_CFG_ENABLE_SERVICE
#define SYS_TS_CFG_ENABLE_SERVICE    0
#endif

#define SYS_TS_USE_SW_TSDRIVER       NULL

#ifndef SYS_TS_CFG_TSDRIVER_PARAMS
#define SYS_TS_CFG_TSDRIVER_PARAMS   SYS_TS_USE_SW_TSDRIVER
#endif

#if (SYS_TS_CFG_ENABLE_SERVICE == 1) && !defined(SYS_TS_CFG_TSDRIVER_FREQ_HZ)
#error "Please define SYS_TS_CFG_TSDRIVER_FREQ equal to the hardware timer clock frequency in Hz"
#endif

/**
 * Create  type name for ::_SysTimestamp.
 */
typedef struct _SysTimestamp SysTimestamp_t;

/**
 * ::SysTimestamp internal state.
 */
struct _SysTimestamp
{
  /**
   * Driver IF used to control the timer source for the timestamp.
   */
  ITSDriver_t *m_pxDriver;
};


/** Public API declaration */
/***************************/

/**
 * Start the system timestamp service. The service must be started before getting the timestamp value.
 * If the service is not started the value returned by SysTsGetTimestampF() and SysTsGetTimestampN() is undefined.
 * It is possible to reset the timestamp counter to zero by using the bReset parameter.
 *
 * @param _this [IN] specifies a system timestamp object.
 * @param bReset [IN] if `true` the timestamp counter is reset to zero.
 * @return SYS_NO_ERROR_CODE if success, SYS_TS_SERVICE_ISSUE_ERROR_CODE otherwise
 */
sys_error_code_t SysTsStart(SysTimestamp_t *_this, bool bReset);

/**
 * Stop the system timestamp service. When the service is stopped the value of the timestamp counter is frozen.
 *
 * @param _this [IN] specifies a system timestamp object.
 * @return SYS_NO_ERROR_CODE if success, SYS_TS_SERVICE_ISSUE_ERROR_CODE otherwise
 */
sys_error_code_t SysTsStop(SysTimestamp_t *_this);

/**
 * Get the system timestamp in seconds. If the service was not started then the value is undefined.
 * It can be used also form an ISR.
 *
 * @param _this [IN] specifies a system timestamp object.
 * @return the value of the system timestamp in seconds.
 */
double SysTsGetTimestampF(SysTimestamp_t *_this);

/**
 * Get the system timestamp in ??tick??. If the service was not started then the value is undefined.
 * It can be used also form an ISR.
 *
 * @param _this [IN] specifies a system timestamp object.
 * @return the value of the system timestamp in ??tick??.
 */
uint64_t SysTsGetTimestampN(SysTimestamp_t *_this);

/**
 * Get an instance of the system timestamp service.
 *
 * @return an instance of the system timestamp service.
 */
SysTimestamp_t *SysGetTimestampSrv(void);


#endif /* ELOOM_INC_SERVICES_SYSTIMESTAMP_H_ */
