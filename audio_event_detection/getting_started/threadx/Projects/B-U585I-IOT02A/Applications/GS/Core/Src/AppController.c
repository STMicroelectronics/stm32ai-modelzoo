/**
 ******************************************************************************
 * @file    AppController.c
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

#include "AppController.h"
#include "AppController_vtbl.h"
#include "AppControllerMessagesDef.h"
#include "app_messages_parser.h"
#include "services/SQuery.h"
#include "services/sysdebug.h"
#include "services/syserror.h"
#include "services/sysmem.h"
#include "services/SysTimestamp.h"

#include "DefDataBuilder.h"
#include "DefDataBuilder_vtbl.h"
#include "Int16toFloatDataBuilder.h"
#include "Int16toFloatDataBuilder_vtbl.h"

#include "tx_execution_profile.h"
#include "config.h"

#ifndef CTRL_TASK_CFG_IN_QUEUE_LENGTH
#define CTRL_TASK_CFG_IN_QUEUE_LENGTH         (20U)
#endif

#define CTRL_TASK_CFG_IN_QUEUE_ITEM_SIZE      (sizeof(struct CtrlMessage_t))
#define CTRL_TASK_CFG_IN_QUEUE_SIZE           (CTRL_TASK_CFG_IN_QUEUE_LENGTH)*(CTRL_TASK_CFG_IN_QUEUE_ITEM_SIZE)

#define CTRL_TASK_CFG_OUT_CH                  stdout

#define CTRL_AI_CB_ITEMS                      (2U)
#define CTRL_PRE_PROC_CB_ITEMS                (2U)

#define SYS_DEBUGF(level, message)            SYS_DEBUGF3(SYS_DBG_CTRL, level, message)

#if defined(DEBUG) || defined (SYS_DEBUG)
#define sTaskObj                              sAppCTRLTaskObj
#endif

#if (CTRL_X_CUBE_AI_SENSOR_TYPE != COM_TYPE_ACC && CTRL_X_CUBE_AI_SENSOR_TYPE != COM_TYPE_MIC)
#error only accelerometer or microphone type is supoported
#endif

#if (CTRL_AI_HW_SELECT != B_U585I_IOT02A)
#error only B-U585I-IOT02A board is supported
#endif


/**
 * Class object declaration. The class object encapsulates members that are shared between
 * all instance of the class.
 */
typedef struct _AppControllerClass_t {
  /**
   * AppController class virtual table.
   */
  AManagedTaskEx_vtbl vtbl;

  /**
   * Data event listener virtual table
   */
  IDataEventListener_vtbl data_evt_listener_vtbl;

  /**
   * AppController class (PM_STATE, ExecuteStepFunc) map. The map is implemented with an array and
   * the key is the index. Number of items of this array must be equal to the number of PM state
   * of the application. If the managed task does nothing in a PM state, then set to NULL the
   * relative entry in the map.
   */
  pExecuteStepFunc_t p_pm_state2func_map[];

} AppControllerClass_t;


/* Private member function declaration */
/***************************************/

/**
 * Execute one step of the task control loop while the system is in STATE1.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t AppControllerExecuteStepState1(AManagedTask *_this);

/**
 * Execute one step of the task control loop while the system is in AI_ACTIVE.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t AppControllerExecuteStepAIActive(AManagedTask *_this);

/**
 * Start an execution phase. Processing this command will trigger an PM transaction.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param exec_phase [IN] specifies an execution phase. Valid value are:
 *   - CTRL_CMD_PARAM_AI
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static sys_error_code_t AppControllerStartExecutionPhase(AppController_t *_this, uint32_t exec_phase);

/**
 * Detach the sensor from the active AI.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param active_ai_proc [IN] specifies the active AI proces
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static sys_error_code_t AppControllerDetachSensorFromAIProc(AppController_t *_this, uint32_t active_ai_proc);


/**
 * print AI inference results.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return none.
 */
static void AppControllerPrintAIRes(uint32_t cnt, float *p_out);

/**
 * print real time statistics.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return none.
 */
