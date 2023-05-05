/**
  ******************************************************************************
  * @file    AI_Task.h
  * @author  STMicroelectronics - AIS - MCD Team
  * @version $Version$
  * @date    $Date$
  *
  * @brief
  *
  * <DESCRIPTIOM>
  *
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef SRC_AI_TASK_H_
#define SRC_AI_TASK_H_

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "DProcessTask1.h"
#include "DProcessTask1_vtbl.h"
#include "AI_DPU.h"
#include "AI_DPU_vtbl.h"
#include "AI_MessagesDef.h"


#define AI_TASK_DPU_TAG                   (0x30U)

/* Exported types ------------------------------------------------------------*/
/**
 * Create  type name for _AI_Task_t.
 */
typedef struct _AI_Task_t AI_Task_t;

/**
 *  AI_Task_t internal structure.
 */
struct _AI_Task_t {
  /**
   * Base class object.
   */
  DProcessTask1_t super;

  /* Task variables should be added here. */

  /**
   * Digital processing Unit specialized for the HAR X-Cube-AI library.
   */
   AI_DPU_t dpu;
};


/* Exported functions --------------------------------------------------------*/

/* Public API declaration */
/**************************/

/**
 * Allocate an instance of AI_Task_t.
 *
 * @return a pointer to the generic object ::AManagedTaskEx if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *AI_TaskAlloc(void);

/**
 * Allocate an instance of ::AI_Task_t in a memory block specified by the application.
 * The size of the memory block must be greater or equal to `sizeof(AI_Task_t)`.
 * This allocator allows the application to avoid the dynamic allocation.
 *
 * \code
 * AI_Task_t process_task;
 * AI_StaticAlloc(&process_task);
 * \endcode
 *
 * @param p_mem_block [IN] specify a memory block allocated by the application.
 *        The size of the memory block must be greater or equal to `sizeof(AI_Task_t)`.
 * @return a pointer to the generic object ::AManagedTaskEx_t if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *AI_StaticAlloc(void *p_mem_block);

/**
 * Set the input buffer for the DPU. The buffer is allocated in the system heap. The buffers size depends
 * on the numbers of signals. More signals allows to decouple the data source task from this processing task.
 * The buffer size is computed as ADPU2_GetInDataPayloadSize((ADPU2_t*)&_this->dpu) * input_signals_count;
 *
 * If `input_signals_count` is equal to zero then the resources of the input buffer are released.
 *
 * This method is asynchronous.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param input_signals_count [IN] specifies the maximum number of signals stored in the task to allow in parallels data acquisition and processing.
 * @return return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t AI_TaskAllocBufferForDPU(AI_Task_t *_this, uint8_t input_signals_count);

/**
 * load and initialize an AI model
 *
 * This method is asynchronous.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param model_name [IN] specifies the model name
 * @return return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t AI_LoadModel(AI_Task_t *_this, const char *p_model_name);

/**
 * release AI model
 *
 * This method is asynchronous.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t AI_ReleaseModel(AI_Task_t *_this);

/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* SRC_AI_TASK_H_ */
