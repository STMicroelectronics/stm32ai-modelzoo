/**
 ******************************************************************************
 * @file    AppController.c
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

#include "AppController.h"
#include "AppController_vtbl.h"
#include "AppControllerMessagesDef.h"
#include "app_messages_parser.h"
#include "AIMessagesDef.h"
#include "services/SQuery.h"
#include "services/sysdebug.h"
#include "config.h"

#ifndef CTRL_TASK_CFG_IN_QUEUE_LENGTH
#define CTRL_TASK_CFG_IN_QUEUE_LENGTH                  20
#endif
#define CTRL_TASK_CFG_IN_QUEUE_ITEM_SIZE               (sizeof(struct CtrlMessage_t))
#define CTRL_TASK_CFG_OUT_CH                           stdout

#define CTRL_AI_CB_ITEMS                               3

#define SYS_DEBUGF(level, message)                     SYS_DEBUGF3(SYS_DBG_CTRL, level, message)

#if defined(DEBUG) || defined (SYS_DEBUG)
#define sTaskObj                                       sAppCTRLTaskObj
#endif

#if (CTRL_X_CUBE_AI_SENSOR_TYPE != COM_TYPE_ACC)
#error only accelerometer type is supoported
#endif

#if (CTRL_AI_HW_SELECT != STWIN1B)
#error only STWIN1B board is supoported
#endif

static const IProcessEventListener_vtbl sACProcesEventListener_vtbl = {
    ACProcEvtListener_vtblOnStatusChange,
    ACProcEvtListener_vtblSetOwner,
    ACProcEvtListener_vtblGetOwner,
    ACProcEvtListener_vtblOnProcessedDataReady
};

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
 * @param active_ai_proc [IN] specifies teh active AI process. Valid param are:
 *  - CTRL_CMD_PARAM_AI
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static sys_error_code_t AppControllerDetachSensorFromAIProc(AppController_t *_this, uint32_t active_ai_proc);

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
  /* In this application there is only one Keyboard task,
   * so this allocator implement the singleton design pattern.
   */

  /* Initialize the super class */
  AMTInitEx(&sTaskObj.super);

  sTaskObj.super.vptr = &sTheClass.vtbl;

  /* "alloc" the listener IF */
  sTaskObj.listenetIF.super.vptr = &sACProcesEventListener_vtbl;

  return (AManagedTaskEx*)&sTaskObj;
}
sys_error_code_t AppControllerSetAIProcessesInQueue(AppController_t *_this, QueueHandle_t ai_queue)
{
  assert_param(_this != NULL);
  _this->ai_in_queue     = ai_queue;
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

sys_error_code_t AppController_vtblOnCreateTask(AManagedTask *_this, TaskFunction_t *p_task_code, const char **p_name, unsigned short *p_stack_depth, void **p_params, UBaseType_t *p_priority)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;

  /* initialize the object software resource here. */
  p_obj->in_queue = xQueueCreate(CTRL_TASK_CFG_IN_QUEUE_LENGTH, CTRL_TASK_CFG_IN_QUEUE_ITEM_SIZE);
  if (p_obj->in_queue == NULL) {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }

  /* initialize the IProcessEventListener interface */
  IEventListenerSetOwner((IEventListener*)&p_obj->listenetIF, p_obj);

#ifdef DEBUG
  vQueueAddToRegistry(p_obj->in_queue, "CTRL_Q");
#endif

  p_obj->seq_index             = 0;
  p_obj->signal_count          = 0;
  p_obj->signals               = 0;
  p_obj->ai_in_queue           = NULL;
  p_obj->sequence              = sCtrl_sequence;
  p_obj->ai_task_xt_in_us      = 0;
  p_obj->xt_in_us_scale_factor = (1<<CORE_CLOCK_RSHIFT)*1000000.0F/SystemCoreClock;

  /* set the (PM_STATE, ExecuteStepFunc) map from the class object.  */
  _this->m_pfPMState2FuncMap = sTheClass.p_pm_state2func_map;

  *p_task_code = AMTExRun;
  *p_name = "CTRL";
  *p_stack_depth = CTRL_TASK_CFG_STACK_DEPTH;
  *p_params = _this;
  *p_priority = CTRL_TASK_CFG_PRIORITY;

  return res;
}