static void AppControllerPrintStats(AManagedTask *_this);

/**
 * check if silence is detected .
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return 0 if silence.
 */
static int AppControllerIsNotSilence(AppController_t *p_obj);

/**
 * The only instance of the task object.
 */
static AppController_t sTaskObj;

/**
 * The class object.
 */
static const AppControllerClass_t sTheClass = {
    /* Class virtual table */
    {
        AppController_vtblHardwareInit,
        AppController_vtblOnCreateTask,
        AppController_vtblDoEnterPowerMode,
        AppController_vtblHandleError,
        AppController_vtblOnEnterTaskControlLoop,
        AppController_vtblForceExecuteStep,
        AppController_vtblOnEnterPowerMode
    },
    /* IDataEventListener_t virtual table*/
    {
        AppController_vtblOnStatusChange,
        AppController_vtblSetOwner,
        AppController_vtblGetOwner,
        AppController_vtblOnNewDataReady
    },
    /* class (PM_STATE, ExecuteStepFunc) map */
    {
        AppControllerExecuteStepState1,
        NULL,
        NULL,
        AppControllerExecuteStepAIActive,
    }
};

/**
 * Specifies the labels for the classes of the HAR demo.
 */
static const char* sAiClassLabels[CTRL_X_CUBE_AI_MODE_CLASS_NUMBER] = CTRL_X_CUBE_AI_MODE_CLASS_LIST;

/**
 * Specifies the sequence of execution phases
 */
static uint32_t sCtrl_sequence []= CTRL_SEQUENCE ;


/* Public API definition */
/*************************/

AManagedTaskEx *AppControllerAlloc(void)
{
  /* Initialize the super class */
  AMTInitEx(&sTaskObj.super);

  sTaskObj.super.vptr = &sTheClass.vtbl;
  sTaskObj.listener_if.vptr = &sTheClass.data_evt_listener_vtbl;

  return (AManagedTaskEx*)&sTaskObj;

}

sys_error_code_t AppControllerConnectAppTasks(AppController_t *_this, AI_Task_t *p_ai_task, PreProc_Task_t *p_preproc_task)
{
  assert_param(_this != NULL);
  _this->p_ai_task   = p_ai_task;
  _this->p_preproc_task = p_preproc_task;

  return SYS_NO_ERROR_CODE;
}

sys_error_code_t AppControllerSetAISensor(AppController_t *_this, uint8_t sensor_id )
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  if (sensor_id >= SMGetNsensor())
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
  }
  else
  {
    _this->p_ai_sensor_obs  =  SMGetSensorObserver(sensor_id);
  }
  return res;
}

/* AManagedTask virtual functions definition */
/*********************************************/

sys_error_code_t AppController_vtblHardwareInit(AManagedTask *_this, void *p_params)
{
  assert_param(_this != NULL);
  return SYS_NO_ERROR_CODE;
}

sys_error_code_t AppController_vtblOnCreateTask (AManagedTask *_this, tx_entry_function_t *pTaskCode, CHAR **pName,
    VOID **pStackStart, ULONG *pStackDepth,
    UINT *pPriority, UINT *pPreemptThreshold,
    ULONG *pTimeSlice, ULONG *pAutoStart,
    ULONG *pParams)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;

  p_obj->seq_index              = 0;
  p_obj->signal_count           = 0;
  p_obj->signals                = 0;
  p_obj->sequence               = sCtrl_sequence;
  p_obj->p_ai_task              = NULL;
  p_obj->p_listener_if_owner    = NULL;
  p_obj->p_ai_sensor_obs        = NULL;
  p_obj->pre_proc_type          = CTRL_X_CUBE_AI_PREPROC;
  p_obj->sensor_type            = CTRL_X_CUBE_AI_SENSOR_TYPE;
  p_obj->ai_task_time_init      = 0.0F;
  p_obj->preproc_task_time_init = 0.0F;

  _this->m_pfPMState2FuncMap = sTheClass.p_pm_state2func_map;

  *pTaskCode = AMTExRun;
  *pName = "CTRL";
  *pStackStart = NULL; // allocate the task stack in the system memory pool.
  *pStackDepth = CTRL_TASK_CFG_STACK_DEPTH;
  *pParams = (ULONG)_this;
  *pPriority = CTRL_TASK_CFG_PRIORITY;
  *pPreemptThreshold = CTRL_TASK_CFG_PRIORITY;
  *pTimeSlice = TX_NO_TIME_SLICE;
  *pAutoStart = TX_AUTO_START;

  /* initialize the object software resource here. */
  VOID *pvQueueItemsBuff = SysAlloc(CTRL_TASK_CFG_IN_QUEUE_SIZE);
  if (pvQueueItemsBuff == NULL)
  {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }
  if (TX_SUCCESS != tx_queue_create(&p_obj->in_queue, "CTRL_Q",
      CTRL_TASK_CFG_IN_QUEUE_ITEM_SIZE/sizeof(uint32_t) , pvQueueItemsBuff,
      CTRL_TASK_CFG_IN_QUEUE_SIZE))
  {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }

  return res;
}

