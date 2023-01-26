/**
******************************************************************************
* @file    iis3dwb.c
* @author  SRA
* @brief   IIS3DWB driver file
******************************************************************************
* @attention
*
* <h2><center>&copy; Copyright (c) 2021 STMicroelectronics. 
* All rights reserved.</center></h2>
*
* This software component is licensed by ST under BSD 3-Clause license,
* the "License"; You may not use this file except in compliance with the 
* License. You may obtain a copy of the License at:
*                        opensource.org/licenses/BSD-3-Clause
*
******************************************************************************
*/

/* Includes ------------------------------------------------------------------*/
#include "iis3dwb.h"

/** @addtogroup BSP BSP
 * @{
 */

/** @addtogroup Component Component
 * @{
 */

/** @defgroup IIS3DWB IIS3DWB
 * @{
 */

/** @defgroup IIS3DWB_Exported_Variables IIS3DWB Exported Variables
 * @{
 */

IIS3DWB_CommonDrv_t IIS3DWB_COMMON_Driver =
{
  IIS3DWB_Init,
  IIS3DWB_DeInit,
  IIS3DWB_ReadID,
  IIS3DWB_GetCapabilities,
};

IIS3DWB_ACC_Drv_t IIS3DWB_ACC_Driver =
{
  IIS3DWB_ACC_Enable,
  IIS3DWB_ACC_Disable,
  IIS3DWB_ACC_GetSensitivity,
  IIS3DWB_ACC_GetOutputDataRate,
  IIS3DWB_ACC_SetOutputDataRate,
  IIS3DWB_ACC_GetFullScale,
  IIS3DWB_ACC_SetFullScale,
  IIS3DWB_ACC_GetAxes,
  IIS3DWB_ACC_GetAxesRaw,
};

/**
 * @}
 */

/** @defgroup IIS3DWB_Private_Function_Prototypes IIS3DWB Private Function Prototypes
 * @{
 */

static int32_t ReadRegWrap(void *Handle, uint8_t Reg, uint8_t *pData, uint16_t Length);
static int32_t WriteRegWrap(void *Handle, uint8_t Reg, uint8_t *pData, uint16_t Length);

/**
 * @}
 */

/** @defgroup IIS3DWB_Exported_Functions IIS3DWB Exported Functions
 * @{
 */

