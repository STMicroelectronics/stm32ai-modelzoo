/**
 ******************************************************************************
 * @file    AManagedTask.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Jan 13, 2017
 * @brief   This file declare the Managed task Interface.
 *
 * TODO - STF - what is a managed task?
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

#ifndef INCLUDE_SERVICES_AMANAGEDTASK_H_
#define INCLUDE_SERVICES_AMANAGEDTASK_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "syslowpower.h"
/* MISRA messages linked to FreeRTOS include are ignored */
/*cstat -MISRAC2012-* */
#include "tx_api.h"
/*cstat -MISRAC2012-* */

/**
 * Specifies the maximum number of errors that can be tracked by a managed task.
 */
#define MT_MAX_ERROR_COUNT       0x3U

#ifndef MT_ALLOWED_ERROR_COUNT
/**
 * Specifies the maximum number of error a task can report before resetting the nIsTaskStillRunning flag.
 * If the AEM (::AppErrorManager) is used it will in turn trigger a system reset due to the WWDG.
 */
#define MT_ALLOWED_ERROR_COUNT   0x2U
#endif

#define AMT_MS_TO_TICKS( xTimeInMs ) ( (uint32_t) (((uint32_t )(xTimeInMs) * (uint32_t)TX_TIMER_TICKS_PER_SECOND) / (uint32_t)1000))


/**
 * Create  type name for _AManagedTask.
 */
typedef struct _AManagedTask AManagedTask;

/**
 * Create a type name for the step execution function.
 */
typedef sys_error_code_t (ExecuteStepFunc_t)(AManagedTask *_this);

/**
 * Create a type name for a pointer to a step execution function.
 */
typedef sys_error_code_t (*pExecuteStepFunc_t)(AManagedTask *_this);


/* Public API declaration */
/**************************/

/**
 * Task specific function called by the framework to initialize
 * task related hardware resources. This function is called by the INIT task.
 *
 * @param this [IN] specifies a task object pointer.
 * @param pParams [IN] specifies a pointer to task specific hardware initialization parameters.
 * @return \a SYS_NO_ERROR_CODE if success, one of the following error codes otherwise:
 *         - SYS_OUT_OF_MEMORY_ERROR_CODE if is not possible to instantiate the driver object.
 *         - Other task specific error code
 */
static inline sys_error_code_t AMTHardwareInit(AManagedTask *_this, void *pParams);

/**
 * Task specific function called by the framework before the task is created.
 * An application should use this function in order to perform task specific software initialization
 * and pass task specific parameters to the INIT task.
 *
 * @param _this [IN] specifies a task object pointer.
 * @param pvTaskCode [OUT] used by the application to specify the task main function.
 * @param pcName [OUT] used by the application to specify a descriptive name for the task.
 * @param pvStackStart [OUT] used by the application to specify the start address of the stack. If it is NULL, the the stack is allocated in the system main memory pool.
 * @param pnStackSize [OUT] used by the application to specify the task stack size.
 * @param pnPriority [OUT] used by the application to specify the task priority. Legal values range from 0 through (TX_MAX_PRIORITIES-1), where a value of 0 represents the highest priority.
 * @param pnPreemptThreshold [OUT] used by the application to specify the task preemptive threshold.
 *        Highest priority level (0 through (TX_MAX_PRIORITIES-1)) of disabled preemption. Only priorities higher than this
 *        level are allowed to preempt this thread. This value must be less than or equal to the specified priority.
 *        A value equal to the thread priority disables preemption-threshold.
 * @param pnTimeSlice [OUT] Number of timer-ticks this thread is allowed to run before other ready threads of the same
 *        priority are given a chance to run. Note that using preemption-threshold disables time-slicing.
 *        Legal time-slice values range from 1 to 0xFFFFFFFF (inclusive).
 *        A value of TX_NO_TIME_SLICE (a value of 0) disables time-slicing of this thread.
 * @param pnAutoStart [OUT] Specifies whether the thread starts immediately or is placed in a suspended state.
 *        Legal options are TX_AUTO_START (0x01) and TX_DONT_START (0x00). If TX_DONT_START is specified,
 *        the application must later call tx_thread_resume in order for the thread to run.
 * @param npParams [OUT] A 32-bit value that is passed to the thread's entry function when it first executes. The use for this input is determined exclusively by the application.
 * @return \a SYS_NO_ERROR_CODE if success, a task specific error code otherwise. If the function
 * fails the task creation process is stopped.
 */
static inline sys_error_code_t AMTOnCreateTask(AManagedTask *_this, tx_entry_function_t *pvTaskCode, CHAR **pcName,
    VOID **pvStackStart, ULONG *pnStackSize,
    UINT *pnPriority, UINT *pnPreemptThreshold,
    ULONG *pnTimeSlice, ULONG *pnAutoStart,
    ULONG *pnParams);

/**
 * Task specific function called by the framework when the system is entering a specific power mode, in order to
 * implement the transaction in the power mode state machine.
 * This function is executed in the INIT task execution flow.
 * A managed task should modify its internal state to be ready to execute steps in the new power mode.
 * The implementation of the managed task control loop, provided with the framework template, suspend the task
 * after this function is called. The INIT task is in charge to resume the task when all the tasks are ready
 * and the new power mode become actual.
 *
 * @param _this [IN] specifies a task object pointer.
 * @param eActivePowerMode [IN] specifies the current power mode of the system.
 * @param eNewPowerMode [IN] specifies the new power mode that is to be activated by the system.
 * @return \a SYS_NO_ERROR_CODE if success, a task specific error code otherwise.
 */
