/**
 ******************************************************************************
 * @file    LPS22HHClass.h
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
#ifndef LPS22HHCLASS_H_
#define LPS22HHCLASS_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systp.h"
#include "services/syserror.h"
#include "SMMessageParser.h"
#include "I2CBusIF.h"
#include "lps22hh_reg.h"
#include "ISensor.h"
#include "ISensor_vtbl.h"
#include "timers.h"
#include "queue.h"


#define LPS22HH_CFG_MAX_LISTENERS         2


#ifndef LPS22HH_CLASS_CFG_STACK_DEPTH
#define LPS22HH_CLASS_CFG_STACK_DEPTH              200
#endif

#ifndef LPS22HH_CLASS_CFG_PRIORITY
#define LPS22HH_CLASS_CFG_PRIORITY                 (tskIDLE_PRIORITY)
#endif

#ifndef LPS22HH_CLASS_CFG_IN_QUEUE_LENGTH
#define LPS22HH_CLASS_CFG_IN_QUEUE_LENGTH          20
#endif

#ifndef LPS22HH_CLASS_CFG_TIMER_PERIOD_MS
#define LPS22HH_CLASS_CFG_TIMER_PERIOD_MS          500
#endif

#define LPS22HH_CLASS_CFG_IN_QUEUE_ITEM_SIZE       sizeof(HIDReport)


/**
 * Create a type name for _LPS22HHClass.
 */
typedef struct _LPS22HHClass LPS22HHClass;


/**
 *  LPS22HHClass internal structure.
 */
struct _LPS22HHClass {

  /**
   * I2C IF object used to connect the sensor task to the SPI bus.
   */
  I2CBusIF sensor_if;

  /**
   * Implements the temperature ISensor interface.
   */
  ISensor_t temp_sensor_if;

  /**
   * Implements the pressure ISensor interface.
   */
  ISensor_t press_sensor_if;

  /**
   * Specifies temperature sensor capabilities.
   */
  const SensorDescriptor_t *temp_sensor_descriptor;

  /**
   * Specifies temperature sensor configuration.
   */
  SensorStatus_t temp_sensor_status;

  /**
   * Specifies pressure sensor capabilities.
   */
  const SensorDescriptor_t *press_sensor_descriptor;

  /**
   * Specifies pressure sensor configuration.
   */
  SensorStatus_t press_sensor_status;

  /**
   * Specifies the sensor ID for the temperature subsensor.
   */
  uint8_t temp_id;

  /**
   * Specifies the sensor ID for the pressure subsensor.
   */
  uint8_t press_id;

  /**
   * Buffer to store the data read from the sensor FIFO
   */
  uint8_t p_sensor_data_buff[256*5];

  /**
   * Temperautre data
   */
  float p_temp_data_buff[128 * 2];

  /**
   * Pressure data
   */
  float p_press_data_buff[128 * 2];

  /**
   * ::IEventSrc interface implementation for this class.
   */
  IEventSrc *p_temp_event_src;

  /**
   * ::IEventSrc interface implementation for this class.
   */
  IEventSrc *p_press_event_src;

  /**
   * Specifies the FIFO watermark level (it depends from ODR)
   */
  uint8_t fifo_level;

  /**
   * Specifies the ms delay between 2 consecutive read (it depends from ODR)
   */
  uint16_t task_delay;

  /**
   * Software timer used to generate the read command
   */
  TimerHandle_t read_fifo_timer;

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


// Public API declaration
//***********************

/**
 * Get the ISourceObservable interface for the accelerometer.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *LPS22HHClassGetTempSensorIF(LPS22HHClass *_this);

/**
 * Get the ISourceObservable interface for the gyroscope.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *LPS22HHClassGetPressSensorIF(LPS22HHClass *_this);

/**
 * Get the SPI interface for the sensor task.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the SPI interface of the sensor.
 */
I2CBusIF *LPS22HHClassGetSensorIF(LPS22HHClass *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *LPS22HHClassGetTempEventSrcIF(LPS22HHClass *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *LPS22HHClassGetPressEventSrcIF(LPS22HHClass *_this);

/**
 * Initialize the sensor according to the actual parameters.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
sys_error_code_t LPS22HHClassSensorInit(LPS22HHClass *_this);

/**
 * Read the data from the sensor.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
sys_error_code_t LPS22HHClassSensorReadData(LPS22HHClass *_this);

/**
 * Initialize the default parameters.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise
 */
sys_error_code_t LPS22HHClassSensorInitClassParams(LPS22HHClass *_this);

/**
 * Private implementation of sensor interface methods for LPS22HH sensor
 */
sys_error_code_t LPS22HHClassSensorStart(LPS22HHClass *_this);
sys_error_code_t LPS22HHClassSensorStop(LPS22HHClass *_this);
sys_error_code_t LPS22HHClassSensorSetODR(LPS22HHClass *_this, float ODR, uint8_t id);
sys_error_code_t LPS22HHClassSensorSetFS(LPS22HHClass *_this, float FS, uint8_t id);
sys_error_code_t LPS22HHClassSensorEnable(LPS22HHClass *_this, uint8_t id);
sys_error_code_t LPS22HHClassSensorDisable(LPS22HHClass *_this, uint8_t id);

/**
 * Check if the sensor is active. The sensor is active if at least one of the sub sensor is active.
 * @param _this [IN] specifies a pointer to a task object.
 * @return TRUE if the sensor is active, FALSE otherwise.
 */
boolean_t LPS22HHClassSensorIsActive(const LPS22HHClass *_this);

sys_error_code_t LPS22HHClassEnterLowPowerMode(const LPS22HHClass *_this);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* LPS22HHCLASS_H_ */