sys_error_code_t AppController_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;

  if (new_power_mode == E_POWER_MODE_STATE1)
  {
    struct CtrlMessage_t msg = {
        .msg_id = APP_MESSAGE_ID_CTRL,
        .cmd_id = CTRL_CMD_DID_STOP,
        .param = (uint32_t) active_power_mode
    };

    if (TX_SUCCESS != tx_queue_send(&p_obj->in_queue, &msg,AMT_MS_TO_TICKS(150)))
    {
      res = SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE);
    }
  }
  return res;
}

sys_error_code_t AppController_vtblHandleError(AManagedTask *_this, SysEvent error)
{
  assert_param(_this != NULL);
  return SYS_NO_ERROR_CODE;
}


/* AManagedTaskEx virtual functions definition */
/***********************************************/
sys_error_code_t AppController_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode active_power_mode)
{
  assert_param(_this != NULL);
  AppController_t *p_obj = (AppController_t*)_this;
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  struct CtrlMessage_t msg = {
      .msg_id = APP_REPORT_ID_FORCE_STEP
  };

  if (TX_SUCCESS != tx_queue_front_send(&p_obj->in_queue, &msg,AMT_MS_TO_TICKS(100)))
  {
    res = SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE);
  }

  return res;
}

sys_error_code_t AppController_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  if (new_power_mode ==  E_POWER_MODE_X_CUBE_AI_ACTIVE)
  {
    SysTsStart(SysGetTimestampSrv(), true);
  }
  else if (new_power_mode == E_POWER_MODE_STATE1)
  {
    SysTsStop(SysGetTimestampSrv());
  }
  return SYS_NO_ERROR_CODE;
}

/* IListener virtual functions definition */
/******************************************/

sys_error_code_t AppController_vtblOnStatusChange(IListener *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("CTL: Status changed.\r\n"));

  return res;
}

/* IEventListener virtual functions definition */
/***********************************************/

void AppController_vtblSetOwner(IEventListener *_this, void *p_owner)
{
  assert_param(_this != NULL);
  assert_param(p_owner != NULL);
  AppController_t *p_if_owner = (AppController_t*) (((size_t)_this) - offsetof(AppController_t, listener_if));
  p_if_owner->p_listener_if_owner = p_owner;
}

void *AppController_vtblGetOwner(IEventListener *_this)
{
  assert_param(_this != NULL);
  AppController_t *p_if_owner = (AppController_t*) (((size_t)_this) - offsetof(AppController_t, listener_if));
  return p_if_owner->p_listener_if_owner;
}

/* IDataEventListener virtual functions definition */
/***********************************************/

