/**
 ******************************************************************************
 * @file    app_network.h
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

#ifndef INC_APP_NETWORK_H_
#define INC_APP_NETWORK_H_

/* Includes ------------------------------------------------------------------*/
#include "ai_model_config.h"
#include "main.h"

/* Exported functions ------------------------------------------------------- */
void Network_Init(AppConfig_TypeDef *);
void Network_Preprocess(AppConfig_TypeDef *);
void Network_Inference(AppConfig_TypeDef *);
void Network_Postprocess(AppConfig_TypeDef *);

#endif /* INC_APP_NETWORK_H_ */
