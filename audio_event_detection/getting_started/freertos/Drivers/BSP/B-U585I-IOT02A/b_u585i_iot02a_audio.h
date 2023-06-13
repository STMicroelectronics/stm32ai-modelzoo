/**
  ******************************************************************************
  * @file    b_u585i_iot02a_audio.h
  * @author  MCD Application Team
  * @brief   This file contains the common defines and functions prototypes for
  *          the b_u585i_iot02a_audio.c driver.
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
  ******************************************************************************
  */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef B_U585I_IOT02A_AUDIO_H
#define B_U585I_IOT02A_AUDIO_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "b_u585i_iot02a_conf.h"
#include "b_u585i_iot02a_errno.h"
#include "../Components/Common/audio.h"

/** @addtogroup BSP
  * @{
  */

/** @addtogroup B_U585I_IOT02A
  * @{
  */

/** @addtogroup B_U585I_IOT02A_AUDIO
  * @{
  */

/** @defgroup B_U585I_IOT02A_AUDIO_Exported_Types AUDIO Exported Types
  * @{
  */
typedef struct
{
  uint32_t Device;        /* Output or input device */
  uint32_t SampleRate;    /* From 8kHz to 192 kHz */
  uint32_t BitsPerSample; /* From 8 bits per sample to 32 bits per sample */
  uint32_t ChannelsNbr;   /* 1 for mono and 2 for stereo */
  uint32_t Volume;        /* In percentage from 0 to 100 */
} BSP_AUDIO_Init_t;

#if (USE_HAL_MDF_REGISTER_CALLBACKS == 1)
typedef struct
{
  pMDF_CallbackTypeDef  pMspMdfInitCb;
  pMDF_CallbackTypeDef  pMspMdfDeInitCb;

} BSP_AUDIO_IN_Cb_t;
#endif /* USE_HAL_MDF_REGISTER_CALLBACKS == 1 */

typedef struct
{
  /* Filter parameters */
  MDF_Filter_TypeDef   *FilterInstance;
  uint32_t              RegularTrigger;
  uint32_t              SincOrder;
  uint32_t              Oversampling;
  /* Channel parameters */
  MDF_SerialInterfaceTypeDef *ChannelInstance;
  uint32_t              DigitalMicPins;
  uint32_t              DigitalMicType;
  uint32_t              Channel4Filter;
  uint32_t              ClockDivider;
  uint32_t              RightBitShift;
} MX_MDF_InitTypeDef;

/* Audio in context */
typedef struct
{
  uint32_t  Device;              /* Audio IN device to be used     */
  uint32_t  SampleRate;          /* Audio IN Sample rate           */
  uint32_t  BitsPerSample;       /* Audio IN Sample resolution     */
  uint32_t  ChannelsNbr;         /* Audio IN number of channel     */
  uint8_t   *pBuff;              /* Audio IN record buffer         */
  uint32_t  Size;                /* Audio IN record buffer size    */
  uint32_t  Volume;              /* Audio IN volume                */
  uint32_t  State;               /* Audio IN State                 */
} AUDIO_IN_Ctx_t;
/**
  * @}
  */

/** @defgroup B_U585I_IOT02A_AUDIO_Exported_Constants AUDIO Exported Constants
  * @{
  */

/* Audio in instances */
#define AUDIO_IN_INSTANCES_NBR 1U

/* Audio input devices count */
#define AUDIO_IN_DEVICE_NUMBER 2U

/* Audio input devices */
#define AUDIO_IN_DEVICE_DIGITAL_MIC1      0x01U /* digital microphone 1 */
#define AUDIO_IN_DEVICE_DIGITAL_MIC2      0x02U /* digital microphone 2 */
#define AUDIO_IN_DEVICE_DIGITAL_MIC      (AUDIO_IN_DEVICE_DIGITAL_MIC1 | AUDIO_IN_DEVICE_DIGITAL_MIC2)

/* Audio in states */
#define AUDIO_IN_STATE_RESET     0U
#define AUDIO_IN_STATE_RECORDING 1U
#define AUDIO_IN_STATE_STOP      2U
#define AUDIO_IN_STATE_PAUSE     3U

/* Audio sample rate */
#define AUDIO_FREQUENCY_192K 192000U
#define AUDIO_FREQUENCY_176K 176400U
#define AUDIO_FREQUENCY_96K   96000U
#define AUDIO_FREQUENCY_88K   88200U
#define AUDIO_FREQUENCY_48K   48000U
#define AUDIO_FREQUENCY_44K   44100U
#define AUDIO_FREQUENCY_32K   32000U
#define AUDIO_FREQUENCY_22K   22050U
#define AUDIO_FREQUENCY_16K   16000U
#define AUDIO_FREQUENCY_11K   11025U
#define AUDIO_FREQUENCY_8K     8000U

/* Audio bits per sample */
#define AUDIO_RESOLUTION_8B    8U
#define AUDIO_RESOLUTION_16B  16U
#define AUDIO_RESOLUTION_24B  24U
#define AUDIO_RESOLUTION_32B  32U

/* Audio mute state */
#define AUDIO_MUTE_DISABLED   0U
#define AUDIO_MUTE_ENABLED    1U

/* Audio in configuration */
#define AUDIO_MDF1_CCK1_GPIO_PORT          GPIOF
#define AUDIO_MDF1_CCK1_GPIO_CLK_ENABLE()  __HAL_RCC_GPIOF_CLK_ENABLE()
#define AUDIO_MDF1_CCK1_GPIO_PIN           GPIO_PIN_10
#define AUDIO_MDF1_CCK1_GPIO_AF            GPIO_AF6_MDF1

