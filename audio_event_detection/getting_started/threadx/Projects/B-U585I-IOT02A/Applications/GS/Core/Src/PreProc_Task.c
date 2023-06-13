/**
  ******************************************************************************
  * @file    PreProc_Task.c
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


#include "PreProc_Task.h"
#include "PreProc_Task_vtbl.h"
#include "app_messages_parser.h"
#include "services/sysdebug.h"
#include "services/sysmem.h"


#ifndef PRE_PROC_TASK_CFG_STACK_DEPTH
#define PRE_PROC_TASK_CFG_STACK_DEPTH         (TX_MINIMUM_STACK)
#endif

#ifndef PRE_PROC_TASK_CFG_PRIORITY
#define PRE_PROC_TASK_CFG_PRIORITY            (TX_MAX_PRIORITIES-2)
#endif

#ifndef PRE_PROC_TASK_CFG_IN_QUEUE_LENGTH
#define PRE_PROC_TASK_CFG_IN_QUEUE_LENGTH     (10)
#endif
#define PRE_PROC_TASK_CFG_IN_QUEUE_ITEM_SIZE  (sizeof(struct DPU_MSG_Attach_t))  /*!< size of the biggest message managed by the task. */
#define PRE_PROC_TASK_CFG_IN_QUEUE_SIZE       (PRE_PROC_TASK_CFG_IN_QUEUE_ITEM_SIZE*PRE_PROC_TASK_CFG_IN_QUEUE_LENGTH)

#define PRE_PROC_TASK_DPU_TAG                 (0x35U)

#define SYS_DEBUGF(level, message)        SYS_DEBUGF3(SYS_DBG_PRE_PROC, level, message)

/**
 * Class object declaration. The class object encapsulates members that are shared between
 * all instance of the class.
 */
typedef struct _PreProc_TaskClass_t {
  /**
   * PreProc_Task class virtual table.
   */
  AManagedTaskEx_vtbl vtbl;

  /**
   * PreProc_Task class (PM_STATE, ExecuteStepFunc) map. The map is implemented with an array and
   * the key is the index. Number of items of this array must be equal to the number of PM state
   * of the application. If the managed task does nothing in a PM state, then set to NULL the
   * relative entry in the map.
   */
  pExecuteStepFunc_t p_pm_state2func_map[];
} PreProc_TaskClass_t;


/* Private member function declaration */
/***************************************/

/**
 * Execute one step of the task control loop while the system is in STATE1.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t PreProc_TaskExecuteStepState1(AManagedTask *_this);

/**
 * Execute one step of the task control loop while the system is in X_CUBE_AI_ACTIVE.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t PreProc_TaskExecuteStepAIActive(AManagedTask *_this);

/**
 * Disconnect a sensor to the task as data source. Data are collected to form a signal of n axes and signal_size number of sample per axis,
 * and stored in a circular buffer of cb_items signals.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param p_sensor [IN] specifies a pointer to a sensor.
 * @return SYS_NO_ERROR_CODE if success, and error code otherwise.
 */
//static sys_error_code_t PreProc_TaskDetachFromSensor(PreProc_Task_t *_this, ISourceObservable *p_sensor);


/**
 * The class object.
 */
static const PreProc_TaskClass_t sTheClass = {
    /* Class virtual table */
    {
        DProcessTask1_vtblHardwareInit,
        PreProc_Task_vtblOnCreateTask,
        PreProc_Task_vtblDoEnterPowerMode,
        DProcessTask1_vtblHandleError,
        DProcessTask1_vtblOnEnterTaskControlLoop,
        DProcessTask1_vtblForceExecuteStep,
        DProcessTask1_vtblOnEnterPowerMode
    },

    /* class (PM_STATE, ExecuteStepFunc) map */
    {
        PreProc_TaskExecuteStepState1,
        NULL,
        PreProc_TaskExecuteStepAIActive
    }
};


/* Public API definition */
/*************************/

AManagedTaskEx *PreProc_TaskAlloc(void)
{
  AManagedTaskEx *p_root = (AManagedTaskEx*)SysAlloc(sizeof(PreProc_Task_t));

  /* Initialize the super class */
  AMTInitEx(p_root);

  p_root->vptr = &sTheClass.vtbl;

  return p_root;
}