sys_error_code_t AppController_vtblOnNewDataReady(IEventListener *_this, const DataEvent_t *p_evt)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_if_owner = (AppController_t*) (((size_t)_this) - offsetof(AppController_t, listener_if));
  AppMsg_t msg;

  msg.msg_id = APP_MESSAGE_ID_CTRL;

  if(p_evt->tag == AI_TASK_DPU_TAG)
  {
    /* this result come from X-CUBE-AI process. We know the format of the data */
    float *proc_res = (float*) EMD_Data(p_evt->p_data);
    msg.ctrl_msg.cmd_id = CTRL_CMD_AI_PROC_RES;
    msg.ctrl_msg.param = (uint32_t)(proc_res);
  }
  else
  {
    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("CTRL: unexpected TAG ID:0x%x\r\n", p_evt->tag));
    return SYS_INVALID_PARAMETER_ERROR_CODE;
  }

  if (TX_SUCCESS != tx_queue_send(&p_if_owner->in_queue, &msg, AMT_MS_TO_TICKS(100)))
  {
    res = SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE);
  }
  return res;
}


/* Private function definition */
/*******************************/

static sys_error_code_t AppControllerExecuteSequence(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;
  char     *mode_name, *sensor_name;
  uint8_t  sensor_type;
  float    odr,fs;
  uint32_t nb_signals;

  /* First disable all sensors*/
  SIterator_t iterator;
  uint16_t sensor_id = SI_NULL_SENSOR_ID;

  SIInit(&iterator, SMGetSensorManager());
  while (SIHasNext(&iterator))
  {
    sensor_id = SINext(&iterator);
    SMSensorDisable(sensor_id);
  }

  int32_t mode = p_obj->sequence[p_obj->seq_index];

  /* set sensor type */
  p_obj->p_ai_task->dpu.sensor_type = p_obj->sensor_type;

  switch (mode)
  {
  case CTRL_CMD_PARAM_AI:
    mode_name   = CTRL_X_CUBE_AI_MODE_NAME;
    sensor_name = CTRL_X_CUBE_AI_SENSOR_NAME;
    sensor_type = CTRL_X_CUBE_AI_SENSOR_TYPE;
    odr         = CTRL_X_CUBE_AI_SENSOR_ODR;
    fs          = CTRL_X_CUBE_AI_SENSOR_FS;
    nb_signals  = CTRL_X_CUBE_AI_NB_SAMPLES;
    break;
  default:
    return SYS_UNDEFINED_ERROR_CODE;
  }

  p_obj->seq_index++;
  SQuery_t query;
  SQInit(&query, SMGetSensorManager());
  sensor_id = SQNextByNameAndType(&query, sensor_name ,  sensor_type);
  if (sensor_id != SI_NULL_SENSOR_ID)
  {
    SMSensorEnable(sensor_id);
    p_obj->signals = nb_signals;
    fprintf(CTRL_TASK_CFG_OUT_CH, "\r\n------------------------------------------------------\r\n\r\n");
    fprintf(CTRL_TASK_CFG_OUT_CH, "Setting up configuration for %s.\r\n\r\n", mode_name);
    SMSensorSetODR(sensor_id, odr);
    SMSensorSetFS(sensor_id, fs);
    switch (mode)
    {
    case CTRL_CMD_PARAM_AI:
      AppControllerSetAISensor(p_obj,sensor_id); // sensor has just been enabled
      AI_LoadModel(p_obj->p_ai_task,CTRL_X_CUBE_AI_MODE_NETWORK_MODEL_NAME);
      /* propagate Q params ,to improve */
      p_obj->p_preproc_task->dpu.output_Q_offset    = p_obj->p_ai_task->dpu.input_Q_offset;
      p_obj->p_preproc_task->dpu.output_Q_inv_scale = p_obj->p_ai_task->dpu.input_Q_inv_scale;
      break;
    default:
      return SYS_INVALID_PARAMETER_ERROR_CODE;
    }
    fprintf(CTRL_TASK_CFG_OUT_CH, "\r\nSensor Informations...\r\n");
    fprintf(CTRL_TASK_CFG_OUT_CH, " Sensor     : %s\r\n", sensor_name);
    fprintf(CTRL_TASK_CFG_OUT_CH, " ODR        : %.1f\r\n", odr);
    fprintf(CTRL_TASK_CFG_OUT_CH, " FS         : %.1f\r\n", fs);
    fprintf(CTRL_TASK_CFG_OUT_CH, " Nb signals : %ld\r\n", nb_signals);
    fprintf(CTRL_TASK_CFG_OUT_CH, "\r\nStart execution phase...\r\n");
    AppControllerStartExecutionPhase((AppController_t*)_this, mode);
  }
  else
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_CTRL_WRONG_CONF_ERROR_CODE);
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("CTRL: %s not found.\r\n"));
  }
  return res;
}

