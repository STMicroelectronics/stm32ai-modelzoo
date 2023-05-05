/**
 ******************************************************************************
 * @file    AManagedTaskEx.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Jul 30, 2018
 *
 * @brief   This file declare the Managed task Interface.
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2018 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef INCLUDE_SERVICES_AMANAGEDTASKEX_H_
#define INCLUDE_SERVICES_AMANAGEDTASKEX_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "AManagedTask.h"


/**
 * Create  type name for _AManagedTaskEx.
 */
typedef struct _AManagedTaskEx AManagedTaskEx;

/**
 * Power mode classes. An ::AManagedTaskEx can belong to only one power mode class.
 * An ::AManagedTask belong, by default, to E_PM_CLASS_0.
 */
typedef enum _EPMClass {
  E_PM_CLASS_0 = 0, /**< E_PM_CLASS_0 - this class is for backward compatibility. A managed task belonging to this class execute the power mode switch as in eLooM v2.*/
  E_PM_CLASS_1 = 1, /**< E_PM_CLASS_1 - a managed task belonging to this class is delayed during a PM transaction until all task belonging to E_PM_CLASS_0 did the transaction. */
  E_PM_CLASS_2 = 2  /**< E_PM_CLASS_2 - a managed task belonging to this class is delayed during a PM transaction until all task belonging to E_PM_CLASS_0 and E_PM_CLASS_1  did the transaction. */
} EPMClass;


// Public API declaration
//***********************

/**
 * Initialize a managed task structure. The application is responsible to allocate
 * a managed task in memory. This method must be called after the allocation.
 *
 * @param _this [IN] specifies a task object pointer.
 * @return \a SYS_NO_ERROR_CODE
 */
static inline sys_error_code_t AMTInitEx(AManagedTaskEx *_this);

/**
 * Called by the framework to force the step execution.
 * During a step execution a task can be suspended waiting for an event or for other reason.
 * The In this situation the INIT task cannot complete the power mode switch, so it calls this method
 * in order to force the task to be ready for the power mode switch.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param eActivePowerMode [IN] specifies the actual power mode
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t AMTExForceExecuteStep(AManagedTaskEx *_this, EPowerMode eActivePowerMode);

/**
 * Task specific function called by the framework just before the system starts the sequence to enter a new
 * specific power mode. Trough this function the system gives a task the option for an early preparation for
 * the transaction in the power mode state machine.
 * This function is executed in the INIT task execution flow.
 * Note that this is different from the AMTDoEnterPowerMode() and a task shall assume that a step in the current
 * power mode is still possible after executing this function.
 *
 * @param _this [IN] specifies a task object pointer.
 * @param eActivePowerMode [IN] specifies the current power mode of the system.
 * @param eNewPowerMode [IN] specifies the new power mode that is to be activated by the system.
 * @return \a SYS_NO_ERROR_CODE if success, a task specific error code otherwise that stops the power mode switch.
 */
static inline sys_error_code_t AMTExOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);

/**
 * A task must use this method to notify the framework when it is entering the suspend state or
 * when is blocking on a event without a timeout. This state is called "inactive".
 * This information is used to the AED to resetting the system because it thinks that the task
 * is not responding.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param bBlockedSuspended [IN] `TRUE` if a the task is entering the inactive state,
 *                                `FALSE` if a task is leaving the inactive state.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t AMTExSetInactiveState(AManagedTaskEx *_this, boolean_t bBlockedSuspended);

/**
 * Check if the a managed task is inactive. A managed task is inactive when:
 * - it is in suspend state
 * - it is in blocked state without a timeout
 *
 * For more information about the task state see https://freertos.org/RTOS-task-states.html
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return `TRUE` if the task is in inactive state, `FALSE` otherwise.
 */
static inline boolean_t AMTExIsTaskInactive(AManagedTaskEx *_this);

/**
 * Set the PM class for the managed task.  During a PM transaction, all tasks belonging to
 * E_PM_CLASS_0 will execute the DoEnterPowerMode() before the managed tasks belonging to
 * E_PM_CLASS_1.
 * The application, for example, can use the AMTExOnEnterPowerMode() function in order to
 * dynamically set the PM Class for the application task. In this way it is possible to control the of the task
 * executing the transaction during a power mode switch.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param eNewPMClass [IN] specifies the new PM class for the task.
 * @return SYS_NO_ERROR_CODE
 */
static inline sys_error_code_t AMTExSetPMClass(AManagedTaskEx *_this, EPMClass eNewPMClass);

/**
 * Get the Power Mode Class of the managed task.
 * @param _this [IN] specifies a pointer to the object.
 * @return the Power Mode Class of the managed task
 */
static inline EPMClass AMTExGetPMClass(AManagedTaskEx *_this);

/**
 * This is the default control loop of a managed task.
 * @param nParams [IN] specify a pointer to the task object:
 * AManagedTaskEx *pTask = (AManagedTaskEx*)pParams;
 */
VOID AMTExRun(ULONG nParam);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_AMANAGEDTASKEX_H_ */