AManagedTaskEx *PreProc_TaskStaticAlloc(void *p_mem_block)
{
  PreProc_Task_t *p_obj = (PreProc_Task_t*)p_mem_block;

  if (p_obj != NULL)
  {
    /* Initialize the super class */
    AMTInitEx(&p_obj->super.super);

    p_obj->super.super.vptr = &sTheClass.vtbl;
  }

  return (AManagedTaskEx*)p_obj;
}

sys_error_code_t PreProc_TaskSetDpuInBuffer(PreProc_Task_t *_this, uint16_t input_signals_count)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;


  struct genericMsg_t msg = {
      .msg_id = APP_MESSAGE_ID_PRE_PROC,
      .cmd_id = PREPROC_CMD_SET_IN_BUFF,
      .param = input_signals_count
  };

  res = DPT1PostMessageToBack((DProcessTask1_t*)_this, (AppMsg_t*)&msg);

  return res;
}

sys_error_code_t PreProc_TaskSetSpectrogramType(PreProc_Task_t *_this, spectrogram_type_t type)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;


  struct genericMsg_t msg = {
      .msg_id = APP_MESSAGE_ID_PRE_PROC,
      .cmd_id = PREPROC_CMD_SET_SPECTROGRAM_TYPE,
      .param = (uint32_t)type
  };

  res = DPT1PostMessageToBack((DProcessTask1_t*)_this, (AppMsg_t*)&msg);

  return res;
}

/* AManagedTask virtual functions definition */
/*********************************************/

sys_error_code_t PreProc_Task_vtblOnCreateTask(AManagedTask *_this,
    tx_entry_function_t *pTaskCode, CHAR **pName, VOID **pStackStart,
    ULONG *pStackDepth, UINT *pPriority, UINT *pPreemptThreshold,
    ULONG *pTimeSlice, ULONG *pAutoStart, ULONG *pParams)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  PreProc_Task_t *p_obj = (PreProc_Task_t*)_this;

  _this->m_pfPMState2FuncMap = sTheClass.p_pm_state2func_map;

  *pTaskCode = AMTExRun;
  *pName = "PRE_PROC";
  *pStackStart = NULL; // allocate the task stack in the system memory pool.
  *pStackDepth = PRE_PROC_TASK_CFG_STACK_DEPTH;
  *pParams = (ULONG)_this;
  *pPriority = PRE_PROC_TASK_CFG_PRIORITY;
  *pPreemptThreshold = PRE_PROC_TASK_CFG_PRIORITY;
  *pTimeSlice = TX_NO_TIME_SLICE;
  *pAutoStart = TX_AUTO_START;

  /* Change the CLASS for the power mode switch because I want to do the
   * transaction after all sensors task. */
  AMTExSetPMClass((AManagedTaskEx*)_this, E_PM_CLASS_1);

  /* initialize the object software resource here. */
  VOID *pvQueueItemsBuff = SysAlloc(PRE_PROC_TASK_CFG_IN_QUEUE_SIZE);
  if (pvQueueItemsBuff == NULL)
  {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }
  if (TX_SUCCESS != tx_queue_create(&p_obj->super.in_queue, "PRE_PROC_Q",
      PRE_PROC_TASK_CFG_IN_QUEUE_ITEM_SIZE/4U , pvQueueItemsBuff,
      PRE_PROC_TASK_CFG_IN_QUEUE_SIZE))
  {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }
  /* Initialize DPU */
  (void) PreProc_DPUStaticAlloc(&p_obj->dpu);
  (void) PreProc_DPUInit(&p_obj->dpu,CTRL_X_CUBE_AI_SPECTROGRAM_PATCH_LENGTH);
  (void) ADPU2_SetTag((ADPU2_t*)&p_obj->dpu, PRE_PROC_TASK_DPU_TAG);
  assert_param(sizeof(p_obj->dpu_out_buff) == ADPU2_GetOutDataPayloadSize((ADPU2_t*)&p_obj->dpu));
  res = ADPU2_SetOutDataBuffer((ADPU2_t*)&p_obj->dpu, (uint8_t*)p_obj->dpu_out_buff, sizeof(p_obj->dpu_out_buff));
  /*register the DPU with the base class*/
  (void) DPT1AddDPU((DProcessTask1_t*)p_obj, (ADPU2_t*)&p_obj->dpu);
  (void) DPT1EnableAsyncDataProcessing((DProcessTask1_t*)p_obj, true);
  /* Initialize the base class */
  p_obj->super.p_dpu_out_buff = p_obj->dpu_out_buff;
  p_obj->super.p_dpu_in_buff = NULL;


  return res;
}

