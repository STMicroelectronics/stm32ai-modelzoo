/**
 ******************************************************************************
 * @file    IIS3DWBTask.c
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
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
 *
 ******************************************************************************
 */

#include "IIS3DWBTask.h"
#include "IIS3DWBTask_vtbl.h"
#include "SMMessageParser.h"
#include "SensorCommands.h"
#include "SensorDef.h"
#include "SensorRegister.h"
#include "events/ISensorEventListener.h"
#include "events/ISensorEventListener_vtbl.h"
#include "SMUtilTask.h"
#include <string.h>
#include "services/sysdebug.h"


#ifndef IIS3DWB_TASK_CFG_STACK_DEPTH
#define IIS3DWB_TASK_CFG_STACK_DEPTH              120
#endif

#ifndef IIS3DWB_TASK_CFG_PRIORITY
#define IIS3DWB_TASK_CFG_PRIORITY                 (tskIDLE_PRIORITY)
#endif

#ifndef IIS3DWB_TASK_CFG_IN_QUEUE_LENGTH
#define IIS3DWB_TASK_CFG_IN_QUEUE_LENGTH          20
#endif

#define IIS3DWB_TASK_CFG_IN_QUEUE_ITEM_SIZE       sizeof(SMMessage)

#ifndef IIS3DWB_USER_PIN_CONFIG           /*!< to allow the definition of the hw configuration at app level */
#define IIS3DWB_USER_PIN_CONFIG           1
#define IIS3DWB_SPI_CS_Pin                        GPIO_PIN_5
#define IIS3DWB_SPI_CS_GPIO_Port                  GPIOF
#define IIS3DWB_SPI_CS_GPIO_CLK_ENABLE()          __HAL_RCC_GPIOF_CLK_ENABLE()
#define IIS3DWB_INT1_Pin                          GPIO_PIN_14
#define IIS3DWB_INT1_GPIO_Port                    GPIOE
#define IIS3DWB_INT1_GPIO_CLK_ENABLE()            __HAL_RCC_GPIOE_CLK_ENABLE()
#define IIS3DWB_INT1_EXTI_IRQn                    EXTI15_10_IRQn
#endif

#define SYS_DEBUGF(level, message)                SYS_DEBUGF3(SYS_DBG_IIS3DWB, level, message)

#if defined(DEBUG) || defined (SYS_DEBUG)
#define sTaskObj                                  sIIS3DWBTaskObj
#endif

#ifndef HSD_USE_DUMMY_DATA
#define HSD_USE_DUMMY_DATA 0
#endif

#if (HSD_USE_DUMMY_DATA == 1)
static uint16_t dummyDataCounter = 0;
#endif


/**
 *  IIS3DWBTask internal structure.
 */
struct _IIS3DWBTask {
  /**
   * Base class object.
   */
  AManagedTaskEx super;

  // Task variables should be added here.

  /**
   * SPI IF object used to connect the sensor task to the SPI bus.
   */
  SPIBusIF sensor_if;

  /**
   * Implements the accelerometer ISensor interface.
   */
  ISensor_t acc_sensor_if;

  /**
   * Specifies accelerometer sensor capabilities.
   */
  const SensorDescriptor_t *acc_sensor_descriptor;

  /**
   * Specifies accelerometer sensor configuration.
   */
  SensorStatus_t acc_sensor_status;

  /**
   * Specifies the sensor ID for the accelerometer subsensor.
   */
  uint8_t acc_id;

  /**
   * Synchronization object used to send command to the task.
   */
  QueueHandle_t in_queue;

  /**
   * Buffer to store the data read from the sensor
   */
  uint8_t p_sensor_data_buff[IIS3DWB_MAX_SAMPLES_PER_IT * 7];

  /**
   * Specifies the FIFO watermark level (it depends from ODR)
   */
  uint16_t samples_per_it;

  /**
   * ::IEventSrc interface implementation for this class.
   */
  IEventSrc *p_event_src;

  /**
   * Specifies the time stamp in tick.
   */
  uint32_t timestamp_tick;

  /**
   * Used during the time stamp computation to manage the overflow of the hardware timer.
   */
  uint32_t old_timestamp_tick;

  /**
   * Specifies the time stamp linked with the sensor data.
   */
  uint64_t timestamp;
};

/**
 * Class object declaration
 */
typedef struct _IIS3DWBTaskClass {
  /**
   * IIS3DWBTask class virtual table.
   */
  AManagedTaskEx_vtbl vtbl;

  /**
   * Accelerometer IF virtual table.
   */
  ISensor_vtbl acc_sensor_if_vtbl;

  /**
   * Specifies accelerometer sensor capabilities.
   */
  SensorDescriptor_t acc_class_descriptor;

  /**
   * IIS3DWBTask (PM_STATE, ExecuteStepFunc) map.
   */
  pExecuteStepFunc_t p_pm_state2func_map[];
} IIS3DWBTaskClass_t;

// Private member function declaration
// ***********************************

/**
 * Execute one step of the task control loop while the system is in RUN mode.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t IIS3DWBTaskExecuteStepState1(AManagedTask *_this);

/**
 * Execute one step of the task control loop while the system is in SENSORS_ACTIVE mode.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t IIS3DWBTaskExecuteStepDatalog(AManagedTask *_this);

/**
 * Initialize the sensor according to the actual parameters.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t IIS3DWBTaskSensorInit(IIS3DWBTask *_this);

/**
 * Read the data from the sensor.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
static sys_error_code_t IIS3DWBTaskSensorReadData(IIS3DWBTask *_this);

/**
 * Register the sensor with the global DB and initialize the default parameters.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise
 */
static sys_error_code_t IIS3DWBTaskSensorRegister(IIS3DWBTask *_this);

/**
 * Initialize the default parameters.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise
 */
static sys_error_code_t IIS3DWBTaskSensorInitTaskParams(IIS3DWBTask *_this);

