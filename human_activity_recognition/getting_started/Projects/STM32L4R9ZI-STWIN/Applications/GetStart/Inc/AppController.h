/**
 ******************************************************************************
 * @file    AppController.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
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
#include "events/IProcessEventListener.h"
#include "events/IProcessEventListener_vtbl.h"
#include "queue.h"
#include "SensorManager.h"

/**
 * Create  type name for struct _ACProcessEventListener_t
 */
typedef struct _ACProcessEventListener_t ACProcessEventListener_t;

struct _ACProcessEventListener_t
{
  IProcessEventListener super;

  void* p_owner;
};

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
  QueueHandle_t in_queue;

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
   * Input queue of the AITask. It is used by the controller to operate the task.
   */
  QueueHandle_t ai_in_queue;

  /**
   * Ai task execution time
   */

  float ai_task_xt_in_us;

  /**
    * scale factor for conversion in microseconds
    */
  float xt_in_us_scale_factor;

  /**
    * scale factor for conversion in microseconds
    */
  uint8_t in_caracter;

  /**
   * Listener IF to listen the process events coming from the DPUs.
   */
  ACProcessEventListener_t listenetIF;
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
 * Register the AI processes input queue with the application controller. They are used by the controller to operate the AI process.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param ai_queue [IN] specifies the AITask input queue.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t AppControllerSetAIProcessesInQueue(AppController_t *_this, QueueHandle_t ai_queue);

#ifdef __cplusplus
}
#endif

#endif /* INC_APPCONTROLLER_H_ */
