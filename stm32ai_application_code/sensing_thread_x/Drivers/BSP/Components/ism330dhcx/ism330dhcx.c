/**
  ******************************************************************************
  * @file    ism330dhcx.c
  * @author  MEMS Software Solutions Team
  * @brief   ISM330DHCX driver file
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2019 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "ism330dhcx.h"

/** @addtogroup BSP BSP
  * @{
  */

/** @addtogroup Component Component
  * @{
  */

/** @defgroup ISM330DHCX ISM330DHCX
  * @{
  */

/** @defgroup ISM330DHCX_Exported_Variables ISM330DHCX Exported Variables
  * @{
  */

ISM330DHCX_CommonDrv_t ISM330DHCX_COMMON_Driver =
{
  ISM330DHCX_Init,
  ISM330DHCX_DeInit,
  ISM330DHCX_ReadID,
  ISM330DHCX_GetCapabilities,
};

ISM330DHCX_ACC_Drv_t ISM330DHCX_ACC_Driver =
{
  ISM330DHCX_ACC_Enable,
  ISM330DHCX_ACC_Disable,
  ISM330DHCX_ACC_GetSensitivity,
  ISM330DHCX_ACC_GetOutputDataRate,
  ISM330DHCX_ACC_SetOutputDataRate,
  ISM330DHCX_ACC_GetFullScale,
  ISM330DHCX_ACC_SetFullScale,
  ISM330DHCX_ACC_GetAxes,
  ISM330DHCX_ACC_GetAxesRaw,
};

ISM330DHCX_GYRO_Drv_t ISM330DHCX_GYRO_Driver =
{
  ISM330DHCX_GYRO_Enable,
  ISM330DHCX_GYRO_Disable,
  ISM330DHCX_GYRO_GetSensitivity,
  ISM330DHCX_GYRO_GetOutputDataRate,
  ISM330DHCX_GYRO_SetOutputDataRate,
  ISM330DHCX_GYRO_GetFullScale,
  ISM330DHCX_GYRO_SetFullScale,
  ISM330DHCX_GYRO_GetAxes,
  ISM330DHCX_GYRO_GetAxesRaw,
};

/**
  * @}
  */

/** @defgroup ISM330DHCX_Private_Function_Prototypes ISM330DHCX Private Function Prototypes
  * @{
  */

static int32_t ReadRegWrap(void *Handle, uint8_t Reg, uint8_t *pData, uint16_t Length);
static int32_t WriteRegWrap(void *Handle, uint8_t Reg, uint8_t *pData, uint16_t Length);
static int32_t ISM330DHCX_ACC_SetOutputDataRate_When_Enabled(ISM330DHCX_Object_t *pObj, float Odr);
static int32_t ISM330DHCX_ACC_SetOutputDataRate_When_Disabled(ISM330DHCX_Object_t *pObj, float Odr);
static int32_t ISM330DHCX_GYRO_SetOutputDataRate_When_Enabled(ISM330DHCX_Object_t *pObj, float Odr);
static int32_t ISM330DHCX_GYRO_SetOutputDataRate_When_Disabled(ISM330DHCX_Object_t *pObj, float Odr);

/**
  * @}
  */

/** @defgroup ISM330DHCX_Exported_Functions ISM330DHCX Exported Functions
  * @{
  */

/**
  * @brief  Register Component Bus IO operations
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_RegisterBusIO(ISM330DHCX_Object_t *pObj, ISM330DHCX_IO_t *pIO)
{
  int32_t ret = ISM330DHCX_OK;

  if (pObj == NULL)
  {
    ret = ISM330DHCX_ERROR;
  }
  else
  {
    pObj->IO.Init      = pIO->Init;
    pObj->IO.DeInit    = pIO->DeInit;
    pObj->IO.BusType   = pIO->BusType;
    pObj->IO.Address   = pIO->Address;
    pObj->IO.WriteReg  = pIO->WriteReg;
    pObj->IO.ReadReg   = pIO->ReadReg;
    pObj->IO.GetTick   = pIO->GetTick;

    pObj->Ctx.read_reg  = ReadRegWrap;
    pObj->Ctx.write_reg = WriteRegWrap;
    pObj->Ctx.mdelay    = pIO->Delay;
    pObj->Ctx.handle   = pObj;

    if (pObj->IO.Init == NULL)
    {
      ret = ISM330DHCX_ERROR;
    }
    else if (pObj->IO.Init() != ISM330DHCX_OK)
    {
      ret = ISM330DHCX_ERROR;
    }
    else
    {
      if (pObj->IO.BusType == ISM330DHCX_SPI_3WIRES_BUS) /* SPI 3-Wires */
      {
        /* Enable the SPI 3-Wires support only the first time */
        if (pObj->is_initialized == 0U)
        {
          /* Enable SPI 3-Wires on the component */
          uint8_t data = 0x0C;

          if (ISM330DHCX_Write_Reg(pObj, ISM330DHCX_CTRL3_C, data) != ISM330DHCX_OK)
          {
            ret = ISM330DHCX_ERROR;
          }
        }
      }
    }
  }

  return ret;
}

