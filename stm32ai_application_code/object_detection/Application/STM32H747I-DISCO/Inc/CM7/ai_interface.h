/**
 ******************************************************************************
 * @file    ai_interface.h
 * @author  MCD Application Team
 * @brief   Header for ai_interface.c module
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __AI_IF_H
#define __AI_IF_H

#ifdef __cplusplus
extern "C"
{
#endif

/* Includes ------------------------------------------------------------------*/
#include "network.h"
#include "network_data.h"

/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/
/* External variables --------------------------------------------------------*/
/* Exported macros -----------------------------------------------------------*/
#define AI_NET_INPUT_SIZE AI_NETWORK_IN_1_SIZE
#define AI_NET_INPUT_SIZE_BYTES AI_NETWORK_IN_1_SIZE_BYTES

#define AI_NET_OUTPUT_SIZE AI_NETWORK_OUT_1_SIZE
#define AI_NET_OUTPUT_SIZE_BYTES AI_NETWORK_OUT_1_SIZE_BYTES

#define AI_ACTIVATION_SIZE_BYTES_TOTAL AI_NETWORK_DATA_ACTIVATIONS_SIZE
#define AI_ACTIVATION_SIZE_BYTES AI_NETWORK_DATA_ACTIVATIONS_SIZE
#define AI_ACTIVATION_1_SIZE_BYTES AI_NETWORK_DATA_ACTIVATION_1_SIZE
#define AI_ACTIVATION_2_SIZE_BYTES AI_NETWORK_DATA_ACTIVATION_2_SIZE
#define AI_ACTIVATION_3_SIZE_BYTES AI_NETWORK_DATA_ACTIVATION_3_SIZE
#define AI_ACTIVATION_BUFFERS_COUNT AI_NETWORK_DATA_ACTIVATIONS_COUNT

 /*** @GENERATED CODE START - DO NOT TOUCH@ ***/
#define AI_NETWORK_INPUTS_IN_ACTIVATIONS_INDEX 0
#define AI_NETWORK_INPUTS_IN_ACTIVATIONS_SIZE AI_ACTIVATION_1_SIZE_BYTES

 /*** @GENERATED CODE STOP - DO NOT TOUCH@ ***/


#define AI_WEIGHT_SIZE_BYTES      AI_NETWORK_DATA_WEIGHTS_SIZE

#define AI_NETWORK_IN_SHIFT   1
#define AI_NETWORK_OUT_SHIFT  7

#define AI_NETWORK_WIDTH    AI_NETWORK_IN_1_WIDTH
#define AI_NETWORK_HEIGHT   AI_NETWORK_IN_1_HEIGHT
#define AI_NETWORK_CHANNEL  AI_NETWORK_IN_1_CHANNEL

/*********Quantization scheme******************/
#define AI_FXP_Q          (0x0) /*Fixed Point Qm,n*/
#define AI_UINT_Q         (0x1) /*Unsigned Integer Arithmetic*/
#define AI_SINT_Q         (0x2) /*Signed Integer Arithmetic*/

/* Exported functions ------------------------------------------------------- */
ai_size ai_get_input_quantized_format(void);
ai_float ai_get_output_fxp_scale(void);
ai_float ai_get_input_scale(void);
ai_i32  ai_get_input_zero_point(void);
ai_float ai_get_output_scale(void);
ai_i32 ai_get_output_zero_point(void);
uint32_t ai_get_input_quantization_scheme(void);
uint32_t ai_get_output_quantization_scheme(void);
ai_size ai_get_output_format(void);
ai_size ai_get_input_format(void);

void ai_init(void**, ai_handle*, ai_handle*);
void ai_deinit(void);
void ai_run(void*, void**);

#ifdef __cplusplus
}
#endif

#endif /*__AI_IF_H */

