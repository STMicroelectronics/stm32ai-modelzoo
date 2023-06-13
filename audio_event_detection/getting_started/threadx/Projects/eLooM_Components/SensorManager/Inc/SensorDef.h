/**
  ******************************************************************************
  * @file    SensorDef.h
  * @author  SRA - MCD
  *
  *
  *
  * @brief
  *
  *
  *
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  *
  ******************************************************************************
  */
#ifndef SENSORDEF_H_
#define SENSORDEF_H_

#ifdef __cplusplus
extern "C" {
#endif



#include "services/systp.h"
#include "services/syserror.h"


#define COM_TYPE_ACC    1
#define COM_TYPE_MAG    2
#define COM_TYPE_GYRO   3
#define COM_TYPE_TEMP   4
#define COM_TYPE_PRESS  5
#define COM_TYPE_HUM    6
#define COM_TYPE_MIC    7
#define COM_TYPE_MLC    8
#define COM_TYPE_ISPU   9

#define DATA_TYPE_UINT8     (uint8_t)(0x00)
#define DATA_TYPE_INT8      (uint8_t)(0x01)
#define DATA_TYPE_UINT16    (uint8_t)(0x02)
#define DATA_TYPE_INT16     (uint8_t)(0x03)
#define DATA_TYPE_UINT32    (uint8_t)(0x04)
#define DATA_TYPE_INT32     (uint8_t)(0x05)
#define DATA_TYPE_FLOAT     (uint8_t)(0x06)

#define COM_END_OF_LIST_INT           -1
#define COM_END_OF_LIST_FLOAT         -1.0f

#define COM_LIST_SEPARATOR_INT        -2
#define COM_LIST_SEPARATOR_FLOAT      -2.0f


#ifndef SM_MAX_SENSOR_COMBO
#define SM_MAX_SENSOR_COMBO           4
#endif
#ifndef SM_MAX_SUPPORTED_ODR
#define SM_MAX_SUPPORTED_ODR          16
#endif
#ifndef SM_MAX_SUPPORTED_FS
#define SM_MAX_SUPPORTED_FS           16
#endif
#ifndef SM_MAX_DIM_LABELS
#define SM_MAX_DIM_LABELS             16U
#endif
#ifndef SM_DIM_LABELS_LENGTH
#define SM_DIM_LABELS_LENGTH          4U
#endif


/**
  * Create  type name for _SensorDescriptor_t.
  */
typedef struct _SensorDescriptor_t SensorDescriptor_t;

/**
  *  SensorDescriptor_t internal structure.
  */
struct _SensorDescriptor_t
{

  /**
    * Specifies the sensor name.
    */
  char Name[SM_MAX_DIM_LABELS];

  /**
    * Specifies the sensor type (ACC, GYRO, TEMP, ...).
    */
  uint8_t SensorType;

  /**
    * Specifies the supported data rates.
    */
  float pODR[SM_MAX_SUPPORTED_ODR];

  /**
    * Specifies the supported full scales.
    */
  float pFS[SM_MAX_SUPPORTED_FS];

  /**
    * Specifies a label for each axes.
    */
  char DimensionsLabel[SM_MAX_DIM_LABELS][SM_DIM_LABELS_LENGTH];

  /**
    * Specifies the unit of measurement for each axes.
    */
  char unit[SM_MAX_DIM_LABELS];

  /**
    * Specifies the supported values for SamplesPerTimestamp variable.
    */
  uint16_t pSamplesPerTimestamp[2];
};

/**
  * Create  type name for _SensorManager_t.
 */
typedef struct _SensorStatus_t SensorStatus_t;

/**
  *  SensorStatus_t internal structure.
 */
struct _SensorStatus_t
{
  /**
    * Specifies the full scale.
    */
  float FS;

  /**
    * Specifies the sensitivity.
    */
  float Sensitivity;

  /**
    * Specifies if the subsensor is active or not.
    */
  boolean_t IsActive;

  /**
    * Specifies the nominal data rate.
    */
  float ODR;

  /**
    * Specifies the effective data rate.
    */
  float MeasuredODR;
};



/* Public API declaration */
/**************************/


/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* SENSORDEF_H_ */
