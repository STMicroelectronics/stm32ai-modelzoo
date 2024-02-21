/**
 ******************************************************************************
 * @file    IApplicationErrorDelegate.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Aug 4, 2017
 *
 * @brief   Application error manager delegate.
 *
 * This interface is implemented by a application specific object that is in
 * charge to manage the error events. The application can implement the
 * SysGetErrorDelegate() function to provide its own IApplicationErrorDelegate.
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
#ifndef INCLUDE_SERVICES_IAPPLICATIONERRORDELEGATE_H_
#define INCLUDE_SERVICES_IAPPLICATIONERRORDELEGATE_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "ApplicationContext.h"
#include "IErrorFirstResponder.h"
#include "IErrorFirstResponderVtbl.h"

/**
 * Create  type name for _IApplicationErrorDelegate.
 */
typedef struct _IApplicationErrorDelegate IApplicationErrorDelegate;


// Public API declaration
//***********************

/**
 * Initialize the driver. This method should be used by a task object during
 * the hardware initialization process.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 * @param pParams specifies a pointer to a subclass defined initialization parameters.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IAEDInit(IApplicationErrorDelegate *_this, void *pParams);

/**
 * Called by the system just before the control is released to the application tasks.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 * @param pxContext [IN] specifies a pointer to the application context.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IAEDOnStartApplication(IApplicationErrorDelegate *_this, ApplicationContext *pxContext);

/**
 * The INIT task uses this function to deliver an error event to the application error manager delegate object.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 * @param pxContext [IN] specifies a pointer to the application context.
 * @param xEvent [IN] specifies an error event
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IAEDProcessEvent(IApplicationErrorDelegate *_this, ApplicationContext *pxContext, SysEvent xEvent);

/**
 * The INIT task call this method as soon as a new error event is posted by the application. This
 * allows the application error delegate to provide a first respond to critical errors. The application
 * error delegate should notify the first responder objects starting from the highest priority one.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 * @param xEvent xEvent [IN] specifies an error event
 * @return SYS_NO_EROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IAEDOnNewErrEvent(IApplicationErrorDelegate *_this, SysEvent xEvent);

/**
 * Used by the AED to notify the system if the last error has been recovered or not.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 * @return \a TRUE if the last error has been recovered, \a FALSE otherwise
 */
static inline boolean_t IAEDIsLastErrorPending(IApplicationErrorDelegate *_this);

/**
 * Add a first responder object. The first responders are grouped in a priority set. Zero is the highest priority.
 * If an IErrFirstResponder object with the same priority was already added, then it is replaced with the new one.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 * @param pFirstResponder [IN] specifies a pointer to the a first responder object. If it is \a NULL then
 *        the IErrFirstResponder with nPriority priority is removed from the application error delegate.
 * @param nPriority [IN] specifies the priority of the error first responder. Zero is the highest priority.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IAEDAddFirstResponder(IApplicationErrorDelegate *_this, IErrFirstResponder *pFirstResponder, uint8_t nPriority);

/**
 * Remove a first responder object rom the application error delegate.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 * @param pFirstResponder [IN] specifies a pointer to the a first responder object to be removed.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IAEDRemoveFirstResponder(IApplicationErrorDelegate *_this, IErrFirstResponder *pFirstResponder);

/**
 * Get the highest priority allowed for a first responder object.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 * @return he highest priority allowed for a first responder object.
 */
static inline uint8_t IAEDGetMaxFirstResponderPriority(const IApplicationErrorDelegate *_this);

/**
 * Reset the counter of the AED. Usually an AED use some kind of timeout to check that all managed tasks are working fine.
 * A task should call this method before a critical operation, that is for example a write operation in FLASH or EEPROM,
 * or a long critical section.
 * For convenience the managed task interface has a function IMTResetAEDCounter() that can be used by a task instead of
 * call directly this function.
 *
 * @param _this [IN] specifies a pointer to an IApplicationErrorDelegate object.
 */
static inline void IAEDResetCounter(IApplicationErrorDelegate *_this);

// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_IAPPLICATIONERRORDELEGATE_H_ */
