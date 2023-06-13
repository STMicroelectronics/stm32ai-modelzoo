/**
  ******************************************************************************
  * @file    PreProc_Task.h
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
#ifndef SRC_PREPROC_TASK_H_
#define SRC_PREPROC_TASK_H_

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "DProcessTask1.h"
#include "DProcessTask1_vtbl.h"
#include "PreProc_DPU.h"
#include "PreProc_DPU_vtbl.h"
#include "PreProc_MessagesDef.h"


/* Exported types ------------------------------------------------------------*/
/**
 * Create  type name for _PreProc_Task_t.
 */
typedef struct _PreProc_Task_t PreProc_Task_t;

/**
 *  PreProc_Task_t internal structure.
 */
struct _PreProc_Task_t
{
  /**
   * Base class object.
   */
  DProcessTask1_t super;

  /* Task variables should be added here. */

  /**
   * Digital processing Unit specialized for the preproc library.
   */
  PreProc_DPU_t dpu;

  /**
   * Data buffer used by the DPU but allocated by the task.
   */
  int8_t dpu_out_buff[CTRL_X_CUBE_AI_SPECTROGRAM_NMEL * CTRL_X_CUBE_AI_SPECTROGRAM_COL];
};

/* Exported functions --------------------------------------------------------*/

/* Public API declaration */
/**************************/

/**
 * Allocate an instance of PreProc_Task_t.
 *
 * @return a pointer to the generic object ::AManagedTaskEx if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *PreProc_TaskAlloc(void);

/**
 * Allocate an instance of ::PreProc_TaskTask_t in a memory block specified by the application.
 * The size of the memory block must be greater or equal to `sizeof(PreProc_Task_t)`.
 * This allocator allows the application to avoid the dynamic allocation.
 *
 * \code
 * PreProc_Task_t process_task;
 * PreProc_TaskStaticAlloc(&process_task);
 * \endcode
 *
 * @param p_mem_block [IN] specify a memory block allocated by the application.
 *        The size of the memory block must be greater or equal to `sizeof(PreProc_Task_t)`.
 * @return a pointer to the generic object ::AManagedTaskEx_t if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *PreProc_TaskStaticAlloc(void *p_mem_block);

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
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t PreProc_TaskSetDpuInBuffer(PreProc_Task_t *_this, uint16_t input_signals_count);

/**
 * Set the type of spectrogram  processing type (mel, logmel or mfcc)
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param spectrogram_type_t [IN] specifies the processing type
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t PreProc_TaskSetSpectrogramType(PreProc_Task_t *_this, spectrogram_type_t type);

/**
 * Set the parameters of spectrogram output quantization
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param  inv_scale [IN] specifies the invert of the scale
 * @param  offset [IN] specifies the offset
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t PreProc_TaskSetQuantizeParam(PreProc_Task_t *_this, float inv_scale, int8_t offset);

/**
 * Check if the input buffer for the DPU has been allocated.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return `true` if the buffer has been allocated, `false` otherwise.
 */
static inline bool PreProc_TaskIsDpuInBufferAllocated(PreProc_Task_t *_this);


/* Inline functions definition */
/*******************************/

static inline
bool PreProc_TaskIsDpuInBufferAllocated(PreProc_Task_t *_this)
{
  assert_param(_this != NULL);
  return _this->super.p_dpu_in_buff != NULL;
}

#ifdef __cplusplus
}
#endif

#endif /* SRC_PREPROC_TASK_H_ */
