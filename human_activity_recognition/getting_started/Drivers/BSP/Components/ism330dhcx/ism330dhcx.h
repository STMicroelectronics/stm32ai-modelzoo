/**
 ******************************************************************************
 * @file    ism330dhcx.h
 * @author  MEMS Software Solutions Team
 * @brief   ISM330DHCX header driver file
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; Copyright (c) 2019 STMicroelectronics.
 * All rights reserved.</center></h2>
 *
 * This software component is licensed by ST under BSD 3-Clause license,
 * the "License"; You may not use this file except in compliance with the
 * License. You may obtain a copy of the License at:
 *                        opensource.org/licenses/BSD-3-Clause
 *
 ******************************************************************************
 */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef ISM330DHCX_H
#define ISM330DHCX_H

#ifdef __cplusplus
extern "C"
{
#endif

/* Includes ------------------------------------------------------------------*/
#include "ism330dhcx_reg.h"
#include <string.h>

/** @addtogroup BSP BSP
 * @{
 */

/** @addtogroup Component Component
 * @{
 */

/** @addtogroup ISM330DHCX ISM330DHCX
 * @{
 */

/** @defgroup ISM330DHCX_Exported_Types ISM330DHCX Exported Types
 * @{
 */

typedef int32_t (*ISM330DHCX_Init_Func)(void);
typedef int32_t (*ISM330DHCX_DeInit_Func)(void);
typedef int32_t (*ISM330DHCX_GetTick_Func)(void);
typedef int32_t (*ISM330DHCX_WriteReg_Func)(uint16_t, uint16_t, uint8_t *, uint16_t);
typedef int32_t (*ISM330DHCX_ReadReg_Func)(uint16_t, uint16_t, uint8_t *, uint16_t);

typedef enum
{
  ISM330DHCX_INT1_PIN,
  ISM330DHCX_INT2_PIN,
} ISM330DHCX_SensorIntPin_t;

typedef struct
{
  ISM330DHCX_Init_Func          Init;
  ISM330DHCX_DeInit_Func        DeInit;
  uint32_t                     BusType; /*0 means I2C, 1 means SPI 4-Wires, 2 means SPI-3-Wires */
  uint8_t                      Address;
  ISM330DHCX_WriteReg_Func      WriteReg;
  ISM330DHCX_ReadReg_Func       ReadReg;
  ISM330DHCX_GetTick_Func       GetTick;
} ISM330DHCX_IO_t;

typedef struct
{
  int16_t x;
  int16_t y;
  int16_t z;
} ISM330DHCX_AxesRaw_t;

typedef struct
{
  int32_t x;
  int32_t y;
  int32_t z;
} ISM330DHCX_Axes_t;

typedef struct
{
  unsigned int FreeFallStatus : 1;
  unsigned int TapStatus : 1;
  unsigned int DoubleTapStatus : 1;
  unsigned int WakeUpStatus : 1;
  unsigned int StepStatus : 1;
  unsigned int TiltStatus : 1;
  unsigned int D6DOrientationStatus : 1;
  unsigned int SleepStatus : 1;
} ISM330DHCX_Event_Status_t;

typedef struct
{
  ISM330DHCX_IO_t        IO;
  stmdev_ctx_t           Ctx;
  uint8_t                is_initialized;
  uint8_t                acc_is_enabled;
  uint8_t                gyro_is_enabled;
  ism330dhcx_odr_xl_t    acc_odr;
  ism330dhcx_odr_g_t     gyro_odr;
} ISM330DHCX_Object_t;

typedef struct
{
  uint8_t   Acc;
  uint8_t   Gyro;
  uint8_t   Magneto;
  uint8_t   LowPower;
  uint32_t  GyroMaxFS;
  uint32_t  AccMaxFS;
  uint32_t  MagMaxFS;
  float     GyroMaxOdr;
  float     AccMaxOdr;
  float     MagMaxOdr;
} ISM330DHCX_Capabilities_t;

typedef struct
{
  int32_t (*Init)(ISM330DHCX_Object_t *);
  int32_t (*DeInit)(ISM330DHCX_Object_t *);
  int32_t (*ReadID)(ISM330DHCX_Object_t *, uint8_t *);
  int32_t (*GetCapabilities)(ISM330DHCX_Object_t *, ISM330DHCX_Capabilities_t *);
} ISM330DHCX_CommonDrv_t;

typedef struct
{
  int32_t (*Enable)(ISM330DHCX_Object_t *);
  int32_t (*Disable)(ISM330DHCX_Object_t *);
  int32_t (*GetSensitivity)(ISM330DHCX_Object_t *, float *);
  int32_t (*GetOutputDataRate)(ISM330DHCX_Object_t *, float *);
  int32_t (*SetOutputDataRate)(ISM330DHCX_Object_t *, float);
  int32_t (*GetFullScale)(ISM330DHCX_Object_t *, int32_t *);
  int32_t (*SetFullScale)(ISM330DHCX_Object_t *, int32_t);
  int32_t (*GetAxes)(ISM330DHCX_Object_t *, ISM330DHCX_Axes_t *);
  int32_t (*GetAxesRaw)(ISM330DHCX_Object_t *, ISM330DHCX_AxesRaw_t *);
} ISM330DHCX_ACC_Drv_t;

typedef struct
{
  int32_t (*Enable)(ISM330DHCX_Object_t *);
  int32_t (*Disable)(ISM330DHCX_Object_t *);
  int32_t (*GetSensitivity)(ISM330DHCX_Object_t *, float *);
  int32_t (*GetOutputDataRate)(ISM330DHCX_Object_t *, float *);
  int32_t (*SetOutputDataRate)(ISM330DHCX_Object_t *, float);
  int32_t (*GetFullScale)(ISM330DHCX_Object_t *, int32_t *);
  int32_t (*SetFullScale)(ISM330DHCX_Object_t *, int32_t);
  int32_t (*GetAxes)(ISM330DHCX_Object_t *, ISM330DHCX_Axes_t *);
  int32_t (*GetAxesRaw)(ISM330DHCX_Object_t *, ISM330DHCX_AxesRaw_t *);
} ISM330DHCX_GYRO_Drv_t;

typedef union{
  int16_t i16bit[3];
  uint8_t u8bit[6];
} ism330dhcx_axis3bit16_t;

typedef union{
  int16_t i16bit;
  uint8_t u8bit[2];
} ism330dhcx_axis1bit16_t;

typedef union{
  int32_t i32bit[3];
  uint8_t u8bit[12];
} ism330dhcx_axis3bit32_t;

typedef union{
  int32_t i32bit;
  uint8_t u8bit[4];
} ism330dhcx_axis1bit32_t;

/**
 * @}
 */

/** @defgroup ISM330DHCX_Exported_Constants ISM330DHCX Exported Constants
 * @{
 */

#define ISM330DHCX_OK                       0
#define ISM330DHCX_ERROR                   -1

#define ISM330DHCX_I2C_BUS                 0U
#define ISM330DHCX_SPI_4WIRES_BUS          1U
#define ISM330DHCX_SPI_3WIRES_BUS          2U

#define ISM330DHCX_ACC_SENSITIVITY_FS_2G   0.061f
#define ISM330DHCX_ACC_SENSITIVITY_FS_4G   0.122f
#define ISM330DHCX_ACC_SENSITIVITY_FS_8G   0.244f
#define ISM330DHCX_ACC_SENSITIVITY_FS_16G  0.488f

#define ISM330DHCX_GYRO_SENSITIVITY_FS_125DPS    4.375f
#define ISM330DHCX_GYRO_SENSITIVITY_FS_250DPS    8.750f
#define ISM330DHCX_GYRO_SENSITIVITY_FS_500DPS   17.500f
#define ISM330DHCX_GYRO_SENSITIVITY_FS_1000DPS  35.000f
#define ISM330DHCX_GYRO_SENSITIVITY_FS_2000DPS  70.000f
#define ISM330DHCX_GYRO_SENSITIVITY_FS_4000DPS 140.000f

/**
 * @}
 */

/** @addtogroup ISM330DHCX_Exported_Functions ISM330DHCX Exported Functions
 * @{
 */

int32_t ISM330DHCX_RegisterBusIO(ISM330DHCX_Object_t *pObj, ISM330DHCX_IO_t *pIO);
int32_t ISM330DHCX_Init(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_DeInit(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ReadID(ISM330DHCX_Object_t *pObj, uint8_t *Id);
int32_t ISM330DHCX_GetCapabilities(ISM330DHCX_Object_t *pObj, ISM330DHCX_Capabilities_t *Capabilities);

int32_t ISM330DHCX_ACC_Enable(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ACC_Disable(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ACC_GetSensitivity(ISM330DHCX_Object_t *pObj, float *Sensitivity);
int32_t ISM330DHCX_ACC_GetOutputDataRate(ISM330DHCX_Object_t *pObj, float *Odr);
int32_t ISM330DHCX_ACC_SetOutputDataRate(ISM330DHCX_Object_t *pObj, float Odr);
int32_t ISM330DHCX_ACC_GetFullScale(ISM330DHCX_Object_t *pObj, int32_t *FullScale);
int32_t ISM330DHCX_ACC_SetFullScale(ISM330DHCX_Object_t *pObj, int32_t FullScale);
int32_t ISM330DHCX_ACC_GetAxesRaw(ISM330DHCX_Object_t *pObj, ISM330DHCX_AxesRaw_t *Value);
int32_t ISM330DHCX_ACC_GetAxes(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *Acceleration);

int32_t ISM330DHCX_GYRO_Enable(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_GYRO_Disable(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_GYRO_GetSensitivity(ISM330DHCX_Object_t *pObj, float *Sensitivity);
int32_t ISM330DHCX_GYRO_GetOutputDataRate(ISM330DHCX_Object_t *pObj, float *Odr);
int32_t ISM330DHCX_GYRO_SetOutputDataRate(ISM330DHCX_Object_t *pObj, float Odr);
int32_t ISM330DHCX_GYRO_GetFullScale(ISM330DHCX_Object_t *pObj, int32_t *FullScale);
int32_t ISM330DHCX_GYRO_SetFullScale(ISM330DHCX_Object_t *pObj, int32_t FullScale);
int32_t ISM330DHCX_GYRO_GetAxesRaw(ISM330DHCX_Object_t *pObj, ISM330DHCX_AxesRaw_t *Value);
int32_t ISM330DHCX_GYRO_GetAxes(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *AngularRate);

int32_t ISM330DHCX_Read_Reg(ISM330DHCX_Object_t *pObj, uint8_t reg, uint8_t *Data);
int32_t ISM330DHCX_Write_Reg(ISM330DHCX_Object_t *pObj, uint8_t reg, uint8_t Data);
int32_t ISM330DHCX_Set_Interrupt_Latch(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_Set_INT1_Drdy(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_Set_INT2_Drdy(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_Set_Drdy_Mode(ISM330DHCX_Object_t *pObj, uint8_t Status);

int32_t ISM330DHCX_ACC_Enable_Free_Fall_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin);
int32_t ISM330DHCX_ACC_Disable_Free_Fall_Detection(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ACC_Set_Free_Fall_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Threshold);
int32_t ISM330DHCX_ACC_Set_Free_Fall_Duration(ISM330DHCX_Object_t *pObj, uint8_t Duration);

int32_t ISM330DHCX_ACC_Enable_Tilt_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin);
int32_t ISM330DHCX_ACC_Disable_Tilt_Detection(ISM330DHCX_Object_t *pObj);

int32_t ISM330DHCX_ACC_Enable_Wake_Up_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin);
int32_t ISM330DHCX_ACC_Disable_Wake_Up_Detection(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ACC_Set_Wake_Up_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Threshold);
int32_t ISM330DHCX_ACC_Set_Wake_Up_Duration(ISM330DHCX_Object_t *pObj, uint8_t Duration);

int32_t ISM330DHCX_ACC_Enable_Single_Tap_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin);
int32_t ISM330DHCX_ACC_Disable_Single_Tap_Detection(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ACC_Enable_Double_Tap_Detection(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin);
int32_t ISM330DHCX_ACC_Disable_Double_Tap_Detection(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ACC_Set_Tap_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Threshold);
int32_t ISM330DHCX_ACC_Set_Tap_Shock_Time(ISM330DHCX_Object_t *pObj, uint8_t Time);
int32_t ISM330DHCX_ACC_Set_Tap_Quiet_Time(ISM330DHCX_Object_t *pObj, uint8_t Time);
int32_t ISM330DHCX_ACC_Set_Tap_Duration_Time(ISM330DHCX_Object_t *pObj, uint8_t Time);

int32_t ISM330DHCX_ACC_Enable_6D_Orientation(ISM330DHCX_Object_t *pObj, ISM330DHCX_SensorIntPin_t IntPin);
int32_t ISM330DHCX_ACC_Disable_6D_Orientation(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ACC_Set_6D_Orientation_Threshold(ISM330DHCX_Object_t *pObj, uint8_t Threshold);
int32_t ISM330DHCX_ACC_Get_6D_Orientation_XL(ISM330DHCX_Object_t *pObj, uint8_t *XLow);
int32_t ISM330DHCX_ACC_Get_6D_Orientation_XH(ISM330DHCX_Object_t *pObj, uint8_t *XHigh);
int32_t ISM330DHCX_ACC_Get_6D_Orientation_YL(ISM330DHCX_Object_t *pObj, uint8_t *YLow);
int32_t ISM330DHCX_ACC_Get_6D_Orientation_YH(ISM330DHCX_Object_t *pObj, uint8_t *YHigh);
int32_t ISM330DHCX_ACC_Get_6D_Orientation_ZL(ISM330DHCX_Object_t *pObj, uint8_t *ZLow);
int32_t ISM330DHCX_ACC_Get_6D_Orientation_ZH(ISM330DHCX_Object_t *pObj, uint8_t *ZHigh);

int32_t ISM330DHCX_ACC_Get_Event_Status(ISM330DHCX_Object_t *pObj, ISM330DHCX_Event_Status_t *Status);
int32_t ISM330DHCX_ACC_Set_SelfTest(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_ACC_Get_DRDY_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status);
int32_t ISM330DHCX_ACC_Get_Init_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status);
int32_t ISM330DHCX_ACC_Enable_HP_Filter(ISM330DHCX_Object_t *pObj, ism330dhcx_hp_slope_xl_en_t CutOff);

int32_t ISM330DHCX_GYRO_Set_SelfTest(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_GYRO_Get_DRDY_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status);
int32_t ISM330DHCX_GYRO_Get_Init_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status);

int32_t ISM330DHCX_FIFO_Get_Num_Samples(ISM330DHCX_Object_t *pObj, uint16_t *NumSamples);
int32_t ISM330DHCX_FIFO_Get_Full_Status(ISM330DHCX_Object_t *pObj, uint8_t *Status);
int32_t ISM330DHCX_FIFO_ACC_Set_BDR(ISM330DHCX_Object_t *pObj, float Bdr);
int32_t ISM330DHCX_FIFO_GYRO_Set_BDR(ISM330DHCX_Object_t *pObj, float Bdr);
int32_t ISM330DHCX_FIFO_Set_INT1_FIFO_Full(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_FIFO_Set_INT2_FIFO_Full(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_FIFO_Set_Watermark_Level(ISM330DHCX_Object_t *pObj, uint16_t Watermark);
int32_t ISM330DHCX_FIFO_Set_Stop_On_Fth(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_FIFO_Set_Mode(ISM330DHCX_Object_t *pObj, uint8_t Mode);
int32_t ISM330DHCX_FIFO_Get_Tag(ISM330DHCX_Object_t *pObj, uint8_t *Tag);
int32_t ISM330DHCX_FIFO_Get_Data(ISM330DHCX_Object_t *pObj, uint8_t *Data);
int32_t ISM330DHCX_FIFO_ACC_Get_Axes(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *Acceleration);
int32_t ISM330DHCX_FIFO_GYRO_Get_Axes(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *AngularVelocity);
int32_t ISM330DHCX_FIFO_Full_Set_INT1(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_FIFO_Set_INT2_Drdy(ISM330DHCX_Object_t *pObj, uint8_t Status);
int32_t ISM330DHCX_FIFO_Get_Data_Word(ISM330DHCX_Object_t *pObj, int16_t *data_raw);
int32_t ISM330DHCX_FIFO_ACC_Get_Axis(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *Acceleration);
int32_t ISM330DHCX_FIFO_GYRO_Get_Axis(ISM330DHCX_Object_t *pObj, ISM330DHCX_Axes_t *AngularVelocity);

int32_t ISM330DHCX_ACC_Enable_DRDY_On_INT1(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_ACC_Disable_DRDY_On_INT1(ISM330DHCX_Object_t *pObj);

int32_t ISM330DHCX_GYRO_Enable_DRDY_On_INT2(ISM330DHCX_Object_t *pObj);
int32_t ISM330DHCX_GYRO_Disable_DRDY_On_INT2(ISM330DHCX_Object_t *pObj);

int32_t ISM330DHCX_DRDY_Set_Mode(ISM330DHCX_Object_t *pObj, uint8_t Mode);

/**
 * @}
 */

/** @addtogroup ISM330DHCX_Exported_Variables ISM330DHCX Exported Variables
 * @{
 */

extern ISM330DHCX_CommonDrv_t ISM330DHCX_COMMON_Driver;
extern ISM330DHCX_ACC_Drv_t ISM330DHCX_ACC_Driver;
extern ISM330DHCX_GYRO_Drv_t ISM330DHCX_GYRO_Driver;

/**
 * @}
 */

#ifdef __cplusplus
}
#endif

#endif

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