sys_error_code_t AppController_vtblOnEnterTaskControlLoop(AManagedTask *_this)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("CTRL: start.\r\n"));
  res = DPT1AddDPUListener((DProcessTask1_t*)p_obj->p_ai_task, &p_obj->listener_if);
  res = AppControllerExecuteSequence(_this);
  return res;
}

static sys_error_code_t AppControllerExecuteStepState1(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;
  struct CtrlMessage_t msg = {0};

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);

  if (TX_SUCCESS == tx_queue_receive(&p_obj->in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    if (msg.msg_id == APP_MESSAGE_ID_CTRL)
    {
      switch (msg.cmd_id)
      {
      case CTRL_CMD_DID_STOP:
      {
        AI_ReleaseModel(p_obj->p_ai_task);
        res = AppControllerDetachSensorFromAIProc(p_obj, msg.param);
        fprintf(CTRL_TASK_CFG_OUT_CH, "}\r\n");
        AppControllerPrintStats(_this);
        fprintf(CTRL_TASK_CFG_OUT_CH, "\r\n...End of execution phase\r\n");

        /* check & start next execution phase */
        res = AppControllerExecuteSequence(_this);
      }
      break;

      case CTRL_RX_CAR :
        break;

      default:
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("CTRL: unexpected command ID:0x%x\r\n", msg.cmd_id));
        break;
      }
    }
    else if (msg.msg_id == APP_REPORT_ID_FORCE_STEP)
    {
      __NOP();
    }
  }
  return res;
}

static sys_error_code_t AppControllerExecuteStepAIActive(AManagedTask *_this)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;
  struct CtrlMessage_t msg = {0};

  UART_Start_Receive_IT(&huart1, &p_obj->in_caracter, 1);

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (TX_SUCCESS == tx_queue_receive(&p_obj->in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    if (msg.msg_id == APP_MESSAGE_ID_CTRL)
    {
      switch (msg.cmd_id)
      {
      case CTRL_RX_CAR :
      {
        /* generate the system event.*/
        SysEvent evt = {
            .nRawEvent = SYS_PM_MAKE_EVENT(SYS_PM_EVT_SRC_CTRL, SYS_PM_EVENT_PARAM_STOP_PROCESSING)
        };
        SysPostPowerModeEvent(evt);
      }
      break;

      case CTRL_CMD_AI_PROC_RES:
      {
        /* I am going to consume the data. Increase the signal_count. */
        ++p_obj->signal_count;
        float * p_ai_out = (float *) msg.param;
        if (AppControllerIsNotSilence(p_obj))
        {
          AppControllerPrintAIRes(p_obj->signal_count, p_ai_out);
        }
        if ((p_obj->signals != 0) && !(p_obj->signal_count < p_obj->signals))
        {
          /* generate the system event.*/
          SysEvent evt = {
              .nRawEvent = SYS_PM_MAKE_EVENT(SYS_PM_EVT_SRC_CTRL, SYS_PM_EVENT_PARAM_STOP_PROCESSING)
          };
          SysPostPowerModeEvent(evt);
        }
        break;
      }
      default:
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("CTRL: unexpected command ID:0x%x\r\n", msg.cmd_id));
        break;
      }
    }
    else if (msg.msg_id == APP_REPORT_ID_FORCE_STEP)
    {
      __NOP();
    }
  }
  return res;
}

