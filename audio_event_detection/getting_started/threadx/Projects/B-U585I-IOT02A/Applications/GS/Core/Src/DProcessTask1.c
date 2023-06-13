/**
 ********************************************************************************
 * @file    DProcessTask1.c
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

#include "DProcessTask1.h"
#include "DProcessTask1_vtbl.h"
#include "services/sysmem.h"
#include "services/sysdebug.h"


#ifndef DPT1_TASK_CFG_STACK_DEPTH
#define DPT1_TASK_CFG_STACK_DEPTH         (TX_MINIMUM_STACK*2U)
#endif

#ifndef DPT1_TASK_CFG_PRIORITY
#define DPT1_TASK_CFG_PRIORITY            (TX_MAX_PRIORITIES-1U)
#endif

#ifndef DPT1_TASK_CFG_IN_QUEUE_LENGTH
#define DPT1_TASK_CFG_IN_QUEUE_LENGTH     (10)
#endif
#define DPT1_TASK_CFG_IN_QUEUE_ITEM_SIZE  (sizeof(struct DPU_MSG_Attach_t))  /*!< size of the biggest message managed by the task. */
#define DPT1_TASK_CFG_IN_QUEUE_SIZE       (DPT1_TASK_CFG_IN_QUEUE_ITEM_SIZE * DPT1_TASK_CFG_IN_QUEUE_LENGTH)


#define SYS_DEBUGF(level, message)      SYS_DEBUGF3(SYS_DBG_DPT1, level, message)


/**
 * Class object declaration. The class object encapsulates members that are shared between
 * all instance of the class.
 */
typedef struct _DProcessTask1Class_t {
  /**
   * DigitalProcessTask1 class virtual table.
   */
  AManagedTaskEx_vtbl vtbl;

  /**
   * (PM_STATE, ExecuteStepFunc) map. The map is implemented with an array and
   * the key is the index. Number of items of this array must be equal to the number of PM state
   * of the application. If the managed task does nothing in a PM state, then set to NULL the
   * relative entry in the map.
   */
  pExecuteStepFunc_t p_pm_state2func_map[];
} DProcessTask1Class_t;


/* Private member function declaration */
/***************************************/

/**
 * Execute one step of the task control loop while the system is in STATE1.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t DPT1ExecuteStepState1(AManagedTask *_this);

/**
 * Execute one step of the task control loop while the system is in X_CUBE_AI_ACTIVE.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t DPT1ExecuteStepProcessActive(AManagedTask *_this);

/**
 * Process a message from the `in_queue` in STATE1.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_msg [IN] specify a pointer to the message to be processed.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t DPT1ProcessMsgState1(DProcessTask1_t *_this, AppMsg_t *p_msg);

/**
 * Process a message from the `in_queue` in PROCESS_ACTIVE.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_msg [IN] specify a pointer to the message to be processed.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t DPT1ProcessMsgProcessActive(DProcessTask1_t *_this, AppMsg_t *p_msg);

/**
 * Callback used get the notification from the DPU.
 *
 * @param _this [IN] specifies the DPU that triggered the callback.
 * @param p_param [IN] specifies an application specific parameter.
 */
static void DPT1DPUCallback(IDPU2_t *_this, void* p_param);


/* Private object definition */
/*****************************/

/**
 * The class object.
 */
static const DProcessTask1Class_t sTheClass = {
    /* Class virtual table */
    {
        DProcessTask1_vtblHardwareInit,
        DProcessTask1_vtblOnCreateTask,
        DProcessTask1_vtblDoEnterPowerMode,
        DProcessTask1_vtblHandleError,
        DProcessTask1_vtblOnEnterTaskControlLoop,
        DProcessTask1_vtblForceExecuteStep,
        DProcessTask1_vtblOnEnterPowerMode
    },

    /* class (PM_STATE, ExecuteStepFunc) map */
    {
        DPT1ExecuteStepState1,
        NULL,
        DPT1ExecuteStepProcessActive,
    }
};