/**
 * Private implementation of sensor interface methods for IIS3DWB sensor
 */
static sys_error_code_t IIS3DWBTaskSensorStart(IIS3DWBTask *_this, SMMessage report);
static sys_error_code_t IIS3DWBTaskSensorStop(IIS3DWBTask *_this, SMMessage report);
static sys_error_code_t IIS3DWBTaskSensorSetODR(IIS3DWBTask *_this, SMMessage report);
static sys_error_code_t IIS3DWBTaskSensorSetFS(IIS3DWBTask *_this, SMMessage report);
static sys_error_code_t IIS3DWBTaskSensorEnable(IIS3DWBTask *_this, SMMessage report);
static sys_error_code_t IIS3DWBTaskSensorDisable(IIS3DWBTask *_this, SMMessage report);

/**
 * Check if the sensor is active. The sensor is active if at least one of the sub sensor is active.
 * @param _this [IN] specifies a pointer to a task object.
 * @return TRUE if the sensor is active, FALSE otherwise.
 */
static boolean_t IIS3DWBTaskSensorIsActive(const IIS3DWBTask *_this);

static sys_error_code_t IIS3DWBTaskEnterLowPowerMode(const IIS3DWBTask *_this);

static sys_error_code_t IIS3DWBTaskConfigureIrqPin(const IIS3DWBTask *_this, boolean_t LowPower);

/**
 * SPI CS Pin interrupt callback
 */
void IIS3DWBTask_EXTI_Callback(uint16_t nPin);


// Inline function forward declaration
// ***********************************

/**
 * Private function used to post a report into the front of the task queue.
 * Used to resume the task when the required by the INIT task.
 *
 * @param this [IN] specifies a pointer to the task object.
 * @param pReport [IN] specifies a report to send.
 * @return SYS_NO_EROR_CODE if success, SYS_APP_TASK_REPORT_LOST_ERROR_CODE.
 */
static inline sys_error_code_t IIS3DWBTaskPostReportToFront(IIS3DWBTask *_this, SMMessage *pReport);

/**
 * Private function used to post a report into the back of the task queue.
 * Used to resume the task when the required by the INIT task.
 *
 * @param this [IN] specifies a pointer to the task object.
 * @param pReport [IN] specifies a report to send.
 * @return SYS_NO_EROR_CODE if success, SYS_APP_TASK_REPORT_LOST_ERROR_CODE.
 */
static inline sys_error_code_t IIS3DWBTaskPostReportToBack(IIS3DWBTask *_this, SMMessage *pReport);

#if defined (__GNUC__)
// Inline function defined inline in the header file IIS3DWBTask.h must be declared here as extern function.
#endif


/* Objects instance */
/********************/

/**
 * The only instance of the task object.
 */
static IIS3DWBTask sTaskObj;

/**
 * The class object.
 */
static const IIS3DWBTaskClass_t sTheClass = {
    /* class virtual table */
    {
        IIS3DWBTask_vtblHardwareInit,
        IIS3DWBTask_vtblOnCreateTask,
        IIS3DWBTask_vtblDoEnterPowerMode,
        IIS3DWBTask_vtblHandleError,
        IIS3DWBTask_vtblOnEnterTaskControlLoop,
        IIS3DWBTask_vtblForceExecuteStep,
        IIS3DWBTask_vtblOnEnterPowerMode
    },

    /* class::acc_sensor_if_vtbl virtual table */
    {
        IIS3DWBTask_vtblAccGetId,
        IIS3DWBTask_vtblGetEventSourceIF,
        IIS3DWBTask_vtblAccGetODR,
        IIS3DWBTask_vtblAccGetFS,
        IIS3DWBTask_vtblAccGetSensitivity,
        IIS3DWBTask_vtblSensorStart,
        IIS3DWBTask_vtblSensorStop,
        IIS3DWBTask_vtblSensorSetODR,
        IIS3DWBTask_vtblSensorSetFS,
        IIS3DWBTask_vtblSensorEnable,
        IIS3DWBTask_vtblSensorDisable,
        IIS3DWBTask_vtblSensorIsEnabled,
        IIS3DWBTask_vtblSensorGetDescription,
        IIS3DWBTask_vtblSensorGetStatus
    },

    /* ACCELEROMETER DESCRIPTOR */
    {
        "iis3dwb",
        COM_TYPE_ACC,
        {
            26667.0,
            COM_END_OF_LIST_FLOAT,
        },
        {
            2.0f,
            4.0f,
            8.0f,
            16.0f,
            COM_END_OF_LIST_FLOAT,
        },
        {
            "x",
            "y",
            "z",
        },
        "g",
        {
            0,
            1000,
        }
    },

    /* class (PM_STATE, ExecuteStepFunc) map */
    {
        IIS3DWBTaskExecuteStepState1,
        NULL,
        IIS3DWBTaskExecuteStepDatalog,
    }
};


// Public API definition
// *********************

ISourceObservable *IIS3DWBTaskGetAccSensorIF(IIS3DWBTask *_this){
  return (ISourceObservable *)&(_this->acc_sensor_if);
}

AManagedTaskEx *IIS3DWBTaskAlloc() {
  // In this application there is only one Keyboard task,
  // so this allocator implement the singleton design pattern.

  // Initialize the super class
  AMTInitEx(&sTaskObj.super);

  sTaskObj.super.vptr = &sTheClass.vtbl;
  sTaskObj.acc_sensor_if.vptr = &sTheClass.acc_sensor_if_vtbl;
  sTaskObj.acc_sensor_descriptor = &sTheClass.acc_class_descriptor;

  return (AManagedTaskEx*)&sTaskObj;
}

SPIBusIF *IIS3DWBTaskGetSensorIF(IIS3DWBTask *_this) {
  assert_param(_this);

  return &_this->sensor_if;
}

IEventSrc *IIS3DWBTaskGetEventSrcIF(IIS3DWBTask *_this) {
  assert_param(_this);

  return (IEventSrc*)_this->p_event_src;
}

