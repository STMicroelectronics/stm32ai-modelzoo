/**
 ******************************************************************************
 * @file    app_network.c
 * @author  MCD Application Team
 * @brief   Library to manage neural network related operation
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

/* Includes ------------------------------------------------------------------*/
#include "app_network.h"
#include "network.h"
#include "network_data.h"

#include <stdio.h>

/* Global variables ----------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;

/* Private macro -------------------------------------------------------------*/
#define RANGING_OK_5                              (5U)
#define RANGING_OK_9                              (9U)

#define THRESHOLD_NN_OUTPUT                       (0.9)

/* Private variables ---------------------------------------------------------*/
/* Declare AI variables */
static float pool0[AI_NETWORK_DATA_ACTIVATION_1_SIZE];
static ai_handle network;
static ai_buffer* ai_input;
static ai_buffer* ai_output;
#if !defined(AI_NETWORK_INPUTS_IN_ACTIVATIONS)
  AI_ALIGNED(4) float data_in_1[AI_NETWORK_IN_1_SIZE_BYTES];
  static float* data_ins[AI_NETWORK_IN_NUM] = {data_in_1};
#else
  static float* data_ins[AI_NETWORK_IN_NUM] = {NULL};
#endif
#if !defined(AI_NETWORK_OUTPUTS_IN_ACTIVATIONS)
  AI_ALIGNED(4) float data_out_1[AI_NETWORK_OUT_1_SIZE_BYTES];
  static float* data_outs[AI_NETWORK_OUT_NUM] = {data_out_1};
#else
  static float* data_outs[AI_NETWORK_OUT_NUM] = {NULL};
#endif

/* Private function prototypes -----------------------------------------------*/
/* Post processing functions */
static int argmax(const float *, uint32_t, float);
static int label_filter(int, HANDPOSTURE_Data_t *);
/* AI functions */
static int AI_Init(void);
static int AI_Run(float *pIn, float *pOut);
static int AI_CopyInputData(HANDPOSTURE_Input_Data_t *HANDPOSTURE_Input_Data, VL53LMZ_ResultsData *pRangingData);
/* Frame validation */
static int ValidateFrame(HANDPOSTURE_Data_t *AI_Data, HANDPOSTURE_Input_Data_t *Input_AI_Data);
/* Data normalization */
static int NormalizeData(float *normalized_data, HANDPOSTURE_Input_Data_t *Input_AI_Data);
/* Output post-processing */
static int output_selection(const float * data, uint32_t len, HANDPOSTURE_Data_t *AI_Data);

/* Private function definitions ----------------------------------------------*/

/**
 * @brief  Get the index of the maximum value in a vector if it is higher than a threshold
 * @param  values Vector
 * @param  len Length of the vector
 * @param  threshold Threshold to be exceeded by the maximum value
 * @retval Index of the maximum value, or 0 if the highest value is lower than the threshold
 */
static int argmax(const float *values, uint32_t len, float threshold)
{
  float max_value = values[0];
  uint32_t max_index = 0;
  for (uint32_t i = 1; i < len; i++)
  {
    if (values[i] > max_value && values[i] > threshold)
    {
      max_value = values[i];
      max_index = i;
    }
  }
  return(max_index);
}

/**
 * @brief  Filter the NN output to avoid the classifier output to toggle
 * @param  current_label Index of the label from the argmax function
 * @param  AI_Data Data structure to save the result
 * @retval 0
 */
static int label_filter(int current_label, HANDPOSTURE_Data_t *AI_Data)
{
  if (current_label == AI_Data->previous_label)
  {
    if (AI_Data->label_count < LABEL_FILTER_N)
      AI_Data->label_count++;
    else if (AI_Data->label_count == LABEL_FILTER_N)
      AI_Data->handposture_label = current_label;
    else
      AI_Data->label_count = 0;
  }
  else
  {
    AI_Data->label_count = 0;
#if KEEP_LAST_VALID == 0
    /* This line to reset the valid Posture if a different posture is detected,
    by removing this line, we save the previous valid posture until a new valid one is detected */
    AI_Data->handposture_label = 0;
#endif
  }

  AI_Data->previous_label = current_label;
  return(0);
}

/**
 * @brief  AI Model init function
 * @param  None
 * @retval 0
 */
