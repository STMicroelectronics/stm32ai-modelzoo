/**
  ******************************************************************************
  * @file    I2CBusTask.c
  * @author  SRA - MCD
  * @brief   This task is the gatekeeper for sensor I2C Bus
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  ******************************************************************************
  */

#include "I2CBusTask.h"
#include "I2CBusTask_vtbl.h"
#include "drivers/I2CMasterDriver.h"
#include "drivers/I2CMasterDriver_vtbl.h"
#include "SMMessageParser.h"
#include "SensorManager.h"
#include "services/sysdebug.h"

#ifndef I2CBUS_TASK_CFG_STACK_DEPTH
#define I2CBUS_TASK_CFG_STACK_DEPTH        120
#endif

#ifndef I2CBUS_TASK_CFG_PRIORITY
#define I2CBUS_TASK_CFG_PRIORITY           (3)
#endif

#ifndef I2CBUS_TASK_CFG_INQUEUE_LENGTH
#define I2CBUS_TASK_CFG_INQUEUE_LENGTH     20
#endif

#define I2CBUS_OP_WAIT_MS                  50

#define SYS_DEBUGF(level, message)         SYS_DEBUGF3(SYS_DBG_I2CBUS, level, message)

#if defined(DEBUG) || defined (SYS_DEBUG)
#define sTaskObj                        sI2CBUSTaskObj
#endif

/**
  * IBus virtual table.
  */
static const IBus_vtbl sIBus_vtbl =
{
  I2CBusTask_vtblCtrl,
  I2CBusTask_vtblConnectDevice,
  I2CBusTask_vtblDisconnectDevice
};

typedef struct _I2CBusTaskIBus
{
  IBus super;

  I2CBusTask *p_owner;
} I2CBusTaskIBus;

/**
  * Class object declaration
  */
typedef struct _I2CBusTaskClass
{
  /**
    * I2CBusTask class virtual table.
    */
  AManagedTaskEx_vtbl vtbl;

  /**
    * I2CBusTask (PM_STATE, ExecuteStepFunc) map.
    */
  pExecuteStepFunc_t p_pm_state2func_map[3];
} I2CBusTaskClass_t;

/* Private member function declaration */
/***************************************/

/**
  * Execute one step of the task control loop while the system is in RUN mode.
  *
  * @param _this [IN] specifies a pointer to a task object.
  * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
  */
static sys_error_code_t I2CBusTaskExecuteStep(AManagedTask *_this);

/**
  * Task control function.
  *
  * @param pParams .
  */
static int32_t I2CBusTaskWrite(void *p_sensor, uint8_t reg, uint8_t *data, uint16_t size);
static int32_t I2CBusTaskRead(void *p_sensor, uint8_t reg, uint8_t *data, uint16_t size);

static sys_error_code_t I2CBusTaskCtrl(ABusIF *_this, EBusCtrlCmd ctrl_cmd, uint32_t params);

/* Inline function forward declaration */
// ***********************************

#if defined (__GNUC__)
#endif

/**
  * The class object.
  */
static const I2CBusTaskClass_t sTheClass =
{
  /* Class virtual table */
  {
    I2CBusTask_vtblHardwareInit,
    I2CBusTask_vtblOnCreateTask,
    I2CBusTask_vtblDoEnterPowerMode,
    I2CBusTask_vtblHandleError,
    I2CBusTask_vtblOnEnterTaskControlLoop,
    I2CBusTask_vtblForceExecuteStep,
    I2CBusTask_vtblOnEnterPowerMode
  },

  /* class (PM_STATE, ExecuteStepFunc) map */
  {
    I2CBusTaskExecuteStep,
    NULL,
    I2CBusTaskExecuteStep,
  }
};

/* Public API definition */
// *********************

AManagedTaskEx *I2CBusTaskAlloc(const void *p_mx_drv_cfg)
{
  I2CBusTask *p_task = SysAlloc(sizeof(I2CBusTask));

  /* Initialize the super class */
  AMTInitEx(&p_task->super);

  p_task->super.vptr = &sTheClass.vtbl;
  p_task->p_mx_drv_cfg = p_mx_drv_cfg;

  return (AManagedTaskEx *) p_task;
}

sys_error_code_t I2CBusTaskConnectDevice(I2CBusTask *_this, I2CBusIF *p_bus_if)
{
  assert_param(_this);

  ((ABusIF*)p_bus_if)->p_request_queue = &_this->in_queue;

  return IBusConnectDevice(_this->p_bus_if, &p_bus_if->super);
}

sys_error_code_t I2CBusTaskDisconnectDevice(I2CBusTask *_this, I2CBusIF *p_bus_if)
{
  assert_param(_this);

  return IBusDisconnectDevice(_this->p_bus_if, &p_bus_if->super);
}