// AManagedTask virtual functions definition
// ***********************************************

sys_error_code_t IIS3DWBTask_vtblHardwareInit(AManagedTask *_this, void *pParams) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_obj = (IIS3DWBTask*)_this;

  IIS3DWBTaskConfigureIrqPin(p_obj, FALSE);

  return res;
}

sys_error_code_t IIS3DWBTask_vtblOnCreateTask(AManagedTask *_this, TaskFunction_t *pvTaskCode, const char **pcName, unsigned short *pnStackDepth, void **pParams, UBaseType_t *pxPriority) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_obj = (IIS3DWBTask*)_this;

  // Create task specific sw resources.

  p_obj->in_queue = xQueueCreate(IIS3DWB_TASK_CFG_IN_QUEUE_LENGTH, IIS3DWB_TASK_CFG_IN_QUEUE_ITEM_SIZE);
  if (p_obj->in_queue == NULL) {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }

#ifdef DEBUG
  vQueueAddToRegistry(p_obj->in_queue, "IIS3DWB_Q");
#endif

  res = SPIBusIFInit(&p_obj->sensor_if, 0, IIS3DWB_SPI_CS_GPIO_Port, IIS3DWB_SPI_CS_Pin);
  if (SYS_IS_ERROR_CODE(res)) {
    return res;
  }
  // set the SPIBusIF object as handle the IF connector because the SPIBus task
  // will use the handle to access the SPIBusIF.
  ABusIFSetHandle(&p_obj->sensor_if.super, &p_obj->sensor_if);

  // Initialize the EventSrc interface.
  p_obj->p_event_src = SensorEventSrcAlloc();
  if (p_obj->p_event_src == NULL) {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
    res = SYS_OUT_OF_MEMORY_ERROR_CODE;
    return res;
  }
  IEventSrcInit(p_obj->p_event_src);

  memset(p_obj->p_sensor_data_buff, 0, sizeof(p_obj->p_sensor_data_buff));
  p_obj->acc_id = 0;
  p_obj->timestamp_tick = 0;
  p_obj->old_timestamp_tick = 0;
  p_obj->timestamp = 0;
  p_obj->samples_per_it = 0;
  _this->m_pfPMState2FuncMap = sTheClass.p_pm_state2func_map;

  *pvTaskCode = AMTExRun;
  *pcName = "IIS3DWB";
  *pnStackDepth = IIS3DWB_TASK_CFG_STACK_DEPTH;
  *pParams = _this;
  *pxPriority = IIS3DWB_TASK_CFG_PRIORITY;

  res = IIS3DWBTaskSensorInitTaskParams(p_obj);
  if (SYS_IS_ERROR_CODE(res)) {
    res = SYS_TASK_HEAP_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    return res;
  }

  res = IIS3DWBTaskSensorRegister(p_obj);
  if (SYS_IS_ERROR_CODE(res)) {
    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: unable to register with DB\r\n"));
    sys_error_handler();
  }

  return res;
}

sys_error_code_t IIS3DWBTask_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_obj = (IIS3DWBTask*)_this;
  stmdev_ctx_t *p_sensor_drv = (stmdev_ctx_t*) &p_obj->sensor_if.super.m_xConnector;

  if (NewPowerMode == E_POWER_MODE_SENSORS_ACTIVE) {
    if (IIS3DWBTaskSensorIsActive(p_obj)) {
      SMMessage report = {
          .sensorMessage.messageId = SM_MESSAGE_ID_SENSOR_CMD,
          .sensorMessage.nCmdID = SENSOR_CMD_ID_START
      };

      if (xQueueSendToBack(p_obj->in_queue, &report, pdMS_TO_TICKS(100)) != pdTRUE) {
        res = SYS_APP_TASK_REPORT_LOST_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_APP_TASK_REPORT_LOST_ERROR_CODE);
      }


      // reset the variables for the time stamp computation.
      p_obj->timestamp_tick = 0;
      p_obj->old_timestamp_tick = 0;
      p_obj->timestamp = 0;
    }

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: -> SENSORS_ACTIVE\r\n"));
    SYS_DEBUGF3(SYS_DBG_APP, SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: -> SENSORS_ACTIVE\r\n"));
  }
  else if (NewPowerMode == E_POWER_MODE_STATE1) {
    if (ActivePowerMode == E_POWER_MODE_SENSORS_ACTIVE) {
      /* SM_SENSOR_STATE_SUSPENDING */
      iis3dwb_fifo_xl_batch_set(p_sensor_drv, IIS3DWB_XL_NOT_BATCHED);
      xQueueReset(p_obj->in_queue);
    }

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: -> STATE1\r\n"));
    SYS_DEBUGF3(SYS_DBG_APP, SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: -> RUN\r\n"));
  }
  else if (NewPowerMode == E_POWER_MODE_SLEEP_1) {
    // the MCU is going in stop so I put the sensor in low power
    // from the INIT task
    res = IIS3DWBTaskEnterLowPowerMode(p_obj);
    if (SYS_IS_ERROR_CODE(res)) {
      sys_error_handler();
    }
    IIS3DWBTaskConfigureIrqPin(p_obj, TRUE);
    // notify the bus
    if (p_obj->sensor_if.super.m_pfBusCtrl != NULL) {
      p_obj->sensor_if.super.m_pfBusCtrl(&p_obj->sensor_if.super, E_BUS_CTRL_DEV_NOTIFY_POWER_MODE, 0);
    }

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: -> SLEEP_1\r\n"));
    SYS_DEBUGF3(SYS_DBG_APP, SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: -> SLEEP_1\r\n"));
  }

  return res;
}

sys_error_code_t IIS3DWBTask_vtblHandleError(AManagedTask *_this, SysEvent xError) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  //  IIS3DWBTask *p_obj = (IIS3DWBTask*)_this;


  return res;
}

