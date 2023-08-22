/**
  ******************************************************************************
  * @file    app_postprocess.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   Post processing of Object Detection algorithms
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2018 STMicroelectronics.
  * All rights reserved.
  *
  * This software component is licensed by ST under Ultimate Liberty license
  * SLA0044, the "License"; You may not use this file except in compliance with
  * the License. You may obtain a copy of the License at:
  *                             www.st.com/SLA0044
  *
  ******************************************************************************
  */
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __APP_POSTPROCESS_H
#define __APP_POSTPROCESS_H

#ifdef __cplusplus
extern "C"
{
#endif

#include "main.h"

/* Exported functions ------------------------------------------------------- */
int32_t app_postprocess_init( AppConfig_TypeDef *App_Config_Ptr);
int32_t app_postprocess_run( void **pInput,
                             postprocess_out_t*pOutput,
                             void *pInput_static_param);

#ifdef __cplusplus
}
#endif

#endif /*__APP_POSTPROCESS_H */