IBus *I2CBusTaskGetBusIF(I2CBusTask *_this)
{
  assert_param(_this);

  return _this->p_bus_if;
}

// AManagedTask virtual functions definition
// ***********************************************

sys_error_code_t I2CBusTask_vtblHardwareInit(AManagedTask *_this, void *p_params)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CBusTask *p_obj = (I2CBusTask *) _this;

  p_obj->p_driver = I2CMasterDriverAlloc();
  if (p_obj->p_driver == NULL)
  {
    SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("I2CBus task: unable to alloc driver object.\r\n"));
    res = SYS_GET_LAST_LOW_LEVEL_ERROR_CODE();
  }
  else
  {
    I2CMasterDriverParams_t driver_cfg =
    {
      .p_mx_i2c_cfg = (void *) p_obj->p_mx_drv_cfg
    };
    res = IDrvInit((IDriver *) p_obj->p_driver, &driver_cfg);
    if (SYS_IS_ERROR_CODE(res))
    {
      SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("I2CBus task: error during driver initialization\r\n"));
    }
  }

  return res;
}


sys_error_code_t I2CBusTask_vtblOnCreateTask(AManagedTask *_this, tx_entry_function_t *pvTaskCode, CHAR **pcName,
                                             VOID **pvStackStart,
                                             ULONG *pnStackDepth, UINT *pxPriority, UINT *pPreemptThreshold, ULONG *pTimeSlice, ULONG *pAutoStart,
                                             ULONG *pParams)
{

  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CBusTask *p_obj = (I2CBusTask *) _this;

  // initialize the software resources.

  uint32_t item_size = (uint32_t)SMMessageGetSize(SM_MESSAGE_ID_I2C_BUS_READ);
  VOID *p_queue_items_buff = SysAlloc(I2CBUS_TASK_CFG_INQUEUE_LENGTH * item_size);

  if (p_queue_items_buff != NULL)
  {
    if (TX_SUCCESS == tx_queue_create(&p_obj->in_queue, "I2CBUS_Q", item_size / 4u, p_queue_items_buff,
                                      I2CBUS_TASK_CFG_INQUEUE_LENGTH * item_size))
    {
      p_obj->p_bus_if = SysAlloc(sizeof(I2CBusTaskIBus));
      if (p_obj->p_bus_if != NULL)
      {
        p_obj->p_bus_if->vptr = &sIBus_vtbl;
        ((I2CBusTaskIBus *) p_obj->p_bus_if)->p_owner = p_obj;

        p_obj->connected_devices = 0;
        _this->m_pfPMState2FuncMap = sTheClass.p_pm_state2func_map;

        *pvTaskCode = AMTExRun;
        *pcName = "I2CBUS";

        *pvStackStart = NULL; // allocate the task stack in the system memory pool.
        *pnStackDepth = I2CBUS_TASK_CFG_STACK_DEPTH;
        *pParams = (ULONG) _this;
        *pxPriority = I2CBUS_TASK_CFG_PRIORITY;
        *pPreemptThreshold = I2CBUS_TASK_CFG_PRIORITY;
        *pTimeSlice = TX_NO_TIME_SLICE;
        *pAutoStart = TX_AUTO_START;
      }
      else
      {
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
        res = SYS_OUT_OF_MEMORY_ERROR_CODE;
      }
    }
    else
    {
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
      res = SYS_OUT_OF_MEMORY_ERROR_CODE;
    }
  }
  return res;
}

sys_error_code_t I2CBusTask_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode eActivePowerMode,
                                                 const EPowerMode eNewPowerMode)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CBusTask *p_obj = (I2CBusTask *) _this;

  IDrvDoEnterPowerMode((IDriver *) p_obj->p_driver, eActivePowerMode, eNewPowerMode);

  if (eNewPowerMode == E_POWER_MODE_SLEEP_1)
  {
    tx_queue_flush(&p_obj->in_queue);
  }

  if ((eActivePowerMode == E_POWER_MODE_SENSORS_ACTIVE) && (eNewPowerMode == E_POWER_MODE_STATE1))
  {
    tx_queue_flush(&p_obj->in_queue);
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("I2CBUS: -> %d\r\n", eNewPowerMode));

  return res;
}

sys_error_code_t I2CBusTask_vtblHandleError(AManagedTask *_this, SysEvent xError)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  return res;
}

sys_error_code_t I2CBusTask_vtblOnEnterTaskControlLoop(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CBusTask *p_obj = (I2CBusTask *) _this;

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("I2C: start.\r\n"));

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("I2CBUS: start the driver.\r\n"));