sys_error_code_t IIS3DWBTask_vtblOnEnterTaskControlLoop(AManagedTask *_this) {
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: start.\r\n"));

  // At this point all system has been initialized.
  // Execute task specific delayed one time initialization.

#if (configUSE_APPLICATION_TASK_TAG == 1 && defined(DEBUG_PIN_IIS3DWB))
  vTaskSetApplicationTaskTag( NULL, (TaskHookFunction_t)DEBUG_PIN_IIS3DWB );
#endif

  return res;
}

sys_error_code_t IIS3DWBTask_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode ActivePowerMode) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_obj = (IIS3DWBTask*)_this;

  SMMessage report = {
      .internalMessageFE.messageId = SM_MESSAGE_ID_FORCE_STEP,
      .internalMessageFE.nData = 0
  };

  if ((ActivePowerMode == E_POWER_MODE_STATE1) || (ActivePowerMode == E_POWER_MODE_SENSORS_ACTIVE)) {
    if(AMTExIsTaskInactive(_this)) {
      res = IIS3DWBTaskPostReportToFront(p_obj, (SMMessage*)&report);
    }
    else {
      // do nothing and wait for the step to complete.
      //      _this->m_xStatus.nDelayPowerModeSwitch = 0;
    }
  }
  else {
    if(eTaskGetState(_this->m_xThaskHandle) == eSuspended) {
      vTaskResume(_this->m_xThaskHandle);
    }
  }

  return res;
}

sys_error_code_t IIS3DWBTask_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  //  IIS3DWBTask *p_obj = (IIS3DWBTask*)_this;

  return res;
}


// ISensor virtual functions definition
// *******************************************

uint8_t IIS3DWBTask_vtblAccGetId(ISourceObservable *_this){
  assert_param(_this != NULL);
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));
  uint8_t res = p_if_owner->acc_id;

  return res;
}

IEventSrc *IIS3DWBTask_vtblGetEventSourceIF(ISourceObservable *_this){
  assert_param(_this != NULL);
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));

  return p_if_owner->p_event_src;
}

sys_error_code_t IIS3DWBTask_vtblAccGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal){
  assert_param(_this != NULL);
  /*get the object implementing the ISourceObservable IF */
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /* parameter validation */
  if ((p_measured) == NULL || (p_nominal == NULL))
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }
  else
  {
  	*p_measured =  p_if_owner->acc_sensor_status.MeasuredODR;
  	*p_nominal =  p_if_owner->acc_sensor_status.ODR;
  }

  return res;
}

float IIS3DWBTask_vtblAccGetFS(ISourceObservable *_this){
  assert_param(_this != NULL);
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));
  float res = p_if_owner->acc_sensor_status.FS;

  return res;
}

float IIS3DWBTask_vtblAccGetSensitivity(ISourceObservable *_this){
  assert_param(_this != NULL);
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));
  float res = p_if_owner->acc_sensor_status.Sensitivity;

  return res;
}

sys_error_code_t IIS3DWBTask_vtblSensorStart(ISensor_t *_this){
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NOT_IMPLEMENTED_ERROR_CODE;

  return res;
}

sys_error_code_t IIS3DWBTask_vtblSensorStop(ISensor_t *_this){
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NOT_IMPLEMENTED_ERROR_CODE;

  return res;
}

sys_error_code_t IIS3DWBTask_vtblSensorSetODR(ISensor_t *_this, float ODR){
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));

  EPowerMode log_status = AMTGetTaskPowerMode((AManagedTask *)p_if_owner);
  uint8_t sensor_id = ISourceGetId((ISourceObservable *)_this);

  if ((log_status == E_POWER_MODE_SENSORS_ACTIVE) && ISensorIsEnabled(_this))
  {
    res = SYS_INVALID_FUNC_CALL_ERROR_CODE;
  }
  else
  {
    /* Set a new command message in the queue */
    SMMessage report = {
        .sensorMessage.messageId = SM_MESSAGE_ID_SENSOR_CMD,
        .sensorMessage.nCmdID = SENSOR_CMD_ID_SET_ODR,
        .sensorMessage.nSensorId = sensor_id,
        .sensorMessage.nParam = (uint32_t)ODR
    };
    res = IIS3DWBTaskPostReportToBack(p_if_owner, (SMMessage*)&report);
  }

  return res;
}

sys_error_code_t IIS3DWBTask_vtblSensorSetFS(ISensor_t *_this, float FS){
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));

  EPowerMode log_status = AMTGetTaskPowerMode((AManagedTask *)p_if_owner);
  uint8_t sensor_id = ISourceGetId((ISourceObservable *)_this);

  if ((log_status == E_POWER_MODE_SENSORS_ACTIVE) && ISensorIsEnabled(_this))
  {
    res = SYS_INVALID_FUNC_CALL_ERROR_CODE;
  }
  else
  {
    /* Set a new command message in the queue */
    SMMessage report = {
        .sensorMessage.messageId = SM_MESSAGE_ID_SENSOR_CMD,
        .sensorMessage.nCmdID = SENSOR_CMD_ID_SET_FS,
        .sensorMessage.nSensorId = sensor_id,
        .sensorMessage.nParam = (uint32_t)FS
    };
    res = IIS3DWBTaskPostReportToBack(p_if_owner, (SMMessage*)&report);
  }

  return res;

}

sys_error_code_t IIS3DWBTask_vtblSensorEnable(ISensor_t *_this){
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));

  EPowerMode log_status = AMTGetTaskPowerMode((AManagedTask *)p_if_owner);
  uint8_t sensor_id = ISourceGetId((ISourceObservable *)_this);

  if ((log_status == E_POWER_MODE_SENSORS_ACTIVE) && ISensorIsEnabled(_this))
  {
    res = SYS_INVALID_FUNC_CALL_ERROR_CODE;
  }
  else
  {
    /* Set a new command message in the queue */
    SMMessage report = {
        .sensorMessage.messageId = SM_MESSAGE_ID_SENSOR_CMD,
        .sensorMessage.nCmdID = SENSOR_CMD_ID_ENABLE,
        .sensorMessage.nSensorId = sensor_id,
    };
    res = IIS3DWBTaskPostReportToBack(p_if_owner, (SMMessage*)&report);
  }

  return res;
}

