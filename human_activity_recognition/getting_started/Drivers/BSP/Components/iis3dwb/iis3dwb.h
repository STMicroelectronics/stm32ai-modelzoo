/**
******************************************************************************
* @file    iis3dwb.h
* @author  SRA
* @brief   IIS3DWB header driver file
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef IIS3DWB_H
#define IIS3DWB_H

#ifdef __cplusplus
extern "C"
{
#endif

/* Includes ------------------------------------------------------------------*/
#include "iis3dwb_reg.h"
#include <string.h>

/** @addtogroup BSP BSP
 * @{
 */

/** @addtogroup Component Component
 * @{
 */

/** @addtogroup IIS3DWB IIS3DWB
 * @{
 */

/** @defgroup IIS3DWB_Exported_Types IIS3DWB Exported Types
 * @{
 */

typedef int32_t (*IIS3DWB_Init_Func)(void);
typedef int32_t (*IIS3DWB_DeInit_Func)(void);
typedef int32_t (*IIS3DWB_GetTick_Func)(void);
typedef int32_t (*IIS3DWB_WriteReg_Func)(uint16_t, uint16_t, uint8_t *, uint16_t);
typedef int32_t (*IIS3DWB_ReadReg_Func)(uint16_t, uint16_t, uint8_t *, uint16_t);

typedef enum
{
  IIS3DWB_INT1_PIN,
  IIS3DWB_INT2_PIN,
} IIS3DWB_SensorIntPin_t;

typedef struct
{
  IIS3DWB_Init_Func         Init;
  IIS3DWB_DeInit_Func       DeInit;
  uint32_t                   BusType; /*0 means I2C, 1 means SPI 4-Wires, 2 means SPI-3-Wires */
  uint8_t                    Address;
  IIS3DWB_WriteReg_Func     WriteReg;
  IIS3DWB_ReadReg_Func      ReadReg;
  IIS3DWB_GetTick_Func      GetTick;
} IIS3DWB_IO_t;


typedef struct
{
  int16_t x;
  int16_t y;
  int16_t z;
} IIS3DWB_AxesRaw_t;

typedef struct
{
  int32_t x;
  int32_t y;
  int32_t z;
} IIS3DWB_Axes_t;

typedef struct
{
  unsigned int WakeUpStatus : 1;
  unsigned int SleepStatus : 1;
} IIS3DWB_Event_Status_t;

typedef struct
{
  IIS3DWB_IO_t       IO;
  stmdev_ctx_t      Ctx;
  uint8_t             is_initialized;
  uint8_t             acc_is_enabled;
  float               acc_odr;
} IIS3DWB_Object_t;

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
} IIS3DWB_Capabilities_t;

typedef struct
{
  int32_t (*Init)(IIS3DWB_Object_t *);
  int32_t (*DeInit)(IIS3DWB_Object_t *);
  int32_t (*ReadID)(IIS3DWB_Object_t *, uint8_t *);
  int32_t (*GetCapabilities)(IIS3DWB_Object_t *, IIS3DWB_Capabilities_t *);
} IIS3DWB_CommonDrv_t;

typedef struct
{
  int32_t (*Enable)(IIS3DWB_Object_t *);
  int32_t (*Disable)(IIS3DWB_Object_t *);
  int32_t (*GetSensitivity)(IIS3DWB_Object_t *, float *);
  int32_t (*GetOutputDataRate)(IIS3DWB_Object_t *, float *);
  int32_t (*SetOutputDataRate)(IIS3DWB_Object_t *, float);
  int32_t (*GetFullScale)(IIS3DWB_Object_t *, int32_t *);
  int32_t (*SetFullScale)(IIS3DWB_Object_t *, int32_t);
  int32_t (*GetAxes)(IIS3DWB_Object_t *, IIS3DWB_Axes_t *);
  int32_t (*GetAxesRaw)(IIS3DWB_Object_t *, IIS3DWB_AxesRaw_t *);
} IIS3DWB_ACC_Drv_t;

typedef union{
  int16_t i16bit[3];
  uint8_t u8bit[6];
} iis3dwb_axis3bit16_t;

typedef union{
  int16_t i16bit;
  uint8_t u8bit[2];
} iis3dwb_axis1bit16_t;

typedef union{
  int32_t i32bit[3];
  uint8_t u8bit[12];
} iis3dwb_axis3bit32_t;

