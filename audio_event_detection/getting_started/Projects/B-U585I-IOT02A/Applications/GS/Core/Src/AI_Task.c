/**
  ******************************************************************************
  * @file    AI_Task.c
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

#include "AI_Task.h"
#include "AI_Task_vtbl.h"
#include "app_messages_parser.h"
#include "services/sysmem.h"
#include "services/sysdebug.h"
#include "ai_platform_interface.h" /* AI Run-time header files */

#ifndef AI_TASK_CFG_STACK_DEPTH
#define AI_TASK_CFG_STACK_DEPTH            (TX_MINIMUM_STACK)
#endif

#ifndef AI_TASK_CFG_PRIORITY
#define AI_TASK_CFG_PRIORITY               (TX_MAX_PRIORITIES-2)
#endif

#ifndef AI_TASK_CFG_IN_QUEUE_LENGTH
#define AI_TASK_CFG_IN_QUEUE_LENGTH        (10)
#endif
#define AI_TASK_CFG_IN_QUEUE_ITEM_SIZE    (sizeof(struct DPU_MSG_Attach_t))  /*!< size of the biggest message managed by the task. */
#define AI_TASK_CFG_IN_QUEUE_SIZE         ((AI_TASK_CFG_IN_QUEUE_ITEM_SIZE)*(AI_TASK_CFG_IN_QUEUE_LENGTH))


#define AI_AXIS_NUMBER                    (3)
#define AI_DATA_INPUT_USER                (24)

#define AI_LSB_16B                        (1.0F/32768) // Value of an LSB for a 16 bit signed arithmetic

#define SYS_DEBUGF(level, message)            SYS_DEBUGF3(SYS_DBG_AI, level, message)

/**
 * Class object declaration. The class object encapsulates members that are shared between
 * all instance of the class.
 */
typedef struct _AI_TaskClass_t {
  /**
   * AI_Task class virtual table.
   */
  AManagedTaskEx_vtbl vtbl;

  /**
   * AI_Task class (PM_STATE, ExecuteStepFunc) map. The map is implemente with an array and
   * the key is the index. Number of items of this array must be equal to the number of PM state
   * of the application. If the managed task does nothing in a PM state, then set to NULL the
   * relative entry in the map.
   */
  pExecuteStepFunc_t p_pm_state2func_map[];
} AI_TaskClass_t;


/* Private member function declaration */
/***************************************/

/**
 * Execute one step of the task control loop while the system is in STATE1.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t AI_TaskExecuteStepState1(AManagedTask *_this);

/**
 * Execute one step of the task control loop while the system is in X_CUBE_AI_ACTIVE.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t AI_TaskExecuteStepAIActive(AManagedTask *_this);

/**
 * Implement the public asynchronous method AI_TaskAlloceBufferForDPU()
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param input_signals_count [IN] specifies the maximum number of signals stored in the task to allow in parallels data acquisition and processing.
 * @return return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static sys_error_code_t _AI_TaskAllocBufferForDPU(AI_Task_t *_this, uint8_t input_signals_count);


/**
 * The class object.
 */
static const AI_TaskClass_t sTheClass = {
    /* Class virtual table */
    {
        DProcessTask1_vtblHardwareInit,
        AI_Task_vtblOnCreateTask,
        DProcessTask1_vtblDoEnterPowerMode,
        DProcessTask1_vtblHandleError,
        DProcessTask1_vtblOnEnterTaskControlLoop,
        DProcessTask1_vtblForceExecuteStep,
        DProcessTask1_vtblOnEnterPowerMode
    },

    /* class (PM_STATE, ExecuteStepFunc) map */
    {
        AI_TaskExecuteStepState1,
        NULL,
        AI_TaskExecuteStepAIActive,
    }
};

/* Public API definition */
/*************************/

AManagedTaskEx *AI_TaskAlloc(void)
{
  AManagedTaskEx *p_root = (AManagedTaskEx*)SysAlloc(sizeof(AI_Task_t));

  /* Initialize the super class */
  AMTInitEx(p_root);

  p_root->vptr = &sTheClass.vtbl;

  return p_root;
}

AManagedTaskEx *AI_StaticAlloc(void *p_mem_block)
{
  AI_Task_t *p_obj = (AI_Task_t*)p_mem_block;

  if (p_obj != NULL)
  {
    /* Initialize the super class */
    AMTInitEx(&p_obj->super.super);

    p_obj->super.super.vptr = &sTheClass.vtbl;
  }

  return (AManagedTaskEx*)p_obj;
}