sys_error_code_t IIS3DWBTask_vtblSensorDisable(ISensor_t *_this){
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));

  EPowerMode log_status = AMTGetTaskPowerMode((AManagedTask *)p_if_owner);
  uint8_t sensor_id = ISourceGetId((ISourceObservable *)_this);

  if ((log_status == E_POWER_MODE_SENSORS_ACTIVE) && ISensorIsEnabled(_this))
  {
    res = SYS_INVALID_FUNC_CALL_ERROR_CODE;
  }
  else
  {
    /* Set a new command message in the queue */
    SMMessage report = {
        .sensorMessage.messageId = SM_MESSAGE_ID_SENSOR_CMD,
        .sensorMessage.nCmdID = SENSOR_CMD_ID_DISABLE,
        .sensorMessage.nSensorId = sensor_id,
    };
    res = IIS3DWBTaskPostReportToBack(p_if_owner, (SMMessage*)&report);
  }

  return res;
}

boolean_t IIS3DWBTask_vtblSensorIsEnabled(ISensor_t *_this){
  assert_param(_this != NULL);
  boolean_t res = FALSE;
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));

  if(ISourceGetId((ISourceObservable *)_this) == p_if_owner->acc_id)
    res = p_if_owner->acc_sensor_status.IsActive;

  return res;
}

SensorDescriptor_t IIS3DWBTask_vtblSensorGetDescription(ISensor_t *_this){
  assert_param(_this != NULL);
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));

  return *p_if_owner->acc_sensor_descriptor;
}

SensorStatus_t IIS3DWBTask_vtblSensorGetStatus(ISensor_t *_this){
  assert_param(_this != NULL);
  IIS3DWBTask *p_if_owner = (IIS3DWBTask*)((uint32_t)_this - offsetof(IIS3DWBTask, acc_sensor_if));

  return p_if_owner->acc_sensor_status;
}


// Private function definition
// ***************************

static sys_error_code_t IIS3DWBTaskExecuteStepState1(AManagedTask *_this) {
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_obj = (IIS3DWBTask*)_this;
  SMMessage report = {0};

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (pdTRUE == xQueueReceive(p_obj->in_queue, &report, portMAX_DELAY)) {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);

    switch (report.messageID)
    {
      case SM_MESSAGE_ID_FORCE_STEP:
      {
        // do nothing. I need only to resume.
        __NOP();
        break;
      }
      case SM_MESSAGE_ID_SENSOR_CMD:
      {
        switch (report.sensorMessage.nCmdID)
        {
          case SENSOR_CMD_ID_START:
            res = IIS3DWBTaskSensorStart(p_obj, report);
            break;
          case SENSOR_CMD_ID_STOP:
            res = IIS3DWBTaskSensorStop(p_obj, report);
            break;
          case SENSOR_CMD_ID_SET_ODR:
            res = IIS3DWBTaskSensorSetODR(p_obj, report);
            break;
          case SENSOR_CMD_ID_SET_FS:
            res = IIS3DWBTaskSensorSetFS(p_obj, report);
            break;
          case SENSOR_CMD_ID_ENABLE:
            res = IIS3DWBTaskSensorEnable(p_obj, report);
            break;
          case SENSOR_CMD_ID_DISABLE:
            res = IIS3DWBTaskSensorDisable(p_obj, report);
            break;
          default:
            // unwanted report
            res = SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE;
            SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE);

            SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("IIS3DWB: unexpected report in Run: %i\r\n", report.messageID));
            SYS_DEBUGF3(SYS_DBG_APP, SYS_DBG_LEVEL_WARNING, ("IIS3DWB: unexpected report in Run: %i\r\n", report.messageID));
            break;
        }
        break;
      }
      default:
      {
        // unwanted report
        res = SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE);

        SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("IIS3DWB: unexpected report in Run: %i\r\n", report.messageID));
        SYS_DEBUGF3(SYS_DBG_APP, SYS_DBG_LEVEL_WARNING, ("IIS3DWB: unexpected report in Run: %i\r\n", report.messageID));
        break;
      }
    }
  }

  return res;
}