typedef union{
  int32_t i32bit;
  uint8_t u8bit[4];
} iis3dwb_axis1bit32_t;

/**
 * @}
 */

/** @defgroup IIS3DWB_Exported_Constants IIS3DWB Exported Constants
 * @{
 */

#define IIS3DWB_OK                       0
#define IIS3DWB_ERROR                   -1

#define IIS3DWB_I2C_BUS                 0U
#define IIS3DWB_SPI_4WIRES_BUS          1U
#define IIS3DWB_SPI_3WIRES_BUS          2U

#define IIS3DWB_ACC_SENSITIVITY_FOR_FS_2G_LOPOW1_MODE   0.061f  /**< Sensitivity value for 2g full scale, Low-power1 mode [mg/LSB] */
#define IIS3DWB_ACC_SENSITIVITY_FOR_FS_2G_OTHER_MODES   0.061f  /**< Sensitivity value for 2g full scale, all other modes except Low-power1 [mg/LSB] */

#define IIS3DWB_ACC_SENSITIVITY_FOR_FS_4G_LOPOW1_MODE   0.122f  /**< Sensitivity value for 4g full scale, Low-power1 mode [mg/LSB] */
#define IIS3DWB_ACC_SENSITIVITY_FOR_FS_4G_OTHER_MODES   0.122f  /**< Sensitivity value for 4g full scale, all other modes except Low-power1 [mg/LSB] */

#define IIS3DWB_ACC_SENSITIVITY_FOR_FS_8G_LOPOW1_MODE   0.244f  /**< Sensitivity value for 8g full scale, Low-power1 mode [mg/LSB] */
#define IIS3DWB_ACC_SENSITIVITY_FOR_FS_8G_OTHER_MODES   0.244f  /**< Sensitivity value for 8g full scale, all other modes except Low-power1 [mg/LSB] */

#define IIS3DWB_ACC_SENSITIVITY_FOR_FS_16G_LOPOW1_MODE  0.488f  /**< Sensitivity value for 16g full scale, Low-power1 mode [mg/LSB] */
#define IIS3DWB_ACC_SENSITIVITY_FOR_FS_16G_OTHER_MODES  0.488f  /**< Sensitivity value for 16g full scale, all other modes except Low-power1 [mg/LSB] */

/**
 * @}
 */

/** @addtogroup IIS3DWB_Exported_Functions IIS3DWB Exported Functions
 * @{
 */

int32_t IIS3DWB_RegisterBusIO(IIS3DWB_Object_t *pObj, IIS3DWB_IO_t *pIO);
int32_t IIS3DWB_Init(IIS3DWB_Object_t *pObj);
int32_t IIS3DWB_DeInit(IIS3DWB_Object_t *pObj);
int32_t IIS3DWB_ReadID(IIS3DWB_Object_t *pObj, uint8_t *Id);
int32_t IIS3DWB_GetCapabilities(IIS3DWB_Object_t *pObj, IIS3DWB_Capabilities_t *Capabilities);

int32_t IIS3DWB_ACC_Enable(IIS3DWB_Object_t *pObj);
int32_t IIS3DWB_ACC_Disable(IIS3DWB_Object_t *pObj);
int32_t IIS3DWB_ACC_GetSensitivity(IIS3DWB_Object_t *pObj, float *Sensitivity);
int32_t IIS3DWB_ACC_GetOutputDataRate(IIS3DWB_Object_t *pObj, float *Odr);
int32_t IIS3DWB_ACC_SetOutputDataRate(IIS3DWB_Object_t *pObj, float Odr);
int32_t IIS3DWB_ACC_GetFullScale(IIS3DWB_Object_t *pObj, int32_t *FullScale);
int32_t IIS3DWB_ACC_SetFullScale(IIS3DWB_Object_t *pObj, int32_t FullScale);
int32_t IIS3DWB_ACC_GetAxesRaw(IIS3DWB_Object_t *pObj, IIS3DWB_AxesRaw_t *Value);
int32_t IIS3DWB_ACC_GetAxes(IIS3DWB_Object_t *pObj, IIS3DWB_Axes_t *Acceleration);