/* Public API definition */
/*************************/

AManagedTaskEx *DProcessTask1Alloc()
{
  DProcessTask1_t *p_new_obj = SysAlloc(sizeof(DProcessTask1_t));
  /* Initialize the super class */
  AMTInitEx(&p_new_obj->super);

  p_new_obj->super.vptr = &sTheClass.vtbl;

  return (AManagedTaskEx*)p_new_obj;
}

AManagedTaskEx *DProcessTask1StaticAlloc(void *p_mem_block)
{
  DProcessTask1_t *p_obj = (DProcessTask1_t*)p_mem_block;

  if (p_obj != NULL)
  {
    /* Initialize the super class */
    AMTInitEx(&p_obj->super);

    ((DProcessTask1_t*)p_obj)->super.vptr = &sTheClass.vtbl;
  }

  return (AManagedTaskEx*)p_obj;
}

sys_error_code_t DPT1ProcessMsg(DProcessTask1_t *_this, AppMsg_t *p_msg)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  EPowerMode active_power_mode = AMTGetTaskPowerMode((AManagedTask*)_this);

  if (active_power_mode == E_POWER_MODE_STATE1)
  {
    res = DPT1ProcessMsgState1(_this, p_msg);
  }
  else if (active_power_mode == 2U) //TODO: STF - E_POWER_MODE_SENSORS_ACTIVE
  {
    res = DPT1ProcessMsgProcessActive(_this, p_msg);
  }

  return res;
}