/**
  * @brief  Initialize the ISM330DHCX sensor
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_Init(ISM330DHCX_Object_t *pObj)
{
  /* Set DEVICE_CONF bit */
  if (ism330dhcx_device_conf_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable register address automatically incremented during a multiple byte
  access with a serial interface. */
  if (ism330dhcx_auto_increment_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* SW reset */
  if (ism330dhcx_reset_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable register address automatically incremented during a multiple byte
     access with a serial interface. */
  if (ism330dhcx_auto_increment_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable BDU */
  if (ism330dhcx_block_data_update_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* FIFO mode selection */
  if (ism330dhcx_fifo_mode_set(&(pObj->Ctx), ISM330DHCX_BYPASS_MODE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Select default output data rate. */
  pObj->acc_odr = ISM330DHCX_XL_ODR_104Hz;

  /* Output data rate selection - power down. */
  if (ism330dhcx_xl_data_rate_set(&(pObj->Ctx), ISM330DHCX_XL_ODR_OFF) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Full scale selection. */
  if (ism330dhcx_xl_full_scale_set(&(pObj->Ctx), ISM330DHCX_2g) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Select default output data rate. */
  pObj->gyro_odr = ISM330DHCX_GY_ODR_104Hz;

  /* Output data rate selection - power down. */
  if (ism330dhcx_gy_data_rate_set(&(pObj->Ctx), ISM330DHCX_GY_ODR_OFF) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Full scale selection. */
  if (ism330dhcx_gy_full_scale_set(&(pObj->Ctx), ISM330DHCX_2000dps) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pObj->is_initialized = 1;

  return ISM330DHCX_OK;
}

/**
  * @brief  Deinitialize the ISM330DHCX sensor
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_DeInit(ISM330DHCX_Object_t *pObj)
{
  /* Disable the component */
  if (ISM330DHCX_ACC_Disable(pObj) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ISM330DHCX_GYRO_Disable(pObj) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset output data rate. */
  pObj->acc_odr = ISM330DHCX_XL_ODR_OFF;
  pObj->gyro_odr = ISM330DHCX_GY_ODR_OFF;

  pObj->is_initialized = 0;

  return ISM330DHCX_OK;
}

/**
  * @brief  Read component ID
  * @param  pObj the device pObj
  * @param  Id the WHO_AM_I value
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ReadID(ISM330DHCX_Object_t *pObj, uint8_t *Id)
{
  if (ism330dhcx_device_id_get(&(pObj->Ctx), Id) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get ISM330DHCX sensor capabilities
  * @param  pObj Component object pointer
  * @param  Capabilities pointer to ISM330DHCX sensor capabilities
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GetCapabilities(ISM330DHCX_Object_t *pObj, ISM330DHCX_Capabilities_t *Capabilities)
{
  /* Prevent unused argument(s) compilation warning */
  (void)(pObj);

  Capabilities->Acc          = 1;
  Capabilities->Gyro         = 1;
  Capabilities->Magneto      = 0;
  Capabilities->LowPower     = 0;
  Capabilities->GyroMaxFS    = 4000;
  Capabilities->AccMaxFS     = 16;
  Capabilities->MagMaxFS     = 0;
  Capabilities->GyroMaxOdr   = 6667.0f;
  Capabilities->AccMaxOdr    = 6667.0f;
  Capabilities->MagMaxOdr    = 0.0f;
  return ISM330DHCX_OK;
}

/**
  * @brief  Enable the ISM330DHCX accelerometer sensor
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Enable(ISM330DHCX_Object_t *pObj)
{
  /* Check if the component is already enabled */
  if (pObj->acc_is_enabled == 1U)
  {
    return ISM330DHCX_OK;
  }

  /* Output data rate selection. */
  if (ism330dhcx_xl_data_rate_set(&(pObj->Ctx), pObj->acc_odr) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pObj->acc_is_enabled = 1;

  return ISM330DHCX_OK;
}

/**
  * @brief  Disable the ISM330DHCX accelerometer sensor
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Disable(ISM330DHCX_Object_t *pObj)
{
  /* Check if the component is already disabled */
  if (pObj->acc_is_enabled == 0U)
  {
    return ISM330DHCX_OK;
  }

  /* Get current output data rate. */
  if (ism330dhcx_xl_data_rate_get(&(pObj->Ctx), &pObj->acc_odr) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Output data rate selection - power down. */
  if (ism330dhcx_xl_data_rate_set(&(pObj->Ctx), ISM330DHCX_XL_ODR_OFF) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pObj->acc_is_enabled = 0;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX accelerometer sensor sensitivity
  * @param  pObj the device pObj
  * @param  Sensitivity pointer
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_GetSensitivity(ISM330DHCX_Object_t *pObj, float *Sensitivity)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_fs_xl_t full_scale;

  /* Read actual full scale selection from sensor. */
  if (ism330dhcx_xl_full_scale_get(&(pObj->Ctx), &full_scale) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Store the Sensitivity based on actual full scale. */
  switch (full_scale)
  {
    case ISM330DHCX_2g:
      *Sensitivity = ISM330DHCX_ACC_SENSITIVITY_FS_2G;
      break;

    case ISM330DHCX_4g:
      *Sensitivity = ISM330DHCX_ACC_SENSITIVITY_FS_4G;
      break;

    case ISM330DHCX_8g:
      *Sensitivity = ISM330DHCX_ACC_SENSITIVITY_FS_8G;
      break;

    case ISM330DHCX_16g:
      *Sensitivity = ISM330DHCX_ACC_SENSITIVITY_FS_16G;
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Get the ISM330DHCX accelerometer sensor output data rate
  * @param  pObj the device pObj
  * @param  Odr pointer where the output data rate is written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_GetOutputDataRate(ISM330DHCX_Object_t *pObj, float *Odr)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_odr_xl_t odr_low_level;

  /* Get current output data rate. */
  if (ism330dhcx_xl_data_rate_get(&(pObj->Ctx), &odr_low_level) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  switch (odr_low_level)
  {
    case ISM330DHCX_XL_ODR_OFF:
      *Odr = 0.0f;
      break;

    case ISM330DHCX_XL_ODR_12Hz5:
      *Odr = 12.5f;
      break;

    case ISM330DHCX_XL_ODR_26Hz:
      *Odr = 26.0f;
      break;

    case ISM330DHCX_XL_ODR_52Hz:
      *Odr = 52.0f;
      break;

    case ISM330DHCX_XL_ODR_104Hz:
      *Odr = 104.0f;
      break;

    case ISM330DHCX_XL_ODR_208Hz:
      *Odr = 208.0f;
      break;

    case ISM330DHCX_XL_ODR_416Hz:
      *Odr = 416.0f;
      break;

    case ISM330DHCX_XL_ODR_833Hz:
      *Odr = 833.0f;
      break;

    case ISM330DHCX_XL_ODR_1666Hz:
      *Odr = 1666.0f;
      break;

    case ISM330DHCX_XL_ODR_3332Hz:
      *Odr = 3332.0f;
      break;

    case ISM330DHCX_XL_ODR_6667Hz:
      *Odr = 6667.0f;
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Set the ISM330DHCX accelerometer sensor output data rate
  * @param  pObj the device pObj
  * @param  Odr the output data rate value to be set
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_SetOutputDataRate(ISM330DHCX_Object_t *pObj, float Odr)
{
  /* Check if the component is enabled */
  if (pObj->acc_is_enabled == 1U)
  {
    return ISM330DHCX_ACC_SetOutputDataRate_When_Enabled(pObj, Odr);
  }
  else
  {
    return ISM330DHCX_ACC_SetOutputDataRate_When_Disabled(pObj, Odr);
  }
}

/**
  * @brief  Get the ISM330DHCX accelerometer sensor full scale
  * @param  pObj the device pObj
  * @param  FullScale pointer where the full scale is written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_GetFullScale(ISM330DHCX_Object_t *pObj, int32_t *FullScale)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_fs_xl_t fs_low_level;

  /* Read actual full scale selection from sensor. */
  if (ism330dhcx_xl_full_scale_get(&(pObj->Ctx), &fs_low_level) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  switch (fs_low_level)
  {
    case ISM330DHCX_2g:
      *FullScale =  2;
      break;

    case ISM330DHCX_4g:
      *FullScale =  4;
      break;

    case ISM330DHCX_8g:
      *FullScale =  8;
      break;

    case ISM330DHCX_16g:
      *FullScale = 16;
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Set the ISM330DHCX accelerometer sensor full scale
  * @param  pObj the device pObj
  * @param  FullScale the functional full scale to be set
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_SetFullScale(ISM330DHCX_Object_t *pObj, int32_t FullScale)
{
  ism330dhcx_fs_xl_t new_fs;

  /* Seems like MISRA C-2012 rule 14.3a violation but only from single file statical analysis point of view because
     the parameter passed to the function is not known at the moment of analysis */
  new_fs = (FullScale <= 2) ? ISM330DHCX_2g
           : (FullScale <= 4) ? ISM330DHCX_4g
           : (FullScale <= 8) ? ISM330DHCX_8g
           :                    ISM330DHCX_16g;

  if (ism330dhcx_xl_full_scale_set(&(pObj->Ctx), new_fs) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX accelerometer sensor raw axes
  * @param  pObj the device pObj
  * @param  Value pointer where the raw values of the axes are written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_GetAxesRaw(ISM330DHCX_Object_t *pObj, ISM330DHCX_AxesRaw_t *Value)
{
  ism330dhcx_axis3bit16_t data_raw;

  /* Read raw data values. */
  if (ism330dhcx_acceleration_raw_get(&(pObj->Ctx), data_raw.i16bit) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Format the data. */
  Value->x = data_raw.i16bit[0];
  Value->y = data_raw.i16bit[1];
  Value->z = data_raw.i16bit[2];

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX accelerometer sensor axes
  * @param  pObj the device pObj
  * @param  Acceleration pointer where the values of the axes are written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_GetAxes(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *Acceleration)
{
  ism330dhcx_axis3bit16_t data_raw;
  float sensitivity = 0.0f;

  /* Read raw data values. */
  if (ism330dhcx_acceleration_raw_get(&(pObj->Ctx), data_raw.i16bit) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Get ISM330DHCX actual sensitivity. */
  if (ISM330DHCX_ACC_GetSensitivity(pObj, &sensitivity) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Calculate the data. */
  Acceleration->x = (int32_t)((float)((float)data_raw.i16bit[0] * sensitivity));
  Acceleration->y = (int32_t)((float)((float)data_raw.i16bit[1] * sensitivity));
  Acceleration->z = (int32_t)((float)((float)data_raw.i16bit[2] * sensitivity));

  return ISM330DHCX_OK;
}

/**
  * @brief  Enable the ISM330DHCX gyroscope sensor
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_Enable(ISM330DHCX_Object_t *pObj)
{
  /* Check if the component is already enabled */
  if (pObj->gyro_is_enabled == 1U)
  {
    return ISM330DHCX_OK;
  }

  /* Output data rate selection. */
  if (ism330dhcx_gy_data_rate_set(&(pObj->Ctx), pObj->gyro_odr) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pObj->gyro_is_enabled = 1;

  return ISM330DHCX_OK;
}

/**
  * @brief  Disable the ISM330DHCX gyroscope sensor
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_Disable(ISM330DHCX_Object_t *pObj)
{
  /* Check if the component is already disabled */
  if (pObj->gyro_is_enabled == 0U)
  {
    return ISM330DHCX_OK;
  }

  /* Get current output data rate. */
  if (ism330dhcx_gy_data_rate_get(&(pObj->Ctx), &pObj->gyro_odr) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Output data rate selection - power down. */
  if (ism330dhcx_gy_data_rate_set(&(pObj->Ctx), ISM330DHCX_GY_ODR_OFF) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pObj->gyro_is_enabled = 0;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX gyroscope sensor sensitivity
  * @param  pObj the device pObj
  * @param  Sensitivity pointer
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_GetSensitivity(ISM330DHCX_Object_t *pObj, float *Sensitivity)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_fs_g_t full_scale;

  /* Read actual full scale selection from sensor. */
  if (ism330dhcx_gy_full_scale_get(&(pObj->Ctx), &full_scale) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Store the sensitivity based on actual full scale. */
  switch (full_scale)
  {
    case ISM330DHCX_125dps:
      *Sensitivity = ISM330DHCX_GYRO_SENSITIVITY_FS_125DPS;
      break;

    case ISM330DHCX_250dps:
      *Sensitivity = ISM330DHCX_GYRO_SENSITIVITY_FS_250DPS;
      break;

    case ISM330DHCX_500dps:
      *Sensitivity = ISM330DHCX_GYRO_SENSITIVITY_FS_500DPS;
      break;

    case ISM330DHCX_1000dps:
      *Sensitivity = ISM330DHCX_GYRO_SENSITIVITY_FS_1000DPS;
      break;

    case ISM330DHCX_2000dps:
      *Sensitivity = ISM330DHCX_GYRO_SENSITIVITY_FS_2000DPS;
      break;

    case ISM330DHCX_4000dps:
      *Sensitivity = ISM330DHCX_GYRO_SENSITIVITY_FS_4000DPS;
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Get the ISM330DHCX gyroscope sensor output data rate
  * @param  pObj the device pObj
  * @param  Odr pointer where the output data rate is written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_GetOutputDataRate(ISM330DHCX_Object_t *pObj, float *Odr)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_odr_g_t odr_low_level;

  /* Get current output data rate. */
  if (ism330dhcx_gy_data_rate_get(&(pObj->Ctx), &odr_low_level) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  switch (odr_low_level)
  {
    case ISM330DHCX_GY_ODR_OFF:
      *Odr = 0.0f;
      break;

    case ISM330DHCX_GY_ODR_12Hz5:
      *Odr = 12.5f;
      break;

    case ISM330DHCX_GY_ODR_26Hz:
      *Odr = 26.0f;
      break;

    case ISM330DHCX_GY_ODR_52Hz:
      *Odr = 52.0f;
      break;

    case ISM330DHCX_GY_ODR_104Hz:
      *Odr = 104.0f;
      break;

    case ISM330DHCX_GY_ODR_208Hz:
      *Odr = 208.0f;
      break;

    case ISM330DHCX_GY_ODR_416Hz:
      *Odr = 416.0f;
      break;

    case ISM330DHCX_GY_ODR_833Hz:
      *Odr = 833.0f;
      break;

    case ISM330DHCX_GY_ODR_1666Hz:
      *Odr =  1666.0f;
      break;

    case ISM330DHCX_GY_ODR_3332Hz:
      *Odr =  3332.0f;
      break;

    case ISM330DHCX_GY_ODR_6667Hz:
      *Odr =  6667.0f;
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Set the ISM330DHCX gyroscope sensor output data rate
  * @param  pObj the device pObj
  * @param  Odr the output data rate value to be set
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_SetOutputDataRate(ISM330DHCX_Object_t *pObj, float Odr)
{
  /* Check if the component is enabled */
  if (pObj->gyro_is_enabled == 1U)
  {
    return ISM330DHCX_GYRO_SetOutputDataRate_When_Enabled(pObj, Odr);
  }
  else
  {
    return ISM330DHCX_GYRO_SetOutputDataRate_When_Disabled(pObj, Odr);
  }
}

/**
  * @brief  Get the ISM330DHCX gyroscope sensor full scale
  * @param  pObj the device pObj
  * @param  FullScale pointer where the full scale is written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_GetFullScale(ISM330DHCX_Object_t *pObj, int32_t  *FullScale)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_fs_g_t fs_low_level;

  /* Read actual full scale selection from sensor. */
  if (ism330dhcx_gy_full_scale_get(&(pObj->Ctx), &fs_low_level) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  switch (fs_low_level)
  {
    case ISM330DHCX_125dps:
      *FullScale =  125;
      break;

    case ISM330DHCX_250dps:
      *FullScale =  250;
      break;

    case ISM330DHCX_500dps:
      *FullScale =  500;
      break;

    case ISM330DHCX_1000dps:
      *FullScale = 1000;
      break;

    case ISM330DHCX_2000dps:
      *FullScale = 2000;
      break;

    case ISM330DHCX_4000dps:
      *FullScale = 4000;
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Set the ISM330DHCX gyroscope sensor full scale
  * @param  pObj the device pObj
  * @param  FullScale the functional full scale to be set
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_SetFullScale(ISM330DHCX_Object_t *pObj, int32_t FullScale)
{
  ism330dhcx_fs_g_t new_fs;

  new_fs = (FullScale <= 125)  ? ISM330DHCX_125dps
           : (FullScale <= 250)  ? ISM330DHCX_250dps
           : (FullScale <= 500)  ? ISM330DHCX_500dps
           : (FullScale <= 1000) ? ISM330DHCX_1000dps
           : (FullScale <= 2000) ? ISM330DHCX_2000dps
           :                       ISM330DHCX_4000dps;

  if (ism330dhcx_gy_full_scale_set(&(pObj->Ctx), new_fs) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX gyroscope sensor raw axes
  * @param  pObj the device pObj
  * @param  Value pointer where the raw values of the axes are written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_GetAxesRaw(ISM330DHCX_Object_t *pObj, ISM330DHCX_AxesRaw_t *Value)
{
  ism330dhcx_axis3bit16_t data_raw;

  /* Read raw data values. */
  if (ism330dhcx_angular_rate_raw_get(&(pObj->Ctx), data_raw.i16bit) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Format the data. */
  Value->x = data_raw.i16bit[0];
  Value->y = data_raw.i16bit[1];
  Value->z = data_raw.i16bit[2];

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX gyroscope sensor axes
  * @param  pObj the device pObj
  * @param  AngularRate pointer where the values of the axes are written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_GetAxes(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *AngularRate)
{
  ism330dhcx_axis3bit16_t data_raw;
  float sensitivity;

  /* Read raw data values. */
  if (ism330dhcx_angular_rate_raw_get(&(pObj->Ctx), data_raw.i16bit) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Get ISM330DHCX actual sensitivity. */
  if (ISM330DHCX_GYRO_GetSensitivity(pObj, &sensitivity) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Calculate the data. */
  AngularRate->x = (int32_t)((float)((float)data_raw.i16bit[0] * sensitivity));
  AngularRate->y = (int32_t)((float)((float)data_raw.i16bit[1] * sensitivity));
  AngularRate->z = (int32_t)((float)((float)data_raw.i16bit[2] * sensitivity));

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX register value
  * @param  pObj the device pObj
  * @param  Reg address to be read
  * @param  Data pointer where the value is written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_Read_Reg(ISM330DHCX_Object_t *pObj, uint8_t Reg, uint8_t *Data)
{
  if (ism330dhcx_read_reg(&(pObj->Ctx), Reg, Data, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX register value
  * @param  pObj the device pObj
  * @param  Reg address to be written
  * @param  Data value to be written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_Write_Reg(ISM330DHCX_Object_t *pObj, uint8_t Reg, uint8_t Data)
{
  if (ism330dhcx_write_reg(&(pObj->Ctx), Reg, &Data, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the interrupt latch
  * @param  pObj the device pObj
  * @param  Status value to be written
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_Set_Interrupt_Latch(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  if (Status > 1U)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_int_notification_set(&(pObj->Ctx), (ism330dhcx_lir_t)Status) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO full interrupt on INT1 pin
  * @param  pObj the device pObj
  * @param  Status DRDY interrupt on INT1 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_Set_INT1_Drdy(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int1_ctrl.int1_drdy_xl = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO full interrupt on INT1 pin
  * @param  pObj the device pObj
  * @param  Status DRDY interrupt on INT1 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_Set_Drdy_Mode(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  if (ism330dhcx_data_ready_mode_set(&(pObj->Ctx), (ism330dhcx_dataready_pulsed_t)Status) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }
  return ISM330DHCX_OK;
}

/**
  * @brief  Enable free fall detection
  * @param  pObj the device pObj
  * @param  IntPin interrupt pin line to be used
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Enable_Free_Fall_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Output Data Rate selection */
  if (ISM330DHCX_ACC_SetOutputDataRate(pObj, 416.0f) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Full scale selection */
  if (ISM330DHCX_ACC_SetFullScale(pObj, 2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* FF_DUR setting */
  if (ism330dhcx_ff_dur_set(&(pObj->Ctx), 0x06) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* WAKE_DUR setting */
  if (ism330dhcx_wkup_dur_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* SLEEP_DUR setting */
  if (ism330dhcx_act_sleep_dur_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* FF_THS setting */
  if (ism330dhcx_ff_threshold_set(&(pObj->Ctx), ISM330DHCX_FF_TSH_312mg) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable free fall event on either INT1 or INT2 pin */
  switch (IntPin)
  {
    case ISM330DHCX_INT1_PIN:
      if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val1.md1_cfg.int1_ff = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    case ISM330DHCX_INT2_PIN:
      if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val2.md2_cfg.int2_ff = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Disable free fall detection
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Disable_Free_Fall_Detection(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Disable free fall event on both INT1 and INT2 pins */
  if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val1.md1_cfg.int1_ff = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val2.md2_cfg.int2_ff = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* FF_DUR setting */
  if (ism330dhcx_ff_dur_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* FF_THS setting */
  if (ism330dhcx_ff_threshold_set(&(pObj->Ctx), ISM330DHCX_FF_TSH_156mg) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set free fall threshold
  * @param  pObj the device pObj
  * @param  Threshold free fall detection threshold
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_Free_Fall_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Threshold)
{
  if (ism330dhcx_ff_threshold_set(&(pObj->Ctx), (ism330dhcx_ff_ths_t)Threshold) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set free fall duration
  * @param  pObj the device pObj
  * @param  Duration free fall detection duration
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_Free_Fall_Duration(ISM330DHCX_Object_t *pObj, uint8_t Duration)
{
  if (ism330dhcx_ff_dur_set(&(pObj->Ctx), Duration) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Enable wake up detection
  * @param  pObj the device pObj
  * @param  IntPin interrupt pin line to be used
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Enable_Wake_Up_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Output Data Rate selection */
  if (ISM330DHCX_ACC_SetOutputDataRate(pObj, 416.0f) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Full scale selection */
  if (ISM330DHCX_ACC_SetFullScale(pObj, 2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* WAKE_DUR setting */
  if (ism330dhcx_wkup_dur_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Set wake up threshold. */
  if (ism330dhcx_wkup_threshold_set(&(pObj->Ctx), 0x02) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable wake up event on either INT1 or INT2 pin */
  switch (IntPin)
  {
    case ISM330DHCX_INT1_PIN:
      if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val1.md1_cfg.int1_wu = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    case ISM330DHCX_INT2_PIN:
      if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val2.md2_cfg.int2_wu = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Disable wake up detection
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Disable_Wake_Up_Detection(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Disable wake up event on both INT1 and INT2 pins */
  if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val1.md1_cfg.int1_wu = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val2.md2_cfg.int2_wu = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset wake up threshold. */
  if (ism330dhcx_wkup_threshold_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* WAKE_DUR setting */
  if (ism330dhcx_wkup_dur_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set wake up threshold
  * @param  pObj the device pObj
  * @param  Threshold wake up detection threshold
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_Wake_Up_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Threshold)
{
  /* Set wake up threshold. */
  if (ism330dhcx_wkup_threshold_set(&(pObj->Ctx), Threshold) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set wake up duration
  * @param  pObj the device pObj
  * @param  Duration wake up detection duration
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_Wake_Up_Duration(ISM330DHCX_Object_t *pObj, uint8_t Duration)
{
  /* Set wake up duration. */
  if (ism330dhcx_wkup_dur_set(&(pObj->Ctx), Duration) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Enable single tap detection
  * @param  pObj the device pObj
  * @param  IntPin interrupt pin line to be used
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Enable_Single_Tap_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Output Data Rate selection */
  if (ISM330DHCX_ACC_SetOutputDataRate(pObj, 416.0f) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Full scale selection */
  if (ISM330DHCX_ACC_SetFullScale(pObj, 2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable X direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_x_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable Y direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_y_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable Z direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_z_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Set tap threshold. */
  if (ism330dhcx_tap_threshold_x_set(&(pObj->Ctx), 0x08) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Set tap shock time window. */
  if (ism330dhcx_tap_shock_set(&(pObj->Ctx), 0x02) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Set tap quiet time window. */
  if (ism330dhcx_tap_quiet_set(&(pObj->Ctx), 0x01) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* _NOTE_: Tap duration time window - don't care for single tap. */

  /* _NOTE_: Single/Double Tap event - don't care of this flag for single tap. */

  /* Enable single tap event on either INT1 or INT2 pin */
  switch (IntPin)
  {
    case ISM330DHCX_INT1_PIN:
      if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val1.md1_cfg.int1_single_tap = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    case ISM330DHCX_INT2_PIN:
      if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val2.md2_cfg.int2_single_tap = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Disable single tap detection
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Disable_Single_Tap_Detection(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Disable single tap event on both INT1 and INT2 pins */
  if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val1.md1_cfg.int1_single_tap = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val2.md2_cfg.int2_single_tap = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset tap quiet time window. */
  if (ism330dhcx_tap_quiet_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset tap shock time window. */
  if (ism330dhcx_tap_shock_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset tap threshold. */
  if (ism330dhcx_tap_threshold_x_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Disable Z direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_z_set(&(pObj->Ctx), PROPERTY_DISABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Disable Y direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_y_set(&(pObj->Ctx), PROPERTY_DISABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Disable X direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_x_set(&(pObj->Ctx), PROPERTY_DISABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Enable double tap detection
  * @param  pObj the device pObj
  * @param  IntPin interrupt pin line to be used
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Enable_Double_Tap_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Output Data Rate selection */
  if (ISM330DHCX_ACC_SetOutputDataRate(pObj, 416.0f) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Full scale selection */
  if (ISM330DHCX_ACC_SetFullScale(pObj, 2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable X direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_x_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable Y direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_y_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable Z direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_z_set(&(pObj->Ctx), PROPERTY_ENABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Set tap threshold. */
  if (ism330dhcx_tap_threshold_x_set(&(pObj->Ctx), 0x08) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Set tap shock time window. */
  if (ism330dhcx_tap_shock_set(&(pObj->Ctx), 0x03) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Set tap quiet time window. */
  if (ism330dhcx_tap_quiet_set(&(pObj->Ctx), 0x03) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Set tap duration time window. */
  if (ism330dhcx_tap_dur_set(&(pObj->Ctx), 0x08) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Single and double tap enabled. */
  if (ism330dhcx_tap_mode_set(&(pObj->Ctx), ISM330DHCX_BOTH_SINGLE_DOUBLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable double tap event on either INT1 or INT2 pin */
  switch (IntPin)
  {
    case ISM330DHCX_INT1_PIN:
      if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val1.md1_cfg.int1_double_tap = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    case ISM330DHCX_INT2_PIN:
      if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val2.md2_cfg.int2_double_tap = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Disable double tap detection
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Disable_Double_Tap_Detection(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Disable double tap event on both INT1 and INT2 pins */
  if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val1.md1_cfg.int1_double_tap = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val2.md2_cfg.int2_double_tap = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Only single tap enabled. */
  if (ism330dhcx_tap_mode_set(&(pObj->Ctx), ISM330DHCX_ONLY_SINGLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset tap duration time window. */
  if (ism330dhcx_tap_dur_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset tap quiet time window. */
  if (ism330dhcx_tap_quiet_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset tap shock time window. */
  if (ism330dhcx_tap_shock_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset tap threshold. */
  if (ism330dhcx_tap_threshold_x_set(&(pObj->Ctx), 0x00) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Disable Z direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_z_set(&(pObj->Ctx), PROPERTY_DISABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Disable Y direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_y_set(&(pObj->Ctx), PROPERTY_DISABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Disable X direction in tap recognition. */
  if (ism330dhcx_tap_detection_on_x_set(&(pObj->Ctx), PROPERTY_DISABLE) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set tap threshold
  * @param  pObj the device pObj
  * @param  Threshold tap threshold
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_Tap_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Threshold)
{
  /* Set tap threshold. */
  if (ism330dhcx_tap_threshold_x_set(&(pObj->Ctx), Threshold) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set tap shock time
  * @param  pObj the device pObj
  * @param  Time tap shock time
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_Tap_Shock_Time(ISM330DHCX_Object_t *pObj, uint8_t Time)
{
  /* Set tap shock time window. */
  if (ism330dhcx_tap_shock_set(&(pObj->Ctx), Time) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set tap quiet time
  * @param  pObj the device pObj
  * @param  Time tap quiet time
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_Tap_Quiet_Time(ISM330DHCX_Object_t *pObj, uint8_t Time)
{
  /* Set tap quiet time window. */
  if (ism330dhcx_tap_quiet_set(&(pObj->Ctx), Time) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set tap duration time
  * @param  pObj the device pObj
  * @param  Time tap duration time
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_Tap_Duration_Time(ISM330DHCX_Object_t *pObj, uint8_t Time)
{
  /* Set tap duration time window. */
  if (ism330dhcx_tap_dur_set(&(pObj->Ctx), Time) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Enable 6D orientation detection
  * @param  pObj the device pObj
  * @param  IntPin interrupt pin line to be used
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Enable_6D_Orientation(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin)
{
  int32_t ret = ISM330DHCX_OK;
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Output Data Rate selection */
  if (ISM330DHCX_ACC_SetOutputDataRate(pObj, 416.0f) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Full scale selection */
  if (ISM330DHCX_ACC_SetFullScale(pObj, 2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* 6D orientation enabled. */
  if (ism330dhcx_6d_threshold_set(&(pObj->Ctx), ISM330DHCX_DEG_60) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Enable 6D orientation event on either INT1 or INT2 pin */
  switch (IntPin)
  {
    case ISM330DHCX_INT1_PIN:
      if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val1.md1_cfg.int1_6d = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    case ISM330DHCX_INT2_PIN:
      if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }

      val2.md2_cfg.int2_6d = PROPERTY_ENABLE;

      if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
      {
        return ISM330DHCX_ERROR;
      }
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  return ret;
}

/**
  * @brief  Disable 6D orientation detection
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Disable_6D_Orientation(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int1_route_t val1;
  ism330dhcx_pin_int2_route_t val2;

  /* Disable 6D orientation event on both INT1 and INT2 pins */
  if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val1.md1_cfg.int1_6d = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &val1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  val2.md2_cfg.int2_6d = PROPERTY_DISABLE;

  if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &val2) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  /* Reset 6D orientation. */
  if (ism330dhcx_6d_threshold_set(&(pObj->Ctx), ISM330DHCX_DEG_80) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set 6D orientation threshold
  * @param  pObj the device pObj
  * @param  Threshold free fall detection threshold
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_6D_Orientation_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Threshold)
{
  if (ism330dhcx_6d_threshold_set(&(pObj->Ctx), (ism330dhcx_sixd_ths_t)Threshold) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the status of XLow orientation
  * @param  pObj the device pObj
  * @param  XLow the status of XLow orientation
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_6D_Orientation_XL(ISM330DHCX_Object_t *pObj, uint8_t *XLow)
{
  ism330dhcx_d6d_src_t data;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_D6D_SRC, (uint8_t *)&data, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  *XLow = data.xl;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the status of XHigh orientation
  * @param  pObj the device pObj
  * @param  XHigh the status of XHigh orientation
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_6D_Orientation_XH(ISM330DHCX_Object_t *pObj, uint8_t *XHigh)
{
  ism330dhcx_d6d_src_t data;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_D6D_SRC, (uint8_t *)&data, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  *XHigh = data.xh;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the status of YLow orientation
  * @param  pObj the device pObj
  * @param  YLow the status of YLow orientation
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_6D_Orientation_YL(ISM330DHCX_Object_t *pObj, uint8_t *YLow)
{
  ism330dhcx_d6d_src_t data;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_D6D_SRC, (uint8_t *)&data, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  *YLow = data.yl;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the status of YHigh orientation
  * @param  pObj the device pObj
  * @param  YHigh the status of YHigh orientation
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_6D_Orientation_YH(ISM330DHCX_Object_t *pObj, uint8_t *YHigh)
{
  ism330dhcx_d6d_src_t data;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_D6D_SRC, (uint8_t *)&data, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  *YHigh = data.yh;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the status of ZLow orientation
  * @param  pObj the device pObj
  * @param  ZLow the status of ZLow orientation
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_6D_Orientation_ZL(ISM330DHCX_Object_t *pObj, uint8_t *ZLow)
{
  ism330dhcx_d6d_src_t data;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_D6D_SRC, (uint8_t *)&data, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  *ZLow = data.zl;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the status of ZHigh orientation
  * @param  pObj the device pObj
  * @param  ZHigh the status of ZHigh orientation
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_6D_Orientation_ZH(ISM330DHCX_Object_t *pObj, uint8_t *ZHigh)
{
  ism330dhcx_d6d_src_t data;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_D6D_SRC, (uint8_t *)&data, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  *ZHigh = data.zh;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the status of all hardware events
  * @param  pObj the device pObj
  * @param  Status the status of all hardware events
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_Event_Status(ISM330DHCX_Object_t *pObj, ISM330DHCX_Event_Status_t *Status)
{
  ism330dhcx_wake_up_src_t wake_up_src;
  ism330dhcx_tap_src_t tap_src;
  ism330dhcx_d6d_src_t d6d_src;
  ism330dhcx_md1_cfg_t md1_cfg;
  ism330dhcx_md2_cfg_t md2_cfg;
  ism330dhcx_int1_ctrl_t int1_ctrl;

  (void)memset((void *)Status, 0x0, sizeof(ISM330DHCX_Event_Status_t));

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_WAKE_UP_SRC, (uint8_t *)&wake_up_src, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_TAP_SRC, (uint8_t *)&tap_src, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_D6D_SRC, (uint8_t *)&d6d_src, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_MD1_CFG, (uint8_t *)&md1_cfg, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_MD2_CFG, (uint8_t *)&md2_cfg, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, (uint8_t *)&int1_ctrl, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if ((md1_cfg.int1_ff == 1U) || (md2_cfg.int2_ff == 1U))
  {
    if (wake_up_src.ff_ia == 1U)
    {
      Status->FreeFallStatus = 1;
    }
  }

  if ((md1_cfg.int1_wu == 1U) || (md2_cfg.int2_wu == 1U))
  {
    if (wake_up_src.wu_ia == 1U)
    {
      Status->WakeUpStatus = 1;
    }
  }

  if ((md1_cfg.int1_single_tap == 1U) || (md2_cfg.int2_single_tap == 1U))
  {
    if (tap_src.single_tap == 1U)
    {
      Status->TapStatus = 1;
    }
  }

  if ((md1_cfg.int1_double_tap == 1U) || (md2_cfg.int2_double_tap == 1U))
  {
    if (tap_src.double_tap == 1U)
    {
      Status->DoubleTapStatus = 1;
    }
  }

  if ((md1_cfg.int1_6d == 1U) || (md2_cfg.int2_6d == 1U))
  {
    if (d6d_src.d6d_ia == 1U)
    {
      Status->D6DOrientationStatus = 1;
    }
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set self test
  * @param  pObj the device pObj
  * @param  val the value of st_xl in reg CTRL5_C
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Set_SelfTest(ISM330DHCX_Object_t *pObj, uint8_t val)
{
  ism330dhcx_st_xl_t reg;

  reg = (val == 0U)  ? ISM330DHCX_XL_ST_DISABLE
        : (val == 1U)  ? ISM330DHCX_XL_ST_POSITIVE
        : (val == 2U)  ? ISM330DHCX_XL_ST_NEGATIVE
        :                ISM330DHCX_XL_ST_DISABLE;

  if (ism330dhcx_xl_self_test_set(&(pObj->Ctx), reg) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX ACC data ready bit value
  * @param  pObj the device pObj
  * @param  Status the status of data ready bit
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_DRDY_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status)
{
  if (ism330dhcx_xl_flag_data_ready_get(&(pObj->Ctx), Status) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX ACC initialization status
  * @param  pObj the device pObj
  * @param  Status 1 if initialized, 0 otherwise
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Get_Init_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status)
{
  if (pObj == NULL)
  {
    return ISM330DHCX_ERROR;
  }

  *Status = pObj->is_initialized;

  return ISM330DHCX_OK;
}

/**
  * @brief  Set HP filter
  * @param  pObj the device pObj
  * @param  CutOff frequency
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Enable_HP_Filter(ISM330DHCX_Object_t *pObj, ism330dhcx_hp_slope_xl_en_t CutOff)
{
  if (ism330dhcx_xl_hp_path_on_out_set(&(pObj->Ctx), CutOff) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }
  return ISM330DHCX_OK;
}

/**
  * @brief  Set self test
  * @param  pObj the device pObj
  * @param  val the value of st_xl in reg CTRL5_C
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_Set_SelfTest(ISM330DHCX_Object_t *pObj, uint8_t val)
{
  ism330dhcx_st_g_t reg;

  reg = (val == 0U)  ? ISM330DHCX_GY_ST_DISABLE
        : (val == 1U)  ? ISM330DHCX_GY_ST_POSITIVE
        : (val == 3U)  ? ISM330DHCX_GY_ST_NEGATIVE
        :                ISM330DHCX_GY_ST_DISABLE;


  if (ism330dhcx_gy_self_test_set(&(pObj->Ctx), reg) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX GYRO data ready bit value
  * @param  pObj the device pObj
  * @param  Status the status of data ready bit
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_Get_DRDY_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status)
{
  if (ism330dhcx_gy_flag_data_ready_get(&(pObj->Ctx), Status) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX GYRO initialization status
  * @param  pObj the device pObj
  * @param  Status 1 if initialized, 0 otherwise
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_Get_Init_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status)
{
  if (pObj == NULL)
  {
    return ISM330DHCX_ERROR;
  }

  *Status = pObj->is_initialized;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO number of samples
  * @param  pObj the device pObj
  * @param  NumSamples number of samples
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Get_Num_Samples(ISM330DHCX_Object_t *pObj, uint16_t *NumSamples)
{
  if (ism330dhcx_fifo_data_level_get(&(pObj->Ctx), NumSamples) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO full status
  * @param  pObj the device pObj
  * @param  Status FIFO full status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Get_Full_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_FIFO_STATUS1, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_FIFO_STATUS2, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  *Status = reg.fifo_status2.fifo_full_ia;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO all status
  * @param  pObj the device pObj
  * @param  Status FIFO register content
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Get_All_Status(ISM330DHCX_Object_t *pObj, ISM330DHCX_Fifo_Status_t *Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_FIFO_STATUS1, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_FIFO_STATUS2, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  Status->FifoWatermark = reg.fifo_status2.fifo_wtm_ia;
  Status->FifoFull = reg.fifo_status2.fifo_full_ia;
  Status->FifoOverrun = reg.fifo_status2.fifo_ovr_ia;
  Status->FifoOverrunLatched = reg.fifo_status2.over_run_latched;
  Status->CounterBdr = reg.fifo_status2.counter_bdr_ia;

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO ACC ODR value
  * @param  pObj the device pObj
  * @param  Odr FIFO ODR value
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_ACC_Set_BDR(ISM330DHCX_Object_t *pObj, float Bdr)
{
  ism330dhcx_bdr_xl_t new_odr;

  new_odr = (Bdr <=   12.5f) ? ISM330DHCX_XL_BATCHED_AT_12Hz5
            : (Bdr <=   26.0f) ? ISM330DHCX_XL_BATCHED_AT_26Hz
            : (Bdr <=   52.0f) ? ISM330DHCX_XL_BATCHED_AT_52Hz
            : (Bdr <=  104.0f) ? ISM330DHCX_XL_BATCHED_AT_104Hz
            : (Bdr <=  208.0f) ? ISM330DHCX_XL_BATCHED_AT_208Hz
            : (Bdr <=  417.0f) ? ISM330DHCX_XL_BATCHED_AT_417Hz
            : (Bdr <=  833.0f) ? ISM330DHCX_XL_BATCHED_AT_833Hz
            : (Bdr <= 1667.0f) ? ISM330DHCX_XL_BATCHED_AT_1667Hz
            : (Bdr <= 3333.0f) ? ISM330DHCX_XL_BATCHED_AT_3333Hz
            :                    ISM330DHCX_XL_BATCHED_AT_6667Hz;

  if (ism330dhcx_fifo_xl_batch_set(&(pObj->Ctx), new_odr) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO GYRO ODR value
  * @param  pObj the device pObj
  * @param  Odr FIFO ODR value
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_GYRO_Set_BDR(ISM330DHCX_Object_t *pObj, float Bdr)
{
  ism330dhcx_bdr_gy_t new_odr;

  new_odr = (Bdr <=   12.5f) ? ISM330DHCX_GY_BATCHED_AT_12Hz5
            : (Bdr <=   26.0f) ? ISM330DHCX_GY_BATCHED_AT_26Hz
            : (Bdr <=   52.0f) ? ISM330DHCX_GY_BATCHED_AT_52Hz
            : (Bdr <=  104.0f) ? ISM330DHCX_GY_BATCHED_AT_104Hz
            : (Bdr <=  208.0f) ? ISM330DHCX_GY_BATCHED_AT_208Hz
            : (Bdr <=  417.0f) ? ISM330DHCX_GY_BATCHED_AT_417Hz
            : (Bdr <=  833.0f) ? ISM330DHCX_GY_BATCHED_AT_833Hz
            : (Bdr <= 1667.0f) ? ISM330DHCX_GY_BATCHED_AT_1667Hz
            : (Bdr <= 3333.0f) ? ISM330DHCX_GY_BATCHED_AT_3333Hz
            :                    ISM330DHCX_GY_BATCHED_AT_6667Hz;

  if (ism330dhcx_fifo_gy_batch_set(&(pObj->Ctx), new_odr) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO full interrupt on INT1 pin
  * @param  pObj the device pObj
  * @param  Status FIFO full interrupt on INT1 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_INT1_FIFO_Full(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int1_ctrl.int1_fifo_full = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO threshold interrupt on INT1 pin
  * @param  pObj the device pObj
  * @param  Status FIFO threshold interrupt on INT1 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_INT1_FIFO_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int1_ctrl.int1_fifo_th = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO overrun interrupt on INT1 pin
  * @param  pObj the device pObj
  * @param  Status FIFO overrun interrupt on INT1 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_INT1_FIFO_Overrun(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int1_ctrl.int1_fifo_ovr = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO full interrupt on INT2 pin
  * @param  pObj the device pObj
  * @param  Status FIFO full interrupt on INT2 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_INT2_FIFO_Full(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int2_ctrl.int2_fifo_full = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO threshold interrupt on INT2 pin
  * @param  pObj the device pObj
  * @param  Status FIFO threshold interrupt on INT2 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_INT2_FIFO_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int2_ctrl.int2_fifo_th = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO overrun interrupt on INT2 pin
  * @param  pObj the device pObj
  * @param  Status FIFO overrun interrupt on INT2 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_INT2_FIFO_Overrun(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int2_ctrl.int2_fifo_ovr = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO watermark level
  * @param  pObj the device pObj
  * @param  Watermark FIFO watermark level
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_Watermark_Level(ISM330DHCX_Object_t *pObj, uint16_t Watermark)
{
  if (ism330dhcx_fifo_watermark_set(&(pObj->Ctx), Watermark) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO stop on watermark
  * @param  pObj the device pObj
  * @param  Status FIFO stop on watermark status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_Stop_On_Fth(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  if (ism330dhcx_fifo_stop_on_wtm_set(&(pObj->Ctx), Status) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO mode
  * @param  pObj the device pObj
  * @param  Mode FIFO mode
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_Mode(ISM330DHCX_Object_t *pObj, uint8_t Mode)
{
  int32_t ret = ISM330DHCX_OK;

  /* Verify that the passed parameter contains one of the valid values. */
  switch ((ism330dhcx_fifo_mode_t)Mode)
  {
    case ISM330DHCX_BYPASS_MODE:
    case ISM330DHCX_FIFO_MODE:
    case ISM330DHCX_STREAM_TO_FIFO_MODE:
    case ISM330DHCX_BYPASS_TO_STREAM_MODE:
    case ISM330DHCX_STREAM_MODE:
      break;

    default:
      ret = ISM330DHCX_ERROR;
      break;
  }

  if (ret == ISM330DHCX_ERROR)
  {
    return ret;
  }

  if (ism330dhcx_fifo_mode_set(&(pObj->Ctx), (ism330dhcx_fifo_mode_t)Mode) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ret;
}

/**
  * @brief  Get the ISM330DHCX FIFO tag
  * @param  pObj the device pObj
  * @param  Tag FIFO tag
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Get_Tag(ISM330DHCX_Object_t *pObj, uint8_t *Tag)
{
  ism330dhcx_fifo_tag_t tag_local;

  if (ism330dhcx_fifo_sensor_tag_get(&(pObj->Ctx), &tag_local) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  *Tag = (uint8_t)tag_local;

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO raw data
  * @param  pObj the device pObj
  * @param  Data FIFO raw data array [6]
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Get_Data(ISM330DHCX_Object_t *pObj, uint8_t *Data)
{
  if (ism330dhcx_fifo_out_raw_get(&(pObj->Ctx), Data) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO accelero single sample (16-bit data per 3 axes) and calculate acceleration [mg]
  * @param  pObj the device pObj
  * @param  Acceleration FIFO accelero axes [mg]
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_ACC_Get_Axes(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *Acceleration)
{
  uint8_t data[6];
  int16_t data_raw[3];
  float sensitivity = 0.0f;
  float acceleration_float[3];

  if (ISM330DHCX_FIFO_Get_Data(pObj, data) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  data_raw[0] = ((int16_t)data[1] << 8) | data[0];
  data_raw[1] = ((int16_t)data[3] << 8) | data[2];
  data_raw[2] = ((int16_t)data[5] << 8) | data[4];

  if (ISM330DHCX_ACC_GetSensitivity(pObj, &sensitivity) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  acceleration_float[0] = (float)data_raw[0] * sensitivity;
  acceleration_float[1] = (float)data_raw[1] * sensitivity;
  acceleration_float[2] = (float)data_raw[2] * sensitivity;

  Acceleration->x = (int32_t)acceleration_float[0];
  Acceleration->y = (int32_t)acceleration_float[1];
  Acceleration->z = (int32_t)acceleration_float[2];

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO gyro single sample (16-bit data per 3 axes) and calculate angular velocity [mDPS]
  * @param  pObj the device pObj
  * @param  AngularVelocity FIFO gyro axes [mDPS]
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_GYRO_Get_Axes(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *AngularVelocity)
{
  uint8_t data[6];
  int16_t data_raw[3];
  float sensitivity = 0.0f;
  float angular_velocity_float[3];

  if (ISM330DHCX_FIFO_Get_Data(pObj, data) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  data_raw[0] = ((int16_t)data[1] << 8) | data[0];
  data_raw[1] = ((int16_t)data[3] << 8) | data[2];
  data_raw[2] = ((int16_t)data[5] << 8) | data[4];

  if (ISM330DHCX_GYRO_GetSensitivity(pObj, &sensitivity) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  angular_velocity_float[0] = (float)data_raw[0] * sensitivity;
  angular_velocity_float[1] = (float)data_raw[1] * sensitivity;
  angular_velocity_float[2] = (float)data_raw[2] * sensitivity;

  AngularVelocity->x = (int32_t)angular_velocity_float[0];
  AngularVelocity->y = (int32_t)angular_velocity_float[1];
  AngularVelocity->z = (int32_t)angular_velocity_float[2];

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO full interrupt on INT1 pin
  * @param  pObj the device pObj
  * @param  Status FIFO full interrupt on INT1 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Full_Set_INT1(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int1_ctrl.int1_fifo_full = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT1_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO accelero single sample (16-bit data) and calculate acceleration [mg]
  * @param  pObj the device pObj
  * @param  Acceleration FIFO single accelero axis [mg]
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_ACC_Get_Axis(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *Acceleration)
{
  uint8_t data[6];
  int16_t data_raw[3];
  float sensitivity = 0.0f;
  float acceleration_float[3];

  if (ISM330DHCX_FIFO_Get_Data(pObj, data) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  data_raw[0] = ((int16_t)data[1] << 8) | data[0];
  data_raw[1] = ((int16_t)data[3] << 8) | data[2];
  data_raw[2] = ((int16_t)data[5] << 8) | data[4];

  if (ISM330DHCX_ACC_GetSensitivity(pObj, &sensitivity) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  acceleration_float[0] = (float)data_raw[0] * sensitivity;
  acceleration_float[1] = (float)data_raw[1] * sensitivity;
  acceleration_float[2] = (float)data_raw[2] * sensitivity;

  Acceleration->x = (int32_t)acceleration_float[0];
  Acceleration->y = (int32_t)acceleration_float[1];
  Acceleration->z = (int32_t)acceleration_float[2];

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO accelero single word (16-bit data)
  * @param  pObj the device pObj
  * @param  Acceleration FIFO single data
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Get_Data_Word(ISM330DHCX_Object_t *pObj, int16_t *data_raw)
{
  uint8_t data[6];

  if (ISM330DHCX_FIFO_Get_Data(pObj, data) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  data_raw[0] = ((int16_t)data[1] << 8) | data[0];
  data_raw[1] = ((int16_t)data[3] << 8) | data[2];
  data_raw[2] = ((int16_t)data[5] << 8) | data[4];

  return ISM330DHCX_OK;
}

/**
  * @brief  Get the ISM330DHCX FIFO gyro single sample (16-bit data) and calculate angular velocity [mDPS]
  * @param  pObj the device pObj
  * @param  AngularVelocity FIFO single gyro axis [mDPS]
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_GYRO_Get_Axis(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t  *AngularVelocity)
{
  uint8_t data[6];
  int16_t data_raw[3];
  float sensitivity = 0.0f;
  float angular_velocity_float[3];

  if (ISM330DHCX_FIFO_Get_Data(pObj, data) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  data_raw[0] = ((int16_t)data[1] << 8) | data[0];
  data_raw[1] = ((int16_t)data[3] << 8) | data[2];
  data_raw[2] = ((int16_t)data[5] << 8) | data[4];

  if (ISM330DHCX_GYRO_GetSensitivity(pObj, &sensitivity) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  angular_velocity_float[0] = (float)data_raw[0] * sensitivity;
  angular_velocity_float[1] = (float)data_raw[1] * sensitivity;
  angular_velocity_float[2] = (float)data_raw[2] * sensitivity;

  AngularVelocity->x = (int32_t)angular_velocity_float[0];
  AngularVelocity->y = (int32_t)angular_velocity_float[1];
  AngularVelocity->z = (int32_t)angular_velocity_float[2];

  return ISM330DHCX_OK;
}

/**
  * @brief  Enable ISM330DHCX accelerometer DRDY interrupt on INT1
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Enable_DRDY_On_INT1(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int1_route_t pin_int1_route;

  /* Enable accelerometer DRDY Interrupt on INT1 */
  if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &pin_int1_route) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pin_int1_route.int1_ctrl.int1_drdy_xl = 1;
  pin_int1_route.int1_ctrl.int1_drdy_g = 0;

  if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &pin_int1_route) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Disable ISM330DHCX accelerometer DRDY interrupt on INT1
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_ACC_Disable_DRDY_On_INT1(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int1_route_t pin_int1_route;

  /* Disable accelerometer DRDY Interrupt on INT1 */
  if (ism330dhcx_pin_int1_route_get(&(pObj->Ctx), &pin_int1_route) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pin_int1_route.int1_ctrl.int1_drdy_xl = 0;

  if (ism330dhcx_pin_int1_route_set(&(pObj->Ctx), &pin_int1_route) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Enable ISM330DHCX gyroscope DRDY interrupt on INT2
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_Enable_DRDY_On_INT2(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int2_route_t pin_int2_route;

  /* Enable gyroscope DRDY Interrupt on INT2 */
  if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &pin_int2_route) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pin_int2_route.int2_ctrl.int2_drdy_xl = 0;
  pin_int2_route.int2_ctrl.int2_drdy_g = 1;

  if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &pin_int2_route) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Disable ISM330DHCX gyroscope DRDY interrupt on INT2
  * @param  pObj the device pObj
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_GYRO_Disable_DRDY_On_INT2(ISM330DHCX_Object_t *pObj)
{
  ism330dhcx_pin_int2_route_t pin_int2_route;

  /* Disable gyroscope DRDY Interrupt on INT2 */
  if (ism330dhcx_pin_int2_route_get(&(pObj->Ctx), &pin_int2_route) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  pin_int2_route.int2_ctrl.int2_drdy_g = 0;

  if (ism330dhcx_pin_int2_route_set(&(pObj->Ctx), &pin_int2_route) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set ISM330DHCX DRDY mode
  * @param  pObj the device pObj
  * @param  Mode DRDY mode
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_DRDY_Set_Mode(ISM330DHCX_Object_t *pObj, uint8_t Mode)
{
  /* Set DRDY mode */
  if (ism330dhcx_data_ready_mode_set(&(pObj->Ctx), (ism330dhcx_dataready_pulsed_t)Mode) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @}
  */

/** @defgroup ISM330DHCX_Private_Functions ISM330DHCX Private Functions
  * @{
  */

/**
  * @brief  Set the ISM330DHCX accelerometer sensor output data rate when enabled
  * @param  pObj the device pObj
  * @param  Odr the functional output data rate to be set
  * @retval 0 in case of success, an error code otherwise
  */
static int32_t ISM330DHCX_ACC_SetOutputDataRate_When_Enabled(ISM330DHCX_Object_t *pObj, float Odr)
{
  ism330dhcx_odr_xl_t new_odr;

  new_odr = (Odr <=   12.5f) ? ISM330DHCX_XL_ODR_12Hz5
            : (Odr <=   26.0f) ? ISM330DHCX_XL_ODR_26Hz
            : (Odr <=   52.0f) ? ISM330DHCX_XL_ODR_52Hz
            : (Odr <=  104.0f) ? ISM330DHCX_XL_ODR_104Hz
            : (Odr <=  208.0f) ? ISM330DHCX_XL_ODR_208Hz
            : (Odr <=  416.0f) ? ISM330DHCX_XL_ODR_416Hz
            : (Odr <=  833.0f) ? ISM330DHCX_XL_ODR_833Hz
            : (Odr <= 1666.0f) ? ISM330DHCX_XL_ODR_1666Hz
            : (Odr <= 3332.0f) ? ISM330DHCX_XL_ODR_3332Hz
            :                    ISM330DHCX_XL_ODR_6667Hz;

  /* Output data rate selection. */
  if (ism330dhcx_xl_data_rate_set(&(pObj->Ctx), new_odr) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX accelerometer sensor output data rate when disabled
  * @param  pObj the device pObj
  * @param  Odr the functional output data rate to be set
  * @retval 0 in case of success, an error code otherwise
  */
static int32_t ISM330DHCX_ACC_SetOutputDataRate_When_Disabled(ISM330DHCX_Object_t *pObj, float Odr)
{
  pObj->acc_odr = (Odr <=   12.5f) ? ISM330DHCX_XL_ODR_12Hz5
                  : (Odr <=   26.0f) ? ISM330DHCX_XL_ODR_26Hz
                  : (Odr <=   52.0f) ? ISM330DHCX_XL_ODR_52Hz
                  : (Odr <=  104.0f) ? ISM330DHCX_XL_ODR_104Hz
                  : (Odr <=  208.0f) ? ISM330DHCX_XL_ODR_208Hz
                  : (Odr <=  416.0f) ? ISM330DHCX_XL_ODR_416Hz
                  : (Odr <=  833.0f) ? ISM330DHCX_XL_ODR_833Hz
                  : (Odr <= 1666.0f) ? ISM330DHCX_XL_ODR_1666Hz
                  : (Odr <= 3332.0f) ? ISM330DHCX_XL_ODR_3332Hz
                  :                    ISM330DHCX_XL_ODR_6667Hz;

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX gyroscope sensor output data rate when enabled
  * @param  pObj the device pObj
  * @param  Odr the functional output data rate to be set
  * @retval 0 in case of success, an error code otherwise
  */
static int32_t ISM330DHCX_GYRO_SetOutputDataRate_When_Enabled(ISM330DHCX_Object_t *pObj, float Odr)
{
  ism330dhcx_odr_g_t new_odr;

  new_odr = (Odr <=   12.5f) ? ISM330DHCX_GY_ODR_12Hz5
            : (Odr <=   26.0f) ? ISM330DHCX_GY_ODR_26Hz
            : (Odr <=   52.0f) ? ISM330DHCX_GY_ODR_52Hz
            : (Odr <=  104.0f) ? ISM330DHCX_GY_ODR_104Hz
            : (Odr <=  208.0f) ? ISM330DHCX_GY_ODR_208Hz
            : (Odr <=  416.0f) ? ISM330DHCX_GY_ODR_416Hz
            : (Odr <=  833.0f) ? ISM330DHCX_GY_ODR_833Hz
            : (Odr <= 1666.0f) ? ISM330DHCX_GY_ODR_1666Hz
            : (Odr <= 3332.0f) ? ISM330DHCX_GY_ODR_3332Hz
            :                    ISM330DHCX_GY_ODR_6667Hz;

  /* Output data rate selection. */
  if (ism330dhcx_gy_data_rate_set(&(pObj->Ctx), new_odr) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX gyroscope sensor output data rate when disabled
  * @param  pObj the device pObj
  * @param  Odr the functional output data rate to be set
  * @retval 0 in case of success, an error code otherwise
  */
static int32_t ISM330DHCX_GYRO_SetOutputDataRate_When_Disabled(ISM330DHCX_Object_t *pObj, float Odr)
{
  pObj->gyro_odr = (Odr <=   12.5f) ? ISM330DHCX_GY_ODR_12Hz5
                   : (Odr <=   26.0f) ? ISM330DHCX_GY_ODR_26Hz
                   : (Odr <=   52.0f) ? ISM330DHCX_GY_ODR_52Hz
                   : (Odr <=  104.0f) ? ISM330DHCX_GY_ODR_104Hz
                   : (Odr <=  208.0f) ? ISM330DHCX_GY_ODR_208Hz
                   : (Odr <=  416.0f) ? ISM330DHCX_GY_ODR_416Hz
                   : (Odr <=  833.0f) ? ISM330DHCX_GY_ODR_833Hz
                   : (Odr <= 1666.0f) ? ISM330DHCX_GY_ODR_1666Hz
                   : (Odr <= 3332.0f) ? ISM330DHCX_GY_ODR_3332Hz
                   :                    ISM330DHCX_GY_ODR_6667Hz;

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO full interrupt on INT2 pin
  * @param  pObj the device pObj
  * @param  Status FIFO full interrupt on INT2 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_FIFO_Set_INT2_Drdy(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int2_ctrl.int2_fifo_full = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}

/**
  * @brief  Set the ISM330DHCX FIFO full interrupt on INT2 pin
  * @param  pObj the device pObj
  * @param  Status DRDY interrupt on INT2 pin status
  * @retval 0 in case of success, an error code otherwise
  */
int32_t ISM330DHCX_Set_INT2_Drdy(ISM330DHCX_Object_t *pObj, uint8_t Status)
{
  ism330dhcx_reg_t reg;

  if (ism330dhcx_read_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)
  {
    return ISM330DHCX_ERROR;
  }

  reg.int2_ctrl.int2_drdy_xl = Status;

  if (ism330dhcx_write_reg(&(pObj->Ctx), ISM330DHCX_INT2_CTRL, &reg.byte, 1) != ISM330DHCX_OK)

  {
    return ISM330DHCX_ERROR;
  }

  return ISM330DHCX_OK;
}
/**
  * @brief  Wrap Read register component function to Bus IO function
  * @param  Handle the device handler
  * @param  Reg the register address
  * @param  pData the stored data pointer
  * @param  Length the length
  * @retval 0 in case of success, an error code otherwise
  */
static int32_t ReadRegWrap(void *Handle, uint8_t Reg, uint8_t *pData, uint16_t Length)
{
  ISM330DHCX_Object_t *pObj = (ISM330DHCX_Object_t *)Handle;

  return pObj->IO.ReadReg(pObj->IO.Address, Reg, pData, Length);
}

/**
  * @brief  Wrap Write register component function to Bus IO function
  * @param  Handle the device handler
  * @param  Reg the register address
  * @param  pData the stored data pointer
  * @param  Length the length
  * @retval 0 in case of success, an error code otherwise
  */
static int32_t WriteRegWrap(void *Handle, uint8_t Reg, uint8_t *pData, uint16_t Length)
{
  ISM330DHCX_Object_t *pObj = (ISM330DHCX_Object_t *)Handle;

  return pObj->IO.WriteReg(pObj->IO.Address, Reg, pData, Length);
}

/**
  * @}
  */

/**
  * @}
  */

/**
  * @}
  */

/**
  * @}
  */