sys_error_code_t PreProc_Task_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{

  assert_param(_this != NULL);

  sys_error_code_t res = SYS_NO_ERROR_CODE;
  PreProc_Task_t *p_obj = (PreProc_Task_t*)_this;

  struct genericMsg_t msg = {
      .msg_id = APP_MESSAGE_ID_PRE_PROC
  };

  if (new_power_mode == E_POWER_MODE_STATE1)
  {
    if (active_power_mode == E_POWER_MODE_SENSORS_ACTIVE)
    {
      msg.cmd_id = PREPROC_CMD_STOP_PROCESSING;
      if (TX_SUCCESS != tx_queue_send(&p_obj->super.in_queue, &msg,AMT_MS_TO_TICKS(100)))
      {
        res = SYS_PREPROC_TASK_IN_QUEUE_FULL_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_PREPROC_TASK_IN_QUEUE_FULL_ERROR_CODE);
      }
    }
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PRE_PROC: -> %d \r\n", (uint32_t)new_power_mode));

  return res;
}


/* AManagedTaskEx virtual functions definition */
/***********************************************/


/* Private function definition */
/*******************************/

static sys_error_code_t PreProc_TaskExecuteStepState1(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  PreProc_Task_t *p_obj = (PreProc_Task_t*)_this;
  AppMsg_t msg = {0};

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (TX_SUCCESS == tx_queue_receive(&p_obj->super.in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    if (msg.msg_id == APP_MESSAGE_ID_PRE_PROC)
    {
      switch (msg.generic_msg.cmd_id)
      {
        case PREPROC_CMD_STOP_PROCESSING:
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PREPROC: PREPROC_CMD_STOP_PROCESSING\r\n"));
          PreProc_DPUPrepareToProcessData(&p_obj->dpu);
          break;

        case PREPROC_CMD_SET_IN_BUFF:
        {
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PREPROC: PREPROC_CMD_SET_IN_BUFF\r\n"));
          size_t buff_size = ADPU2_GetInDataPayloadSize((ADPU2_t*)&p_obj->dpu) * msg.generic_msg.param;
          if (buff_size > 0)
          {
            p_obj->super.p_dpu_in_buff = SysAlloc(buff_size);
            if (p_obj->super.p_dpu_in_buff == NULL)
            {
              res = SYS_OUT_OF_MEMORY_ERROR_CODE;
            }
            else
            {
              SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PREPROC: input dpu buffer = %d bytes\r\n", buff_size));
              res = ADPU2_SetInDataBuffer((ADPU2_t*)&p_obj->dpu, p_obj->super.p_dpu_in_buff, buff_size);
            }
          }
          else
          {
            /* buff_size == 0 then release the resources*/
            res = ADPU2_SetInDataBuffer((ADPU2_t*)&p_obj->dpu, p_obj->super.p_dpu_in_buff, buff_size);
            if (p_obj->super.p_dpu_in_buff != NULL)
            {
              SysFree(p_obj->super.p_dpu_in_buff);
            }
          }
        }
        break;
        case PREPROC_CMD_SET_SPECTROGRAM_TYPE:
          p_obj->dpu.type = (spectrogram_type_t) msg.generic_msg.param ;
          break;

        default:
          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PRE_PROC: unexpected command ID:0x%x\r\n", msg.generic_msg.cmd_id));
          break;
      }
    }
    else {
      res = DPT1ProcessMsg((DProcessTask1_t*)p_obj, &msg);
      if(res == SYS_DPT1_UNKOWN_MSG)
      {
        /*unsupported message.*/
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PRE_PROC: unexpected message ID:0x%x\r\n", msg.msg_id));
      }
    }
  }

  return res;
}

static sys_error_code_t PreProc_TaskExecuteStepAIActive(AManagedTask *_this)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  PreProc_Task_t *p_obj = (PreProc_Task_t*)_this;
  AppMsg_t msg = {0};

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (TX_SUCCESS == tx_queue_receive(&p_obj->super.in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    res = DPT1ProcessMsg((DProcessTask1_t*)p_obj, &msg);
    if(res == SYS_DPT1_UNKOWN_MSG)
    {
      /*unsupported message.*/
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("PRE_PROC: unexpected message ID:0x%x\r\n", msg.msg_id));
    }
  }

  return res;
}

