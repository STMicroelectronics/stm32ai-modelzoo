/**
  ******************************************************************************
  * @file    b_u585i_iot02a_audio.c
  * @author  MCD Application Team
  * @brief   This file provides the Audio driver for the B_U585I_IOT02A board.
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
  @verbatim
  How To use this driver:
  -----------------------
   + This driver supports STM32U5xx devices on B_U585I_IOT02A(MB1551) board.

   + Call the function BSP_AUDIO_IN_Init() for AUDIO IN initialization:
        Instance : Select the input instance. Can only be 0.
        AudioInit: Audio In structure to select the following parameters.
                   - Device: Select the input device (only digital).
                   - SampleRate: Select the input sample rate (8Khz .. 96Khz).
                   - BitsPerSample: Select the input resolution (16 or 32bits per sample).
                   - ChannelsNbr: Select the input channels number(1 for mono, 2 for stereo).
                                  Stereo mode is working only with 2 Michrophones (Device = AUDIO_IN_DEVICE_DIGITAL_MIC)
                   - Volume: Select the input volume(0% .. 100%).

      This function configures all the hardware required for the audio application (MDF,
      GPIOs, DMA and interrupt if needed). This function returns BSP_ERROR_NONE if configuration is OK.

      User can update the MDF configuration or the clock configurations by overriding the weak MX functions
      MX_MDF1_Init() and MX_MDF1_ClockConfig()
      User can override the default MSP configuration and register his own MSP callbacks (defined at application level)
      by calling BSP_AUDIO_IN_RegisterMspCallbacks() function.
      User can restore the default MSP configuration by calling BSP_AUDIO_IN_RegisterDefaultMspCallbacks().
      To use these two functions, user have to enable USE_HAL_MDF_REGISTER_CALLBACKS
      within stm32u5xx_hal_conf.h file.

   + Call the function BSP_EVAL_AUDIO_IN_Record() to record audio stream. The recorded data are stored
        to user buffer in raw (First buffer half contains MIC1 samples and second buffer half contains MIC2 samples ).
        Instance : Select the input instance. Can be only 0 (MDF).
        pBuf: pointer to user buffer.
        NbrOfBytes: Total size of the buffer to be sent in Bytes.
        User can retrieve the written data via BSP_AUDIO_IN_TransferComplete_CallBack() and
        BSP_AUDIO_IN_HalfTransfer_CallBack() callback functions.

   + Call the function BSP_AUDIO_IN_Pause() to pause recording.
   + Call the function BSP_AUDIO_IN_Resume() to resume recording.
   + Call the function BSP_AUDIO_IN_Stop() to stop recording.
   + Call the function BSP_AUDIO_IN_SetDevice() to update the AUDIO IN device.
   + Call the function BSP_AUDIO_IN_GetDevice() to get the AUDIO IN device.
   + Call the function BSP_AUDIO_IN_SetSampleRate() to update the AUDIO IN sample rate.
   + Call the function BSP_AUDIO_IN_GetSampleRate() to get the AUDIO IN sample rate.
   + Call the function BSP_AUDIO_IN_SetBitPerSample() to update the AUDIO IN resolution.
   + Call the function BSP_AUDIO_IN_GetBitPerSample() to get the AUDIO IN resolution.
   + Call the function BSP_AUDIO_IN_SetChannelsNbr() to update the AUDIO IN number of channels.
   + Call the function BSP_AUDIO_IN_GetChannelsNbr() to get the AUDIO IN number of channels.
   + Call the function BSP_AUDIO_IN_SetVolume() to update the AUDIO IN volume.
   + Call the function BSP_AUDIO_IN_GetVolume() to get the AUDIO IN volume.
   + Call the function BSP_AUDIO_IN_GetState() to get the AUDIO IN state.

   + For each mode, you may need to implement the relative callback functions into your code.
      The Callback functions are named AUDIO_IN_XXX_CallBack() and only their prototypes are declared in
      the b_u585i_iot02a_audio.h file (refer to the example for more details on the callbacks implementations).

   + The driver API and the callback functions are at the end of the b_u585i_iot02a_audio.h file.

  @endverbatim
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "b_u585i_iot02a_audio.h"

/** @addtogroup BSP
  * @{
  */

/** @addtogroup B_U585I_IOT02A
  * @{
  */

/** @defgroup B_U585I_IOT02A_AUDIO AUDIO
  * @{
  */

/** @defgroup B_U585I_IOT02A_AUDIO_Private_Macros AUDIO Private Macros
  * @{
  */
#define MDF_DECIMATION_RATIO(__FREQUENCY__) \
  ((__FREQUENCY__) == (AUDIO_FREQUENCY_8K)) ? (512U) \
  : ((__FREQUENCY__) == (AUDIO_FREQUENCY_11K)) ? (256U) \
  : ((__FREQUENCY__) == (AUDIO_FREQUENCY_16K)) ? (176U) \
  : ((__FREQUENCY__) == (AUDIO_FREQUENCY_22K)) ? (128U) \
  : ((__FREQUENCY__) == (AUDIO_FREQUENCY_32K)) ? (88U) \
  : ((__FREQUENCY__) == (AUDIO_FREQUENCY_44K)) ? (64U) \
  : ((__FREQUENCY__) == (AUDIO_FREQUENCY_48K)) ? (44U) : (128U)

/**
  * @}
  */

/** @defgroup B_U585I_IOT02A_AUDIO_Exported_Variables AUDIO Exported Variables
  * @{
  */
/* Audio in and out context */
AUDIO_IN_Ctx_t  Audio_In_Ctx[AUDIO_IN_INSTANCES_NBR] = {{
    AUDIO_IN_DEVICE_DIGITAL_MIC,
    AUDIO_FREQUENCY_11K,
    AUDIO_RESOLUTION_16B,
    2U,
    NULL,
    0U,
    50U,
    AUDIO_IN_STATE_RESET
  }
};

/* Audio component object */
void *Audio_CompObj = NULL;

/* Audio driver */
AUDIO_Drv_t *Audio_Drv = NULL;

/* Audio in MDF handles */
MDF_HandleTypeDef   haudio_in_mdf_filter[AUDIO_IN_DEVICE_NUMBER] = {{0}, {0}};
DMA_HandleTypeDef   haudio_mdf[AUDIO_IN_DEVICE_NUMBER] = {{0}, {0}};

static MDF_FilterConfigTypeDef filterConfig;
static MDF_DmaConfigTypeDef dmaConfig;

/**
  * @}
  */

/** @defgroup B_U585I_IOT02A_AUDIO_Private_Variables AUDIO Private Variables
  * @{
  */
/* Queue variables declaration */
static DMA_QListTypeDef MdfQueue1;
static DMA_QListTypeDef MdfQueue2;

#if (USE_HAL_MDF_REGISTER_CALLBACKS == 1)
static uint32_t AudioIn_IsMspCbValid[AUDIO_IN_INSTANCES_NBR] = {0};
#endif /* USE_HAL_MDF_REGISTER_CALLBACKS == 1 */
/**
  * @}
  */

/** @defgroup B_U585I_IOT02A_AUDIO_Private_Function_Prototypes AUDIO Private Function Prototypes
  * @{
  */
static void    MDF_BlockMspInit(MDF_HandleTypeDef *hmdf);
static void    MDF_BlockMspDeInit(MDF_HandleTypeDef *hmdf);

#if (USE_HAL_MDF_REGISTER_CALLBACKS == 1)
static void    MDF_AcquisitionCpltCallback(MDF_HandleTypeDef *hmdf_filter);
static void    MDF_AcquisitionHalfCpltCallback(MDF_HandleTypeDef *hmdf_filter);
static void    MDF_ErrorCallback(MDF_HandleTypeDef *hmdf_filter);
#endif /* (USE_HAL_MDF_REGISTER_CALLBACKS == 1) */
/**
  * @}
  */