static sys_error_code_t AppControllerStartExecutionPhase(AppController_t *_this, uint32_t exec_phase)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  _this->signal_count = 0;

  if (exec_phase == CTRL_CMD_PARAM_AI)
  {
    /*prepare to connect the DPU to the data source.*/
    IDataBuilder_t *p_data_builder;
    switch (_this->pre_proc_type){
    case CTRL_AI_GRAV_ROT_SUPPR:
    case CTRL_AI_GRAV_ROT:
    case CTRL_AI_PREPROC:
    case CTRL_AI_SCALING:
    case CTRL_AI_BYPASS:
      p_data_builder = Int16ToFloatDB_Alloc();
      if (p_data_builder == NULL)
      {
        /*SYS_OUT_OF_MEMORY_ERROR_CODE. Block the execution to notify the error.*/
        sys_error_handler();
      }
      if (!SYS_IS_ERROR_CODE(DPT1AttachToDataSource((DProcessTask1_t*)_this->p_ai_task, _this->p_ai_sensor_obs, p_data_builder, E_IDB_NO_DATA_LOSS)))
      {
        /*allocate the DPU buffer in term of number of input signals */
        res = AI_TaskAllocBufferForDPU(_this->p_ai_task, CTRL_AI_CB_ITEMS);
      }
      break;
    case CTRL_AI_SPECTROGRAM_MEL:
    case CTRL_AI_SPECTROGRAM_LOG_MEL:
    case CTRL_AI_SPECTROGRAM_MFCC:
      //        p_data_builder = Int16ToFloatDB_Alloc();
      p_data_builder = DefDB_Alloc();
      if (p_data_builder == NULL)
      {
        /*SYS_OUT_OF_MEMORY_ERROR_CODE. Block the execution to notify the error.*/
        sys_error_handler();
      }
      if (!SYS_IS_ERROR_CODE(DPT1AttachToDataSource((DProcessTask1_t*)_this->p_preproc_task, _this->p_ai_sensor_obs, p_data_builder, E_IDB_NO_DATA_LOSS)))
      {
        /*allocate the input buffer for the Preproc DPU*/
        (void)PreProc_TaskSetDpuInBuffer(_this->p_preproc_task, CTRL_PRE_PROC_CB_ITEMS);
        /*set processing type */
        spectrogram_type_t processing_type;
        switch (_this->pre_proc_type){
        case CTRL_AI_SPECTROGRAM_MEL:
          processing_type = SPECTROGRAM_MEL;
          break;
        case CTRL_AI_SPECTROGRAM_LOG_MEL:
          processing_type = SPECTROGRAM_LOG_MEL;
          break;
        case CTRL_AI_SPECTROGRAM_MFCC:
          processing_type = SPECTROGRAM_MFCC;
          break;
        default:
          processing_type = SPECTROGRAM_BYPASS;
          break;
        }
        (void)PreProc_TaskSetSpectrogramType(_this->p_preproc_task,processing_type);
      }
      p_data_builder = DefDB_Alloc();
      if (p_data_builder == NULL)
      {
        /*SYS_OUT_OF_MEMORY_ERROR_CODE. Block the execution to notify the error.*/
        sys_error_handler();
      }
      if (!SYS_IS_ERROR_CODE(DPT1AttachToDPU((DProcessTask1_t*)_this->p_preproc_task, (IDPU2_t*)DPT1GetDPU((DProcessTask1_t*)_this->p_ai_task), p_data_builder, E_IDB_NO_DATA_LOSS/* E_IDB_SKIP_DATA*/)))
      {
        /*allocate the DPU buffer in term of number of input signals */
        res = AI_TaskAllocBufferForDPU(_this->p_ai_task, CTRL_AI_CB_ITEMS);
      }
      break;
    }
    /* trigger the power mode transaction */
    SysEvent evt = {
        .nRawEvent = SYS_PM_MAKE_EVENT(SYS_PM_EVT_SRC_CTRL, SYS_PM_EVENT_PARAM_START_ML)
    };
    SysPostPowerModeEvent(evt);
  }
  return res;
}