sys_error_code_t AI_TaskAllocBufferForDPU(AI_Task_t *_this, uint8_t input_signals_count)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;


  struct genericMsg_t msg = {
      .msg_id = APP_MESSAGE_ID_AI,
      .cmd_id = AI_CMD_ALLOC_DATA_BUFF,
      .param = (uint32_t) input_signals_count
  };

  res = DPT1PostMessageToBack((DProcessTask1_t*)_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t AI_LoadModel(AI_Task_t *_this, const char *p_model_name)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  struct genericMsg_t msg = {
      .msg_id = APP_MESSAGE_ID_AI,
      .cmd_id = AI_CMD_LOAD_MODEL,
      .param = (uint32_t)p_model_name
  };

  res = DPT1PostMessageToBack((DProcessTask1_t*)_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t AI_ReleaseModel(AI_Task_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  struct genericMsg_t msg = {
      .msg_id = APP_MESSAGE_ID_AI,
      .cmd_id = AI_CMD_UNLOAD_MODEL,
  };

  res = DPT1PostMessageToBack((DProcessTask1_t*)_this, (AppMsg_t*)&msg);

  return res;
}

/* AManagedTask virtual functions definition */
/*********************************************/

sys_error_code_t AI_Task_vtblOnCreateTask(AManagedTask *_this,
    tx_entry_function_t *pTaskCode, CHAR **pName, VOID **pStackStart,
    ULONG *pStackDepth, UINT *pPriority, UINT *pPreemptThreshold,
    ULONG *pTimeSlice, ULONG *pAutoStart, ULONG *pParams)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AI_Task_t *p_obj = (AI_Task_t*)_this;

  _this->m_pfPMState2FuncMap = sTheClass.p_pm_state2func_map;

  *pTaskCode = AMTExRun;
  *pName = "AI";
  *pStackStart = NULL; // allocate the task stack in the system memory pool.
  *pStackDepth = AI_TASK_CFG_STACK_DEPTH;
  *pParams = (ULONG)_this;
  *pPriority = AI_TASK_CFG_PRIORITY;
  *pPreemptThreshold = AI_TASK_CFG_PRIORITY;
  *pTimeSlice = TX_NO_TIME_SLICE;
  *pAutoStart = TX_AUTO_START;

  /* Change the CLASS for the power mode switch because I want to do the transaction after all
     sensors task. */
  AMTExSetPMClass((AManagedTaskEx *)_this, E_PM_CLASS_1);

  /* initialize the object software resource here. */
  VOID *pvQueueItemsBuff = SysAlloc(AI_TASK_CFG_IN_QUEUE_SIZE);
  if (pvQueueItemsBuff == NULL)
  {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }
  if (TX_SUCCESS != tx_queue_create(&p_obj->super.in_queue, "AI_Q",
      AI_TASK_CFG_IN_QUEUE_ITEM_SIZE/4U, pvQueueItemsBuff,
      AI_TASK_CFG_IN_QUEUE_SIZE))
  {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }
  /* Initialize DPU                   */
  (void) AI_DPU_StaticAlloc(&p_obj->dpu);
  (void) AI_DPU_Init(&p_obj->dpu);

  /* Initialize the data event source IF*/
  (void) ADPU2_SetTag((ADPU2_t*)&p_obj->dpu, AI_TASK_DPU_TAG);

  /*register the DPU with the base class*/
  (void) DPT1AddDPU((DProcessTask1_t*)p_obj, (ADPU2_t*)&p_obj->dpu);
  (void) DPT1EnableAsyncDataProcessing((DProcessTask1_t*)p_obj, true);
  /* Initialize the base class */
  p_obj->super.p_dpu_out_buff = NULL;
  p_obj->super.p_dpu_in_buff = NULL;

  return res;
}


/* AManagedTaskEx virtual functions definition */
/***********************************************/


/* Private function definition */
/*******************************/

static sys_error_code_t AI_TaskExecuteStepState1(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AI_Task_t *p_obj = (AI_Task_t*)_this;
  AppMsg_t msg = {0};
  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (TX_SUCCESS == tx_queue_receive(&p_obj->super.in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);

    if (APP_MESSAGE_ID_AI == msg.msg_id)
    {
      switch (msg.generic_msg.cmd_id)
      {
      case AI_CMD_ALLOC_DATA_BUFF:
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("AI: AI_CMD_ALLOC_DATA_BUFF\r\n"));
        res = _AI_TaskAllocBufferForDPU(p_obj, msg.generic_msg.param);
       break;

      case AI_CMD_LOAD_MODEL:
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("AI: AI_CMD_LOAD_MODEL\r\n"));
        res = AiDPULoadModel(&p_obj->dpu,(const char *)msg.generic_msg.param);
       break;

      case AI_CMD_UNLOAD_MODEL:
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("AI: AI_CMD_UNLOAD_MODEL\r\n"));
        res = AiDPUReleaseModel(&p_obj->dpu);
       break;

      default:
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("AI: unexpected command ID:0x%x\r\n", msg.generic_msg.cmd_id));
        break;
      }
    }
    else {
      res = DPT1ProcessMsg((DProcessTask1_t*)p_obj, &msg);
      if (msg.msg_id == DPU_MESSAGE_ID_ATTACH_TO_DATA_SRC)
      {
        /* special case: other then attach the DPU to a data source we set the sensitivity of the DPU*/
        (void)AI_DPU_SetSensitivity(&p_obj->dpu, ISourceGetFS(msg.dpu_msg_attach.p_data_obj.p_data_source)*AI_LSB_16B);
      }
      if(res == SYS_DPT1_UNKOWN_MSG)
      {
        /*unsupported message.*/
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("AI: unexpected message ID:0x%x\r\n", msg.msg_id));
      }
    }
  }
  return res;
}