#define AUDIO_MDF1_SDIN0_GPIO_PORT         GPIOB
#define AUDIO_MDF1_SDIN0_GPIO_CLK_ENABLE() __HAL_RCC_GPIOB_CLK_ENABLE()
#define AUDIO_MDF1_SDIN0_GPIO_PIN          GPIO_PIN_1
#define AUDIO_MDF1_SDIN0_GPIO_AF           GPIO_AF6_MDF1

#define AUDIO_ADF1_CCK0_GPIO_PORT          GPIOE
#define AUDIO_ADF1_CCK0_GPIO_CLK_ENABLE()  __HAL_RCC_GPIOE_CLK_ENABLE()
#define AUDIO_ADF1_CCK0_GPIO_PIN           GPIO_PIN_9
#define AUDIO_ADF1_CCK0_GPIO_AF            GPIO_AF3_ADF1

#define AUDIO_ADF1_SDINx_GPIO_PORT         GPIOE
#define AUDIO_ADF1_SDINx_GPIO_CLK_ENABLE() __HAL_RCC_GPIOE_CLK_ENABLE()
#define AUDIO_ADF1_SDINx_GPIO_PIN          GPIO_PIN_10
#define AUDIO_ADF1_SDINx_GPIO_AF           GPIO_AF3_ADF1

#define AUDIO_MDF1_CLK_ENABLE()            __HAL_RCC_MDF1_CLK_ENABLE()
#define AUDIO_MDF1_CLK_DISABLE()           __HAL_RCC_MDF1_CLK_DISABLE()

#define AUDIO_ADF1_CLK_ENABLE()            __HAL_RCC_ADF1_CLK_ENABLE()
#define AUDIO_ADF1_CLK_DISABLE()           __HAL_RCC_ADF1_CLK_DISABLE()
/**
  * @}
  */

/** @addtogroup B_U585I_IOT02A_AUDIO_Exported_Variables
  * @{
  */

/* Audio in DMA handle used by MDF */
extern DMA_HandleTypeDef   haudio_mdf[AUDIO_IN_DEVICE_NUMBER];

/* Audio in and out context */
extern AUDIO_IN_Ctx_t  Audio_In_Ctx[AUDIO_IN_INSTANCES_NBR];

/* Audio component object */
extern void *Audio_CompObj;

/* Audio driver */
extern AUDIO_Drv_t *Audio_Drv;

/* Audio in MDF handle */
extern MDF_HandleTypeDef haudio_in_mdf_filter[AUDIO_IN_DEVICE_NUMBER];
/**
  * @}
  */

/** @defgroup B_U585I_IOT02A_AUDIO_IN_Exported_Functions AUDIO Exported Functions
  * @{
  */
int32_t           BSP_AUDIO_IN_Init(uint32_t Instance, BSP_AUDIO_Init_t *AudioInit);
int32_t           BSP_AUDIO_IN_DeInit(uint32_t Instance);
int32_t           BSP_AUDIO_IN_Record(uint32_t Instance, uint8_t *pData, uint32_t NbrOfBytes);
int32_t           BSP_AUDIO_IN_Pause(uint32_t Instance);
int32_t           BSP_AUDIO_IN_Resume(uint32_t Instance);
int32_t           BSP_AUDIO_IN_Stop(uint32_t Instance);
int32_t           BSP_AUDIO_IN_SetVolume(uint32_t Instance, uint32_t Volume);
int32_t           BSP_AUDIO_IN_GetVolume(uint32_t Instance, uint32_t *Volume);
int32_t           BSP_AUDIO_IN_SetSampleRate(uint32_t Instance, uint32_t SampleRate);
int32_t           BSP_AUDIO_IN_GetSampleRate(uint32_t Instance, uint32_t *SampleRate);
int32_t           BSP_AUDIO_IN_SetDevice(uint32_t Instance, uint32_t Device);
int32_t           BSP_AUDIO_IN_GetDevice(uint32_t Instance, uint32_t *Device);
int32_t           BSP_AUDIO_IN_SetBitsPerSample(uint32_t Instance, uint32_t BitsPerSample);
int32_t           BSP_AUDIO_IN_GetBitsPerSample(uint32_t Instance, uint32_t *BitsPerSample);
int32_t           BSP_AUDIO_IN_SetChannelsNbr(uint32_t Instance, uint32_t ChannelNbr);
int32_t           BSP_AUDIO_IN_GetChannelsNbr(uint32_t Instance, uint32_t *ChannelNbr);
int32_t           BSP_AUDIO_IN_GetState(uint32_t Instance, uint32_t *State);

#if (USE_HAL_MDF_REGISTER_CALLBACKS == 1)
int32_t           BSP_AUDIO_IN_RegisterDefaultMspCallbacks(uint32_t Instance);
int32_t           BSP_AUDIO_IN_RegisterMspCallbacks(uint32_t Instance, BSP_AUDIO_IN_Cb_t *CallBacks);
#endif /* USE_HAL_MDF_REGISTER_CALLBACKS == 1 */

void              BSP_AUDIO_IN_TransferComplete_CallBack(uint32_t Instance);
void              BSP_AUDIO_IN_HalfTransfer_CallBack(uint32_t Instance);
void              BSP_AUDIO_IN_Error_CallBack(uint32_t Instance);

void              BSP_AUDIO_IN_IRQHandler(uint32_t Instance, uint32_t Device);

HAL_StatusTypeDef MX_MDF1_ClockConfig(MDF_HandleTypeDef *hDfsdmBlock, uint32_t SampleRate);
HAL_StatusTypeDef MX_MDF1_Init(MDF_HandleTypeDef *hAdfBlock, MX_MDF_InitTypeDef *MXInit);
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

#ifdef __cplusplus
}
#endif

#endif /* B_U585I_IOT02A_AUDIO_H */