#if defined(ENABLE_THREADX_DBG_PIN) && defined (I2CBUS_TASK_CFG_TAG)
  p_obj->super.m_xTaskHandle.pxTaskTag = I2CBUS_TASK_CFG_TAG;
#endif

  res = IDrvStart((IDriver *) p_obj->p_driver);
  if (SYS_IS_ERROR_CODE(res))
  {
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("I2CBUS - Driver start failed.\r\n"));
    res = SYS_BASE_LOW_LEVEL_ERROR_CODE;
  }

  return res;
}

sys_error_code_t I2CBusTask_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode eActivePowerMode)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CBusTask *p_obj = (I2CBusTask *) _this;

  /* to resume the task we send an empty message. */
  SMMessage xReport =
  {
    .messageID = SM_MESSAGE_ID_FORCE_STEP
  };
  if ((eActivePowerMode == E_POWER_MODE_STATE1) || (eActivePowerMode == E_POWER_MODE_SENSORS_ACTIVE))
  {
    if (AMTExIsTaskInactive(_this))
    {
      if (TX_SUCCESS != tx_queue_front_send(&p_obj->in_queue, &xReport, AMT_MS_TO_TICKS(100)))
      {

        SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("I2CBUS: unable to resume the task.\r\n"));

        res = SYS_I2CBUS_TASK_RESUME_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_I2CBUS_TASK_RESUME_ERROR_CODE);
      }
    }
    else
    {
      /* do nothing and wait for the step to complete. */
    }
  }
  else
  {
    UINT state;
    if (TX_SUCCESS == tx_thread_info_get(&_this->m_xTaskHandle, TX_NULL, &state, TX_NULL, TX_NULL, TX_NULL, TX_NULL,
                                         TX_NULL, TX_NULL))
    {
      if (state == TX_SUSPENDED)
      {
        tx_thread_resume(&_this->m_xTaskHandle);
      }
    }
  }

  return res;
}

sys_error_code_t I2CBusTask_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode eActivePowerMode,
                                                 const EPowerMode eNewPowerMode)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  AMTExSetPMClass(_this, E_PM_CLASS_1);

  return res;
}

/* IBus virtual functions definition */

sys_error_code_t I2CBusTask_vtblCtrl(IBus *_this, EBusCtrlCmd eCtrlCmd, uint32_t nParams)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  return res;
}

sys_error_code_t I2CBusTask_vtblConnectDevice(IBus *_this, ABusIF *pxBusIF)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;


  if (pxBusIF != NULL)
  {
    pxBusIF->m_xConnector.pfReadReg = I2CBusTaskRead;
    pxBusIF->m_xConnector.pfWriteReg = I2CBusTaskWrite;
    pxBusIF->m_pfBusCtrl = I2CBusTaskCtrl;
    pxBusIF->m_pxBus = _this;
    ((I2CBusTaskIBus*) _this)->p_owner->connected_devices++;

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("I2CBUS: connected device: %d\r\n", ((I2CBusTaskIBus *)_this)->p_owner->connected_devices));
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }

  return res;
}

sys_error_code_t I2CBusTask_vtblDisconnectDevice(IBus *_this, ABusIF *pxBusIF)
{
  assert_param(_this);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (pxBusIF != NULL)
  {
    pxBusIF->m_xConnector.pfReadReg = ABusIFNullRW;
    pxBusIF->m_xConnector.pfWriteReg = ABusIFNullRW;
    pxBusIF->m_pfBusCtrl = NULL;
    pxBusIF->m_pxBus = NULL;
    pxBusIF->p_request_queue = NULL;
    ((I2CBusTaskIBus *) _this)->p_owner->connected_devices--;

    SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("I2CBUS: connected device: %d\r\n",
                                       ((I2CBusTaskIBus *)_this)->p_owner->connected_devices));
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }

  return res;
}

/* Private function definition */

static sys_error_code_t I2CBusTaskCtrl(ABusIF *_this, EBusCtrlCmd ctrl_cmd, uint32_t params)
{
  return IBusCtrl(_this->m_pxBus, ctrl_cmd, params);
}