static int AI_Init(void)
{
  ai_handle act_addr[] = {pool0};

  /* Create and initialize an instance of the model */
  ai_network_create_and_init(&network, act_addr, NULL);

  ai_input = ai_network_inputs_get(network, NULL);
  ai_output = ai_network_outputs_get(network, NULL);

#if defined(AI_NETWORK_INPUTS_IN_ACTIVATIONS)
  /*  In the case where "--allocate-inputs" option is used, memory buffer can be
   *  used from the activations buffer. This is not mandatory.
   */
  for (int idx=0; idx < AI_NETWORK_IN_NUM; idx++)
  {
    data_ins[idx] = ai_input[idx].data;
  }
#else
  for (int idx=0; idx < AI_NETWORK_IN_NUM; idx++)
  {
    ai_input[idx].data = data_ins[idx];
  }
#endif

#if defined(AI_NETWORK_OUTPUTS_IN_ACTIVATIONS)
  /*  In the case where "--allocate-outputs" option is used, memory buffer can be
   *  used from the activations buffer. This is no mandatory.
   */
  for (int idx=0; idx < AI_NETWORK_OUT_NUM; idx++)
  {
    data_outs[idx] = ai_output[idx].data;
  }
#else
  for (int idx=0; idx < AI_NETWORK_OUT_NUM; idx++)
  {
    ai_output[idx].data = data_outs[idx];
  }
#endif

  return(0);
}

/**
 * @brief  AI Model run function
 * @param  pIn Pointer to input data
 * @param  pOut Pointer to output data
 * @retval 0 if succeeded, 1 if failed
 */
static int AI_Run(float *pIn, float *pOut)
{
  ai_i32 batch;
  ai_input[0].data = AI_HANDLE_PTR(pIn);
  ai_output[0].data = AI_HANDLE_PTR(pOut);
  batch = ai_network_run(network, ai_input, ai_output);
  return(batch<=0);
}

/**
 * @brief  Format data from L5 driver to Gesture algorithm
 * @param  HANDPOSTURE_Input_Data Pointer to destination
 * @param  pRangingData Pointer to source
 * @retval 0
 */
static int AI_CopyInputData(HANDPOSTURE_Input_Data_t *HANDPOSTURE_Input_Data, VL53LMZ_ResultsData *pRangingData)
{
  int idx;

  HANDPOSTURE_Input_Data->timestamp_ms = (int32_t) HAL_GetTick();
  for (int i = 0; i < SENSOR__MAX_NB_OF_ZONES; i++)
  {
    /* Use SENSOR_ROTATION_180 macro to rotate the data */
    #if SENSOR_ROTATION_180
      idx = SENSOR__MAX_NB_OF_ZONES - i;
    #else
      idx = i;
    #endif
    HANDPOSTURE_Input_Data->ranging[idx] = pRangingData->distance_mm[idx]/FIXED_POINT_14_2_TO_FLOAT; /* Signed 14.2 */
    HANDPOSTURE_Input_Data->peak[idx] = pRangingData->signal_per_spad[idx]/FIXED_POINT_21_11_TO_FLOAT; /* Unsigned 21.11 */
    HANDPOSTURE_Input_Data->target_status[idx] = pRangingData->target_status[idx];
    HANDPOSTURE_Input_Data->nb_targets[idx] = pRangingData->nb_target_detected[idx];
  }

  return(0);
}

/**
 * @brief  Is it a valid frame ?
 * @param  AI_Data Pointer save the result of the frame validation
 * @param  Input_AI_Data Pointer to frame data structure
 * @retval 0
 */
static int ValidateFrame(HANDPOSTURE_Data_t *AI_Data, HANDPOSTURE_Input_Data_t *Input_AI_Data)
{
  bool valid;
  int idx;
  float min = 4000.0;

  /* Find minimum valid distance */
  for (idx = 0; idx < SENSOR__MAX_NB_OF_ZONES; idx++){
    if ((Input_AI_Data->nb_targets[idx] > 0)
      && (Input_AI_Data->target_status[idx] == RANGING_OK_5 || Input_AI_Data->target_status[idx] == RANGING_OK_9)
      && Input_AI_Data->ranging[idx] < min)
    {
      min = Input_AI_Data->ranging[idx];
    }
  }

  if (min < MAX_DISTANCE && min > MIN_DISTANCE)
    AI_Data->is_valid_frame = 1;
  else
    AI_Data->is_valid_frame = 0;

  for (idx = 0; idx <SENSOR__MAX_NB_OF_ZONES; idx++)
  {
    /* Check if the data is valid */
    valid = (Input_AI_Data->nb_targets[idx] > 0)
        && (Input_AI_Data->target_status[idx] == RANGING_OK_5 || Input_AI_Data->target_status[idx] == RANGING_OK_9)
        && (Input_AI_Data->ranging[idx] < min + BACKGROUND_REMOVAL);

    /* If not valid, load default value */
    if (!valid)
    {
      Input_AI_Data->ranging[idx] = DEFAULT_RANGING_VALUE;
      Input_AI_Data->peak[idx] = DEFAULT_SIGNAL_VALUE;
    }
  }
  return(0);
}

