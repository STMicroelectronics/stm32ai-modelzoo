/**
 ******************************************************************************
 * @file    AppController.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 *********************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *********************************************************************************
 */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef INC_APPCONTROLLER_H_
#define INC_APPCONTROLLER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>

#include "services/systp.h"
#include "services/syserror.h"
#include "services/AManagedTaskEx.h"
#include "services/AManagedTaskEx_vtbl.h"
#include "AppControllerMessagesDef.h"
#include "AI_Task.h"
#include "PreProc_Task.h"
#include "events/IDataEventListener.h"
#include "events/IDataEventListener_vtbl.h"
#include "SensorManager.h"

/* Task error codes */
/********************/
#ifndef SYS_NO_ERROR_CODE
#define SYS_NO_ERROR_CODE                  0
#endif
#ifndef SYS_BASE_CTRL_TASK_ERROR_CODE
#define SYS_BASE_CTRL_TASK_ERROR_CODE      1
#endif
#define SYS_CTRL_IN_BUFF_FULL_ERROR_CODE   SYS_BASE_CTRL_TASK_ERROR_CODE + 1
#define SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE  SYS_BASE_CTRL_TASK_ERROR_CODE + 2
#define SYS_CTRL_INVALID_PARAM_ERROR_CODE  SYS_BASE_CTRL_TASK_ERROR_CODE + 3
#define SYS_CTRL_TIMER_ERROR_CODE          SYS_BASE_CTRL_TASK_ERROR_CODE + 4
#define SYS_CTRL_WRONG_CONF_ERROR_CODE     SYS_BASE_CTRL_TASK_ERROR_CODE + 5

#define CTRL_TASK_CFG_MAX_IN_LENGTH        (1024U)
#define CTRL_TASK_CFG_MAX_OUT_LENGTH       (512U)

typedef enum {
CTRL_AI_GRAV_ROT_SUPPR,
CTRL_AI_GRAV_ROT,
CTRL_AI_PREPROC,
CTRL_AI_SPECTROGRAM_MEL,
CTRL_AI_SPECTROGRAM_LOG_MEL,
CTRL_AI_SPECTROGRAM_MFCC,
CTRL_AI_SCALING,
CTRL_AI_BYPASS
}Ctrl_preproc_t;

/**
 * Create  type name for struct _AppController_t.
 */
typedef struct _AppController_t AppController_t;

/**
 *  AppController_t internal structure.
 */
struct _AppController_t {
  /**
   * Base class object.
   */
  AManagedTaskEx super;

  /* Task variables should be added here. */

  /**
   * Task input message queue. The task receives message of type struct CtrlMessage_t in this queue.
   * This is one of the way the task expose its services at application level.
   */
  TX_QUEUE in_queue;

  /**
   * sequence of execution_phase.
   */
  uint32_t *sequence ;

  /**
   * index of the execution phase .
   */
   uint16_t seq_index;

  /**
   * Specifies the number of signals to evaluate in the next phase.
   */
  uint32_t signals;

  /**
   * Used to count the evaluated signals during a detection or learning phase.
   */
  uint32_t signal_count;

  /**
   * pointer to sensor connected to AI DPU.
   */
  ISourceObservable *p_ai_sensor_obs;

  /**
   * AI task. It executes the AI inference in a separate thread.
   */
  AI_Task_t *p_ai_task;

  /**
   * Preprocessing  task. It executes the preprocessing in a separate thread.
   */
  PreProc_Task_t *p_preproc_task;

  /**
   * AI task. time spent during init.
   */
  float ai_task_time_init;

  /**
   * Preprocessing task. time spent during init.
   */
  float preproc_task_time_init;


  /**
    * scale factor for conversion in microseconds
    */
  uint8_t in_caracter;

  /**
   * Listener IF to listen the data events coming from the DPUs.
   */
  IDataEventListener_t listener_if;

  /**
   * To comply with the IListener IF (even if it is no more used because we use the offsetof() to get a pointer to the IF owner.).
   */
  void *p_listener_if_owner;

  /**
   * To configure pre processing chain
   */
  Ctrl_preproc_t pre_proc_type;

  /**
   * type of sensor connected
   */
  uint32_t sensor_type;
};


/* Public API declaration */
/**************************/

/**
 * Allocate an instance of AppController_t.
 *
 * @return a pointer to the generic object ::AManagedTaskEx if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *AppControllerAlloc(void);

/**
 * The application is defined by a set o managed tasks. The ::AppController_t coordinate the activities of those task by
 * using their public API or their input message queue so send messages.
 * This method is used to connect the application tasks with the ::AppController_t.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_ai_task [IN] specifies an instance of AI_Task_t used by the application.
 * @param p_preproc_task [IN] specifies an instance of Preproc_Task_t used by the application.
 * @return SYS_NO_ERROR_CODE
 */
sys_error_code_t AppControllerConnectAppTasks(AppController_t *_this, AI_Task_t *p_ai_task, PreProc_Task_t *p_preproc_task);

#ifdef __cplusplus
}
#endif

#endif /* INC_APPCONTROLLER_H_ */