static sys_error_code_t AppControllerDetachSensorFromAIProc(AppController_t *_this, uint32_t active_power_mode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /*free the data buffer for the AI_DPU*/
  AI_TaskAllocBufferForDPU(_this->p_ai_task, 0U);

  if (active_power_mode == E_POWER_MODE_X_CUBE_AI_ACTIVE || \
      active_power_mode == CTRL_AI_SPECTROGRAM_LOG_MEL   || \
      active_power_mode == CTRL_AI_SPECTROGRAM_MFCC)
  {
    /*free the input buffer for the preproc DPU*/
    PreProc_TaskSetDpuInBuffer(_this->p_preproc_task, 0U);
    /*detach the preproc Dpu from the data source*/
    res = DPT1DetachFromDataSource((DProcessTask1_t*)_this->p_preproc_task, _this->p_ai_sensor_obs, true);
    /*detach the preproc Dpu from the AI DPU*/
    res = DPT1DetachFromDPU((DProcessTask1_t*)_this->p_preproc_task, true);
  }
  else
  {
    /*detach the AI_HAR_DPU from the data source*/
    res = DPT1DetachFromDataSource((DProcessTask1_t*)_this->p_ai_task, _this->p_ai_sensor_obs, true);
  }

#if defined(SYS_DEBUG)
  SysDebugLogFreeHeapSize();
#endif

  return res;
}

IEventListener* AppController_getEventListenerIF(AppController_t *_this)
{
  // Get the Event Listener
  assert_param(_this != NULL);
  return (IEventListener*)&_this->listener_if;
}

static int AppControllerIsNotSilence(AppController_t *p_obj)
{
#if (CTRL_X_CUBE_AI_PREPROC==CTRL_AI_SPECTROGRAM_LOG_MEL &&  CTRL_X_CUBE_AI_SPECTROGRAM_SILENCE_THR != 0)

  float spectro_sum = p_obj->p_preproc_task->dpu.S_Spectr.spectro_sum ;
  p_obj->p_preproc_task->dpu.S_Spectr.spectro_sum = 0.0F;
  return (spectro_sum > CTRL_X_CUBE_AI_SPECTROGRAM_SILENCE_THR);
#else
  return 1;
#endif
}

static void AppControllerPrintStats(AManagedTask *_this)
{
  AppController_t *p_obj = (AppController_t*)_this;

  EXECUTION_TIME exec_time,idle_time,isr_time,total_time,thread_time,ai_time,pre_time;
  TX_THREAD *p_Thread;

  /* Disable interrupts.  */
  TX_INTERRUPT_SAVE_AREA
  TX_DISABLE
  _tx_execution_idle_time_get(&idle_time);
  _tx_execution_thread_total_time_get(&exec_time);
  _tx_execution_thread_time_get(&(p_obj->p_preproc_task->super.super.m_xTaskHandle), &pre_time);
  _tx_execution_thread_time_get(&(p_obj->p_ai_task->super.super.m_xTaskHandle), &ai_time);
  _tx_execution_isr_time_get(&isr_time);
  total_time = exec_time + idle_time;

  float ai_time_per_inf = (float)ai_time/(float)(SystemCoreClock/1000);
  ai_time_per_inf -= p_obj->ai_task_time_init;
  ai_time_per_inf /= p_obj->signal_count;
  float pre_time_per_inf = (float)pre_time/(float)(SystemCoreClock/1000);
  pre_time_per_inf -= p_obj->preproc_task_time_init;
  pre_time_per_inf /= p_obj->signal_count;

  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r--------------------------------");
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r         AI Statistics");
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r--------------------------------");
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\rProcessing time per inference\n\r");
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r%20s : %6.2f ms","Pre-process",pre_time_per_inf);
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r%20s : %6.2f ms","AI",ai_time_per_inf);
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r%20s -----------","");
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r%20s : %6.2f ms\n\r","Total",\
      ((float)(ai_time+pre_time)/(float)(SystemCoreClock/1000))/p_obj->signal_count);

  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r--------------------------------");
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r       System Statistics");
  fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r--------------------------------\n\r");
  fprintf(CTRL_TASK_CFG_OUT_CH, "STM32U5 MCU@%ldMhz\r\n\r\n", SystemCoreClock/1000000);
  p_Thread =  &(_this->m_xTaskHandle);
  do
  {
    _tx_execution_thread_time_get(p_Thread , &thread_time);
    fprintf(CTRL_TASK_CFG_OUT_CH, "%20s : %6.2f %%\n\r",p_Thread->tx_thread_name ,\
        (float)thread_time/(float)total_time * 100.0F );
    p_Thread = p_Thread->tx_thread_created_next ;
  }while (p_Thread!= &_this->m_xTaskHandle);
  fprintf(CTRL_TASK_CFG_OUT_CH, "%20s : %6.2f %%\n\r","ISR", (float)isr_time/(float)total_time * 100.0F );
  fprintf(CTRL_TASK_CFG_OUT_CH, "%20s -----------\n\r","");
  fprintf(CTRL_TASK_CFG_OUT_CH, "%20s : %6.2f %%\n\r","Total Load", (float)exec_time/(float)total_time * 100.0F  );

  /* Restore interrupts.  */
  TX_RESTORE
}