static sys_error_code_t IIS3DWBTaskExecuteStepDatalog(AManagedTask *_this) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  IIS3DWBTask *p_obj = (IIS3DWBTask*)_this;
  SMMessage report = {0};

  AMTExSetInactiveState((AManagedTaskEx*)_this, TRUE);
  if (pdTRUE == xQueueReceive(p_obj->in_queue, &report, portMAX_DELAY)) {
    AMTExSetInactiveState((AManagedTaskEx*)_this, FALSE);

    switch (report.messageID) {
      case SM_MESSAGE_ID_FORCE_STEP:
      {
        // do nothing. I need only to resume.
        __NOP();
        break;
      }
      case SM_MESSAGE_ID_IIS3DWB:
      {
//        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: new data.\r\n"));

        res = IIS3DWBTaskSensorReadData(p_obj);
        if (!SYS_IS_ERROR_CODE(res)) {
          // update the time stamp
          uint32_t period = 0;
          if (p_obj->timestamp_tick >= p_obj->old_timestamp_tick) {
            period = p_obj->timestamp_tick - p_obj->old_timestamp_tick;
          }
          else {
            // overflow of the hw timer
            period = p_obj->timestamp_tick + (0xFFFFFFFF -p_obj->old_timestamp_tick);
          }
          p_obj->old_timestamp_tick = p_obj->timestamp_tick;
          p_obj->timestamp += period;
          // notify the listeners...
          double timestamp = (double)p_obj->timestamp/(double)(SystemCoreClock);
          double delta_timestamp = (double)period/(double)(SystemCoreClock);

          AI_SP_Stream_t stream = {
              .packet.payload = p_obj->p_sensor_data_buff,
              .packet.payload_fmt = AI_SP_FMT_INT16_RESET(),
              .packet.payload_size = p_obj->samples_per_it,
              .mode = AI_SP_MODE_COLUMN //TODO: STF - this means that data are interleaved?!?
              // bonus question: what is AI_LOGGING_SHAPES_DEPTH ??
              // (can I represent anomogeneous matrix [4*4] with this data format ?
          };
          ai_logging_create_shape_2d(&stream.packet.shape, 3, p_obj->samples_per_it);

          SensorEvent evt;
          SensorEventInit((IEvent*)&evt, p_obj->p_event_src, (ai_logging_packet_t*)&stream, timestamp,  p_obj->acc_id);
          IEventSrcSendEvent(p_obj->p_event_src, (IEvent*)&evt, NULL);

          /* update measuredODR */
          p_obj->acc_sensor_status.MeasuredODR = p_obj->samples_per_it/delta_timestamp;

//          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: ts = %f\r\n", (float)timestamp));
        }
        break;
      }
      case SM_MESSAGE_ID_SENSOR_CMD:
      {
        switch (report.sensorMessage.nCmdID)
        {
          case SENSOR_CMD_ID_START:
            res = IIS3DWBTaskSensorInit(p_obj);
            if (!SYS_IS_ERROR_CODE(res)) {
              // enable the IRQs
              IIS3DWBTaskConfigureIrqPin(p_obj, FALSE);
              HAL_NVIC_EnableIRQ(IIS3DWB_INT1_EXTI_IRQn);
            }
            break;
          case SENSOR_CMD_ID_STOP:
            res = IIS3DWBTaskSensorStop(p_obj, report);
            break;
          case SENSOR_CMD_ID_SET_ODR:
            res = IIS3DWBTaskSensorSetODR(p_obj, report);
            break;
          case SENSOR_CMD_ID_SET_FS:
            res = IIS3DWBTaskSensorSetFS(p_obj, report);
            break;
          case SENSOR_CMD_ID_ENABLE:
            res = IIS3DWBTaskSensorEnable(p_obj, report);
            break;
          case SENSOR_CMD_ID_DISABLE:
            res = IIS3DWBTaskSensorDisable(p_obj, report);
            break;
          default:
            // unwanted report
            res = SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE;
            SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE);

            SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("IIS3DWB: unexpected report in Datalog: %i\r\n", report.messageID));
            SYS_DEBUGF3(SYS_DBG_APP, SYS_DBG_LEVEL_WARNING, ("IIS3DWB: unexpected report in Datalog: %i\r\n", report.messageID));
            break;
        }
        break;
      }
      default:
        // unwanted report
        res = SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE);

        SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("IIS3DWB: unexpected report in Datalog: %i\r\n", report.messageID));
        break;
    }
  }

  return res;
}

static inline sys_error_code_t IIS3DWBTaskPostReportToFront(IIS3DWBTask *_this, SMMessage *pReport) {
  assert_param(_this);
  assert_param(pReport);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (SYS_IS_CALLED_FROM_ISR()) {
    if (pdTRUE != xQueueSendToFrontFromISR(_this->in_queue, pReport, NULL)) {
      res = SYS_APP_TASK_REPORT_LOST_ERROR_CODE;
      // this function is private and the caller will ignore this return code.
    }
  }
  else {
    if (pdTRUE != xQueueSendToFront(_this->in_queue, pReport, pdMS_TO_TICKS(100))) {
      res = SYS_APP_TASK_REPORT_LOST_ERROR_CODE;
      // this function is private and the caller will ignore this return code.
    }
  }

  return res;
}