static sys_error_code_t AI_TaskExecuteStepAIActive(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AI_Task_t *p_obj = (AI_Task_t*)_this;
  AppMsg_t msg = {0};
  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (TX_SUCCESS == tx_queue_receive(&p_obj->super.in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    res = DPT1ProcessMsg((DProcessTask1_t*)p_obj, &msg);
    if(res == SYS_DPT1_UNKOWN_MSG)
    {
      /*unsupported message.*/
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("AI: unexpected message ID:0x%x\r\n", msg.msg_id));
    }
  }
  return res;
}

static sys_error_code_t _AI_TaskAllocBufferForDPU(AI_Task_t *_this, uint8_t input_signals_count)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /*first release the memory if a buffer was already allocated.*/
  if (_this->super.p_dpu_in_buff != NULL)
  {
    (void)ADPU2_SetInDataBuffer((ADPU2_t*)&_this->dpu, _this->super.p_dpu_in_buff, 0U);
    SysFree(_this->super.p_dpu_in_buff);
    _this->super.p_dpu_in_buff = NULL;
  }
  if (_this->super.p_dpu_out_buff != NULL)
  {
    (void)ADPU2_SetOutDataBuffer((ADPU2_t*)&_this->dpu, _this->super.p_dpu_out_buff, 0U);
    SysFree(_this->super.p_dpu_out_buff);
    _this->super.p_dpu_out_buff = NULL;
  }

  size_t buff_size = ADPU2_GetInDataPayloadSize((ADPU2_t*)&_this->dpu) * input_signals_count;
  if (buff_size > 0)
  {
    /* allocate the input buffer */
    _this->super.p_dpu_in_buff = SysAlloc(buff_size);
    if (_this->super.p_dpu_in_buff == NULL)
    {
      res = SYS_OUT_OF_MEMORY_ERROR_CODE;
    }
    else
    {
      res = ADPU2_SetInDataBuffer((ADPU2_t*)&_this->dpu, _this->super.p_dpu_in_buff, buff_size);

      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("AI: input dpu buffer  = %i bytes\r\n", buff_size));
    }
    if (!SYS_IS_ERROR_CODE(res))
    {
      /* allocate the output buffer */
      buff_size = ADPU2_GetOutDataPayloadSize((ADPU2_t*)&_this->dpu);
      _this->super.p_dpu_out_buff = SysAlloc(buff_size);
      if (_this->super.p_dpu_out_buff != NULL)
      {
        (void)ADPU2_SetOutDataBuffer((ADPU2_t*)&_this->dpu, _this->super.p_dpu_out_buff, buff_size);

        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("AI: output dpu buffer = %i bytes\r\n", buff_size));
      }
    }
  }

  return res;
}