static inline sys_error_code_t AMTDoEnterPowerMode(AManagedTask *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);

/**
 * Called by the framework to handle a system wide error. This function is executed in the INIT task execution flow.
 *
 * @param _this [IN] specifies a task object pointer.
 * @param xError [IN] specifies a system error
 * @return \a SYS_NO_ERROR_CODE if success, a task specific error code otherwise.
 */
static inline sys_error_code_t AMTHandleError(AManagedTask *_this, SysEvent xError);

/**
 * Called by the framework before the task enters the main control loop. At this moment the system
 * is up and running, a managed task can do some delayed initialization, if needed.
 * This function is executed in the INIT task execution flow.
 *
 * @param _this [IN] specifies a task object.
 * @return \a SYS_NO_ERROR_CODE if success, a task specific error code otherwise.
 */
static inline sys_error_code_t AMTOnEnterTaskControlLoop(AManagedTask *_this);

/**
 * Initialize a managed task structure. The application is responsible to allocate
 * a managed task in memory. This method must be called after the allocation.
 *
 * @param _this [IN] specifies a task object pointer.
 * @return \a SYS_NO_ERROR_CODE
 */
static inline sys_error_code_t AMTInit(AManagedTask *_this);

/**
 * Utility function to retrieve the current power mode of the system.
 *
 * @return the current power mode of the system
 */
static inline EPowerMode AMTGetSystemPowerMode(void);

/**
 * Utility function to retrieve the current power mode of the managed task.
 *
 *@param _this [IN] specifies a task object pointer.
 * @return the current power mode of the system remapped according to the task
 *         (PMState, PMState) PM map.
 */
static inline EPowerMode AMTGetTaskPowerMode(AManagedTask *_this);

/**
 * Notify the system that the task is still running. If an application error manage delegate is installed (_IApplicationErrorDelegate),
 * then a managed task must notify the system that it is working fine in order to prevent a system reset.
 *
 * @param _this [IN] specifies a task object pointer.
 * @param nStepError [IN] specifies an error code. Usually it is the error code reported during the task step execution.
 * @return \a SYS_NO_ERROR_CODE if success, a task specific error code otherwise.
 */
static inline sys_error_code_t AMTNotifyIsStillRunning(AManagedTask *_this, sys_error_code_t nStepError);

/**
 * A managed task can handle an error during the step execution by itself. Another option is to let
 * the error navigate up to the main control loop of the task where it will be reported to the system
 * using the AMTNotifyIsStillRunning() function.
 * But if an error occurs and the managed task want to ignore the error and proceed with the step execution,
 * it should notify the system using this function before the error is overwritten. For example:
 *
 *     xRes = HCPExeuteCommand(&_this->m_xProtocol, xReport.outputReport11.nCommandID, NULL, _this->m_pxDriver);
 *     if (SYS_IS_ERROR_CODE(xRes)) {
 *       AMTReportErrOnStepExecution(_this, xRes);
 *     }
 *     // continue with the step execution.
 *
 * In this why the error is logged and the AED count the error when it check if the task is still running properly.
 *
 * @param _this [IN] specifies a task object pointer.
 * @param nStepError [IN] specifies an error code.
 */
static inline void AMTReportErrOnStepExecution(AManagedTask *_this, sys_error_code_t nStepError);

/**
 * This function is a convenient method to call the call the system function SysResetAEDCounter() from a task code.
 *
 * @param _this [IN] specifies a task object pointer.
 */
static inline void AMTResetAEDCounter(AManagedTask *_this);

/**
 * Check if the INIT task has requested a power mode switch.
 *
 * @param _this [IN] specifies a task object pointer.
 * @return `TRUE` if there is power mode switch pending request, `FALSE` otherwise.
 */
static inline boolean_t AMTIsPowerModeSwitchPending(AManagedTask *_this);

/**
 * Set the PM state remapping function for a managed task object. It is used by the application to re-map the behavior of an ::AManagedTask
 * during a power mode switch. Image a developer that want to use an existing managed task (MyManagedTask1) in a new application. Probably
 * the new application has a different PM (PM_SM_2) state machine than the one used to design and implement the managed task
 * MyManagedTask1 (PM_SM_1). In this scenario it is possible to reuse the managed task as it is if exist a subjective function
 * f(x) -> (PM_SM_2, PM_SM_1), that map all states of PM_SM_1 in one or more states of PM_SM_2.
 * It is possible to set this member to NULL, and, in this case no remapping is done.
 *
 * @param _this  [IN] specifies a task object pointer.
 * @param pPMState2PMStateMap specifies a map (PMState, PMState). The map must be implemented with an array.
 *        The number of elements of the array must be equal to the number of states of the PM state machine.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t AMTSetPMStateRemapFunc(AManagedTask *_this, const EPowerMode *pPMState2PMStateMap);

/**
 * This is the default control loop of a managed task.
 * @param pParams [IN] specify a pointer to the task object:
 * AManagedTask *pTask = (AManagedTask*)pParams;
 */
VOID AMTRun(ULONG pParams);


#ifdef __cplusplus
}
#endif


#endif /* INCLUDE_SERVICES_AMANAGEDTASK_H_ */