static inline sys_error_code_t IIS3DWBTaskPostReportToBack(IIS3DWBTask *_this, SMMessage *pReport) {
  assert_param(_this);
  assert_param(pReport);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (SYS_IS_CALLED_FROM_ISR()) {
    if (pdTRUE != xQueueSendToBackFromISR(_this->in_queue, pReport, NULL)) {
      res = SYS_APP_TASK_REPORT_LOST_ERROR_CODE;
      // this function is private and the caller will ignore this return code.
    }
  }
  else {
    if (pdTRUE != xQueueSendToBack(_this->in_queue, pReport, pdMS_TO_TICKS(100))) {
      res = SYS_APP_TASK_REPORT_LOST_ERROR_CODE;
      // this function is private and the caller will ignore this return code.
    }
  }

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorInit(IIS3DWBTask *_this) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  stmdev_ctx_t *p_sensor_drv = (stmdev_ctx_t*) &_this->sensor_if.super.m_xConnector;

  uint8_t reg0 = 0;
  int32_t ret_val = 0;
  uint16_t iis3dwb_wtm_level = 0;
  // if this variable need to persist then I move it in the managed task class declaration.
  iis3dwb_pin_int1_route_t pin_int1_route = {0};

  ret_val = iis3dwb_device_id_get(p_sensor_drv, (uint8_t *)&reg0);
  if (!ret_val) {
    SPIBusIFSetWhoAmI(&_this->sensor_if, reg0);
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("IIS3DWB: sensor - I am 0x%x.\r\n", reg0));

  // reset the sensor
  ret_val = iis3dwb_reset_set(p_sensor_drv, 1);
  do {
    iis3dwb_reset_get(p_sensor_drv, &reg0);
  } while(reg0);

  //TODO: STF - what is this?
  iis3dwb_read_reg(p_sensor_drv, IIS3DWB_CTRL1_XL, (uint8_t *)&reg0, 1);
  reg0 |= 0xA0;
  iis3dwb_write_reg(p_sensor_drv, IIS3DWB_CTRL1_XL, (uint8_t *)&reg0, 1);

  /* Calculation of watermark and samples per int*/
  iis3dwb_wtm_level = ((uint16_t)_this->acc_sensor_status.ODR * (uint16_t)IIS3DWB_MAX_DRDY_PERIOD);
  if (iis3dwb_wtm_level > IIS3DWB_MAX_WTM_LEVEL)
  {
    iis3dwb_wtm_level = IIS3DWB_MAX_WTM_LEVEL;
  }
  else if (iis3dwb_wtm_level < IIS3DWB_MIN_WTM_LEVEL)
  {
    iis3dwb_wtm_level = IIS3DWB_MIN_WTM_LEVEL;
  }

  _this->samples_per_it = iis3dwb_wtm_level;

  /*Disable the I2C interfacer and set fifo in continuous / stream mode*/
  iis3dwb_i2c_interface_set(p_sensor_drv, IIS3DWB_I2C_DISABLE);
  iis3dwb_fifo_mode_set(p_sensor_drv, IIS3DWB_STREAM_MODE);

  /*Set watermark*/
  iis3dwb_fifo_watermark_set(p_sensor_drv, iis3dwb_wtm_level);
  /*Data Ready pulse mode*/
  iis3dwb_data_ready_mode_set(p_sensor_drv, IIS3DWB_DRDY_PULSED);

  /*Set full scale*/
  if(_this->acc_sensor_status.FS < 3.0f)
    iis3dwb_xl_full_scale_set(p_sensor_drv, IIS3DWB_2g);
  else if(_this->acc_sensor_status.FS < 5.0f)
    iis3dwb_xl_full_scale_set(p_sensor_drv, IIS3DWB_4g);
  else if(_this->acc_sensor_status.FS < 9.0f)
    iis3dwb_xl_full_scale_set(p_sensor_drv, IIS3DWB_8g);
  else
    iis3dwb_xl_full_scale_set(p_sensor_drv, IIS3DWB_16g);

  /*Set 2nd stage filter*/
  iis3dwb_xl_filt_path_on_out_set(p_sensor_drv,IIS3DWB_LP_6k3Hz);
  /* FIFO_WTM_IA routing on pin INT1 */
  iis3dwb_pin_int1_route_get(p_sensor_drv, &pin_int1_route);
  *(uint8_t*)&(pin_int1_route) = 0;
  pin_int1_route.fifo_th = PROPERTY_ENABLE;
  iis3dwb_pin_int1_route_set(p_sensor_drv, &pin_int1_route);

  /*Enable writing to FIFO*/
  iis3dwb_fifo_xl_batch_set(p_sensor_drv, IIS3DWB_XL_BATCHED_AT_26k7Hz);

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorReadData(IIS3DWBTask *_this) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  stmdev_ctx_t *p_sensor_drv = (stmdev_ctx_t*) &_this->sensor_if.super.m_xConnector;

  uint8_t reg[2];
  uint16_t fifo_level = 0;
  uint16_t i;

  /* Check FIFO_WTM_IA and fifo level. We do not use PID in order to avoid reading one register twice */
  iis3dwb_read_reg(p_sensor_drv, IIS3DWB_FIFO_STATUS1, reg, 2);

  fifo_level = ((reg[1] & 0x03) << 8) + reg[0];

  if((reg[1]) & 0x80  && (fifo_level >= _this->samples_per_it) ) {
    iis3dwb_read_reg(p_sensor_drv, IIS3DWB_FIFO_DATA_OUT_TAG, (uint8_t *)_this->p_sensor_data_buff, _this->samples_per_it * 7);

#if (HSD_USE_DUMMY_DATA == 1)
    int16_t * p16 = (int16_t *)_this->p_sensor_data_buff;

    for (i = 0; i < _this->samples_per_it; i++)
    {
      *p16++ = dummyDataCounter++;
      *p16++ = dummyDataCounter++;
      *p16++ = dummyDataCounter++;
    }
#else
    /* Arrange Data */
    int16_t * p16_src = (int16_t *)_this->p_sensor_data_buff;
    int16_t * p16_dest = (int16_t *)_this->p_sensor_data_buff;
    for (i=0; i < _this->samples_per_it; i++) {
      p16_src = (int16_t *)&((uint8_t *)(p16_src))[1];
      *p16_dest++ = *p16_src++;
      *p16_dest++ = *p16_src++;
      *p16_dest++ = *p16_src++;
    }
#endif
  }
  else
  {
    res = SYS_BASE_ERROR_CODE;
  }

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorRegister(IIS3DWBTask *_this) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  ISensor_t *acc_if = (ISensor_t *)IIS3DWBTaskGetAccSensorIF(_this);
  _this->acc_id = SMAddSensor(acc_if);

  return res;
}


static sys_error_code_t IIS3DWBTaskSensorInitTaskParams(IIS3DWBTask *_this) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /* ACCELEROMETER SENSOR STATUS */
  _this->acc_sensor_status.DataType = DATA_TYPE_INT16;
  _this->acc_sensor_status.Dimensions = 3;
  _this->acc_sensor_status.IsActive = TRUE;
  _this->acc_sensor_status.FS = 16.0f;
  _this->acc_sensor_status.Sensitivity = 0.0000305f *  _this->acc_sensor_status.FS;
  _this->acc_sensor_status.ODR = 26667.0f;
  _this->acc_sensor_status.MeasuredODR = 0.0f;
  _this->acc_sensor_status.InitialOffset = 0.0f;
#if (HSD_USE_DUMMY_DATA == 1)
  _this->acc_sensor_status.SamplesPerTimestamp = 0;
#else
  _this->acc_sensor_status.SamplesPerTimestamp = 1000;