sys_error_code_t DPT1AddDPUListener(DProcessTask1_t *_this, IDataEventListener_t *p_listener)
{
  assert_param(_this != NULL);
  assert_param(p_listener != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_AddRemoveListener_t msg = {
      .msg_id = DPU_MESSAGE_ID_ADD_LISTENER,
      .p_listener = p_listener
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}


sys_error_code_t DPT1RemoveDPUListener(DProcessTask1_t *_this, IDataEventListener_t *p_listener)
{
  assert_param(_this != NULL);
  assert_param(p_listener != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_AddRemoveListener_t msg = {
      .msg_id = DPU_MESSAGE_ID_REMOVE_LISTENER,
      .p_listener = p_listener
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1AttachToDPU(DProcessTask1_t *_this, IDPU2_t *p_next_dpu, IDataBuilder_t *p_data_builder, IDB_BuildStrategy_e build_strategy)
{
  assert_param(_this != NULL);
  assert_param(p_data_builder != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_Attach_t msg = {
      .msg_id = DPU_MESSAGE_ID_ATTACH_TO_DPU,
      .p_data_obj.p_next_dpu = p_next_dpu,
      .p_data_builder = p_data_builder,
      .build_strategy = build_strategy
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1DetachFromDPU(DProcessTask1_t *_this, bool release_data_builder)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_Detach_t msg = {
      .msg_id = DPU_MESSAGE_ID_DETACH_FROM_DPU,
      .release_data_builder = release_data_builder
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1AttachToDataSource(DProcessTask1_t *_this, ISourceObservable *p_data_src, IDataBuilder_t *p_data_builder, IDB_BuildStrategy_e build_strategy)
{
  assert_param(_this != NULL);
  assert_param(p_data_src != NULL);
  assert_param(p_data_builder != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_Attach_t msg = {
      .msg_id = DPU_MESSAGE_ID_ATTACH_TO_DATA_SRC,
      .p_data_obj.p_data_source = p_data_src,
      .p_data_builder = p_data_builder,
      .build_strategy = build_strategy
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1DetachFromDataSource(DProcessTask1_t *_this, ISourceObservable *p_data_src, bool release_data_builder)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_Detach_t msg = {
      .msg_id = DPU_MESSAGE_ID_DETACH_FROM_DATA_SRC,
      .p_data_source = p_data_src,
      .release_data_builder = release_data_builder
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}


sys_error_code_t DPT1SetInDataBuffer(DProcessTask1_t *_this, uint8_t *p_buffer, uint32_t buffer_size)
{
  assert_param(_this != NULL);
  assert_param((buffer_size == 0) || (p_buffer != NULL));
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_SetBuffer_t msg = {
      .msg_id = DPU_MESSAGE_ID_SET_IN_BUFFER,
      .buffer_size = buffer_size,
      .p_buffer = p_buffer
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1SetOutDataBuffer(DProcessTask1_t *_this, uint8_t *p_buffer, uint32_t buffer_size)
{
  assert_param(_this != NULL);
  assert_param((buffer_size == 0) || (p_buffer != NULL));
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_SetBuffer_t msg = {
      .msg_id = DPU_MESSAGE_ID_SET_OUT_BUFFER,
      .buffer_size = buffer_size,
      .p_buffer = p_buffer
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1SuspendDPU(DProcessTask1_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_Cmd_t msg = {
      .msg_id = DPU_MESSAGE_ID_CMD,
      .cmd_id = DPT1_CMD_SUSPEND_DPU
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1ResumeDPU(DProcessTask1_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_Cmd_t msg = {
      .msg_id = DPU_MESSAGE_ID_CMD,
      .cmd_id = DPT1_CMD_RESUME_DPU
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1ResetDPU(DProcessTask1_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_Cmd_t msg = {
      .msg_id = DPU_MESSAGE_ID_CMD,
      .cmd_id = DPT1_CMD_RESET_DPU
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1OnNewInDataReady(DProcessTask1_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  struct DPU_MSG_Cmd_t msg = {
      .msg_id = DPU_MESSAGE_ID_CMD,
      .cmd_id = DPT1_CMD_NEW_IN_DATA_READY
  };

  res = DPT1PostMessageToBack(_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t DPT1PostMessageToBack(DProcessTask1_t *_this, AppMsg_t *p_msg)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (SYS_IS_CALLED_FROM_ISR())
  {
    if (TX_SUCCESS != tx_queue_send(&_this->in_queue, p_msg, TX_NO_WAIT))
    {
      res = SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE);
    }
  }
  else
  {
    if (TX_SUCCESS != tx_queue_send(&_this->in_queue, p_msg, AMT_MS_TO_TICKS(100)))
    {
      res = SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE);
    }
  }

  return res;
}

sys_error_code_t DPT1EnableAsyncDataProcessing(DProcessTask1_t *_this, bool enable)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /*check if we can change the asynchronous processing.*/
  if ((AMTGetTaskPowerMode((AManagedTask*)_this) != E_POWER_MODE_STATE1) || (_this->p_dpu == NULL))
  {
    res = SYS_INVALID_FUNC_CALL_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_FUNC_CALL_ERROR_CODE);
  }
  else {
    if (enable)
    {
      (void) IDPU2_RegisterNotifyCallback((IDPU2_t*)_this->p_dpu, DPT1DPUCallback, _this);
    }
    else
    {
      (void) IDPU2_RegisterNotifyCallback((IDPU2_t*)_this->p_dpu, NULL, NULL);
    }
  }

  return res;
}


/* AManagedTask virtual functions definition */
/*********************************************/

sys_error_code_t DProcessTask1_vtblHardwareInit(AManagedTask *_this, void *pParams)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
//  DProcessTask1_t *p_obj = (DProcessTask1*)_this;

  return res;
}

sys_error_code_t DProcessTask1_vtblOnCreateTask(AManagedTask *_this,
    tx_entry_function_t *pTaskCode, CHAR **pName, VOID **pStackStart,
    ULONG *pStackDepth, UINT *pPriority, UINT *pPreemptThreshold,
    ULONG *pTimeSlice, ULONG *pAutoStart, ULONG *pParams)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  DProcessTask1_t *p_obj = (DProcessTask1_t*)_this;

  /* initialize the object software resource here. */
  VOID *p_queue_items_buff = SysAlloc(DPT1_TASK_CFG_IN_QUEUE_SIZE);
  if (p_queue_items_buff == NULL)
  {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }
  if (TX_SUCCESS != tx_queue_create(&p_obj->in_queue, "DPT1_Q",
      DPT1_TASK_CFG_IN_QUEUE_ITEM_SIZE/4U , p_queue_items_buff,
      DPT1_TASK_CFG_IN_QUEUE_SIZE))
  {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }

  /*initialize other object members.*/
  p_obj->p_dpu = NULL;
  p_obj->p_dpu_in_buff = NULL;
  p_obj->p_dpu_out_buff = NULL;

  _this->m_pfPMState2FuncMap = sTheClass.p_pm_state2func_map;

  *pTaskCode = AMTExRun;
  *pName = "DPT1";
  *pStackStart = NULL; // allocate the task stack in the system memory pool.
  *pStackDepth = DPT1_TASK_CFG_STACK_DEPTH;
  *pParams = (ULONG)_this;
  *pPriority = DPT1_TASK_CFG_PRIORITY;
  *pPreemptThreshold = DPT1_TASK_CFG_PRIORITY;
  *pTimeSlice = TX_NO_TIME_SLICE;
  *pAutoStart = TX_AUTO_START;

  return res;
}

sys_error_code_t DProcessTask1_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode) {
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  DProcessTask1_t *p_obj = (DProcessTask1_t*)_this;

  if (new_power_mode == E_POWER_MODE_STATE1)
  {
    if (active_power_mode == 2U) //TODO: STF - E_POWER_MODE_SENSORS_ACTIVE
    {
      struct DPU_MSG_Cmd_t msg = {
          .msg_id = DPU_MESSAGE_ID_CMD,
          .cmd_id = DPT1_CMD_RESET_DPU
      };
      res = DPT1PostMessageToBack(p_obj, (AppMsg_t*)&msg);
    }
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x -> %d \r\n", p_obj->p_dpu->tag, (uint32_t)new_power_mode));

  return res;
}

sys_error_code_t DProcessTask1_vtblHandleError(AManagedTask *_this, SysEvent xError)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
//  DProcessTask1_t *p_obj = (DProcessTask1_t*)_this;

  return res;
}

sys_error_code_t DProcessTask1_vtblOnEnterTaskControlLoop(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
/*  DProcessTask1_t *p_obj = (DProcessTask1_t*)_this; */

  CHAR *task_name = "DPT1";
  tx_thread_info_get(&_this->m_xTaskHandle, &task_name, TX_NULL, TX_NULL, TX_NULL, TX_NULL, TX_NULL, TX_NULL, TX_NULL);

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("%s: start.\r\n", task_name));

  return res;
}


/* AManagedTaskEx virtual functions definition */
/***********************************************/

sys_error_code_t DProcessTask1_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode eActivePowerMode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  DProcessTask1_t *p_obj = (DProcessTask1_t*)_this;

  struct genericMsg_t msg = {
      .msg_id = APP_REPORT_ID_FORCE_STEP
  };

  if (TX_SUCCESS != tx_queue_front_send(&p_obj->in_queue, &msg, AMT_MS_TO_TICKS(100)))
  {
    res = SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE);
  }

  return res;
}

sys_error_code_t DProcessTask1_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
/*  DProcessTask1 *p_obj = (DProcessTask1*)_this; */

  return res;
}


/* Private function definition */
/*******************************/

static sys_error_code_t DPT1ExecuteStepState1(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  DProcessTask1_t *p_obj = (DProcessTask1_t*)_this;
  AppMsg_t msg = {0};

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (TX_SUCCESS == tx_queue_receive(&p_obj->in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    res = DPT1ProcessMsgState1(p_obj, &msg);
  }

  return res;
}

static sys_error_code_t DPT1ExecuteStepProcessActive(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  DProcessTask1_t *p_obj = (DProcessTask1_t*)_this;
  AppMsg_t msg = {0};

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (TX_SUCCESS == tx_queue_receive(&p_obj->in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    res = DPT1ProcessMsgProcessActive(p_obj, &msg);
  }
  return res;
}

static sys_error_code_t DPT1ProcessMsgState1(DProcessTask1_t *_this, AppMsg_t *p_msg)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  switch (p_msg->msg_id)
  {
    case DPU_MESSAGE_ID_ATTACH_TO_DATA_SRC:
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPU_MESSAGE_ID_ATTACH_TO_DATA_SRC\r\n", _this->p_dpu->tag));

      res = IDPU2_AttachToDataSource((IDPU2_t*)_this->p_dpu, p_msg->dpu_msg_attach.p_data_obj.p_data_source, p_msg->dpu_msg_attach.p_data_builder, p_msg->dpu_msg_attach.build_strategy);
      break;

    case DPU_MESSAGE_ID_DETACH_FROM_DATA_SRC:
    {
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPU_MESSAGE_ID_DETACH_FROM_DATA_SRC\r\n", _this->p_dpu->tag));

      IDataBuilder_t *p_data_builder;
      res = IDPU2_DetachFromDataSource((IDPU2_t*)_this->p_dpu, p_msg->dpu_msg_detach.p_data_source, &p_data_builder);
      if ((p_data_builder != NULL) && p_msg->dpu_msg_detach.release_data_builder)
      {
        SysFree(p_data_builder);
      }
      break;
    }

    case DPU_MESSAGE_ID_ATTACH_TO_DPU:
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPU_MESSAGE_ID_ATTACH_TO_DPU\r\n", _this->p_dpu->tag));

      res = IDPU2_AttachToDPU((IDPU2_t*)_this->p_dpu, p_msg->dpu_msg_attach.p_data_obj.p_next_dpu, p_msg->dpu_msg_attach.p_data_builder, p_msg->dpu_msg_attach.build_strategy);
      break;

    case DPU_MESSAGE_ID_DETACH_FROM_DPU:
    {
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPU_MESSAGE_ID_DETACH_FROM_DPU\r\n", _this->p_dpu->tag));

      IDataBuilder_t *p_data_builder;
      res = IDPU2_DetachFromDPU((IDPU2_t*)_this->p_dpu, &p_data_builder);
      if ((p_data_builder != NULL) && p_msg->dpu_msg_detach.release_data_builder)
      {
        SysFree(p_data_builder);
      }
      break;
    }

    case DPU_MESSAGE_ID_ADD_LISTENER:
    {
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPU_MESSAGE_ID_ADD_LISTENER\r\n", _this->p_dpu->tag));

      IEventSrc *p_evt_src = ADPU2_GetEventSrcIF((ADPU2_t*)_this->p_dpu);
      res = IEventSrcAddEventListener(p_evt_src, (IEventListener*)p_msg->dpu_msg_add_remove_listener.p_listener);
      break;
    }

    case DPU_MESSAGE_ID_REMOVE_LISTENER:
    {
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPU_MESSAGE_ID_REMOVE_LISTENER\r\n", _this->p_dpu->tag));

      IEventSrc *p_evt_src = ADPU2_GetEventSrcIF((ADPU2_t*)_this->p_dpu);
      res = IEventSrcRemoveEventListener(p_evt_src, (IEventListener*)p_msg->dpu_msg_add_remove_listener.p_listener);
      break;
    }

    case DPU_MESSAGE_ID_SET_IN_BUFFER:
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPU_MESSAGE_ID_SET_IN_BUFFER\r\n", _this->p_dpu->tag));

      res = ADPU2_SetInDataBuffer(_this->p_dpu, p_msg->dpu_msg_set_buff.p_buffer, p_msg->dpu_msg_set_buff.buffer_size);
      _this->p_dpu_in_buff = p_msg->dpu_msg_set_buff.p_buffer;
      break;

    case DPU_MESSAGE_ID_SET_OUT_BUFFER:
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPU_MESSAGE_ID_SET_OUT_BUFFER\r\n", _this->p_dpu->tag));

      res = ADPU2_SetOutDataBuffer(_this->p_dpu, p_msg->dpu_msg_set_buff.p_buffer, p_msg->dpu_msg_set_buff.buffer_size);
      _this->p_dpu_out_buff = p_msg->dpu_msg_set_buff.p_buffer;
      break;

    case DPU_MESSAGE_ID_CMD:
      switch (p_msg->dpu_msg_cmd.cmd_id)
      {
        case DPT1_CMD_SUSPEND_DPU:
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPT1_CMD_SUSPEND_DPU\r\n", _this->p_dpu->tag));

          (void)ADPU2_Suspend(_this->p_dpu);
          break;

        case DPT1_CMD_RESUME_DPU:
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPT1_CMD_RESUME_DPU\r\n", _this->p_dpu->tag));

          (void)ADPU2_Resume(_this->p_dpu);
          break;

        case DPT1_CMD_RESET_DPU:
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPT1_CMD_RESET_DPU\r\n", _this->p_dpu->tag));

          res = ADPU2_Reset(_this->p_dpu);
         break;

        default:
          /*unsupported command.*/
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x unexpected command ID:0x%x\r\n", _this->p_dpu->tag, p_msg->dpu_msg_cmd.cmd_id));

          res = SYS_DPT1_UNKOWN_MSG;
          break;
      }
      break;

    case APP_REPORT_ID_FORCE_STEP:
      __NOP();
      break;

    default:
    /*unsupported message.*/
    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x unexpected message ID:0x%x\r\n", _this->p_dpu->tag, p_msg->msg_id));

    res = SYS_DPT1_UNKOWN_MSG;
  }

  return res;
}

static sys_error_code_t DPT1ProcessMsgProcessActive(DProcessTask1_t *_this, AppMsg_t *p_msg)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  switch (p_msg->msg_id)
  {
    case APP_REPORT_ID_FORCE_STEP:
      __NOP();
      break;

    case DPU_MESSAGE_ID_CMD:
      switch (p_msg->dpu_msg_cmd.cmd_id)
      {
        case DPT1_CMD_SUSPEND_DPU:
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPT1_CMD_SUSPEND_DPU\r\n", _this->p_dpu->tag));

          (void)ADPU2_Suspend(_this->p_dpu);
          break;

        case DPT1_CMD_RESUME_DPU:
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPT1_CMD_RESUME_DPU\r\n", _this->p_dpu->tag));

          (void)ADPU2_Resume(_this->p_dpu);
          break;

        case DPT1_CMD_RESET_DPU:
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x DPT1_CMD_RESET_DPU\r\n", _this->p_dpu->tag));

          res = ADPU2_Reset(_this->p_dpu);
         break;

        case DPT1_CMD_NEW_IN_DATA_READY:
          SYS_DEBUGF(SYS_DBG_LEVEL_ALL, ("DPT1:%x DPT1_CMD_NEW_DATA_READY\r\n", _this->p_dpu->tag));

          res = ADPU2_ProcessAndDispatch(_this->p_dpu);
          break;

        default:
          /*unsupported command.*/
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x unexpected command ID:0x%x\r\n", _this->p_dpu->tag, p_msg->dpu_msg_cmd.cmd_id));

          res = SYS_DPT1_UNKOWN_MSG;
          break;
      }
      break;

    default:
    /*unsupported message.*/
    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x unexpected message ID:0x%x\r\n", _this->p_dpu->tag, p_msg->msg_id));

    res = SYS_DPT1_UNKOWN_MSG;
  }

  return res;
}

static void DPT1DPUCallback(IDPU2_t *_this, void* p_param)
{
  DProcessTask1_t *p_obj = (DProcessTask1_t*)p_param;

  if (SYS_NO_ERROR_CODE != DPT1OnNewInDataReady(p_obj))
  {
    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DPT1:%x queue full on new data ready.\r\n", p_obj->p_dpu->tag));

    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_DPT1_IN_QUEUE_FULL_ERROR_CODE);
  }
}
