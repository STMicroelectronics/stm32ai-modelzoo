/**
 ******************************************************************************
 * @file    syserror.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Sep 5, 2016
 * @brief   Define the global error management API.
 *
 * The system uses a single 32 bits global variable to track the last runtime error.
 * This variable stores in the last significant 16 bits (bit [0,15]) the last error occurred in the
 * Low Level API layer. The last error occurred in the Service Layer level is stored
 * in the most significant 16 bits (bit [16, 31]).
 * The application uses the SYS_GET_LAST_ERROR() macro to retrieve the last error.
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

#ifndef SYSERROR_H_
#define SYSERROR_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <assert.h>
#include <stdint.h>
#include "events/sysevent.h"

/**
 * Create type name for sys_error_code_t.
 */
typedef uint16_t sys_error_code_t;

#define SYS_ERR_EVT_SRC_IAED                0x1U  ///< Event generated from the IApplicationErrorDelegate.
// IApplicationErrorDelegate parameters
#define SYS_ERR_EVT_PARAM_CHECK_TASKS       0x1U  ///< Event parameter: check is tasks are still running.
#define SYS_ERR_EVT_PARAM_EFT               0x2U  ///< Event parameter: EFT error detected.
#define SYS_ERR_EVT_PARAM_EFT_TIMEOUT       0x3U  ///< Event parameter: EFT error timeout.
#define SYS_ERR_EVT_PARAM_NOP               0x4U  ///< Event parameter: EFT IRQ to be ignored.

/**
 * Macro to make system error event.
 *
 * @param src [IN] specifies the source of the event
 * @param params [IN] specifies a parameter. Its value depend on the event source.
 */
#define SYS_ERR_MAKE_EVENT(src, params)     ((((src) & 0X7U) | (((params)<<3) & 0xF8U) | (0x1U<<31)) & 0x800000FF)

/**
 * Macro to check the .nEventType of a system event.
 *
 * @param evt [IN] specifies an event
 * @return TRUE if the evt is an error system event, FALSE otherwise
 */
#define SYS_IS_ERROR_EVENT(evt)             ((evt).xEvent.nEventType == 1U)

#ifndef SysPostEvent
#define SysPostErrorEvent SysPostEvent
#endif

/**
 * Notify the system about an event related to the error management.
 * This function can be called also from an ISR.
 *
 * @param xEvent [IN] specifies a error event.
 * @return SYS_NO_ERROR_CODE if the event has been posted in the system queue with success,
 *         an error code otherwise.
 */
sys_error_code_t SysPostErrorEvent(SysEvent xEvent);

/**
 * Reset the counter of the AED. Usually an AED use some kind of timeout to check that all managed tasks are working fine.
 * A task should call this method before a critical operation, that is for example a write operation in FLASH or EEPROM,
 * or a long critical section.
 * For convenience the managed task interface has a function IMTResetAEDCounter() that can be used by a task instead of
 * call directly the system function.
 */
void SysResetAEDCounter(void);


/**
 * Specifies the format of the global error used by the system to track the last error occurred.
 */
typedef union _sys_error_t {
	/**
	 * Field useful to manage the system error.
	 */
  unsigned long error_code;

  /**
   * Defines the sintax of the system error.
   */
  struct {
  	/**
  	 * Specifies the error code for the System Low Level layer.
  	 */
    unsigned int low_level_e:       16;

    /**
     * Specifies the error code for the System Service Level layer.
     */
    unsigned int service_level_e:   16;
  } type;
} sys_error_t;

/**
 * This is the global variable that store the last low level and the last service level error code.
 */
extern sys_error_t g_nSysError;

#if (SYS_TRACE > 1)
void sys_check_error_code(sys_error_code_t xError);
#endif

/**
 * This function is executed in case of error occurrence. If the application is in Debug
 * configuration it inserts a dynamic breakpoint.
 */
void sys_error_handler(void);


