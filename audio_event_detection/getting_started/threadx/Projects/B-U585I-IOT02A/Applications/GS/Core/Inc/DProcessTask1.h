/**
 ********************************************************************************
 * @file    DProcessTask1.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 1.0.0
 * @date    Jul 29, 2022
 *
 * @brief
 *
 * <ADD_FILE_DESCRIPTION>
 *
 ********************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ********************************************************************************
 */
#ifndef DPROCESSTASK1_H_
#define DPROCESSTASK1_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/AManagedTaskEx.h"
#include "services/AManagedTaskEx_vtbl.h"
#include "events/IDataEventListener.h"
#include "events/IDataEventListener_vtbl.h"
#include "ADPU2.h"
#include "ADPU2_vtbl.h"
#include "app_messages_parser.h"
#include "DProcessTask1MessagesDef.h"

/* DProcessTask1 ERROR CODE */
/****************************/

#define DPT1_NO_ERROR_CODE                      0
#ifndef SYS_DPT1_BASE_ERROR_CODE
#define SYS_DPT1_BASE_ERROR_CODE                1  ///<< the base error code is used to remap DPT1 error codes at application level in the file apperror.h
#endif
#define SYS_DPT1_UNKOWN_MSG                     SYS_DPT1_BASE_ERROR_CODE + 1
#define SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE       SYS_DPT1_BASE_ERROR_CODE + 1


/**
 * Create  type name for _DProcessTask1.
 */
typedef struct _DProcessTask1 DProcessTask1_t;

/**
 *  DProcessTask1 internal structure.
 */
struct _DProcessTask1 {
  /**
   * Base class object.
   */
  AManagedTaskEx super;

  /* Task variables should be added here.*/

  /**
   * Task input message queue. The task receives messages in this queue.
   * This is one of the way the task exposes its services at application level.
   */
  TX_QUEUE in_queue;

  /**
   * DPU used to process the data.
   */
  ADPU2_t *p_dpu;

  /**
   * Data buffer used by the DPU but allocated by the task. The size of the buffer depend
   * on many parameters like:
   * - the type of the data used as input by the DPU
   * - the length of the signal
   * - the number of signals to manage in a circular way in order to decouple the data producer from the data process.
   * The correct size in byte is computed by the DPU with the formula: ADPU2_GetInDataPayloadSize() * input_signals_number.
   */
  void *p_dpu_in_buff;

  /**
   * Data buffer used by the DPU but allocated by the task.
   */
  void *p_dpu_out_buff;
};


/* Public API declaration */
/**************************/

/**
 * Allocate an instance of DProcessTask1.
 *
 * @return a pointer to the generic object ::AManagedTaskEx if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *DProcessTask1Alloc();

/**
 * Allocate an instance of ::DProcessTask1_t in a memory block specified by the application.
 * The size of the memory block must be greater or equal to `sizeof(DProcessTask1_t)`.
 * This allocator allows the application to avoid the dynamic allocation.
 *
 * \code
 * DProcessTask1_t process_task;
 * DProcessTask1StaticAlloc(&process_task);
 * \endcode
 *
 * @param p_mem_block [IN] specify a memory block allocated by the application.
 *        The size of the memory block must be greater or equal to `sizeof(DProcessTask1)`.
 * @return a pointer to the generic object ::AManagedTaskEx_t if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *DProcessTask1StaticAlloc(void *p_mem_block);

/**
 * Get the task input queue. The application can use the services exported by the task by sending message
 * of type struct DProcessTask1_t to this queue. The command ID for all supported command are defined in
 * AIMessagesDef.h
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return an handle to the task input message queue.
 */
static inline TX_QUEUE* DPT1GetInQueue(DProcessTask1_t *_this);

/**
 * Register a DPU with the processing task. This class manage only one DPU, so
 * any previous DPU added to the task are ignored.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_dpu [IN] specifies a DPU to register with the task.
 * @return the previous registered DPU if any, or NULL otherwise.
 */
static inline ADPU2_t *DPT1AddDPU(DProcessTask1_t *_this, ADPU2_t *p_dpu);

/**
 * Remove a DPU registered with the task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return the previous registered DPU if any, or NULL otherwise.
 */
