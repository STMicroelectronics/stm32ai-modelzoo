/**
 ******************************************************************************
 * @file    app_network.h
 * @author  MCD Application Team
 * @brief   Header for app_network.c module
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
#ifndef __APP_NETWORK_H
#define __APP_NETWORK_H

#ifdef __cplusplus
extern "C"
{
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "ai_interface.h"

/* Private macros ------------------------------------------------------------*/
#define _MIN(x_, y_) \
  ( ((x_)<(y_)) ? (x_) : (y_) )

#define _MAX(x_, y_) \
    ( ((x_)>(y_)) ? (x_) : (y_) )

#define _CLAMP(x_, min_, max_, type_) \
      (type_) (_MIN(_MAX(x_, min_), max_))

#define _ROUND(v_, type_) \
        (type_) ( ((v_)<0) ? ((v_)-0.5f) : ((v_)+0.5f) )


/* Exported types ------------------------------------------------------------*/


/* Exported constants --------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;

/* Exported functions ------------------------------------------------------- */
void Network_Deinit(void);
void Network_Init(AppConfig_TypeDef *App_Config_Ptr);
void Network_Preprocess(AppConfig_TypeDef *App_Config_Ptr);
void Network_Inference(AppConfig_TypeDef *App_Config_Ptr);
void Network_Postprocess(AppConfig_TypeDef *App_Config_Ptr);


#ifdef __cplusplus
}
#endif

#endif /*__APP_NETWORK_H */