#endif

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorStart(IIS3DWBTask *_this, SMMessage report){
  assert_param(_this);
  sys_error_code_t res = SYS_NOT_IMPLEMENTED_ERROR_CODE;

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorStop(IIS3DWBTask *_this, SMMessage report){
  assert_param(_this);
  sys_error_code_t res = SYS_NOT_IMPLEMENTED_ERROR_CODE;

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorSetODR(IIS3DWBTask *_this, SMMessage report){
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  float ODR = (float)report.sensorMessage.nParam;
  uint8_t id = report.sensorMessage.nSensorId;

  if(id == _this->acc_id)
  {
    if(ODR != 26667.0f)
      ODR = 26667.0f;

    if (!SYS_IS_ERROR_CODE(res))
    {
      _this->acc_sensor_status.ODR = ODR;
      _this->acc_sensor_status.MeasuredODR = 0.0f;
    }
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
  }

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorSetFS(IIS3DWBTask *_this, SMMessage report){
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  stmdev_ctx_t *p_sensor_drv = (stmdev_ctx_t*) &_this->sensor_if.super.m_xConnector;
  float FS = (float)report.sensorMessage.nParam;
  uint8_t id = report.sensorMessage.nSensorId;

  if(id == _this->acc_id)
  {
    if(FS < 3.0f)
    {
      iis3dwb_xl_full_scale_set(p_sensor_drv, IIS3DWB_2g);
      FS = 2.0f;
    }
    else if(FS < 5.0f)
    {
      iis3dwb_xl_full_scale_set(p_sensor_drv, IIS3DWB_4g);
      FS = 4.0f;
    }
    else if(FS < 9.0f)
    {
      iis3dwb_xl_full_scale_set(p_sensor_drv, IIS3DWB_8g);
      FS = 8.0f;
    }
    else
    {
      iis3dwb_xl_full_scale_set(p_sensor_drv, IIS3DWB_16g);
      FS = 16.0f;
    }

    if (!SYS_IS_ERROR_CODE(res))
    {
      _this->acc_sensor_status.FS = FS;
      _this->acc_sensor_status.Sensitivity = 0.0000305f *  _this->acc_sensor_status.FS;
    }
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
  }

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorEnable(IIS3DWBTask *_this, SMMessage report){
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  uint8_t id = report.sensorMessage.nSensorId;

  if(id == _this->acc_id)
    _this->acc_sensor_status.IsActive = TRUE;
  else
    res = SYS_INVALID_PARAMETER_ERROR_CODE;

  return res;
}

static sys_error_code_t IIS3DWBTaskSensorDisable(IIS3DWBTask *_this, SMMessage report){
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  uint8_t id = report.sensorMessage.nSensorId;

  if(id == _this->acc_id)
    _this->acc_sensor_status.IsActive = FALSE;
  else
    res = SYS_INVALID_PARAMETER_ERROR_CODE;

  return res;
}

static boolean_t IIS3DWBTaskSensorIsActive(const IIS3DWBTask *_this) {
  assert_param(_this);
  return _this->acc_sensor_status.IsActive;
}

static sys_error_code_t IIS3DWBTaskEnterLowPowerMode(const IIS3DWBTask *_this) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  stmdev_ctx_t *p_sensor_drv = (stmdev_ctx_t*) &_this->sensor_if.super.m_xConnector;

  if (iis3dwb_xl_data_rate_set(p_sensor_drv, IIS3DWB_XL_ODR_OFF)) {
    res = SYS_SENSOR_TASK_OP_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_SENSOR_TASK_OP_ERROR_CODE);
  }

  return res;
}

static sys_error_code_t IIS3DWBTaskConfigureIrqPin(const IIS3DWBTask *_this, boolean_t LowPower) {
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  GPIO_InitTypeDef GPIO_InitStruct = {0};

  if (!LowPower) {

    /* GPIO Ports Clock Enable */
    IIS3DWB_SPI_CS_GPIO_CLK_ENABLE();
    IIS3DWB_INT1_GPIO_CLK_ENABLE();

    /*Configure GPIO pin Output Level */
    HAL_GPIO_WritePin(IIS3DWB_SPI_CS_GPIO_Port, IIS3DWB_SPI_CS_Pin, GPIO_PIN_SET);

    /*Configure GPIO pin : IIS3DWB_SPI_CS_Pin */
    GPIO_InitStruct.Pin = IIS3DWB_SPI_CS_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(IIS3DWB_SPI_CS_GPIO_Port, &GPIO_InitStruct);

    /*Configure GPIO pins : IIS3DWB_INT1_Pin */
    GPIO_InitStruct.Pin =  IIS3DWB_INT1_Pin ;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(IIS3DWB_INT1_GPIO_Port, &GPIO_InitStruct);

    /* EXTI interrupt init*/
    HAL_NVIC_SetPriority(IIS3DWB_INT1_EXTI_IRQn, 5, 0);
    //  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
    //  HAL_EXTI_GetHandle(&iis3dwb_exti, EXTI_LINE_14);
    //  HAL_EXTI_RegisterCallback(&iis3dwb_exti,  HAL_EXTI_COMMON_CB_ID, IIS3DWB_Int_Callback);
  }
  else {
    // first disable the IRQ to avoid spurious interrupt to wake the MCU up.
    HAL_NVIC_DisableIRQ(IIS3DWB_INT1_EXTI_IRQn);
    HAL_NVIC_ClearPendingIRQ(IIS3DWB_INT1_EXTI_IRQn);
    // then reconfigure the PIN in analog high impedance to reduce the power consumption.
    GPIO_InitStruct.Pin =  IIS3DWB_INT1_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(IIS3DWB_INT1_GPIO_Port, &GPIO_InitStruct);
  }

  return res;
}


// CubeMX integration
// ******************

void IIS3DWBTask_EXTI_Callback(uint16_t nPin) {
  struct iis3dwbMessage_t report = {
      .messageId = SM_MESSAGE_ID_IIS3DWB,
      .bDataReady = 1
  };

  if (sTaskObj.in_queue != NULL && !AMTIsPowerModeSwitchPending((AManagedTask*)&sTaskObj)) {
    if (pdTRUE != xQueueSendToBackFromISR(sTaskObj.in_queue, &report, NULL)) {
      // unable to send the report. Signal the error
      sys_error_handler();
    }
  }
  sTaskObj.timestamp_tick = SMUtilGetTimeStamp();
}