int32_t IIS3DWB_Read_Reg(IIS3DWB_Object_t *pObj, uint8_t reg, uint8_t *Data);
int32_t IIS3DWB_Write_Reg(IIS3DWB_Object_t *pObj, uint8_t reg, uint8_t Data);
int32_t IIS3DWB_Set_Interrupt_Latch(IIS3DWB_Object_t *pObj, uint8_t Status);

int32_t IIS3DWB_ACC_Enable_Wake_Up_Detection(IIS3DWB_Object_t *pObj);
int32_t IIS3DWB_ACC_Disable_Wake_Up_Detection(IIS3DWB_Object_t *pObj);
int32_t IIS3DWB_ACC_Set_Wake_Up_Threshold(IIS3DWB_Object_t *pObj, uint8_t Threshold);
int32_t IIS3DWB_ACC_Set_Wake_Up_Duration(IIS3DWB_Object_t *pObj, uint8_t Duration);

int32_t IIS3DWB_ACC_Enable_Inactivity_Detection(IIS3DWB_Object_t *pObj);
int32_t IIS3DWB_ACC_Disable_Inactivity_Detection(IIS3DWB_Object_t *pObj);
int32_t IIS3DWB_ACC_Set_Sleep_Duration(IIS3DWB_Object_t *pObj, uint8_t Duration);

int32_t IIS3DWB_ACC_Get_Event_Status(IIS3DWB_Object_t *pObj, IIS3DWB_Event_Status_t *Status);
int32_t IIS3DWB_ACC_Get_DRDY_Status(IIS3DWB_Object_t *pObj, uint8_t *Status);
int32_t IIS3DWB_ACC_Get_Init_Status(IIS3DWB_Object_t *pObj, uint8_t *Status);

int32_t IIS3DWB_Filter_Set(IIS3DWB_Object_t *pObj, iis3dwb_filt_xl_en_t bandwidth);
int32_t IIS3DWB_Set_Drdy_Mode(IIS3DWB_Object_t *pObj, uint8_t Status);
int32_t IIS3DWB_INT1_Set_Drdy(IIS3DWB_Object_t *pObj, uint8_t Status);
int32_t IIS3DWB_INT1_Set_FIFO_Full(IIS3DWB_Object_t *pObj, uint8_t Status);
int32_t IIS3DWB_INT2_Set_Drdy(IIS3DWB_Object_t *pObj, uint8_t Status);
int32_t IIS3DWB_INT2_Set_FIFO_Full(IIS3DWB_Object_t *pObj, uint8_t Status);
int32_t IIS3DWB_INT1_Set_FIFO_Threshold(IIS3DWB_Object_t *pObj, uint8_t Status);
int32_t IIS3DWB_INT2_Set_FIFO_Threshold(IIS3DWB_Object_t *pObj, uint8_t Status);
int32_t IIS3DWB_FIFO_Set_Watermark_Level(IIS3DWB_Object_t *pObj, uint16_t Watermark);
int32_t IIS3DWB_FIFO_Set_Stop_On_Fth(IIS3DWB_Object_t *pObj, uint8_t Status);
int32_t IIS3DWB_FIFO_Set_BDR(IIS3DWB_Object_t *pObj, float Bdr);
int32_t IIS3DWB_FIFO_Set_TS_Decimation(IIS3DWB_Object_t *pObj, uint8_t decimation);
int32_t IIS3DWB_FIFO_Set_T_BDR(IIS3DWB_Object_t *pObj, uint8_t bdr);
int32_t IIS3DWB_FIFO_Set_Mode(IIS3DWB_Object_t *pObj, uint8_t mode);
int32_t IIS3DWB_FIFO_Read(IIS3DWB_Object_t *pObj, uint8_t *pBuff, uint16_t Watermark);
int32_t IIS3DWB_FIFO_Get_Num_Samples(IIS3DWB_Object_t *pObj, uint16_t *NumSamples);
int32_t IIS3DWB_FIFO_Get_Full_Status(IIS3DWB_Object_t *pObj, uint8_t *Status);


int32_t IIS3DWB_Reset(IIS3DWB_Object_t *pObj);

/**
 * @}
 */

/** @addtogroup IIS3DWB_Exported_Variables IIS3DWB Exported Variables
 * @{
 */

extern IIS3DWB_CommonDrv_t IIS3DWB_COMMON_Driver;
extern IIS3DWB_ACC_Drv_t IIS3DWB_ACC_Driver;

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