static void AppControllerPrintAIRes(uint32_t cnt, float *p_out)
{

  fprintf(CTRL_TASK_CFG_OUT_CH, "  {\"signal\":%lu",cnt);

#if (CTRL_X_CUBE_AI_MODE_OUTPUT_1 == CTRL_AI_CLASS_IDX )
  fprintf(CTRL_TASK_CFG_OUT_CH, ",\"class\":\"%s\"",sAiClassLabels[(uint32_t) p_out[0]]);
#elif (CTRL_X_CUBE_AI_MODE_OUTPUT_1 == CTRL_AI_CLASS_DISTRIBUTION)
  {
    float max_out = p_out[0];
    int max_idx = 0;
    for(int i = 1; i < CTRL_X_CUBE_AI_MODE_CLASS_NUMBER; i++)
    {
      if(p_out[i] > max_out)
      {
        max_idx = i;
        max_out = p_out[i];
      }
    }
    if (max_out > CTRL_X_CUBE_AI_OOD_THR)
		{	
    fprintf(CTRL_TASK_CFG_OUT_CH, ",\"class\":\"%s\",\"dist\":[%.2f",sAiClassLabels[max_idx],p_out[0]);
    }
    else
    {
     fprintf(CTRL_TASK_CFG_OUT_CH, ",\"class\":\"%s\",\"dist\":[%.2f","Unknown class",p_out[0]);
    }
    for (int i = 1 ; i < CTRL_X_CUBE_AI_MODE_CLASS_NUMBER; i++)
    {
      fprintf(CTRL_TASK_CFG_OUT_CH, ",%.2f",p_out[i]);
    }
    fprintf(CTRL_TASK_CFG_OUT_CH, "]");
  }
#endif
#if (CTRL_X_CUBE_AI_MODE_OUTPUT_2 == CTRL_AI_CLASS_DISTRIBUTION)
  fprintf(CTRL_TASK_CFG_OUT_CH, ",\"dist\":[%.2f",p_out[1]);
  for (int i = 1 ; i < CTRL_X_CUBE_AI_MODE_CLASS_NUMBER; i++)
  {
    fprintf(CTRL_TASK_CFG_OUT_CH, ",%.2f",p_out[i+1]);
  }
  fprintf(CTRL_TASK_CFG_OUT_CH, "]");
#endif

  fprintf(CTRL_TASK_CFG_OUT_CH, "},\r\n");

}

/**
 * @brief  Rx Transfer completed callback
 * @param  UartHandle: UART handle
 * @retval None
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *UartHandle)
{
  struct CtrlMessage_t msg = {
      .msg_id   = APP_MESSAGE_ID_CTRL,
      .cmd_id  = CTRL_RX_CAR
  };
  msg.data[0] =  sTaskObj.in_caracter;
  if (TX_SUCCESS != tx_queue_send(&sTaskObj.in_queue, &msg, TX_NO_WAIT))
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE);
  }
}