sys_error_code_t AppController_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;

  if (new_power_mode == E_POWER_MODE_STATE1)
  {
    xQueueReset(p_obj->in_queue);
    struct CtrlMessage_t msg = {
        .msgId = APP_MESSAGE_ID_CTRL,
        .cmd_id = CTRL_CMD_DID_STOP
    };

    if (active_power_mode == E_POWER_MODE_X_CUBE_AI_ACTIVE)
    {
      msg.param = CTRL_CMD_PARAM_AI;
    }
    xQueueSendToFront(p_obj->in_queue, &msg, pdMS_TO_TICKS(50));
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
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  AppController_t *p_obj = (AppController_t*)_this;

  struct CtrlMessage_t msg = {
      .msgId = APP_REPORT_ID_FORCE_STEP
  };
  if (xQueueSendToFront(p_obj->in_queue, &msg, pdMS_TO_TICKS(100)) != pdTRUE)
  {
    res = SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE);
  }

  return res;
}

sys_error_code_t AppController_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  return SYS_NO_ERROR_CODE;
}

/* IListener virtual functions definition */
/******************************************/

sys_error_code_t ACProcEvtListener_vtblOnStatusChange(IListener *_this)
{
  assert_param(_this != NULL);
  return SYS_NO_ERROR_CODE;
}

/* IEventListener virtual functions definition */
/***********************************************/

void ACProcEvtListener_vtblSetOwner(IEventListener *_this, void *pxOwner)
{
  assert_param(_this != NULL);
  ACProcessEventListener_t *p_obj = (ACProcessEventListener_t*)_this;
  p_obj->p_owner = pxOwner;
}

void *ACProcEvtListener_vtblGetOwner(IEventListener *_this)
{
  assert_param(_this != NULL);
  ACProcessEventListener_t *p_obj = (ACProcessEventListener_t*)_this;
  return p_obj->p_owner;
}

/* IEventListener virtual functions definition */
/***********************************************/

sys_error_code_t ACProcEvtListener_vtblOnProcessedDataReady(IEventListener *_this, const ProcessEvent *pxEvt)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  /*ACProcessEventListener_t *p_obj = (ACProcessEventListener_t*)_this; */
  AppController_t *p_owner = (AppController_t*) (((size_t)_this) - offsetof(AppController_t, listenetIF));
  struct CtrlMessage_t msg = {
      .msgId = APP_MESSAGE_ID_CTRL,
  };

  if(pxEvt->tag == CTRL_CMD_PARAM_AI)
  {
    /* this result come from X-CUBE-AI process. We know the format of the stream */
    msg.cmd_id = CTRL_CMD_AI_PROC_RES;
    msg.param = (uint32_t) pxEvt->stream->payload; // convert HAR percentage in integer value
  }
  else
  {
    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("CTRL: unexpected TAG ID:0x%x\r\n", pxEvt->tag));
    return SYS_INVALID_PARAMETER_ERROR_CODE;
  }

  if (pdTRUE != xQueueSendToBack(p_owner->in_queue, &msg, pdMS_TO_TICKS(100)))
  {
    res = SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE);
  }

  return res;
}

/* Private function definition */
/*******************************/

