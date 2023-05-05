/**
 ******************************************************************************
 * @file    ApplicationContext.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Jan 13, 2017
 *
 * @brief   Define the Application Context public API.
 *
 * TODO - insert here the file description
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

#ifndef INCLUDE_SERVICES_APPLICATIONCONTEXT_H_

#define INCLUDE_SERVICES_APPLICATIONCONTEXT_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "systp.h"
#include "AManagedTask.h"
#include "AManagedTaskEx.h"
#include "AManagedTaskEx_vtbl.h"

/**
 * An application context is a linked list of Managed tasks.
 */
typedef struct _ApplicationContext {
	/**
	 * Specifies the pointer to the first task.
	 */
	AManagedTask *m_pHead;

	/**
	 * Specifies the number of item (Managed Task object) in the list.
	 */
	uint8_t m_nListSize;
}ApplicationContext;

// Public API declaration
//***********************

/**
 * Initialize this application context.
 *
 * @param _this specifies a pointer to the application context object.
 * @return SYS_NO_ERROR_CODE.
 */
sys_error_code_t ACInit(ApplicationContext *_this);

/**
 * Add a managed task to this context. If the task is already in this application context it is not added twice.
 *
 * @param _this specifies a pointer to the application context object.
 * @param pTask specifies a pointer to a managed task object to be added to this context.
 * @return SYS_NO_ERROR_CODE if the the task has been added to the application context, or SYS_AC_TASK_ALREADY_ADDED_ERROR_CODE
 *         if the task is already in this application context.
 */
sys_error_code_t ACAddTask(ApplicationContext *_this, AManagedTask *pTask);

/**
 * Remove a managed task from this context.
 *
 * @param _this specifies a pointer to the application context object.
 * @param pTask specifies a pointer to a managed task object to be removed from this context.
 * @return SYS_NO_ERROR_CODE.
 */
sys_error_code_t ACRemoveTask(ApplicationContext *_this, AManagedTask *pTask);

/**
 * Get the number of managed task in this context.
 *
 * @param _this specifies a pointer to the application context object.
 * @return the number of managed task in this context.
 */
static inline uint8_t ACGetTaskCount(ApplicationContext *_this);

/**
 * Get a pointer to the first task object in this application context.
 *
 * @param _this specifies a pointer to the application context object.
 * @return a pointer to the first task object in this application context, or NULL if the this context is empty.
 */
static inline AManagedTask *ACGetFirstTask(ApplicationContext *_this);

/**
 * Get a pointer to the next task object after pTask in this application context.
 *
 * @param _this specifies a pointer to the application context object.
 * @param pTasks specifies a pointer a managed task object in this context.
 * @return a pointer to the next task object after pTask in this application context.
 */
static inline AManagedTask *ACGetNextTask(ApplicationContext *_this, const AManagedTask *pTask);


// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
uint8_t ACGetTaskCount(ApplicationContext *_this) {
	assert_param(_this != NULL);

	return _this->m_nListSize;
}

SYS_DEFINE_STATIC_INLINE
AManagedTask *ACGetFirstTask(ApplicationContext *_this) {
	assert_param(_this != NULL);

	return _this->m_pHead;
}

SYS_DEFINE_STATIC_INLINE
AManagedTask *ACGetNextTask(ApplicationContext *_this, const AManagedTask *pTask) {
	assert_param(_this != NULL);
	assert_param(pTask != NULL);
	UNUSED(_this);

	return pTask->m_pNext;
}

#ifdef __cplusplus
}
#endif


#endif /* INCLUDE_SERVICES_APPLICATIONCONTEXT_H_ */
