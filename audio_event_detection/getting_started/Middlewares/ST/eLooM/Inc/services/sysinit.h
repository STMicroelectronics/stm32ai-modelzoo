/**
 ******************************************************************************
 * @file    sysinit.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Sep 6, 2016
 *
 * @brief   System global initialization.
 *
 * This file declare the SysInit() API function that initializes the minimum set
 * of resources, hardware and software, in order to start the scheduler.
 * It creates the INIT task, that is the first task running in the minimum
 * initialized environment, and it is responsible for the application startup.
 * INIT implements the sequence diagram displayed in Fig.2
 * \image html 2_system_init_diagram.png "Fig.2 - System initialization diagram"
 * For each managed task ...
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

#ifndef SYSINIT_H_
#define SYSINIT_H_

#include "ApplicationContext.h"
#include "IApplicationErrorDelegate.h"
#include "IApplicationErrorDelegateVtbl.h"
#include "IAppPowerModeHelper.h"
#include "IAppPowerModeHelper_vtbl.h"
#include "IBoot.h"
#include "IBootVtbl.h"

#ifdef __cplusplus
 extern "C" {
#endif

#ifndef INIT_TASK_CFG_ENABLE_BOOT_IF
#define INIT_TASK_CFG_ENABLE_BOOT_IF           0
#endif

#if (INIT_TASK_CFG_ENABLE_BOOT_IF == 0)
#define INIT_TASK_CGF_BOOT_PARAM               false
#else
#define INIT_TASK_CGF_BOOT_PARAM               true
#endif

#define ELOOM_MAGIC_NUMBER  (12974U)

#define SYS_MS_TO_TICKS( xTimeInMs ) ( (uint32_t) (((uint32_t )(xTimeInMs) * (uint32_t)TX_TIMER_TICKS_PER_SECOND) / (uint32_t)1000))

/**
 * It initialize the minimum set of resources, hardware and software, in order to start the scheduler,
 * and create the INIT task.
 * If bEnableBootIF == TRUE the system enable the Boot Interface. It is useful to develop a bootloader.
 *
 * @param bEnableBootIF specifies if the system has to enable the Boot Interface.
 * @return SYS_NO_ERROR_CODE if success, SYS_OUT_OF_MEMORY_ERROR_CODE if it is not possible to instantiate the INIT task.
 */
sys_error_code_t SysInit(boolean_t bEnableBootIF);

/**
  * Pre Sleep Processing. Called by the kernel before it places the MCU into a sleep mode because
  * configPRE_SLEEP_PROCESSING() is defined to SysPreSleepProcessing().
  *
  * @param  ulExpectedIdleTime: [OUT] Expected time in idle state. It is set to 0 to indicate that
  * SysPreSleepProcessing contains its own wait for interrupt or wait for event instruction and so
  * the kernel vPortSuppressTicksAndSleep function does not need to execute the wfi instruction.
  */
void SysPreSleepProcessing(uint32_t * ulExpectedIdleTime);

/**
  * Post Sleep Processing. Called by the kernel when the MCU exits a sleep mode because
  * configPOST_SLEEP_PROCESSING is defined to SysPostSleepProcessing().
  *
  * @param  ulExpectedIdleTime: Not used
  */
void SysPostSleepProcessing(uint32_t * ulExpectedIdleTime);

/**
 * This function is used by the system in order to add all the managed tasks to the application context.
 * It is defined as weak in order to allow the user application to redefine it.
 *
 * @param pAppContext [IN] specifies a pointer to the application context to load with the application specific managed tasks.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t SysLoadApplicationContext(ApplicationContext *pAppContext);

/**
 * This function is called by the framework at the end of the initialization process and before the Init task
 * releases the control to the application tasks. At this point all managed task has been created and the hardware
 * is initialized. The application has a chance to execute some other initialization code before
 * the scheduler runs the first application task.
 *
 * @param pAppContext [IN] specifies a pointer to the application context to load with the application specific managed tasks.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t SysOnStartApplication(ApplicationContext *pAppContext);

/**
 * Not used yet.
 *
 * @param pxTask
 * @return
 */
sys_error_code_t SysTaskErrorHandler(AManagedTask *pxTask);

/**
 * Check if there are pending ::SysEvent.
 *
 * @return `TRUE` if there are SysEvent pending (that means to be served by the INIT task), `FALSE` otherwise.
 */
boolean_t SysEventsPending(void);

/**
 * Get the Application manager error delegate. This function is used by the system during the application startup
 * in order to get an application specific object that implements the ::IApplicationErrorDelegate. The default
 * implementation is defined as \a weak so the application can provide its specific implementation.
 * The default implementation does nothing.
 *
 * @return a pointer to an IApplicationErrorDelegate object.
 */
IApplicationErrorDelegate *SysGetErrorDelegate(void);

/**
 * Get the Application defined Boot interface. A boot loader application should implement this interface.
 * The default implementation is defined as \a weak so the application can provide its specific implementation.
 * The default implementation does nothing.
 *
 * @return a pointer to an IBoot object.
 */
IBoot *SysGetBootIF(void);

/**
 * Get the Application Power Mode Helper.  This function is used by the system during the application startup
 * in order to get an application specific object that implements the ::IAppPowerModeHelper. The default
 * implementation is defined as \a weak so the application can provide its specific implementation.
 * For more information about the default implementation see TODO: STF ...
 *
 * @return a pointer to an IAppPowerModeHelper object.
 */
IAppPowerModeHelper *SysGetPowerModeHelper(void);


#ifdef __cplusplus
}
#endif


#endif /* SYSINIT_H_ */