sys_error_code_t AppControllerGetAIExecTime(AppController_t *_this, const char * str, float *runtime)
{
  TaskStatus_t *pxTaskStatusArray;
  uint32_t NbTask, TotalTime;
  *runtime  = 0.0F;

  NbTask = uxTaskGetNumberOfTasks();
  pxTaskStatusArray = pvPortMalloc( NbTask * sizeof( TaskStatus_t ) );
  if( pxTaskStatusArray != NULL )
  {
    NbTask = uxTaskGetSystemState( pxTaskStatusArray, NbTask, &TotalTime );
    for(int  x = 0; x < NbTask; x++ )
    {
      if (strncmp(str,pxTaskStatusArray[x].pcTaskName,10)==0)
      {
        *runtime = pxTaskStatusArray[x].ulRunTimeCounter*_this->xt_in_us_scale_factor;
        break;
      }
    }
    vPortFree( pxTaskStatusArray );
  }
  return SYS_NO_ERROR_CODE;
}

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
      AppControllerSetAISensor(p_obj,sensor_id);
      {
        struct AIMessage_t msg = {
            .msgId = APP_MESSAGE_ID_AI,
            .cmd_id = AI_CMD_LOAD_MODEL,
            .param = (uint32_t) CTRL_X_CUBE_AI_MODE_NETWORK_MODEL_NAME
        };
        if (pdTRUE != xQueueSendToBack(p_obj->ai_in_queue, &msg, pdMS_TO_TICKS(100)))
        {
          res = SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE;
          SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE);
        }
      }
      break;
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

  struct AIMessage_t msg2 = {
      .msgId = APP_MESSAGE_ID_AI,
      .cmd_id = AI_CMD_ADD_DPU_LISTENER,
      .param = (uint32_t)&p_obj->listenetIF
  };
  if (pdTRUE != xQueueSendToBack(p_obj->ai_in_queue, &msg2, pdMS_TO_TICKS(100)))
  {
    res = SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE);
  }
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

  if (pdTRUE == xQueueReceive(p_obj->in_queue, &msg, portMAX_DELAY))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    if (msg.msgId == APP_MESSAGE_ID_CTRL)
    {
      switch (msg.cmd_id)
      {
      case CTRL_CMD_DID_STOP:
      {
        char stats [300];
        float runtime;
        res = AppControllerDetachSensorFromAIProc(p_obj, msg.param);
        fprintf(CTRL_TASK_CFG_OUT_CH, "}\r\n");
        fprintf(CTRL_TASK_CFG_OUT_CH, "\r\n...End of execution phase\r\n");
        AppControllerGetAIExecTime(p_obj,"AI", &runtime);
        fprintf(CTRL_TASK_CFG_OUT_CH, "\n\r\n\r-------------------\n\r");
        fprintf(CTRL_TASK_CFG_OUT_CH, "Execution Profiling \n\r\n\r");
            fprintf(CTRL_TASK_CFG_OUT_CH, "Average AI process time over %lu signals is %.2f microseconds",\
            p_obj->signal_count ,(runtime - p_obj->ai_task_xt_in_us)/p_obj->signal_count);
        p_obj->ai_task_xt_in_us = runtime;

        vTaskGetRunTimeStats(stats);

        fprintf(CTRL_TASK_CFG_OUT_CH,"\r\n\r\nTasks statistics (unit is %0.2f us)\n\r\n\r", p_obj->xt_in_us_scale_factor);
        fprintf(CTRL_TASK_CFG_OUT_CH,"%s\r\n",stats);
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
    else if (msg.msgId == APP_REPORT_ID_FORCE_STEP)
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

  UART_Start_Receive_IT(&huart2, &p_obj->in_caracter, 1);

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (pdTRUE == xQueueReceive(p_obj->in_queue, &msg, portMAX_DELAY))
  {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);
    if (msg.msgId == APP_MESSAGE_ID_CTRL)
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
        /* deserialize */
        float * p_ai_out = (float *) msg.param;
        fprintf(CTRL_TASK_CFG_OUT_CH, "  {\"signal\":%lu",p_obj->signal_count);

#if (CTRL_X_CUBE_AI_MODE_OUTPUT_1 == CTRL_AI_CLASS_IDX )
        fprintf(CTRL_TASK_CFG_OUT_CH, ",\"class\":\"%s\"",sAiClassLabels[(uint32_t) p_ai_out[0]]);
#elif (CTRL_X_CUBE_AI_MODE_OUTPUT_1 == CTRL_AI_CLASS_DISTRIBUTION)
        {
          float max_out = p_ai_out[0];
          int max_idx = 0;
          for(int i = 1; i < CTRL_X_CUBE_AI_MODE_CLASS_NUMBER; i++)
          {
            if(p_ai_out[i] > max_out)
            {
              max_idx = i;
              max_out = p_ai_out[i];
            }
          }
          fprintf(CTRL_TASK_CFG_OUT_CH, ",\"class\":\"%s\",\"dist\":[%.2f",sAiClassLabels[max_idx],p_ai_out[0]);
          for (int i = 1 ; i < CTRL_X_CUBE_AI_MODE_CLASS_NUMBER; i++)
          {
            fprintf(CTRL_TASK_CFG_OUT_CH, ",%.2f",p_ai_out[i]);
          }
          fprintf(CTRL_TASK_CFG_OUT_CH, "]");
        }
#endif
#if (CTRL_X_CUBE_AI_MODE_OUTPUT_2 == CTRL_AI_CLASS_DISTRIBUTION)
        fprintf(CTRL_TASK_CFG_OUT_CH, ",\"dist\":[%.2f",p_ai_out[1]);
        for (int i = 1 ; i < CTRL_X_CUBE_AI_MODE_CLASS_NUMBER; i++)
        {
          fprintf(CTRL_TASK_CFG_OUT_CH, ",%.2f",p_ai_out[i+1]);
        }
        fprintf(CTRL_TASK_CFG_OUT_CH, "]");
#endif

        fprintf(CTRL_TASK_CFG_OUT_CH, "},\r\n");
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
    else if (msg.msgId == APP_REPORT_ID_FORCE_STEP)
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
  uint8_t sys_evt_param = 0;

  /* 1. find the active sensor and check that there is sonly one sensor active */
  SQuery_t query;
  SQInit(&query, SMGetSensorManager());
  uint16_t sensor_id = SQNextByStatusEnable(&query, true);
  if (sensor_id == SI_NULL_SENSOR_ID)
  {
    fprintf(CTRL_TASK_CFG_OUT_CH, "CTRL: unable to start the execution phase with no sensors active\r\n");
    return res;
  }

  /* 2. connect the sensor to the selected AI engine */
  if (exec_phase == CTRL_CMD_PARAM_AI)
  {
    struct AIMessage_t msg = {
        .msgId = APP_MESSAGE_ID_AI,
        .cmd_id = AI_CMD_CONNECT_TO_SENSOR,
        .sparam = CTRL_AI_CB_ITEMS,
        .param = (uint32_t)_this->p_ai_sensor_obs,
    };
    if (xQueueSendToBack(_this->ai_in_queue, &msg, pdMS_TO_TICKS(100)) != pdTRUE)
    {
      res = SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE);
    }
    sys_evt_param = SYS_PM_EVENT_PARAM_START_ML;
  }
  if (!SYS_IS_ERROR_CODE(res))
  {
    /* 5. wait for the task to process the messages */
    vTaskDelay(pdMS_TO_TICKS(200));

    /* 6. reset part of the task internal state */
    _this->signal_count = 0;
    /* _this->stop_timer, if enabled, is started during the state transaction in order to have a bit more accurate time measurement. */

    if (exec_phase == CTRL_CMD_PARAM_AI)
    {
      fprintf(CTRL_TASK_CFG_OUT_CH, "\r\nX-CUBE-AI: detect\r\n{\r\n");
      AppControllerGetAIExecTime(_this,"AI", &_this->ai_task_xt_in_us);
    }

    /* 7 trigger the power mode transaction */
    SysEvent evt = {
        .nRawEvent = SYS_PM_MAKE_EVENT(SYS_PM_EVT_SRC_CTRL, sys_evt_param)
    };
    SysPostPowerModeEvent(evt);
  }

  return res;
}

static sys_error_code_t AppControllerDetachSensorFromAIProc(AppController_t *_this, uint32_t active_ai_proc)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  if (active_ai_proc == CTRL_CMD_PARAM_AI)
  {
    struct AIMessage_t msg2 = {
        .msgId  = APP_MESSAGE_ID_AI,
        .cmd_id = AI_CMD_DETACH_FROM_SENSOR,
        .param  = (uint32_t)_this->p_ai_sensor_obs
    };
    if (pdTRUE != xQueueSendToBack(_this->ai_in_queue, &msg2, pdMS_TO_TICKS(100)))
    {
      res = SYS_TASK_QUEUE_FULL_ERROR_CODE;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_TASK_QUEUE_FULL_ERROR_CODE);
    }
    struct AIMessage_t msg3 = {
        .msgId  = APP_MESSAGE_ID_AI,
        .cmd_id = AI_CMD_RELEASE_MODEL,
    };
    if (pdTRUE != xQueueSendToBack(_this->ai_in_queue, &msg3, pdMS_TO_TICKS(100)))
    {
      res = SYS_TASK_QUEUE_FULL_ERROR_CODE;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_TASK_QUEUE_FULL_ERROR_CODE);
    }
  }

  return res;
}

void assert_failed(uint8_t* file, uint32_t line)
{
  sys_error_handler();
}

/**
 * @brief  Rx Transfer completed callback
 * @param  UartHandle: UART handle
 * @retval None
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *UartHandle)
{
  struct CtrlMessage_t msg = {
      .msgId   = APP_MESSAGE_ID_CTRL,
      .cmd_id  = CTRL_RX_CAR
  };
  msg.data[0] =  sTaskObj.in_caracter;
  xQueueSendToBackFromISR(sTaskObj.in_queue, &msg, NULL);
}