/**
 * @brief  Register Component Bus IO operations
 * @param  pObj the device pObj
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_RegisterBusIO(IIS3DWB_Object_t *pObj, IIS3DWB_IO_t *pIO)
{
  int32_t ret;

  if (pObj == NULL)
  {
    ret = IIS3DWB_ERROR;
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
    pObj->Ctx.handle   = pObj;

    if (pObj->IO.Init != NULL)
    {
      ret = pObj->IO.Init();
    }
    else
    {
      ret = IIS3DWB_ERROR;
    }
  }

  return ret;
}

/**
 * @brief  Initialize the IIS3DWB sensor
 * @param  pObj the device pObj
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_Init(IIS3DWB_Object_t *pObj)
{
  /* Reset all the configuration registers in order to set correctly */
  if (iis3dwb_reset_set(&(pObj->Ctx),PROPERTY_ENABLE) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* Enable register address automatically incremented during a multiple byte
  access with a serial interface. */
  if (iis3dwb_auto_increment_set(&(pObj->Ctx), PROPERTY_ENABLE) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* Enable BDU */
  if (iis3dwb_block_data_update_set(&(pObj->Ctx), PROPERTY_ENABLE) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* FIFO mode selection */
  if (iis3dwb_fifo_mode_set(&(pObj->Ctx), IIS3DWB_BYPASS_MODE) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* Full scale selection. */
  if (iis3dwb_xl_full_scale_set(&(pObj->Ctx), IIS3DWB_2g) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  pObj->is_initialized = 1;

  return IIS3DWB_OK;
}

/**
 * @brief  Deinitialize the IIS3DWB sensor
 * @param  pObj the device pObj
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_DeInit(IIS3DWB_Object_t *pObj)
{
  /* Disable the component */
  if (IIS3DWB_ACC_Disable(pObj) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  pObj->is_initialized = 0;

  return IIS3DWB_OK;
}

/**
 * @brief  Read component ID
 * @param  pObj the device pObj
 * @param  Id the WHO_AM_I value
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ReadID(IIS3DWB_Object_t *pObj, uint8_t *Id)
{
  if (iis3dwb_device_id_get(&(pObj->Ctx), Id) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Get IIS3DWB sensor capabilities
 * @param  pObj Component object pointer
 * @param  Capabilities pointer to IIS3DWB sensor capabilities
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_GetCapabilities(IIS3DWB_Object_t *pObj, IIS3DWB_Capabilities_t *Capabilities)
{
  /* Prevent unused argument(s) compilation warning */
  (void)(pObj);

  Capabilities->Acc          = 1;
  Capabilities->Gyro         = 0;
  Capabilities->Magneto      = 0;
  Capabilities->LowPower     = 0;
  Capabilities->GyroMaxFS    = 0;
  Capabilities->AccMaxFS     = 16;
  Capabilities->MagMaxFS     = 0;
  Capabilities->GyroMaxOdr   = 0.0f;
  Capabilities->AccMaxOdr    = 26700.0f;
  Capabilities->MagMaxOdr    = 0.0f;
  return IIS3DWB_OK;
}

/**
 * @brief  Enable the IIS3DWB accelerometer sensor
 * @param  pObj the device pObj
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Enable(IIS3DWB_Object_t *pObj)
{
  /* Check if the component is already enabled */
  if (pObj->acc_is_enabled == 1U)
  {
    return IIS3DWB_OK;
  }

  pObj->acc_is_enabled = 1;

  return IIS3DWB_OK;
}

/**
 * @brief  Disable the IIS3DWB accelerometer sensor
 * @param  pObj the device pObj
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Disable(IIS3DWB_Object_t *pObj)
{
  /* Check if the component is already disabled */
  if (pObj->acc_is_enabled == 0U)
  {
    return IIS3DWB_OK;
  }

  /* Output data rate selection - power down. */
  if (iis3dwb_xl_data_rate_set(&(pObj->Ctx), IIS3DWB_XL_ODR_OFF) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  pObj->acc_is_enabled = 0;

  return IIS3DWB_OK;
}

/**
 * @brief  Get the IIS3DWB accelerometer sensor sensitivity
 * @param  pObj the device pObj
 * @param  Sensitivity pointer
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_GetSensitivity(IIS3DWB_Object_t *pObj, float *Sensitivity)
{
  int32_t ret = IIS3DWB_OK;
  iis3dwb_fs_xl_t full_scale;
  
  /* Read actual full scale selection from sensor. */
  if (iis3dwb_xl_full_scale_get(&(pObj->Ctx), &full_scale) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  switch (full_scale)
  {
  case IIS3DWB_2g:
    *Sensitivity = IIS3DWB_ACC_SENSITIVITY_FOR_FS_2G_LOPOW1_MODE;
    break;
    
  case IIS3DWB_4g:
    *Sensitivity = IIS3DWB_ACC_SENSITIVITY_FOR_FS_4G_LOPOW1_MODE;
    break;
    
  case IIS3DWB_8g:
    *Sensitivity = IIS3DWB_ACC_SENSITIVITY_FOR_FS_8G_LOPOW1_MODE;
    break;
    
  case IIS3DWB_16g:
    *Sensitivity = IIS3DWB_ACC_SENSITIVITY_FOR_FS_16G_LOPOW1_MODE;
    break;
    
  default:
    *Sensitivity = -1.0f;
    ret = IIS3DWB_ERROR;
    break;
  }
  
  return ret;
}

/**
 * @brief  Get the IIS3DWB accelerometer sensor output data rate
 * @param  pObj the device pObj
 * @param  odr pointer where the output data rate is written
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_GetOutputDataRate(IIS3DWB_Object_t *pObj, float *odr)
{
  int32_t ret = IIS3DWB_OK;
  iis3dwb_odr_xl_t odr_low_level;
  
  if (iis3dwb_xl_data_rate_get(&(pObj->Ctx), &odr_low_level) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  switch (odr_low_level)
  {
  case IIS3DWB_XL_ODR_OFF:
    *odr =  0.0f;
    break;
  case IIS3DWB_XL_ODR_26k7Hz:
    *odr = 26700.0f;
    break;
  default:
    *odr = -1.0f;
    ret = IIS3DWB_ERROR;
    break;
  }
  
  return ret;
}

/**
 * @brief  Set the IIS3DWB accelerometer sensor output data rate
 * @param  pObj the device pObj
 * @param  Odr the output data rate value to be set
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_SetOutputDataRate(IIS3DWB_Object_t *pObj, float Odr)
{
  iis3dwb_odr_xl_t new_odr;

  new_odr = (Odr <=    1.0f) ? IIS3DWB_XL_ODR_OFF             
          :                    IIS3DWB_XL_ODR_26k7Hz;
                               
  /* Output data rate selection. */
  if (iis3dwb_xl_data_rate_set(&(pObj->Ctx), new_odr) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return IIS3DWB_OK;
}

/**
 * @brief  Get the IIS3DWB accelerometer sensor full scale
 * @param  pObj the device pObj
 * @param  FullScale pointer where the full scale is written
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_GetFullScale(IIS3DWB_Object_t *pObj, int32_t *FullScale)
{
  int32_t ret = IIS3DWB_OK;
  iis3dwb_fs_xl_t fs_low_level;

  /* Read actual full scale selection from sensor. */
  if (iis3dwb_xl_full_scale_get(&(pObj->Ctx), &fs_low_level) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  switch (fs_low_level)
  {
    case IIS3DWB_2g:
      *FullScale =  2;
      break;

    case IIS3DWB_4g:
      *FullScale =  4;
      break;

    case IIS3DWB_8g:
      *FullScale =  8;
      break;

    case IIS3DWB_16g:
      *FullScale = 16;
      break;

    default:
      *FullScale = -1;
      ret = IIS3DWB_ERROR;
      break;
  }

  return ret;
}

/**
 * @brief  Set the IIS3DWB accelerometer sensor full scale
 * @param  pObj the device pObj
 * @param  FullScale the functional full scale to be set
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_SetFullScale(IIS3DWB_Object_t *pObj, int32_t FullScale)
{
  iis3dwb_fs_xl_t new_fs;

  /* Seems like MISRA C-2012 rule 14.3a violation but only from single file statical analysis point of view because
     the parameter passed to the function is not known at the moment of analysis */
  new_fs = (FullScale <= 2) ? IIS3DWB_2g
         : (FullScale <= 4) ? IIS3DWB_4g
         : (FullScale <= 8) ? IIS3DWB_8g
         :                    IIS3DWB_16g;

  if (iis3dwb_xl_full_scale_set(&(pObj->Ctx), new_fs) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Get the IIS3DWB accelerometer sensor raw axes
 * @param  pObj the device pObj
 * @param  Value pointer where the raw values of the axes are written
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_GetAxesRaw(IIS3DWB_Object_t *pObj, IIS3DWB_AxesRaw_t *Value)
{
  iis3dwb_axis3bit16_t data_raw;
  int32_t ret = IIS3DWB_OK;

  /* Read raw data values. */
  if (iis3dwb_acceleration_raw_get(&(pObj->Ctx), data_raw.i16bit) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  /* Format the data. */
  Value->x = data_raw.i16bit[0];
  Value->y = data_raw.i16bit[1];
  Value->z = data_raw.i16bit[2];
      
  return ret;
}

/**
 * @brief  Get the IIS3DWB accelerometer sensor axes
 * @param  pObj the device pObj
 * @param  Acceleration pointer where the values of the axes are written
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_GetAxes(IIS3DWB_Object_t *pObj, IIS3DWB_Axes_t *Acceleration)
{
  iis3dwb_axis3bit16_t data_raw;
  float sensitivity = 0.0f;

  /* Read raw data values. */
  if (iis3dwb_acceleration_raw_get(&(pObj->Ctx), data_raw.i16bit) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* Get IIS3DWB actual sensitivity. */
  if (IIS3DWB_ACC_GetSensitivity(pObj, &sensitivity) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* Calculate the data. */
  Acceleration->x = (int32_t)((float)((float)data_raw.i16bit[0] * sensitivity));
  Acceleration->y = (int32_t)((float)((float)data_raw.i16bit[1] * sensitivity));
  Acceleration->z = (int32_t)((float)((float)data_raw.i16bit[2] * sensitivity));

  return IIS3DWB_OK;
}

/**
 * @brief  Get the IIS3DWB register value
 * @param  pObj the device pObj
 * @param  Reg address to be read
 * @param  Data pointer where the value is written
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_Read_Reg(IIS3DWB_Object_t *pObj, uint8_t Reg, uint8_t *Data)
{
  if (iis3dwb_read_reg(&(pObj->Ctx), Reg, Data, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Set the IIS3DWB register value
 * @param  pObj the device pObj
 * @param  Reg address to be written
 * @param  Data value to be written
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_Write_Reg(IIS3DWB_Object_t *pObj, uint8_t Reg, uint8_t Data)
{
  if (iis3dwb_write_reg(&(pObj->Ctx), Reg, &Data, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Enable wake up detection
 * @param  pObj the device pObj
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Enable_Wake_Up_Detection(IIS3DWB_Object_t *pObj)
{
  int32_t ret = IIS3DWB_OK;
  iis3dwb_pin_int1_route_t val;

  /* WAKE_DUR setting */
  if (iis3dwb_wkup_dur_set(&(pObj->Ctx), 0x00) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* Set wake up threshold. */
  if (iis3dwb_wkup_threshold_set(&(pObj->Ctx), 0x02) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  if (iis3dwb_pin_int1_route_get(&(pObj->Ctx), &val) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  val.wake_up = PROPERTY_ENABLE;

  if (iis3dwb_pin_int1_route_set(&(pObj->Ctx), &val) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return ret;
}

/**
 * @brief  Disable wake up detection
 * @param  pObj the device pObj
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Disable_Wake_Up_Detection(IIS3DWB_Object_t *pObj)
{
  iis3dwb_pin_int1_route_t val1;
  iis3dwb_pin_int2_route_t val2;

  /* Disable wake up event on both INT1 and INT2 pins */
  if (iis3dwb_pin_int1_route_get(&(pObj->Ctx), &val1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  val1.wake_up = PROPERTY_DISABLE;

  if (iis3dwb_pin_int1_route_set(&(pObj->Ctx), &val1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  if (iis3dwb_pin_int2_route_get(&(pObj->Ctx), &val2) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  val2.wake_up = PROPERTY_DISABLE;

  if (iis3dwb_pin_int2_route_set(&(pObj->Ctx), &val2) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* Reset wake up threshold. */
  if (iis3dwb_wkup_threshold_set(&(pObj->Ctx), 0x00) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  /* WAKE_DUR setting */
  if (iis3dwb_wkup_dur_set(&(pObj->Ctx), 0x00) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Set wake up threshold
 * @param  pObj the device pObj
 * @param  Threshold wake up detection threshold
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Set_Wake_Up_Threshold(IIS3DWB_Object_t *pObj, uint8_t Threshold)
{
  /* Set wake up threshold. */
  if (iis3dwb_wkup_threshold_set(&(pObj->Ctx), Threshold) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Set wake up duration
 * @param  pObj the device pObj
 * @param  Duration wake up detection duration
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Set_Wake_Up_Duration(IIS3DWB_Object_t *pObj, uint8_t Duration)
{
  /* Set wake up duration. */
  if (iis3dwb_wkup_dur_set(&(pObj->Ctx), Duration) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}


/**
 * @brief  Set sleep duration
 * @param  pObj the device pObj
 * @param  Duration wake up detection duration
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Set_Sleep_Duration(IIS3DWB_Object_t *pObj, uint8_t Duration)
{
  /* Set wake up duration. */
  if (iis3dwb_act_sleep_dur_set(&(pObj->Ctx), Duration) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Get the status of all hardware events
 * @param  pObj the device pObj
 * @param  Status the status of all hardware events
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Get_Event_Status(IIS3DWB_Object_t *pObj, IIS3DWB_Event_Status_t *Status)
{
  iis3dwb_wake_up_src_t wake_up_src;
  iis3dwb_md1_cfg_t md1_cfg;
  iis3dwb_md2_cfg_t md2_cfg;
  iis3dwb_int1_ctrl_t int1_ctrl;

  (void)memset((void *)Status, 0x0, sizeof(IIS3DWB_Event_Status_t));

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_WAKE_UP_SRC, (uint8_t *)&wake_up_src, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_MD1_CFG, (uint8_t *)&md1_cfg, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_MD2_CFG, (uint8_t *)&md2_cfg, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }


  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_INT1_CTRL, (uint8_t *)&int1_ctrl, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  if ((md1_cfg.int1_wu == 1U) || (md2_cfg.int2_wu == 1U))
  {
    if (wake_up_src.wu_ia == 1U)
    {
      Status->WakeUpStatus = 1;
    }
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Get the IIS3DWB ACC data ready bit value
 * @param  pObj the device pObj
 * @param  Status the status of data ready bit
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Get_DRDY_Status(IIS3DWB_Object_t *pObj, uint8_t *Status)
{
  if (iis3dwb_xl_flag_data_ready_get(&(pObj->Ctx), Status) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @brief  Get the IIS3DWB ACC initialization status
 * @param  pObj the device pObj
 * @param  Status 1 if initialized, 0 otherwise
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_ACC_Get_Init_Status(IIS3DWB_Object_t *pObj, uint8_t *Status)
{
  if (pObj == NULL)
  {
    return IIS3DWB_ERROR;
  }

  *Status = pObj->is_initialized;

  return IIS3DWB_OK;
}

/**
 * @brief  Set the accelerometer filter
 * @param  pObj the device pObj
 * @param  bandwidth Cutoff frequency
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_Filter_Set(IIS3DWB_Object_t *pObj, iis3dwb_filt_xl_en_t bandwidth)
{
  if (iis3dwb_xl_filt_path_on_out_set(&(pObj->Ctx), bandwidth) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return IIS3DWB_OK;
}

/**
 * @brief  Set the dataready mode status
 * @param  pObj the device pObj
 * @param  Status the DRDY mode
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_Set_Drdy_Mode(IIS3DWB_Object_t *pObj, uint8_t Status)
{
  if (iis3dwb_data_ready_mode_set(&(pObj->Ctx), (iis3dwb_dataready_pulsed_t)Status) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return IIS3DWB_OK;
}

/**
* @brief  Set the accelerometer data-ready interrupt on INT1 pin
* @param  pObj the device pObj
* @param  Status DRDY interrupt on INT1 pin status
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_INT1_Set_Drdy(IIS3DWB_Object_t *pObj, uint8_t Status)
{  
  iis3dwb_reg_t reg;

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_INT1_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  reg.int1_ctrl.int1_drdy_xl = Status;

  if (iis3dwb_write_reg(&(pObj->Ctx), IIS3DWB_INT1_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
* @brief  Set the IIS3DWB FIFO full interrupt on INT1 pin
* @param  pObj the device pObj
* @param  Status FIFO full interrupt on INT1 pin status
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_INT1_Set_FIFO_Full(IIS3DWB_Object_t *pObj, uint8_t Status)
{
  iis3dwb_reg_t reg;

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_INT1_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  reg.int1_ctrl.int1_fifo_full = Status;

  if (iis3dwb_write_reg(&(pObj->Ctx), IIS3DWB_INT1_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
* @brief  Set the accelerometer data-ready interrupt on INT2 pin
* @param  pObj the device pObj
* @param  Status DRDY interrupt on INT2 pin status
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_INT2_Set_Drdy(IIS3DWB_Object_t *pObj, uint8_t Status)
{
  iis3dwb_reg_t reg;

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_INT2_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  reg.int2_ctrl.int2_drdy_xl = Status;

  if (iis3dwb_write_reg(&(pObj->Ctx), IIS3DWB_INT2_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
* @brief  Set the IIS3DWB FIFO full interrupt on INT2 pin
* @param  pObj the device pObj
* @param  Status FIFO full interrupt on INT2 pin status
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_INT2_Set_FIFO_Full(IIS3DWB_Object_t *pObj, uint8_t Status)
{
  iis3dwb_reg_t reg;

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_INT2_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  reg.int2_ctrl.int2_fifo_full = (uint8_t) Status; 

  if (iis3dwb_write_reg(&(pObj->Ctx), IIS3DWB_INT2_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
* @brief  Set the IIS3DWB FIFO Threshold on INT2 pin
* @param  pObj the device pObj
* @param  Status FIFO full interrupt on INT2 pin status
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_INT2_Set_FIFO_Threshold(IIS3DWB_Object_t *pObj, uint8_t Status)
{
  iis3dwb_reg_t reg;

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_INT2_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  reg.int2_ctrl.int2_fifo_th = (uint8_t) Status; 

  if (iis3dwb_write_reg(&(pObj->Ctx), IIS3DWB_INT2_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
* @brief  Set the IIS3DWB FIFO Threshold on INT1 pin
* @param  pObj the device pObj
* @param  Status FIFO full interrupt on INT1 pin status
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_INT1_Set_FIFO_Threshold(IIS3DWB_Object_t *pObj, uint8_t Status)
{
  iis3dwb_reg_t reg;

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_INT1_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  reg.int1_ctrl.int1_fifo_th = (uint8_t) Status; 

  if (iis3dwb_write_reg(&(pObj->Ctx), IIS3DWB_INT1_CTRL, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
* @brief  RESET
* @param  pObj the device pObj
* @param  
* @retval 
*/
int32_t IIS3DWB_Reset(IIS3DWB_Object_t *pObj)
{
  iis3dwb_reset_set(&(pObj->Ctx), 1);
  return 0; 
}
/**
* @brief  Set the IIS3DWB FIFO watermark level
* @param  pObj the device pObj
* @param  Watermark FIFO watermark level
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_FIFO_Set_Watermark_Level(IIS3DWB_Object_t *pObj, uint16_t Watermark)
{
  if (iis3dwb_fifo_watermark_set(&(pObj->Ctx), Watermark) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return IIS3DWB_OK;
}

/**
* @brief  Set the IIS3DWB FIFO stop on watermark
* @param  pObj the device pObj
* @param  Status FIFO stop on watermark status
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_FIFO_Set_Stop_On_Fth(IIS3DWB_Object_t *pObj, uint8_t Status)
{
  if (iis3dwb_fifo_stop_on_wtm_set(&(pObj->Ctx), Status) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return IIS3DWB_OK;
}

/**
 * @brief  Set the IIS3DWB FIFO ODR value
 * @param  pObj the device pObj
 * @param  Odr FIFO ODR value
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_FIFO_Set_BDR(IIS3DWB_Object_t *pObj, float Bdr)
{
  iis3dwb_bdr_xl_t new_odr;

  new_odr = (Bdr <= 1.0f) ? IIS3DWB_XL_NOT_BATCHED
            :               IIS3DWB_XL_BATCHED_AT_26k7Hz;

  if (iis3dwb_fifo_xl_batch_set(&(pObj->Ctx), new_odr) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
* @brief  Set the IIS3DWB decimation for timestamp batching in FIFO
* @param  pObj the device pObj
* @param  bdr FIFO Timestamp decimation
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_FIFO_Set_TS_Decimation(IIS3DWB_Object_t *pObj, uint8_t decimation)
{
  if (iis3dwb_fifo_timestamp_decimation_set(&(pObj->Ctx), (iis3dwb_odr_ts_batch_t)decimation) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return IIS3DWB_OK;
}


/**
* @brief  Set the IIS3DWB batching data rate for temperature data
* @param  pObj the device pObj
* @param  bdr FIFO temperature data batching data rate
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_FIFO_Set_T_BDR(IIS3DWB_Object_t *pObj, uint8_t bdr)
{
  if (iis3dwb_fifo_temp_batch_set(&(pObj->Ctx), (iis3dwb_odr_t_batch_t)bdr) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return IIS3DWB_OK;
}

/**
* @brief  Read the IIS3DWB FIFO
* @param  pObj the device pObj
* @param  pBuff Buffer to store the FIFO values
* @param  Watermark FIFO watermark level
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_FIFO_Read(IIS3DWB_Object_t *pObj, uint8_t *pBuff, uint16_t Watermark)
{
  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_FIFO_DATA_OUT_TAG, pBuff, (Watermark * 7)) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return IIS3DWB_OK;
}

/**
* @brief  Set the IIS3DWB FIFO mode
* @param  pObj the device pObj
* @param  mode FIFO mode
* @retval 0 in case of success, an error code otherwise
*/
int32_t IIS3DWB_FIFO_Set_Mode(IIS3DWB_Object_t *pObj, uint8_t mode)
{
  int32_t ret = IIS3DWB_OK;
  
  /* Verify that the passed parameter contains one of the valid values. */
  switch ((iis3dwb_fifo_mode_t)mode)
  {
  case IIS3DWB_BYPASS_MODE:
  case IIS3DWB_FIFO_MODE:
  case IIS3DWB_STREAM_TO_FIFO_MODE:
  case IIS3DWB_BYPASS_TO_STREAM_MODE:
  case IIS3DWB_STREAM_MODE:
  case IIS3DWB_BYPASS_TO_FIFO_MODE:
    break;
    
  default:
    ret = IIS3DWB_ERROR;
    break;
  }
  
  if (ret == IIS3DWB_ERROR)
  {
    return ret;
  }
  
  if (iis3dwb_fifo_mode_set(&(pObj->Ctx), (iis3dwb_fifo_mode_t)mode) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }
  
  return ret;
}

/**
 * @brief  Get the IIS3DWB FIFO full status
 * @param  pObj the device pObj
 * @param  Status FIFO full status
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_FIFO_Get_Full_Status(IIS3DWB_Object_t *pObj, uint8_t *Status)
{
  iis3dwb_reg_t reg;

  if (iis3dwb_read_reg(&(pObj->Ctx), IIS3DWB_FIFO_STATUS2, &reg.byte, 1) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  *Status = reg.fifo_status2.fifo_full_ia;

  return IIS3DWB_OK;
}

/**
 * @brief  Get the IIS3DWB FIFO number of samples
 * @param  pObj the device pObj
 * @param  NumSamples number of samples
 * @retval 0 in case of success, an error code otherwise
 */
int32_t IIS3DWB_FIFO_Get_Num_Samples(IIS3DWB_Object_t *pObj, uint16_t *NumSamples)
{
  if (iis3dwb_fifo_data_level_get(&(pObj->Ctx), NumSamples) != IIS3DWB_OK)
  {
    return IIS3DWB_ERROR;
  }

  return IIS3DWB_OK;
}

/**
 * @}
 */

/** @defgroup IIS3DWB_Private_Functions IIS3DWB Private Functions
 * @{
 */


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
  IIS3DWB_Object_t *pObj = (IIS3DWB_Object_t *)Handle;

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
  IIS3DWB_Object_t *pObj = (IIS3DWB_Object_t *)Handle;

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

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