#define SYS_CLEAR_ERROR()                                     {g_nSysError.error_code = 0;}
#define SYS_CLEAR_LOW_LEVEL_ERROR()                           {g_nSysError.type.low_level_e = 0;}
#define SYS_IS_ERROR(e)                                       ((e).error_code != 0U)
#define SYS_IS_ERROR_CODE(e)                                  ((e)!=0U)
#define SYS_IS_LOW_LEVEL_ERROR(e)                             ( (e).type.low_level_e )
#define SYS_IS_SERVICE_LEVEL_ERROR(e)                         ( (e).type.service_level_e )
#define SYS_SET_LOW_LEVEL_ERROR_CODE(e)                       {g_nSysError.type.low_level_e = (e);}
#define SYS_SET_SERVICE_LEVEL_ERROR_CODE(e)                   {g_nSysError.type.service_level_e = (e);}
#define SYS_GET_LAST_ERROR()                                  g_nSysError
#define SYS_GET_LAST_LOW_LEVEL_ERROR_CODE()                   (g_nSysError.type.low_level_e)
#define SYS_GET_LAST_SERVICE_LEVEL_ERROR_CODE()               (g_nSysError.type.service_level_e)
#define SYS_GET_LOW_LEVEL_ERROR_CODE(e)                       ((e).type.low_level_))
#define SYS_GET_SERVICE_LEVEL_ERROR_CODE(e)                   ((e).type.service_level_e)

#define SYS_GENERIC_LOW_LEVEL_ERROR                           ((sys_error_t){0x1})

#define SYS_NO_ERROR                                          ((sys_error_t){0x0})
#define SYS_NO_ERROR_CODE                                     (0x0)
#define SYS_GROUP_ERROR_COUNT                                 (200)

// Low Level API error constants
#define SYS_BASE_LOW_LEVEL_ERROR                              ((sys_error_t){0x1})
#define SYS_BASE_LOW_LEVEL_ERROR_CODE                         (0x1)

// Task Level Service error constants
#define SYS_BASE_SERVICE_LEVEL_ERROR                          ((sys_error_t){0x10000})
#define SYS_BASE_SERVICE_LEVEL_ERROR_CODE                     (0x1)

/* Error Code definition */
/*************************/

/* General SYS error code */
/**************************/
#define SYS_BASE_ERROR_CODE                                   0X1
#define SYS_UNDEFINED_ERROR_CODE                              SYS_BASE_ERROR_CODE + 1
#define SYS_OUT_OF_MEMORY_ERROR_CODE                          SYS_BASE_ERROR_CODE + 2
#define SYS_INVALID_PARAMETER_ERROR_CODE                      SYS_BASE_ERROR_CODE + 3
#define SYS_INVALID_FUNC_CALL_ERROR_CODE                      SYS_BASE_ERROR_CODE + 4
#define SYS_TIMEOUT_ERROR_CODE                                SYS_BASE_ERROR_CODE + 5
#define SYS_NOT_IMPLEMENTED_ERROR_CODE                        SYS_BASE_ERROR_CODE + 6


/* Low Level API error code */
/****************************/


/* Service Level error code */
/****************************/

// ApplicationContext error
#define SYS_BASE_AC_ERROR_CODE                                SYS_BASE_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_AC_TASK_ALREADY_ADDED_ERROR_CODE                  SYS_BASE_AC_ERROR_CODE + 1

// IEventSrc error code
#define SYS_BASE_IEVTSRC_ERROR_CODE                           SYS_BASE_AC_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_IEVTSRC_FULL_ERROR_CODE                           SYS_BASE_IEVTSRC_ERROR_CODE + 1


/* Task Level Service error code */
/*********************************/

#define SYS_BASE_TASK_ERROR_CODE                              SYS_BASE_IEVTSRC_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE                SYS_BASE_TASK_ERROR_CODE + 1
#define SYS_TASK_INVALID_CALL_ERROR_CODE                      SYS_BASE_TASK_ERROR_CODE + 2
#define SYS_TASK_INVALID_PARAM_ERROR_CODE                     SYS_BASE_TASK_ERROR_CODE + 3
#define SYS_TASK_QUEUE_FULL_ERROR_CODE                        SYS_BASE_TASK_ERROR_CODE + 4

/* Init Task error code */
/************************/
#define SYS_BASE_INIT_TASK_ERROR_CODE                         SYS_BASE_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_INIT_TASK_FAILURE_ERROR_CODE                      SYS_BASE_INIT_TASK_ERROR_CODE + 1
#define SYS_INIT_TASK_POWER_MODE_NOT_ENABLE_ERROR_CODE        SYS_BASE_INIT_TASK_ERROR_CODE + 2

#define SYS_LAST_ERROR_CODE                                   SYS_INIT_TASK_POWER_MODE_NOT_ENABLE_ERROR_CODE

#define APP_BASE_ERROR_CODE                                   SYS_LAST_ERROR_CODE + 1  ///<< Initial value for the application defined error codes.

/*
 * MISRAC2012-Rule-20. #include is not at the top of the source file, preceding all code.
 * This include must be here by design.
 */
#include "apperror.h"

#ifdef __cplusplus
}
#endif

#endif /* SYSERROR_H_ */
