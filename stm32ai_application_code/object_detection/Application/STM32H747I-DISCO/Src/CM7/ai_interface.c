/**
 ******************************************************************************
 * @file    ai_interface.c
 * @author  MCD Application Team
 * @brief   Abstraction interface to AI generated code
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
#include "ai_interface.h"
#include <string.h>
#include "ai_datatypes_defines.h"

/* Private typedef -----------------------------------------------------------*/
/* Private defines -----------------------------------------------------------*/
/* Private macros ------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
static ai_handle network_handle;

/* Array of pointer to manage the model's input/output tensors */
static ai_buffer *ai_input;
static ai_buffer *ai_output;

/* Global variables ----------------------------------------------------------*/
/* Private function prototypes -----------------------------------------------*/
/* Functions Definition ------------------------------------------------------*/

/**
 * @brief Returns the input format type
 * @retval ai_size Input format type: quantized (AI_BUFFER_FMT_TYPE_Q) or float (AI_BUFFER_FMT_TYPE_FLOAT)
 */
ai_size ai_get_input_format(void)
{
  ai_buffer_format fmt = AI_BUFFER_FORMAT(&ai_input[0]);
  return AI_BUFFER_FMT_GET_TYPE(fmt);
}

/**
 * @brief Returns the output format type
 * @retval ai_size Output format type: quantized (AI_BUFFER_FMT_TYPE_Q) or float (AI_BUFFER_FMT_TYPE_FLOAT)
 */
ai_size ai_get_output_format(void)
{
  ai_buffer_format fmt = AI_BUFFER_FORMAT(&ai_output[0]);
  return AI_BUFFER_FMT_GET_TYPE(fmt);
}

/**
 * @brief Returns value of the input quantized format
 * @retval ai_size Input quantized format
 */
ai_size ai_get_input_quantized_format(void)
{
  ai_buffer_format fmt = AI_BUFFER_FORMAT(&ai_input[0]);
  return (AI_BUFFER_FMT_GET_BITS(fmt) - AI_BUFFER_FMT_GET_SIGN(fmt) - AI_BUFFER_FMT_GET_FBITS(fmt));
}

/**
 * @brief Returns the quantization scheme used to quantize the input layer of the neural network
 * @retval ai_size Quantization scheme: AI_FXP_Q, AI_UINT_Q, AI_SINT_Q
 */
uint32_t ai_get_input_quantization_scheme(void)
{
  ai_float scale=ai_get_input_scale();
  
  ai_buffer_format fmt=AI_BUFFER_FORMAT(&ai_input[0]);
  ai_size sign = AI_BUFFER_FMT_GET_SIGN(fmt);  
  
  if(scale==0)
  {
    return AI_FXP_Q;
  }
  else
  {
    if(sign==0)
    {
      return AI_UINT_Q;
    }
    else
    {
      return AI_SINT_Q;
    }
  }
}

/**
 * @brief Returns the quantization scheme used to quantize the output layer of the neural network
 * @retval ai_size Quantization scheme: AI_FXP_Q, AI_UINT_Q, AI_SINT_Q
 */
uint32_t ai_get_output_quantization_scheme(void)
{
  ai_float scale=ai_get_output_scale();
  
  ai_buffer_format fmt=AI_BUFFER_FORMAT(&ai_output[0]);
  ai_size sign = AI_BUFFER_FMT_GET_SIGN(fmt);  
  
  if(scale==0)
  {
    return AI_FXP_Q;
  }
  else
  {
    if(sign==0)
    {
      return AI_UINT_Q;
    }
    else
    {
      return AI_SINT_Q;
    }
  }
}


/**
 * @brief Returns value of the scale for the output quantized format
 * @retval ai_size Scale for output quantized format
 */
ai_float ai_get_output_fxp_scale(void)
{
  float scale;
  ai_buffer_format fmt_1;
  
  /* Retrieve format of the output tensor - index 0 */
  fmt_1 = AI_BUFFER_FORMAT(&ai_output[0]);
  
  /* Build the scale factor for conversion */
  scale = 1.0f / (0x1U << AI_BUFFER_FMT_GET_FBITS(fmt_1));
  
  return scale;
}

/**
 * @brief Returns value of the scale for the input quantized format
 * @retval ai_size Scale for input quantized format
 */
ai_float ai_get_input_scale(void)
{
  return AI_BUFFER_META_INFO_INTQ_GET_SCALE(ai_input[0].meta_info, 0);
}

/**
 * @brief Returns value of the zero point for the input quantized format
 * @retval ai_size Zero point for input quantized format
 */
ai_i32 ai_get_input_zero_point(void)
{
  return AI_BUFFER_META_INFO_INTQ_GET_ZEROPOINT(ai_input[0].meta_info, 0);
}

/**
 * @brief Returns value of the scale for the output quantized format
 * @retval ai_size Scale for output quantized format
 */
ai_float ai_get_output_scale(void)
{
  return AI_BUFFER_META_INFO_INTQ_GET_SCALE(ai_output[0].meta_info, 0);
}


/**
 * @brief Returns value of the zero point for the output quantized format
 * @retval ai_size Zero point for output quantized format
 */
ai_i32 ai_get_output_zero_point(void)
{
  return AI_BUFFER_META_INFO_INTQ_GET_ZEROPOINT(ai_output[0].meta_info, 0);
}


/**
 * @brief Initializes the generated C model for a neural network
 * @param  activation_buffer Pointer to the activation buffer (i.e. working buffer used during NN inference)
 * @retval ai_handle
 */
void ai_init(void** activation_buffer, ai_handle* inputs_buff_Ptr, ai_handle* outputs_buff_Ptr)
{
  network_handle = AI_HANDLE_NULL;
  
  /* Create and initialize the c-model */
#if AI_NETWORK_DATA_ACTIVATIONS_COUNT == 1
  const ai_handle acts[] = { activation_buffer[0] };
#elif AI_NETWORK_DATA_ACTIVATIONS_COUNT == 2
  const ai_handle acts[] = { activation_buffer[0], activation_buffer[1] };
#elif AI_NETWORK_DATA_ACTIVATIONS_COUNT == 3
  const ai_handle acts[] = { activation_buffer[0], activation_buffer[1], activation_buffer[2] };
#endif
  ai_network_create_and_init(&network_handle, acts, NULL);
  uint16_t size_output = 0;
  
  /* Retrieve pointers to the model's input/output tensors */
  ai_input = ai_network_inputs_get(network_handle, NULL);
  ai_output = ai_network_outputs_get(network_handle, &size_output);

  /*Initialize the input and output buffer pointers*/
  *inputs_buff_Ptr=ai_input[0].data;  
  for (uint8_t i = 0; i < AI_NETWORK_OUT_NUM; i++)
  {
    outputs_buff_Ptr[i]=ai_output[i].data;
  }
}

/**
 * @brief De-initializes the generated C model for a neural network
 */
void ai_deinit(void) { ai_network_destroy(network_handle); }

/**
 * @brief  Run an inference of the generated C model for a neural network
 * @param  input   Pointer to the buffer containing the inference input data
 * @param  output  Pointer to the buffer for the inference output data
 */
void ai_run(void* input, void** output)
{
  ai_i32 nbatch;
  ai_input[0].data = AI_HANDLE_PTR(input);
  for (uint8_t i = 0; i < AI_NETWORK_OUT_NUM; i++)
  {
    ai_output[i].data = AI_HANDLE_PTR(output[i]);
  }
  nbatch = ai_network_run(network_handle, &ai_input[0], &ai_output[0]);
  
  if (nbatch != 1) {
        while(1);
  }
}