static inline ADPU2_t *DPT1RemoveDPU(DProcessTask1_t *_this);

/**
 * Get the DPU registered with the task.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return the registered DPU if any, or NULL otherwise.
 */
static inline ADPU2_t *DPT1GetDPU(DProcessTask1_t *_this);

/**
 * Enable or disable the asynchronous data processing.
 * By default a new input data for the DPU is processed as soon as it is ready in the same execution flow
 * of the data source that has completed the data production. Sometimes it is useful to decouple data acquisition
 * and data processing because, for example, the data processing is time consuming. In this case the data processing
 * and dispatching can be done in the execution flow of the digital processing task by enabling the asynchronous data processing.
 *
 * This method can be called only when the task is STATE1 power mode.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param enable [IN] `true` to enable the asynchronous data processing, `false` to disable it.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t DPT1EnableAsyncDataProcessing(DProcessTask1_t *_this, bool enable);

/**
 * Process a message according to the actual power mode state of the task - `AMTGetTaskPowerMode((AManagedTask*)_this)`.
 * This method can be used in the task control loop of a derived class, eg:
 *
 * \code{.c}
 * AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
 * if (TX_SUCCESS == tx_queue_receive(&p_obj->in_queue, &msg, TX_WAIT_FOREVER))
 * {
 *   AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
 *
 *   if (msg specific for the derived class, MY_TASK)
 *   {
 *     // process the message
 *   }
 *   else {
 *     res = DPT1ProcessMsg((DProcessTask1_t*)p_obj, &msg);
 *     if(res == SYS_DPT1_UNKOWN_MSG)
 *     {
 *       SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("MY_TASK: unexpected message ID:0x%x\r\n", msg.msg_id));
 *     }
 *   }
 * }
 * \endcode
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_msg [IN]
 * @return  - SYS_NO_EROR_CODE if success
 *          - SYS_DPT1_UNKOWN_MSG if the message is invalid in the actual power mode state
 *          - a task specific error code otherwise.
 */
sys_error_code_t DPT1ProcessMsg(DProcessTask1_t *_this, AppMsg_t *p_msg);

/**
 * Send a message to the back of the task queue `in_queue`.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_msg [IN] specifies a message to send.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
sys_error_code_t DPT1PostMessageToBack(DProcessTask1_t *_this, AppMsg_t *p_msg);

/**
 * Add a process listener to the DPU owned by the task.
 *
 * The method is asynchronous.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_listener [IN] specifies the ::IDataEventListener_t object to add.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t DPT1AddDPUListener(DProcessTask1_t *_this, IDataEventListener_t *p_listener);

/**
 * Remove a process listener to the DPU owned by the task.
 *
 * The method is asynchronous.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_listener [IN] specifies the ::IDataEventListener_t object to remove.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t DPT1RemoveDPUListener(DProcessTask1_t *_this, IDataEventListener_t *p_listener);

/**
 * Attach as next a DPU object to the DPU owned by the task.
 *
 * The method is asynchronous.
 *
 * @sa IDPU2_AttachToDPU()
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_next_dpu [IN] specifies a pointer to a IDPU2 object that become the next to the DPU chain.
 * @param p_builder [IN] specifies a data builder object used to convert the data from the format of this DPU
 *        to the input format of the p_next_dpu.
 * @param build_strategy [IN] specifies a build strategy.
 * @return SYS_NO_ERROR_CODE, SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE otherwise.
 */
sys_error_code_t DPT1AttachToDPU(DProcessTask1_t *_this, IDPU2_t *p_next_dpu, IDataBuilder_t *p_data_builder, IDB_BuildStrategy_e build_strategy);

/**
 * Detach the DPU object attached as next to the DPU owned by the task.
 *
 * The method is asynchronous.
 *
 * @sa IDPU2_DetachFromDPU()
 * @param _this [IN] specifies a pointer to a task object.
 * @param release_data_builder [IN] id `true` the related data builder is released (SysFree).
 * @return SYS_NO_ERROR_CODE, SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE otherwise.
 */
sys_error_code_t DPT1DetachFromDPU(DProcessTask1_t *_this, bool release_data_builder);

