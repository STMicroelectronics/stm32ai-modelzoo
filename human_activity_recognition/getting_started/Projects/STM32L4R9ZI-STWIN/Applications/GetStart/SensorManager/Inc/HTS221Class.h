/**
 ******************************************************************************
 * @file    HTS221Class.h
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
#ifndef HTS221CLASS_H_
#define HTS221CLASS_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systp.h"
#include "services/syserror.h"
#include "SMMessageParser.h"
#include "I2CBusIF.h"
#include "hts221_reg.h"
#include "ISensor.h"
#include "ISensor_vtbl.h"
#include "queue.h"


#define HTS221_CFG_MAX_LISTENERS         2


#ifndef HTS221_CLASS_CFG_STACK_DEPTH
#define HTS221_CLASS_CFG_STACK_DEPTH              120
#endif

#ifndef HTS221_CLASS_CFG_PRIORITY
#define HTS221_CLASS_CFG_PRIORITY                 (tskIDLE_PRIORITY)
#endif

#ifndef HTS221_CLASS_CFG_IN_QUEUE_LENGTH
#define HTS221_CLASS_CFG_IN_QUEUE_LENGTH          20
#endif

#define HTS221_CLASS_CFG_IN_QUEUE_ITEM_SIZE       sizeof(HIDReport)

#ifndef HTS221_USER_PIN_CONFIG           /*!< to allow the definition of the hw configuration at app level */
#define HTS221_USER_PIN_CONFIG           1
#define HTS221_INT_Pin                  GPIO_PIN_6
#define HTS221_INT_GPIO_Port            GPIOG
#define HTS221_INT_EXTI_IRQn            EXTI9_5_IRQn
#define HTS221_INT_GPIO_ADDITIONAL()    HAL_PWREx_EnableVddIO2()
#define HTS221_INT_GPIO_CLK_ENABLE()    __HAL_RCC_GPIOG_CLK_ENABLE()
#endif


/**
 * Create a type name for _HTS221Class.
 */
typedef struct _HTS221Class HTS221Class;


/**
 *  HTS221Class internal structure.
 */
struct _HTS221Class {

  /**
   * I2C IF object used to connect the sensor task to the SPI bus.
   */
  I2CBusIF sensor_if;

  /**
   * Implements the temperature ISensor interface.
   */
  ISensor_t temp_sensor_if;

  /**
   * Implements the humidity ISensor interface.
   */
  ISensor_t hum_sensor_if;

  /**
   * Specifies temperature sensor capabilities.
   */
  const SensorDescriptor_t *temp_sensor_descriptor;

  /**
   * Specifies temperature sensor configuration.
   */
  SensorStatus_t temp_sensor_status;

  /**
   * Specifies humidity sensor capabilities.
   */
  const SensorDescriptor_t *hum_sensor_descriptor;

  /**
   * Specifies humidity sensor configuration.
   */
  SensorStatus_t hum_sensor_status;

  /**
   * Specifies the sensor ID for the temperature subsensor.
   */
  uint8_t temp_id;

  /**
   * Specifies the sensor ID for the humidity subsensor.
   */
  uint8_t hum_id;

  /**
   * Buffer to store the data read from the sensor
   */
  float p_sensor_data_buff[2];

  /**
   * ::IEventSrc interface implementation for this class.
   */
  IEventSrc *p_temp_event_src;

  /**
   * ::IEventSrc interface implementation for this class.
   */
  IEventSrc *p_hum_event_src;

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

  /*
   * Calibration values
   */
  float x0_t, y0_t, x1_t, y1_t;
  float x0_h, y0_h, x1_h, y1_h;
};


// Public API declaration
//***********************

/**
 * Get the ISourceObservable interface for the accelerometer.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *HTS221ClassGetTempSensorIF(HTS221Class *_this);

/**
 * Get the ISourceObservable interface for the accelerometer.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *HTS221ClassGetHumSensorIF(HTS221Class *_this);

/**
 * Get the SPI interface for the sensor task.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the SPI interface of the sensor.
 */
I2CBusIF *HTS221ClassGetSensorIF(HTS221Class *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *HTS221ClassGetTempEventSrcIF(HTS221Class *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *HTS221ClassGetHumEventSrcIF(HTS221Class *_this);

/**
 * Initialize the sensor according to the actual parameters.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
sys_error_code_t HTS221ClassSensorInit(HTS221Class *_this);

/**
 * Read the data from the sensor.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_EROR_CODE if success, a task specific error code otherwise.
 */
sys_error_code_t HTS221ClassSensorReadData(HTS221Class *_this);

/**
 * Initialize the default parameters.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise
 */
sys_error_code_t HTS221ClassSensorInitClassParams(HTS221Class *_this);

/**
 * Private implementation of sensor interface methods for HTS221 sensor
 */
sys_error_code_t HTS221ClassSensorStart(HTS221Class *_this);
sys_error_code_t HTS221ClassSensorStop(HTS221Class *_this);
sys_error_code_t HTS221ClassSensorSetODR(HTS221Class *_this, float ODR, uint8_t id);
sys_error_code_t HTS221ClassSensorSetFS(HTS221Class *_this, float FS, uint8_t id);
sys_error_code_t HTS221ClassSensorEnable(HTS221Class *_this, uint8_t id);
sys_error_code_t HTS221ClassSensorDisable(HTS221Class *_this, uint8_t id);

/**
 * Check if the sensor is active. The sensor is active if at least one of the sub sensor is active.
 * @param _this [IN] specifies a pointer to a task object.
 * @return TRUE if the sensor is active, FALSE otherwise.
 */
boolean_t HTS221ClassSensorIsActive(const HTS221Class *_this);

sys_error_code_t HTS221ClassEnterLowPowerMode(const HTS221Class *_this);

sys_error_code_t HTS221ClassConfigureIrqPin(const HTS221Class *_this, boolean_t LowPower);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* HTS221CLASS_H_ */