static sys_error_code_t I2CBusTaskExecuteStep(AManagedTask *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  I2CBusTask *p_obj = (I2CBusTask *) _this;

  struct i2cIOMessage_t msg =
  {
    0
  };
  AMTExSetInactiveState((AManagedTaskEx *) _this, TRUE);
  if (TX_SUCCESS == tx_queue_receive(&p_obj->in_queue, &msg, TX_WAIT_FOREVER))
  {
    AMTExSetInactiveState((AManagedTaskEx *) _this, FALSE);
    switch (msg.messageId)
    {
      case SM_MESSAGE_ID_FORCE_STEP:
        __NOP();
        /* do nothing. I need only to resume the task. */
        break;

      case SM_MESSAGE_ID_I2C_BUS_READ:

        I2CMasterDriverSetDeviceAddr((I2CMasterDriver_t *) p_obj->p_driver, msg.pxSensor->address);
        res = IIODrvRead(p_obj->p_driver, msg.pnData, msg.nDataSize, msg.nRegAddr);
        if (!SYS_IS_ERROR_CODE(res))
        {
          res = I2CBusIFNotifyIOComplete(msg.pxSensor);
        }
        break;

      case SM_MESSAGE_ID_I2C_BUS_WRITE:
        I2CMasterDriverSetDeviceAddr((I2CMasterDriver_t *) p_obj->p_driver, msg.pxSensor->address);
        res = IIODrvWrite(p_obj->p_driver, msg.pnData, msg.nDataSize, msg.nRegAddr);
        if (!SYS_IS_ERROR_CODE(res))
        {
          res = I2CBusIFNotifyIOComplete(msg.pxSensor);
        }
        break;

      default:
        SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("I2C: unsupported message id:%d\r\n", msg.messageId));
        res = SYS_I2CBUS_TASK_UNSUPPORTED_CMD_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_I2CBUS_TASK_UNSUPPORTED_CMD_ERROR_CODE);
        break;
    }
  }

  return res;
}

static int32_t I2CBusTaskWrite(void *p_sensor, uint8_t reg, uint8_t *data, uint16_t size)
{
  assert_param(p_sensor);
  I2CBusIF *p_i2c_sensor = (I2CBusIF *) p_sensor;
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  uint8_t auto_inc = p_i2c_sensor->auto_inc;

  struct i2cIOMessage_t msg =
  {
    .messageId = SM_MESSAGE_ID_I2C_BUS_WRITE,
    .pxSensor = p_i2c_sensor,
    .nRegAddr = reg | auto_inc,
    .pnData = data,
    .nDataSize = size
  };

  // if (s_xI2cTaskObj.m_xInQueue != NULL) {//TODO: STF.Port - how to know if the task has been initialized ??
  if (SYS_IS_CALLED_FROM_ISR())
  {
    /* we cannot read and write in the I2C BUS from an ISR. Notify the error */
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_I2CBUS_TASK_IO_ERROR_CODE);
    res = SYS_I2CBUS_TASK_IO_ERROR_CODE;
  }
  else
  {
    if (TX_SUCCESS != tx_queue_send(p_i2c_sensor->super.p_request_queue, &msg, AMT_MS_TO_TICKS(I2CBUS_OP_WAIT_MS)))
    {
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_I2CBUS_TASK_IO_ERROR_CODE);
      res = SYS_I2CBUS_TASK_IO_ERROR_CODE;
    }
  }
  // }

  if (!SYS_IS_ERROR_CODE(res))
  {
    /* Wait until the operation is completed */
    res = I2CBusIFWaitIOComplete(p_i2c_sensor);
  }

  return res;
}

static int32_t I2CBusTaskRead(void *p_sensor, uint8_t reg, uint8_t *data, uint16_t size)
{
  assert_param(p_sensor);
  I2CBusIF *p_i2c_sensor = (I2CBusIF *) p_sensor;
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  uint8_t auto_inc = p_i2c_sensor->auto_inc;

  struct i2cIOMessage_t msg =
  {
    .messageId = SM_MESSAGE_ID_I2C_BUS_READ,
    .pxSensor = p_i2c_sensor,
    .nRegAddr = reg | auto_inc,
    .pnData = data,
    .nDataSize = size
  };

  // if (s_xI2cTaskObj.m_xInQueue != NULL) { //TODO: STF.Port - how to know if the task has been initialized ??
  if (SYS_IS_CALLED_FROM_ISR())
  {
    /* we cannot read and write in the I2C BUS from an ISR. Notify the error */
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_I2CBUS_TASK_IO_ERROR_CODE);
    res = SYS_I2CBUS_TASK_IO_ERROR_CODE;
  }
  else
  {
    if (TX_SUCCESS != tx_queue_send(p_i2c_sensor->super.p_request_queue, &msg, AMT_MS_TO_TICKS(I2CBUS_OP_WAIT_MS)))
    {
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_I2CBUS_TASK_IO_ERROR_CODE);
      res = SYS_I2CBUS_TASK_IO_ERROR_CODE;
    }
  }
  // }

  if (!SYS_IS_ERROR_CODE(res))
  {
    /* Wait until the operation is completed */
    res = I2CBusIFWaitIOComplete(p_i2c_sensor);
  }

  return res;
}