/** @addtogroup B_U585I_IOT02A_AUDIO_IN_Exported_Functions
  * @{
  */
/**
  * @brief  Initialize the audio in peripherals.
  * @param  Instance Audio in instance.
  * @param  AudioInit Audio in init structure.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_Init(uint32_t Instance, BSP_AUDIO_Init_t *AudioInit)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_RESET)
  {
    status = BSP_ERROR_BUSY;
  }
  else if (AudioInit->BitsPerSample != AUDIO_RESOLUTION_16B)
  {
    status = BSP_ERROR_FEATURE_NOT_SUPPORTED;
  }
  else if ((AudioInit->ChannelsNbr == 1U) && (AudioInit->ChannelsNbr ==  AUDIO_IN_DEVICE_DIGITAL_MIC))
  {
    /* Stereo mode is working only with 2 michrophones */
    status = BSP_ERROR_WRONG_PARAM;
  }
  else
  {
    if (Instance == 0U)
    {
      /* Fill audio in context structure */
      Audio_In_Ctx[Instance].Device         = AudioInit->Device;
      Audio_In_Ctx[Instance].SampleRate     = AudioInit->SampleRate;
      Audio_In_Ctx[Instance].BitsPerSample  = AudioInit->BitsPerSample;
      Audio_In_Ctx[Instance].ChannelsNbr    = AudioInit->ChannelsNbr;
      Audio_In_Ctx[Instance].Volume         = AudioInit->Volume;

      /* Set MDF instance according to the selected MIC */
      if ((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC) == AUDIO_IN_DEVICE_DIGITAL_MIC)
      {
        haudio_in_mdf_filter[0].Instance = ADF1_Filter0;
        haudio_in_mdf_filter[1].Instance = MDF1_Filter0;
      }
      else
      {
        haudio_in_mdf_filter[Audio_In_Ctx[Instance].Device - 1U].Instance =
          ((Audio_In_Ctx[Instance].Device == AUDIO_IN_DEVICE_DIGITAL_MIC1) ? ADF1_Filter0 : MDF1_Filter0);
      }
      /* Configure MDF clock */
      if (MX_MDF1_ClockConfig(&haudio_in_mdf_filter[0], AudioInit->SampleRate) != HAL_OK)
      {
        status = BSP_ERROR_CLOCK_FAILURE;
      }
      else if (MX_MDF1_ClockConfig(&haudio_in_mdf_filter[1], AudioInit->SampleRate) != HAL_OK)
      {
        status = BSP_ERROR_CLOCK_FAILURE;
      }
      else
      {
#if (USE_HAL_MDF_REGISTER_CALLBACKS == 0)
        if ((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC1) == AUDIO_IN_DEVICE_DIGITAL_MIC1)
        {
          MDF_BlockMspInit(&haudio_in_mdf_filter[0]);
        }
        if ((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC2) == AUDIO_IN_DEVICE_DIGITAL_MIC2)
        {
          MDF_BlockMspInit(&haudio_in_mdf_filter[1]);
        }
#else
        /* Register the MDF MSP Callbacks */
        if (AudioIn_IsMspCbValid[Instance] == 0U)
        {
          if (BSP_AUDIO_IN_RegisterDefaultMspCallbacks(Instance) != BSP_ERROR_NONE)
          {
            status = BSP_ERROR_PERIPH_FAILURE;
          }
        }
#endif /* (USE_HAL_MDF_REGISTER_CALLBACKS == 0) */
        if (status == BSP_ERROR_NONE)
        {
          /* Prepare MDF peripheral initialization */
          MX_MDF_InitTypeDef mxMdfInit;
          if ((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC1) == AUDIO_IN_DEVICE_DIGITAL_MIC1)
          {
            if (MX_MDF1_Init(&haudio_in_mdf_filter[0], &mxMdfInit) != HAL_OK)
            {
              status = BSP_ERROR_PERIPH_FAILURE;
            }

#if (USE_HAL_MDF_REGISTER_CALLBACKS == 1)
            if (status == BSP_ERROR_NONE)
            {
              /* Register MDF filter TC, HT and Error callbacks */
              if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[0], HAL_MDF_ACQ_COMPLETE_CB_ID,
                                           MDF_AcquisitionCpltCallback) != HAL_OK)
              {
                status = BSP_ERROR_PERIPH_FAILURE;
              }
              else if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[0], HAL_MDF_ACQ_HALFCOMPLETE_CB_ID,
                                                MDF_AcquisitionHalfCpltCallback) != HAL_OK)
              {
                status = BSP_ERROR_PERIPH_FAILURE;
              }
              else
              {
                if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[0], HAL_MDF_ERROR_CB_ID,
                                             MDF_ErrorCallback) != HAL_OK)
                {
                  status = BSP_ERROR_PERIPH_FAILURE;
                }
              }
            }
#endif /* (USE_HAL_MDF_REGISTER_CALLBACKS == 1) */
          }

          if ((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC2) == AUDIO_IN_DEVICE_DIGITAL_MIC2)
          {
            if (MX_MDF1_Init(&haudio_in_mdf_filter[1], &mxMdfInit) != HAL_OK)
            {
              status = BSP_ERROR_PERIPH_FAILURE;
            }

#if (USE_HAL_MDF_REGISTER_CALLBACKS == 1)
            if (status == BSP_ERROR_NONE)
            {
              /* Register MDF filter TC, HT and Error callbacks */
              if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[1], HAL_MDF_ACQ_COMPLETE_CB_ID,
                                           MDF_AcquisitionCpltCallback) != HAL_OK)
              {
                status = BSP_ERROR_PERIPH_FAILURE;
              }
              else if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[1], HAL_MDF_ACQ_HALFCOMPLETE_CB_ID,
                                                MDF_AcquisitionHalfCpltCallback) != HAL_OK)
              {
                status = BSP_ERROR_PERIPH_FAILURE;
              }
              else
              {
                if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[1], HAL_MDF_ERROR_CB_ID,
                                             MDF_ErrorCallback) != HAL_OK)
                {
                  status = BSP_ERROR_PERIPH_FAILURE;
                }
              }
            }
#endif /* (USE_HAL_MDF_REGISTER_CALLBACKS == 1) */
          }

          if (status == BSP_ERROR_NONE)
          {
            /* Update audio in context state */
            Audio_In_Ctx[Instance].State = AUDIO_IN_STATE_STOP;
          }
        }
      }
    }
  }
  return status;
}

/**
  * @brief  De-initialize the audio in peripherals.
  * @param  Instance Audio in instance.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_DeInit(uint32_t Instance)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_RESET)
  {
    if (Instance == 0U)
    {
      if (((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC1) == AUDIO_IN_DEVICE_DIGITAL_MIC1)
          && (status == BSP_ERROR_NONE))
      {
        /* MDF peripheral de-initialization */
        if (HAL_MDF_DeInit(&haudio_in_mdf_filter[0]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        else
        {
#if (USE_HAL_MDF_REGISTER_CALLBACKS == 0)
          MDF_BlockMspDeInit(&haudio_in_mdf_filter[0]);
#endif /* (USE_HAL_MDF_REGISTER_CALLBACKS == 0) */
        }
      }
      if (((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC2) == AUDIO_IN_DEVICE_DIGITAL_MIC2)
          && (status == BSP_ERROR_NONE))
      {
        /* MDF peripheral de-initialization */
        if (HAL_MDF_DeInit(&haudio_in_mdf_filter[1]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        else
        {
#if (USE_HAL_MDF_REGISTER_CALLBACKS == 0)
          MDF_BlockMspDeInit(&haudio_in_mdf_filter[1]);
#endif /* (USE_HAL_MDF_REGISTER_CALLBACKS == 0) */
        }
      }
      if (status == BSP_ERROR_NONE)
      {
        /* Update audio in context */
        Audio_In_Ctx[Instance].State = AUDIO_IN_STATE_RESET;
      }
    }
  }
  else
  {
    /* Nothing to do */
  }
  return status;
}

