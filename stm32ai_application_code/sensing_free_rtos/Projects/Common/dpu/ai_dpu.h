/**
  ******************************************************************************
  * @file    ai_dpu.h
  * @author  MCD Application Team
  * @brief   Header for ai_dpu.c module
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef _AI_DPU_H
#define _AI_DPU_H

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "dpu_config.h"
#include "network.h"
#include "network_data.h"
#include "aiTestHelper.h"

/* Exported constants --------------------------------------------------------*/
#define AI_MNETWORK_NUMBER         (1U)
#define AI_DPU_SHAPE_SIZE          (4U)
#define AI_DPU_SHAPE_BATCH_MAX     (1U)
#define AI_DPU_SHAPE_HEIGHT_MAX    (100U)
#define AI_DPU_SHAPE_WIDTH_MAX     (100U)
#define AI_DPU_SHAPE_CHANNEL_MAX   (100U)
#define AI_DPU_X_CUBE_AI_API_MAJOR (1)
#define AI_DPU_X_CUBE_AI_API_MINOR (2)
#define AI_DPU_X_CUBE_AI_API_MICRO (0)
#define AI_DPU_NB_MAX_INPUT        (1U)
#define AI_DPU_NB_MAX_OUTPUT       (2U)

/* Exported types ------------------------------------------------------------*/
typedef struct {
  /**
	* AI network informations & handler
	*/
  struct ai_network_exec_ctx {
	  ai_handle handle;
	  ai_network_report report;
  }net_exec_ctx[AI_MNETWORK_NUMBER];

  /**
	* AI network activation buffer
	*/
  AI_ALIGNED(32)
  uint8_t activation_buffer[AI_NETWORK_DATA_ACTIVATION_1_SIZE];

#ifndef  AI_NETWORK_INPUTS_IN_ACTIVATIONS
  /**
  * AI network input
  */
  AI_ALIGNED(4)
  uint8_t in[AI_NETWORK_IN_1_SIZE_BYTES];
#endif

#ifndef  AI_NETWORK_OUTPUTS_IN_ACTIVATIONS
  /**
  * AI network output
  */
  AI_ALIGNED(4)
  uint8_t out1[AI_NETWORK_OUT_1_SIZE_BYTES];
#if (AI_NETWORK_OUT_NUM==2)
  AI_ALIGNED(4)
  uint8_t out2[AI_NETWORK_OUT_2_SIZE_BYTES];
#endif
#endif

  /**
   * Specifies AI processing scale factor.
   */
  float scale;

  /**
   * Specifies AI processing scale factor.
   */
  uint32_t sensor_type;

  /**
   * Specifies the quantization parameters of teh unique input of the network
   */
  float  input_Q_inv_scale;
  int8_t input_Q_offset;
}AIProcCtx_t;

/* Exported functions --------------------------------------------------------*/
BaseType_t AiDPULoadModel(AIProcCtx_t * pxCtx, const char *name);
BaseType_t AiDPUReleaseModel(AIProcCtx_t * pxCtx);
BaseType_t AiDPUProcess(AIProcCtx_t *pxCtx, int8_t *p_spectro , float *pf_out);

#endif /* _AI_DPU_H */