sys_error_code_t DPT1AttachToDataSource(DProcessTask1_t *_this, ISourceObservable *p_data_src, IDataBuilder_t *p_data_builder, IDB_BuildStrategy_e build_strategy);
sys_error_code_t DPT1DetachFromDataSource(DProcessTask1_t *_this, ISourceObservable *p_data_src, bool release_data_builder);

/**
 * Set the memory buffer used by the DPU to manage the input data. It must be big enough to store
 * the payload of one or more input data. To know the size in byte of the payload of one input data, it is
 * possible to use the method ADPU2_GetInDataPayloadSize(). If the DPU has already an input buffer,
 * then it is released and replaced with the new one.
 *
 * If `buffer_size` is equal to zero then the DPU releases the buffer resources.
 *
 * If the DPU has no input data buffer then its behavior, when it receive new data, is not defined.
 * This method is asynchronous.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param p_buffer [IN] specifies a buffer .
 * @param buffer_size [IN] specifies the size in byte of the buffer.
 * @return SYS_NO_ERROR_CODE if success, SYS_OUT_OF_MEMORY_ERROR_CODE otherwise.
 */
sys_error_code_t DPT1SetInDataBuffer(DProcessTask1_t *_this, uint8_t *p_buffer, uint32_t buffer_size);

/**
 * Set the memory buffer used by the DPU to manage the output data. It must be big enough to store
 * the payload of one output data. To know the size in byte of the payload of one output data, it is
 * possible to use the method ADPU2_GetOutDataPayloadSize().
 *
 * If the DPU has no output data buffer then its behavior, when it receive new data, is not defined.
 * This method is asynchronous.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param p_buffer [IN] specifies a buffer .
 * @param buffer_size [IN] specifies the size in byte of the buffer.
 * @return SYS_NO_ERROR_CODE if success, SYS_OUT_OF_MEMORY_ERROR_CODE otherwise.
 */
sys_error_code_t DPT1SetOutDataBuffer(DProcessTask1_t *_this, uint8_t *p_buffer, uint32_t buffer_size);

/**
 * Suspend the DPU. This method is asynchronous.
 *
 * @sa ADPU2_Suspend()
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE, SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE otherwise.
 */
sys_error_code_t DPT1SuspendDPU(DProcessTask1_t *_this);

/**
 * Resume the DPU. This method is asynchronous.
 *
 * @sa ADPU2_Resume()
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE, SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE otherwise.
 */
sys_error_code_t DPT1ResumeDPU(DProcessTask1_t *_this);

/**
 * Reset the DPU. This method is asynchronous.
 *
 * @sa ADPU2_Reset()
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE, SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE otherwise.
 */
sys_error_code_t DPT1ResetDPU(DProcessTask1_t *_this);

/**
 * This method start the processing and dispatch job in the task execution flow.
 * It must be called when a new input data is ready to be processed.
 *
 * This method is asynchronous.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE, SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE otherwise.
 */
sys_error_code_t DPT1OnNewInDataReady(DProcessTask1_t *_this);


/* Inline functions definition */
/*******************************/

static inline
TX_QUEUE* DPT1GetInQueue(DProcessTask1_t *_this)
{
  assert_param(_this != NULL);

  return &_this->in_queue;
}

static inline
ADPU2_t *DPT1AddDPU(DProcessTask1_t *_this, ADPU2_t *p_dpu)
{
  assert_param(_this != NULL);

  ADPU2_t *p_prev_dpu = _this->p_dpu;
  _this->p_dpu = p_dpu;

  return p_prev_dpu;
}

static inline
ADPU2_t *DPT1RemoveDPU(DProcessTask1_t *_this)
{
  assert_param(_this != NULL);

  ADPU2_t *p_prev_dpu = _this->p_dpu;
  _this->p_dpu = NULL;

  return p_prev_dpu;
}

static inline
ADPU2_t *DPT1GetDPU(DProcessTask1_t *_this)
{
  assert_param(_this != NULL);

  return _this->p_dpu;
}


#ifdef __cplusplus
}
#endif

#endif /* DPROCESSTASK1_H_ */