/**
  * @brief  Start recording audio stream to a data buffer for a determined size.
  * @param  Instance Audio in instance.
  * @param  pData Pointer on data buffer.
  * @param  NbrOfBytes Size of buffer in bytes. Maximum size is 65535 bytes.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_Record(uint32_t Instance, uint8_t *pData, uint32_t NbrOfBytes)
{
  int32_t  status = BSP_ERROR_NONE;

  if ((Instance >= AUDIO_IN_INSTANCES_NBR) || (pData == NULL) || (NbrOfBytes > 65535U))
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_STOP)
  {
    status = BSP_ERROR_BUSY;
  }
  else
  {
    if (Instance == 0U)
    {
      Audio_In_Ctx[Instance].pBuff = pData;
      Audio_In_Ctx[Instance].Size  = NbrOfBytes / Audio_In_Ctx[Instance].ChannelsNbr;

      /* Initialize the filter configuration parameters */
      filterConfig.DataSource      = MDF_DATA_SOURCE_BSMX;
      filterConfig.Delay           = 0U;
      filterConfig.CicMode         = MDF_ONE_FILTER_SINC5;
      filterConfig.DecimationRatio = 24;
      filterConfig.Offset          = 0;
      filterConfig.Gain            = 2;
      filterConfig.ReshapeFilter.Activation      = ENABLE;
      filterConfig.ReshapeFilter.DecimationRatio = MDF_RSF_DECIMATION_RATIO_4;
      filterConfig.HighPassFilter.Activation      = ENABLE;
      filterConfig.HighPassFilter.CutOffFrequency = MDF_HPF_CUTOFF_0_000625FPCM;
      filterConfig.Integrator.Activation     = DISABLE;
      filterConfig.SoundActivity.Activation           = DISABLE;
      filterConfig.SoundActivity.Mode                 = MDF_SAD_VOICE_ACTIVITY_DETECTOR;
      filterConfig.SoundActivity.FrameSize            = MDF_SAD_8_PCM_SAMPLES;
      filterConfig.SoundActivity.Hysteresis           = DISABLE;
      filterConfig.SoundActivity.SoundTriggerEvent    = MDF_SAD_ENTER_DETECT;
      filterConfig.SoundActivity.DataMemoryTransfer   = MDF_SAD_NO_MEMORY_TRANSFER;
      filterConfig.SoundActivity.MinNoiseLevel        = 0U;
      filterConfig.SoundActivity.HangoverWindow       = MDF_SAD_HANGOVER_4_FRAMES;
      filterConfig.SoundActivity.LearningFrames       = MDF_SAD_LEARNING_2_FRAMES;
      filterConfig.SoundActivity.AmbientNoiseSlope    = 0U;
      filterConfig.SoundActivity.SignalNoiseThreshold = MDF_SAD_SIGNAL_NOISE_18DB;
      filterConfig.AcquisitionMode = MDF_MODE_SYNC_CONT;
      filterConfig.FifoThreshold   = MDF_FIFO_THRESHOLD_NOT_EMPTY;
      filterConfig.DiscardSamples  = 0U;
      filterConfig.Trigger.Source  = MDF_FILTER_TRIG_TRGO;
      filterConfig.Trigger.Edge    = MDF_FILTER_TRIG_RISING_EDGE;
      filterConfig.SnapshotFormat  = MDF_SNAPSHOT_23BITS;

      if ((Audio_In_Ctx[Instance].Device == AUDIO_IN_DEVICE_DIGITAL_MIC1) && (status == BSP_ERROR_NONE))
      {
        /* Initialize DMA configuration parameters */
        dmaConfig.Address    = (uint32_t) Audio_In_Ctx[Instance].pBuff;
        dmaConfig.DataLength = Audio_In_Ctx[Instance].Size;
        dmaConfig.MsbOnly    = ENABLE;

        /* Call the Media layer start function for MIC1 channel */
        if (HAL_MDF_AcqStart_DMA(&haudio_in_mdf_filter[0], &filterConfig, &dmaConfig) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        if (HAL_MDF_GenerateTrgo(&haudio_in_mdf_filter[0]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
      if ((Audio_In_Ctx[Instance].Device == AUDIO_IN_DEVICE_DIGITAL_MIC2) && (status == BSP_ERROR_NONE))
      {
        /* Initialize DMA configuration parameters */
        dmaConfig.Address    = (uint32_t) Audio_In_Ctx[Instance].pBuff;
        dmaConfig.DataLength = Audio_In_Ctx[Instance].Size;
        dmaConfig.MsbOnly    = ENABLE;

        /* Call the Media layer start function for MIC2 channel */
        if (HAL_MDF_AcqStart_DMA(&haudio_in_mdf_filter[1], &filterConfig, &dmaConfig) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        if (HAL_MDF_GenerateTrgo(&haudio_in_mdf_filter[1]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
      if ((Audio_In_Ctx[Instance].Device == AUDIO_IN_DEVICE_DIGITAL_MIC) && (status == BSP_ERROR_NONE))
      {
        /* Initialize DMA configuration parameters */
        dmaConfig.Address    = (uint32_t) Audio_In_Ctx[Instance].pBuff;
        dmaConfig.DataLength = Audio_In_Ctx[Instance].Size;
        dmaConfig.MsbOnly    = ENABLE;

        /* Call the Media layer start function for MIC1 channel */
        if (HAL_MDF_AcqStart_DMA(&haudio_in_mdf_filter[0], &filterConfig, &dmaConfig) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        if (HAL_MDF_GenerateTrgo(&haudio_in_mdf_filter[0]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        /* Initialize DMA configuration parameters */
        dmaConfig.Address    = (uint32_t) &Audio_In_Ctx[Instance].pBuff[Audio_In_Ctx[Instance].Size / 2U];
        dmaConfig.DataLength = Audio_In_Ctx[Instance].Size;
        dmaConfig.MsbOnly    = ENABLE;

        /* Call the Media layer start function for MIC2 channel */
        if (HAL_MDF_AcqStart_DMA(&haudio_in_mdf_filter[1], &filterConfig, &dmaConfig) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        if (HAL_MDF_GenerateTrgo(&haudio_in_mdf_filter[1]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
    }
    if (status == BSP_ERROR_NONE)
    {
      /* Update audio in state */
      Audio_In_Ctx[Instance].State = AUDIO_IN_STATE_RECORDING;
    }
  }
  return status;
}

/**
  * @brief  Pause record of audio stream.
  * @param  Instance Audio in instance.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_Pause(uint32_t Instance)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_RECORDING)
  {
    status = BSP_ERROR_BUSY;
  }
  else
  {
    if (Instance == 0U)
    {
      /* Call the Media layer stop function */
      if (((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC1) == AUDIO_IN_DEVICE_DIGITAL_MIC1)
          && (status == BSP_ERROR_NONE))
      {
        if (HAL_MDF_AcqStop_DMA(&haudio_in_mdf_filter[0]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
      if (((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC2) == AUDIO_IN_DEVICE_DIGITAL_MIC2)
          && (status == BSP_ERROR_NONE))
      {
        if (HAL_MDF_AcqStop_DMA(&haudio_in_mdf_filter[1]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
    }
    if (status == BSP_ERROR_NONE)
    {
      /* Update audio in state */
      Audio_In_Ctx[Instance].State = AUDIO_IN_STATE_PAUSE;
    }
  }
  return status;
}

/**
  * @brief  Resume record of audio stream.
  * @param  Instance Audio in instance.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_Resume(uint32_t Instance)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_PAUSE)
  {
    status = BSP_ERROR_BUSY;
  }
  else
  {
    if (Instance == 0U)
    {

      if (((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC1) == AUDIO_IN_DEVICE_DIGITAL_MIC1)
          && (status == BSP_ERROR_NONE))
      {
        /* Call the Media layer start function for MIC1 channel */
        if (HAL_MDF_AcqStart_DMA(&haudio_in_mdf_filter[0], &filterConfig, &dmaConfig) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        if (HAL_MDF_GenerateTrgo(&haudio_in_mdf_filter[0]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
      if (((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC2) == AUDIO_IN_DEVICE_DIGITAL_MIC2)
          && (status == BSP_ERROR_NONE))
      {
        /* Call the Media layer start function for MIC2 channel */
        if (HAL_MDF_AcqStart_DMA(&haudio_in_mdf_filter[1], &filterConfig, &dmaConfig) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        if (HAL_MDF_GenerateTrgo(&haudio_in_mdf_filter[1]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
    }
  }
  return status;
}

/**
  * @brief  Stop record of audio stream.
  * @param  Instance Audio in instance.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_Stop(uint32_t Instance)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State == AUDIO_IN_STATE_STOP)
  {
    /* Nothing to do */
  }
  else if ((Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_RECORDING) &&
           (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_PAUSE))
  {
    status = BSP_ERROR_BUSY;
  }
  else
  {
    if (Instance == 0U)
    {
      /* Call the Media layer stop function */
      if (((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC1) == AUDIO_IN_DEVICE_DIGITAL_MIC1)
          && (status == BSP_ERROR_NONE))
      {
        if (HAL_MDF_AcqStop_DMA(&haudio_in_mdf_filter[0]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
      if (((Audio_In_Ctx[Instance].Device & AUDIO_IN_DEVICE_DIGITAL_MIC2) == AUDIO_IN_DEVICE_DIGITAL_MIC2)
          && (status == BSP_ERROR_NONE))
      {
        if (HAL_MDF_AcqStop_DMA(&haudio_in_mdf_filter[1]) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
    }
    if (status == BSP_ERROR_NONE)
    {
      /* Update audio in state */
      Audio_In_Ctx[Instance].State = AUDIO_IN_STATE_STOP;
    }
  }
  return status;
}

/**
  * @brief  Set audio in volume.
  * @param  Instance Audio in instance.
  * @param  Volume Volume level in percentage from 0% to 100%.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_SetVolume(uint32_t Instance, uint32_t Volume)
{
  int32_t status;

  if ((Instance >= AUDIO_IN_INSTANCES_NBR) || (Volume > 100U))
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  else /* Feature not supported */
  {
    status = BSP_ERROR_FEATURE_NOT_SUPPORTED;
  }
  return status;
}

/**
  * @brief  Get audio in volume.
  * @param  Instance Audio in instance.
  * @param  Volume Pointer to volume level in percentage from 0% to 100%.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_GetVolume(uint32_t Instance, uint32_t *Volume)
{
  int32_t status;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  else /* Feature not supported */
  {
    *Volume = 0U;
    status = BSP_ERROR_FEATURE_NOT_SUPPORTED;
  }
  return status;
}

/**
  * @brief  Set audio in sample rate.
  * @param  Instance Audio in instance.
  * @param  SampleRate Sample rate of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_SetSampleRate(uint32_t Instance, uint32_t SampleRate)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_STOP)
  {
    status = BSP_ERROR_BUSY;
  }
  /* Check if playback on instance 0 is on going and corresponding sample rate */
  else if ((Audio_In_Ctx[0].State != AUDIO_IN_STATE_RESET) &&
           (Audio_In_Ctx[0].SampleRate != SampleRate))
  {
    status = BSP_ERROR_FEATURE_NOT_SUPPORTED;
  }
  /* Check if sample rate is modified */
  else if (Audio_In_Ctx[Instance].SampleRate == SampleRate)
  {
    /* Nothing to do */
  }
  else
  {
    if (Instance == 0U)
    {
      /* Sample rate will change on audio record restart */
      Audio_In_Ctx[Instance].SampleRate = SampleRate;
    }
  }
  return status;
}

/**
  * @brief  Get audio in sample rate.
  * @param  Instance Audio in instance.
  * @param  SampleRate Pointer to sample rate of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_GetSampleRate(uint32_t Instance, uint32_t *SampleRate)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State == AUDIO_IN_STATE_RESET)
  {
    status = BSP_ERROR_BUSY;
  }
  /* Get the current audio in sample rate */
  else
  {
    *SampleRate = Audio_In_Ctx[Instance].SampleRate;
  }
  return status;
}

/**
  * @brief  Set audio in device.
  * @param  Instance Audio in instance.
  * @param  Device Device of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_SetDevice(uint32_t Instance, uint32_t Device)
{
  int32_t status;

  UNUSED(Device);

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_STOP)
  {
    status = BSP_ERROR_BUSY;
  }
  else
  {
    status = BSP_ERROR_FEATURE_NOT_SUPPORTED;
  }
  return status;
}

/**
  * @brief  Get audio in device.
  * @param  Instance Audio in instance.
  * @param  Device Pointer to device of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_GetDevice(uint32_t Instance, uint32_t *Device)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State == AUDIO_IN_STATE_RESET)
  {
    status = BSP_ERROR_BUSY;
  }
  /* Get the current audio in device */
  else
  {
    *Device = Audio_In_Ctx[Instance].Device;
  }
  return status;
}

/**
  * @brief  Set bits per sample for the audio in stream.
  * @param  Instance Audio in instance.
  * @param  BitsPerSample Bits per sample of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_SetBitsPerSample(uint32_t Instance, uint32_t BitsPerSample)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  else if (BitsPerSample != AUDIO_RESOLUTION_16B)
  {
    status = BSP_ERROR_FEATURE_NOT_SUPPORTED;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_STOP)
  {
    status = BSP_ERROR_BUSY;
  }
  else
  {
    /* Nothing to do because there is only one bits per sample supported (AUDIO_RESOLUTION_16b) */
  }
  return status;
}

/**
  * @brief  Get bits per sample for the audio in stream.
  * @param  Instance Audio in instance.
  * @param  BitsPerSample Pointer to bits per sample of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_GetBitsPerSample(uint32_t Instance, uint32_t *BitsPerSample)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State == AUDIO_IN_STATE_RESET)
  {
    status = BSP_ERROR_BUSY;
  }
  /* Get the current bits per sample of audio in stream */
  else
  {
    *BitsPerSample = Audio_In_Ctx[Instance].BitsPerSample;
  }
  return status;
}

/**
  * @brief  Set channels number for the audio in stream.
  * @param  Instance Audio in instance.
  * @param  ChannelNbr Channels number of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_SetChannelsNbr(uint32_t Instance, uint32_t ChannelNbr)
{
  int32_t status = BSP_ERROR_NONE;

  UNUSED(ChannelNbr);

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State != AUDIO_IN_STATE_STOP)
  {
    status = BSP_ERROR_BUSY;
  }
  else
  {
    /* Nothing to do because channels are already configurated and can't be modified */
  }
  return status;
}

/**
  * @brief  Get channels number for the audio in stream.
  * @param  Instance Audio in instance.
  * @param  ChannelNbr Pointer to channels number of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_GetChannelsNbr(uint32_t Instance, uint32_t *ChannelNbr)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Check audio in state */
  else if (Audio_In_Ctx[Instance].State == AUDIO_IN_STATE_RESET)
  {
    status = BSP_ERROR_BUSY;
  }
  /* Get the current channels number of audio in stream */
  else
  {
    *ChannelNbr = Audio_In_Ctx[Instance].ChannelsNbr;
  }
  return status;
}

/**
  * @brief  Get current state for the audio in stream.
  * @param  Instance Audio in instance.
  * @param  State Pointer to state of the audio in stream.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_GetState(uint32_t Instance, uint32_t *State)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  /* Get the current state of audio in stream */
  else
  {
    *State = Audio_In_Ctx[Instance].State;
  }
  return status;
}

#if (USE_HAL_MDF_REGISTER_CALLBACKS == 1)
/**
  * @brief  Register default BSP AUDIO IN msp callbacks.
  * @param  Instance AUDIO IN Instance.
  * @retval BSP status.
  */
int32_t BSP_AUDIO_IN_RegisterDefaultMspCallbacks(uint32_t Instance)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  else
  {
    if (Instance == 0U)
    {
      if (haudio_in_mdf_filter[0].Instance == ADF1_Filter0)
      {
        /* Register MDF MspInit/MspDeInit callbacks */
        if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[0], HAL_MDF_MSPINIT_CB_ID, MDF_BlockMspInit) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        else
        {
          if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[0], HAL_MDF_MSPDEINIT_CB_ID, MDF_BlockMspDeInit) != HAL_OK)
          {
            status = BSP_ERROR_PERIPH_FAILURE;
          }
        }
      }
      else
      {
        /* Register MDF MspInit/MspDeInit callbacks */
        if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[1], HAL_MDF_MSPINIT_CB_ID, MDF_BlockMspInit) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
        else
        {
          if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[1], HAL_MDF_MSPDEINIT_CB_ID, MDF_BlockMspDeInit) != HAL_OK)
          {
            status = BSP_ERROR_PERIPH_FAILURE;
          }
        }
      }
    }
    else
    {
      status = BSP_ERROR_WRONG_PARAM;
    }

    if (status == BSP_ERROR_NONE)
    {
      AudioIn_IsMspCbValid[Instance] = 1U;
    }
  }
  /* Return BSP status */
  return status;
}

/**
  * @brief  Register BSP AUDIO IN msp callbacks.
  * @param  Instance AUDIO IN Instance.
  * @param  CallBacks Pointer to MspInit/MspDeInit callback functions.
  * @retval BSP status
  */
int32_t BSP_AUDIO_IN_RegisterMspCallbacks(uint32_t Instance, BSP_AUDIO_IN_Cb_t *CallBacks)
{
  int32_t status = BSP_ERROR_NONE;

  if (Instance >= AUDIO_IN_INSTANCES_NBR)
  {
    status = BSP_ERROR_WRONG_PARAM;
  }
  else
  {
    if (Instance == 0U)
    {
      /* Register MDF MspInit/MspDeInit callbacks */
      if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[0], HAL_MDF_MSPINIT_CB_ID, CallBacks->pMspMdfInitCb) != HAL_OK)
      {
        status = BSP_ERROR_PERIPH_FAILURE;
      }
      else
      {
        if (HAL_MDF_RegisterCallback(&haudio_in_mdf_filter[0], HAL_MDF_MSPDEINIT_CB_ID,
                                     CallBacks->pMspMdfDeInitCb) != HAL_OK)
        {
          status = BSP_ERROR_PERIPH_FAILURE;
        }
      }
    }
    else
    {
      status = BSP_ERROR_WRONG_PARAM;
    }
  }
  if (status == BSP_ERROR_NONE)
  {
    AudioIn_IsMspCbValid[Instance] = 1U;
  }
  /* Return BSP status */
  return status;
}
#endif /* USE_HAL_MDF_REGISTER_CALLBACKS == 1 */

/**
  * @brief  Manage the BSP audio in transfer complete event.
  * @param  Instance Audio in instance.
  * @retval None.
  */
__weak void BSP_AUDIO_IN_TransferComplete_CallBack(uint32_t Instance)
{
  /* Prevent unused argument(s) compilation warning */
  UNUSED(Instance);
}

/**
  * @brief  Manage the BSP audio in half transfer complete event.
  * @param  Instance Audio in instance.
  * @retval None.
  */
__weak void BSP_AUDIO_IN_HalfTransfer_CallBack(uint32_t Instance)
{
  /* Prevent unused argument(s) compilation warning */
  UNUSED(Instance);
}

/**
  * @brief  Manages the BSP audio in error event.
  * @param  Instance Audio in instance.
  * @retval None.
  */
__weak void BSP_AUDIO_IN_Error_CallBack(uint32_t Instance)
{
  /* Prevent unused argument(s) compilation warning */
  UNUSED(Instance);
}

/**
  * @brief  BSP AUDIO IN interrupt handler.
  * @param  Instance Audio in instance.
  * @param  Device Device of the audio in stream.
  * @retval None.
  */
void BSP_AUDIO_IN_IRQHandler(uint32_t Instance, uint32_t Device)
{
  if (Instance == 0U)
  {
    if (Device == AUDIO_IN_DEVICE_DIGITAL_MIC1)
    {
      HAL_DMA_IRQHandler(&haudio_mdf[0]);
    }
    else /* Device == AUDIO_IN_DEVICE_DIGITAL_MIC2 */
    {
      HAL_DMA_IRQHandler(&haudio_mdf[1]);
    }
  }
}
/**
  * @}
  */

/** @defgroup B_U585I_IOT02A_AUDIO_Private_Functions AUDIO Private Functions
  * @{
  */

/**
  * @brief  Initialize MDF filter MSP.
  * @param  hmdf MDF filter handle.
  * @retval None.
  */
static void MDF_BlockMspInit(MDF_HandleTypeDef *hmdf)
{
  static DMA_NodeTypeDef     DmaNode[2] = {{{0}}, {{0}}};
  DMA_NodeConfTypeDef dmaNodeConfig;
  GPIO_InitTypeDef  GPIO_InitStruct;

  if (hmdf->Instance == ADF1_Filter0)
  {
    /* Reset ADF1 and enable clock */
    AUDIO_ADF1_CLK_ENABLE();
    __HAL_RCC_ADF1_RELEASE_RESET();
    __HAL_RCC_ADF1_CLK_ENABLE();

    /* ADF pins configuration: ADF1_CCK0, ADF1_DATINx pins */
    AUDIO_ADF1_CCK0_GPIO_CLK_ENABLE();
    GPIO_InitStruct.Mode      = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull      = GPIO_NOPULL;
    GPIO_InitStruct.Speed     = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = AUDIO_ADF1_CCK0_GPIO_AF;
    GPIO_InitStruct.Pin       = AUDIO_ADF1_CCK0_GPIO_PIN;
    HAL_GPIO_Init(AUDIO_ADF1_CCK0_GPIO_PORT, &GPIO_InitStruct);

    AUDIO_ADF1_SDINx_GPIO_CLK_ENABLE();
    GPIO_InitStruct.Alternate = AUDIO_ADF1_SDINx_GPIO_AF;
    GPIO_InitStruct.Pin       = AUDIO_ADF1_SDINx_GPIO_PIN;
    HAL_GPIO_Init(AUDIO_ADF1_SDINx_GPIO_PORT, &GPIO_InitStruct);

    /* Enable the DMA clock */
    __HAL_RCC_GPDMA1_CLK_ENABLE();

    if (MdfQueue1.Head == NULL)
    {
      /* ADF DMA configuration */
      dmaNodeConfig.NodeType                    = DMA_GPDMA_LINEAR_NODE;
      dmaNodeConfig.Init                        = haudio_mdf[0].Init;
      dmaNodeConfig.Init.Request                = GPDMA1_REQUEST_ADF1_FLT0;
      dmaNodeConfig.Init.BlkHWRequest           = DMA_BREQ_SINGLE_BURST;
      dmaNodeConfig.Init.Direction              = DMA_PERIPH_TO_MEMORY;
      dmaNodeConfig.Init.SrcInc                 = DMA_SINC_FIXED;
      dmaNodeConfig.Init.DestInc                = DMA_DINC_INCREMENTED;
      if (Audio_In_Ctx[0].BitsPerSample == AUDIO_RESOLUTION_16B)
      {
        dmaNodeConfig.Init.SrcDataWidth         = DMA_SRC_DATAWIDTH_HALFWORD;
        dmaNodeConfig.Init.DestDataWidth        = DMA_DEST_DATAWIDTH_HALFWORD;
      }
      else /* AUDIO_RESOLUTION_24b */
      {
        dmaNodeConfig.Init.SrcDataWidth         = DMA_SRC_DATAWIDTH_WORD;
        dmaNodeConfig.Init.DestDataWidth        = DMA_DEST_DATAWIDTH_WORD;
      }
      dmaNodeConfig.Init.Priority               = DMA_HIGH_PRIORITY;
      dmaNodeConfig.Init.SrcBurstLength         = 1;
      dmaNodeConfig.Init.DestBurstLength        = 1;
      dmaNodeConfig.Init.TransferAllocatedPort  = DMA_SRC_ALLOCATED_PORT0 | DMA_DEST_ALLOCATED_PORT1;
      dmaNodeConfig.Init.TransferEventMode      = DMA_TCEM_BLOCK_TRANSFER;
      dmaNodeConfig.Init.Mode                   = DMA_NORMAL;

      dmaNodeConfig.DataHandlingConfig.DataExchange       = DMA_EXCHANGE_NONE;
      dmaNodeConfig.DataHandlingConfig.DataAlignment      = DMA_DATA_UNPACK;
      dmaNodeConfig.TriggerConfig.TriggerMode             = DMA_TRIGM_BLOCK_TRANSFER;
      dmaNodeConfig.TriggerConfig.TriggerPolarity         = DMA_TRIG_POLARITY_MASKED;
      dmaNodeConfig.TriggerConfig.TriggerSelection        = GPDMA1_TRIGGER_EXTI_LINE0;
      dmaNodeConfig.RepeatBlockConfig.RepeatCount         = 1U;
      dmaNodeConfig.RepeatBlockConfig.SrcAddrOffset       = 0;
      dmaNodeConfig.RepeatBlockConfig.DestAddrOffset      = 0;
      dmaNodeConfig.RepeatBlockConfig.BlkSrcAddrOffset    = 0;
      dmaNodeConfig.RepeatBlockConfig.BlkDestAddrOffset   = 0;

      /* Build node */
      if (HAL_DMAEx_List_BuildNode(&dmaNodeConfig, &DmaNode[0]) != HAL_OK)
      {
        BSP_AUDIO_IN_Error_CallBack(0);
      }

      /* Insert node to queue */
      if (HAL_DMAEx_List_InsertNode(&MdfQueue1, NULL, &DmaNode[0]) != HAL_OK)
      {
        BSP_AUDIO_IN_Error_CallBack(0);
      }

      /* Set queue in circular mode */
      if (HAL_DMAEx_List_SetCircularMode(&MdfQueue1) != HAL_OK)
      {
        BSP_AUDIO_IN_Error_CallBack(0);
      }
    }
    haudio_mdf[0].Instance               = GPDMA1_Channel6;

    /* Fill linked list structure */
    haudio_mdf[0].InitLinkedList.Priority          = DMA_HIGH_PRIORITY;
    haudio_mdf[0].InitLinkedList.LinkStepMode      = DMA_LSM_FULL_EXECUTION;
    haudio_mdf[0].InitLinkedList.LinkAllocatedPort = DMA_LINK_ALLOCATED_PORT0;
    haudio_mdf[0].InitLinkedList.TransferEventMode = DMA_TCEM_EACH_LL_ITEM_TRANSFER;
    haudio_mdf[0].InitLinkedList.LinkedListMode    = DMA_LINKEDLIST_CIRCULAR;

    /* DMA linked list init */
    if (HAL_DMAEx_List_Init(&haudio_mdf[0]) != HAL_OK)
    {
      BSP_AUDIO_IN_Error_CallBack(0);
    }

    /* Link queue to DMA channel */
    if (HAL_DMAEx_List_LinkQ(&haudio_mdf[0], &MdfQueue1) != HAL_OK)
    {
      BSP_AUDIO_IN_Error_CallBack(0);
    }

    __HAL_LINKDMA(hmdf, hdma, haudio_mdf[0]);

    HAL_NVIC_SetPriority(GPDMA1_Channel6_IRQn, BSP_AUDIO_IN_IT_PRIORITY, 0);
    HAL_NVIC_EnableIRQ(GPDMA1_Channel6_IRQn);
  }
  else if (hmdf->Instance == MDF1_Filter0)
  {
    /* Reset MDF1 and enable clock */
    AUDIO_MDF1_CLK_ENABLE();
    __HAL_RCC_MDF1_FORCE_RESET();
    __HAL_RCC_MDF1_RELEASE_RESET();

    HAL_GPIO_DeInit(AUDIO_MDF1_CCK1_GPIO_PORT, AUDIO_MDF1_CCK1_GPIO_PIN);
    HAL_GPIO_DeInit(AUDIO_MDF1_SDIN0_GPIO_PORT, AUDIO_MDF1_SDIN0_GPIO_PIN);
    /* MDF pins configuration: MDF1_CCK1, MDF1_DATIN0 pins */
    AUDIO_MDF1_CCK1_GPIO_CLK_ENABLE();
    GPIO_InitStruct.Mode      = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull      = GPIO_NOPULL;
    GPIO_InitStruct.Speed     = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = AUDIO_MDF1_CCK1_GPIO_AF;
    GPIO_InitStruct.Pin       = AUDIO_MDF1_CCK1_GPIO_PIN;
    HAL_GPIO_Init(AUDIO_MDF1_CCK1_GPIO_PORT, &GPIO_InitStruct);

    AUDIO_MDF1_SDIN0_GPIO_CLK_ENABLE();
    GPIO_InitStruct.Alternate = AUDIO_MDF1_SDIN0_GPIO_AF;
    GPIO_InitStruct.Pin       = AUDIO_MDF1_SDIN0_GPIO_PIN;
    HAL_GPIO_Init(AUDIO_MDF1_SDIN0_GPIO_PORT, &GPIO_InitStruct);

    /* Enable the DMA clock */
    __HAL_RCC_GPDMA1_CLK_ENABLE();

    if (MdfQueue2.Head == NULL)
    {
      /* MDF DMA configuration */
      dmaNodeConfig.NodeType                    = DMA_GPDMA_LINEAR_NODE;
      dmaNodeConfig.Init                        = haudio_mdf[1].Init;
      dmaNodeConfig.Init.Request                = GPDMA1_REQUEST_MDF1_FLT0;
      dmaNodeConfig.Init.BlkHWRequest           = DMA_BREQ_SINGLE_BURST;
      dmaNodeConfig.Init.Direction              = DMA_PERIPH_TO_MEMORY;
      dmaNodeConfig.Init.SrcInc                 = DMA_SINC_FIXED;
      dmaNodeConfig.Init.DestInc                = DMA_DINC_INCREMENTED;
      if (Audio_In_Ctx[0].BitsPerSample == AUDIO_RESOLUTION_16B)
      {
        dmaNodeConfig.Init.SrcDataWidth         = DMA_SRC_DATAWIDTH_HALFWORD;
        dmaNodeConfig.Init.DestDataWidth        = DMA_DEST_DATAWIDTH_HALFWORD;
      }
      else /* AUDIO_RESOLUTION_24b */
      {
        dmaNodeConfig.Init.SrcDataWidth         = DMA_SRC_DATAWIDTH_WORD;
        dmaNodeConfig.Init.DestDataWidth        = DMA_DEST_DATAWIDTH_WORD;
      }
      dmaNodeConfig.Init.Priority               = DMA_HIGH_PRIORITY;
      dmaNodeConfig.Init.SrcBurstLength         = 1;
      dmaNodeConfig.Init.DestBurstLength        = 1;
      dmaNodeConfig.Init.TransferAllocatedPort  = DMA_SRC_ALLOCATED_PORT0 | DMA_DEST_ALLOCATED_PORT1;
      dmaNodeConfig.Init.TransferEventMode      = DMA_TCEM_BLOCK_TRANSFER;
      dmaNodeConfig.Init.Mode                   = DMA_NORMAL;

      dmaNodeConfig.DataHandlingConfig.DataExchange       = DMA_EXCHANGE_NONE;
      dmaNodeConfig.DataHandlingConfig.DataAlignment      = DMA_DATA_UNPACK;
      dmaNodeConfig.TriggerConfig.TriggerMode             = DMA_TRIGM_BLOCK_TRANSFER;
      dmaNodeConfig.TriggerConfig.TriggerPolarity         = DMA_TRIG_POLARITY_MASKED;
      dmaNodeConfig.TriggerConfig.TriggerSelection        = GPDMA1_TRIGGER_EXTI_LINE0;
      dmaNodeConfig.RepeatBlockConfig.RepeatCount         = 1U;
      dmaNodeConfig.RepeatBlockConfig.SrcAddrOffset       = 0;
      dmaNodeConfig.RepeatBlockConfig.DestAddrOffset      = 0;
      dmaNodeConfig.RepeatBlockConfig.BlkSrcAddrOffset    = 0;
      dmaNodeConfig.RepeatBlockConfig.BlkDestAddrOffset   = 0;

      /* Build node */
      if (HAL_DMAEx_List_BuildNode(&dmaNodeConfig, &DmaNode[1]) != HAL_OK)
      {
        BSP_AUDIO_IN_Error_CallBack(0);
      }

      /* Insert node to queue */
      if (HAL_DMAEx_List_InsertNode(&MdfQueue2, NULL, &DmaNode[1]) != HAL_OK)
      {
        BSP_AUDIO_IN_Error_CallBack(0);
      }

      /* Set queue in circular mode */
      if (HAL_DMAEx_List_SetCircularMode(&MdfQueue2) != HAL_OK)
      {
        BSP_AUDIO_IN_Error_CallBack(0);
      }
    }
    haudio_mdf[1].Instance               = GPDMA1_Channel0;

    /* Fill linked list structure */
    haudio_mdf[1].InitLinkedList.Priority          = DMA_HIGH_PRIORITY;
    haudio_mdf[1].InitLinkedList.LinkStepMode      = DMA_LSM_FULL_EXECUTION;
    haudio_mdf[1].InitLinkedList.LinkAllocatedPort = DMA_LINK_ALLOCATED_PORT0;
    haudio_mdf[1].InitLinkedList.TransferEventMode = DMA_TCEM_EACH_LL_ITEM_TRANSFER;
    haudio_mdf[1].InitLinkedList.LinkedListMode    = DMA_LINKEDLIST_CIRCULAR;

    /* DMA linked list init */
    if (HAL_DMAEx_List_Init(&haudio_mdf[1]) != HAL_OK)
    {
      BSP_AUDIO_IN_Error_CallBack(0);
    }

    /* Link queue to DMA channel */
    if (HAL_DMAEx_List_LinkQ(&haudio_mdf[1], &MdfQueue2) != HAL_OK)
    {
      BSP_AUDIO_IN_Error_CallBack(0);
    }

    __HAL_LINKDMA(hmdf, hdma, haudio_mdf[1]);

    HAL_NVIC_SetPriority(GPDMA1_Channel0_IRQn, BSP_AUDIO_IN_IT_PRIORITY, 0);
    HAL_NVIC_EnableIRQ(GPDMA1_Channel0_IRQn);
  }
  else
  {
    /* Do nothing */
  }

}

/**
  * @brief  DeInitialize MDF filter MSP.
  * @param  hmdf MDF filter handle.
  * @retval None.
  */
static void MDF_BlockMspDeInit(MDF_HandleTypeDef *hmdf)
{
  if (hmdf->Instance == ADF1_Filter0)
  {
    /* De-initialize ADF1_CKOUT, ADF1_DATIN1 pins */
    HAL_GPIO_DeInit(AUDIO_ADF1_CCK0_GPIO_PORT, AUDIO_ADF1_CCK0_GPIO_PIN);
    HAL_GPIO_DeInit(AUDIO_ADF1_SDINx_GPIO_PORT, AUDIO_ADF1_SDINx_GPIO_PIN);

    /* Disable ADF1 clock */
    AUDIO_ADF1_CLK_DISABLE();

    /* Disable DMA  Channel IRQ */
    HAL_NVIC_DisableIRQ(GPDMA1_Channel6_IRQn);

    /* Reset the DMA Channel configuration*/
    if (HAL_DMAEx_List_DeInit(&haudio_mdf[0]) != HAL_OK)
    {
      BSP_AUDIO_IN_Error_CallBack(0);
    }

    /* Reset MdfQueue */
    if (HAL_DMAEx_List_ResetQ(&MdfQueue1) != HAL_OK)
    {
      BSP_AUDIO_IN_Error_CallBack(0);
    }
  }
  else if (hmdf->Instance == MDF1_Filter0)
  {
    /* De-initialize MDF1_CKOUT, MDF1_DATIN1 pins */
    HAL_GPIO_DeInit(AUDIO_MDF1_CCK1_GPIO_PORT, AUDIO_MDF1_CCK1_GPIO_PIN);
    HAL_GPIO_DeInit(AUDIO_MDF1_SDIN0_GPIO_PORT, AUDIO_MDF1_SDIN0_GPIO_PIN);

    /* Disable MDF1 clock */
    AUDIO_MDF1_CLK_DISABLE();

    /* Disable DMA  Channel IRQ */
    HAL_NVIC_DisableIRQ(GPDMA1_Channel0_IRQn);

    /* Reset the DMA Channel configuration*/
    if (HAL_DMAEx_List_DeInit(&haudio_mdf[1]) != HAL_OK)
    {
      BSP_AUDIO_IN_Error_CallBack(0);
    }

    /* Reset MdfQueue */
    if (HAL_DMAEx_List_ResetQ(&MdfQueue2) != HAL_OK)
    {
      BSP_AUDIO_IN_Error_CallBack(0);
    }
  }
  else
  {
    /* Do nothing */
  }
}

#if (USE_HAL_MDF_REGISTER_CALLBACKS == 1)
/**
  * @brief  MDF filter regular conversion complete callback.
  * @param  hmdf_filter MDF filter handle.
  * @retval None.
  */
static void MDF_AcquisitionCpltCallback(MDF_HandleTypeDef *hmdf_filter)
{
  /* Invoke 'TransferCompete' callback function */
  if (hmdf_filter == &haudio_in_mdf_filter[0])
  {
    BSP_AUDIO_IN_TransferComplete_CallBack(0);
  }
  else
  {
    BSP_AUDIO_IN_TransferComplete_CallBack(1);
  }
}

/**
  * @brief  MDF filter regular conversion half complete callback.
  * @param  hmdf_filter MDF filter handle.
  * @retval None.
  */
static void MDF_AcquisitionHalfCpltCallback(MDF_HandleTypeDef *hmdf_filter)
{
  /* Invoke 'TransferCompete' callback function */
  if (hmdf_filter == &haudio_in_mdf_filter[0])
  {
    BSP_AUDIO_IN_HalfTransfer_CallBack(0);
  }
  else
  {
    BSP_AUDIO_IN_HalfTransfer_CallBack(1);
  }
}

/**
  * @brief  MDF filter error callback.
  * @param  hmdf_filter MDF filter handle.
  * @retval None.
  */
static void MDF_ErrorCallback(MDF_HandleTypeDef *hmdf_filter)
{
  UNUSED(hmdf_filter);

  BSP_AUDIO_IN_Error_CallBack(0);
}
#else /* (USE_HAL_MDF_REGISTER_CALLBACKS == 1) */
/**
  * @brief  MDF filter regular conversion complete callback.
  * @param  hmdf MDF filter handle.
  * @retval None.
  */
void HAL_MDF_AcqCpltCallback(MDF_HandleTypeDef *hmdf)
{
  /* Invoke 'TransferCompete' callback function */
  if (hmdf == &haudio_in_mdf_filter[0])
  {
    BSP_AUDIO_IN_TransferComplete_CallBack(0);
  }
  else
  {
    BSP_AUDIO_IN_TransferComplete_CallBack(1);
  }
}

/**
  * @brief  MDF filter regular conversion half complete callback.
  * @param  hmdf MDF filter handle.
  * @retval None.
  */
void HAL_MDF_AcqHalfCpltCallback(MDF_HandleTypeDef *hmdf)
{
  /* Invoke 'TransferCompete' callback function */
  if (hmdf == &haudio_in_mdf_filter[0])
  {
    BSP_AUDIO_IN_HalfTransfer_CallBack(0);
  }
  else
  {
    BSP_AUDIO_IN_HalfTransfer_CallBack(1);
  }
}


/**
  * @brief  MDF filter error callback.
  * @param  hmdf MDF filter handle.
  * @retval None.
  */
void HAL_MDF_ErrorCallback(MDF_HandleTypeDef *hmdf)
{
  UNUSED(hmdf);

  BSP_AUDIO_IN_Error_CallBack(0);
}
#endif /* (USE_HAL_MDF_REGISTER_CALLBACKS == 1) */

/**
  * @brief  MDF1 clock Config.
  * @param  hMdfBlock MDF block handle.
  * @param  SampleRate Audio sample rate used to record the audio stream.
  * @retval HAL status.
  */
__weak HAL_StatusTypeDef MX_MDF1_ClockConfig(MDF_HandleTypeDef *hMdfBlock, uint32_t SampleRate)
{
  HAL_StatusTypeDef status = HAL_OK;
  RCC_PeriphCLKInitTypeDef RCC_ExCLKInitStruct;

  /* Prevent unused argument compilation warning */
  UNUSED(SampleRate);

  if (hMdfBlock->Instance != NULL)
  {
    /* MDF Clock configuration:*/
    RCC_ExCLKInitStruct.PLL3.PLL3Source = RCC_PLLSOURCE_MSI; // clock MSI set @ 48 MHZ
    RCC_ExCLKInitStruct.PLL3.PLL3M = 12;
    RCC_ExCLKInitStruct.PLL3.PLL3N = 96;
    RCC_ExCLKInitStruct.PLL3.PLL3P = 2;
    RCC_ExCLKInitStruct.PLL3.PLL3Q = 25;
    RCC_ExCLKInitStruct.PLL3.PLL3R = 2;
    RCC_ExCLKInitStruct.PLL3.PLL3RGE = RCC_PLLVCIRANGE_0;
    RCC_ExCLKInitStruct.PLL3.PLL3FRACN = 0;
    RCC_ExCLKInitStruct.PLL3.PLL3ClockOut = RCC_PLL3_DIVQ;
    if (hMdfBlock->Instance == ADF1_Filter0)
    {
      RCC_ExCLKInitStruct.PeriphClockSelection = RCC_PERIPHCLK_ADF1;
      RCC_ExCLKInitStruct.Adf1ClockSelection   = RCC_ADF1CLKSOURCE_PLL3;
    }
    else
    {
      RCC_ExCLKInitStruct.PeriphClockSelection = RCC_PERIPHCLK_MDF1;
      RCC_ExCLKInitStruct.Mdf1ClockSelection   = RCC_MDF1CLKSOURCE_PLL3;
    }

    if (HAL_RCCEx_PeriphCLKConfig(&RCC_ExCLKInitStruct) != HAL_OK)
    {
      status = HAL_ERROR;
    }
  }

  return status;
}

/**
  * @brief  Initialize MDF1.
  * @param  hMdfBlock MDF channel handle.
  * @param  MXInit MDF configuration structure.
  * @retval HAL_status.
  */
__weak HAL_StatusTypeDef MX_MDF1_Init(MDF_HandleTypeDef *hMdfBlock, MX_MDF_InitTypeDef *MXInit)
{
  HAL_StatusTypeDef status = HAL_OK;

  UNUSED(MXInit);

  /* Fill the different hMdfBlock parameters */
  hMdfBlock->Init.CommonParam.InterleavedFilters             = 0U;
  hMdfBlock->Init.CommonParam.ProcClockDivider               = 1U;
  hMdfBlock->Init.CommonParam.OutputClock.Activation         = ENABLE;
  hMdfBlock->Init.CommonParam.OutputClock.Pins               = (hMdfBlock->Instance == ADF1_Filter0)
                                                               ? MDF_OUTPUT_CLOCK_0
                                                               : MDF_OUTPUT_CLOCK_1;
  hMdfBlock->Init.CommonParam.OutputClock.Divider            = 10U; /* MDF_CCK = 11.428MHz / 10 = 1,1428 MHz */
  hMdfBlock->Init.CommonParam.OutputClock.Trigger.Activation = ENABLE;
  hMdfBlock->Init.CommonParam.OutputClock.Trigger.Source     = MDF_CLOCK_TRIG_TRGO;
  hMdfBlock->Init.CommonParam.OutputClock.Trigger.Edge       = MDF_CLOCK_TRIG_RISING_EDGE;

  hMdfBlock->Init.SerialInterface.Activation         = ENABLE;
  hMdfBlock->Init.SerialInterface.Mode               = MDF_SITF_NORMAL_SPI_MODE;
  hMdfBlock->Init.SerialInterface.ClockSource        = (hMdfBlock->Instance == ADF1_Filter0) ? MDF_SITF_CCK0_SOURCE
                                                       : MDF_SITF_CCK1_SOURCE;
  hMdfBlock->Init.SerialInterface.Threshold          = 31U;

  hMdfBlock->Init.FilterBistream                     = (hMdfBlock->Instance != ADF1_Filter0) ? MDF_BITSTREAM5_RISING
                                                       : MDF_BITSTREAM0_RISING;

  /* Initialize  MDF */
  if (HAL_MDF_Init(hMdfBlock) != HAL_OK)
  {
    status = HAL_ERROR;
  }
  return status;
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
