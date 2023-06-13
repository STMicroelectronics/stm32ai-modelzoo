/**
  ******************************************************************************
  * @file    SensorRegister.c
  * @author  SRA - MCD
  * @brief
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

/* Includes ------------------------------------------------------------------*/
#include "SensorManager.h"
#include "SensorRegister.h"
#include "stdlib.h"
#include "string.h"
#include "services/sysdebug.h"

#define SYS_DEBUGF(level, message)                   SYS_DEBUGF3(SYS_DBG_APP, level, message)

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Private function prototypes -----------------------------------------------*/
/* Private functions ---------------------------------------------------------*/

uint8_t SMAddSensor(ISensor_t *pSensor)
{
  assert_param(pSensor != NULL);
  uint8_t id = SM_INVALID_SENSOR_ID;
  uint16_t ii = 0;
  boolean_t add_ok = FALSE;
  SensorManager_t *spSMObj = SMGetSensorManager();

  /* check if the sensor has been already registered with the SensorManager. */
  for (ii = 0; ii < spSMObj->n_sensors; ++ii)
  {
    if (spSMObj->Sensors[ii] == pSensor)
    {
      /* sensor already registered with the SensorManager. */

      SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SM: sensor ID=%d already registered.\r\n", ii));

      id = ii;
      return id;
    }
  }

  for (ii = 0; ii < spSMObj->n_sensors + 1; ii++)
  {
    if (spSMObj->Sensors[ii] == NULL)
    {
      spSMObj->Sensors[ii] = pSensor;
      add_ok = TRUE;
      id = ii;
    }
  }

  if (add_ok)
  {
    spSMObj->n_sensors++;
  }
#if defined(DEBUG) || defined(SYS_DEBUG)
  else
  {
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SM: unable to add sensor. MAX_SENSORS = %d\r\n", SM_MAX_SENSORS));
  }
#endif

  return id;
}

sys_error_code_t SMRemoveSensor(ISensor_t *pSensor)
{
  assert_param(pSensor != NULL);
  sys_error_code_t res = SYS_OUT_OF_MEMORY_ERROR_CODE;
  uint8_t id = SM_INVALID_SENSOR_ID;
  uint16_t ii = 0;
  SensorManager_t *spSMObj = SMGetSensorManager();

  /* check if the sensor is part of the SensorManager. */
  for (ii = 0; ii < spSMObj->n_sensors; ++ii)
  {
    if (spSMObj->Sensors[ii] == pSensor)
    {
      /* sensor available within the SensorManager. */
      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("SM: sensor ID=%d available.\r\n", ii));

      id = ii;
      if (spSMObj->Sensors[id] != NULL)
      {
        for (ii = id; ii < spSMObj->n_sensors - 1; ii++)
        {
          spSMObj->Sensors[ii] = spSMObj->Sensors[ii + 1];
        }

        /* sensor removed */
        SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("SM: sensor ID=%d removed.\r\n", id));

        spSMObj->n_sensors--;
        res = SYS_NO_ERROR_CODE;
      }
      return res;
    }
  }

  /* sensor not available within the SensorManager. */
  SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("SM: can't remove sensor. Not available into SM.\r\n"));
  return res;
}