/**
 * @brief  Normalize the data
 * @param  normalized_data Destination of the normalized data
 * @param  Input_AI_Data Source of the data to normalize
 * @retval 0
 */
static int NormalizeData(float *normalized_data, HANDPOSTURE_Input_Data_t *Input_AI_Data)
{
  int idx;
  for (idx = 0; idx <SENSOR__MAX_NB_OF_ZONES; idx++)
  {
    /* Signed 14.2 */
    normalized_data[2*idx] = (Input_AI_Data->ranging[idx] - NORMALIZATION_RANGING_CENTER) / NORMALIZATION_RANGING_IQR;
    /* Unsigned 21.11 */
    normalized_data[2*idx + 1] = (Input_AI_Data->peak[idx] - NORMALIZATION_SIGNAL_CENTER) / NORMALIZATION_SIGNAL_IQR;
  }

  return(0);
}

/**
 * @brief  Get the output class from the NN output vector
 * @param  data NN output vector
 * @param  len Length of the NN output vector
 * @param  AI_Data AI data to update
 * @retval 0
 */
static int output_selection(const float *data, uint32_t len, HANDPOSTURE_Data_t *AI_Data)
{
  int current_label = 0;

  /* If the frame is valid, get the chosen label out of the NN output */
  if (AI_Data->is_valid_frame)
  {
    /* In this example we are using an ArgMax function, but another function can be developed */
    current_label = argmax(data, len, THRESHOLD_NN_OUTPUT);
  }
  /* If the frame is not valid, set the output label as 0 */
  else
  {
    current_label = 0;
  }

  /* Filtering */
  label_filter(current_label, AI_Data);

  return(0);
}

/* Public function definitions -----------------------------------------------*/

/**
 * @brief  NETWORK Initialization
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Network_Init(AppConfig_TypeDef *App_Config)
{
  /* Init the hand posture NN */
  if (AI_Init() < 0)
  {
    printf("AI_Init failed\n");
    Error_Handler();
  }

}

/**
 * @brief  NETWORK Pre-processing
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Network_Preprocess(AppConfig_TypeDef *App_Config)
{
  /* If a new data need to be pre-processed */
  if (App_Config->new_data_received)
  {
    /* Copy the ranging data into the NN input buffer */
    if (AI_CopyInputData(&(App_Config->HANDPOSTURE_Input_Data), &(App_Config->RangingData)) < 0)
    {
      printf("AI_CopyInputData failed\n");
      Error_Handler();
    }

    /* Validate NN input data */
    if (ValidateFrame(&(App_Config->AI_Data), &(App_Config->HANDPOSTURE_Input_Data)) < 0)
    {
      printf("ValidateFrame failed\n");
      Error_Handler();
    }

    /* If the frame is valid */
    if (App_Config->AI_Data.is_valid_frame)
    {
      /* Normalize NN input data */
      if (NormalizeData(App_Config->aiInData, &(App_Config->HANDPOSTURE_Input_Data)) < 0)
      {
        printf("NormalizeData failed\n");
        Error_Handler();
      }
    }
  }

}

/**
 * @brief  NETWORK Inference
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Network_Inference(AppConfig_TypeDef *App_Config)
{
  /* If a new data need to be processed and the frame is valid */
  if (App_Config->new_data_received && App_Config->AI_Data.is_valid_frame)
  {
    /* Run NN inference */
    if (AI_Run(App_Config->aiInData, App_Config->aiOutData) < 0)
    {
      printf("AI_Run failed\n");
      Error_Handler();
    }
  }
  else
  {
	  for (int i = 0; i<AI_NETWORK_OUT_1_SIZE; i++) App_Config->aiOutData[i] = 0;
  }

}

/**
 * @brief  NETWORK Post-processing
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Network_Postprocess(AppConfig_TypeDef *App_Config)
{
  /* If a new data need to be post-processed */
  if (App_Config->new_data_received)
  {
    /* Get class from the NN output vector */
    if (output_selection(App_Config->aiOutData, AI_NETWORK_OUT_1_SIZE, &(App_Config->AI_Data)) < 0)
    {
      printf("AI_Run failed\n");
      Error_Handler();
    }
  }

}
