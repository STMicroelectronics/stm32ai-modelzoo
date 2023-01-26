/**
  ******************************************************************************
  * @file    ai_model_config.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   User header file for Preprocessing configuration
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

/* ---------------    Generated code    ----------------- */
#ifndef __AI_MODEL_CONFIG_H__
#define __AI_MODEL_CONFIG_H__


/* I/O configuration */
#define NB_CLASSES        (5)
#define INPUT_HEIGHT        (128)
#define INPUT_WIDTH       (128)
#define INPUT_CHANNELS        (3)

/* Classes */
#define CLASSES_TABLE const char* classes_table[NB_CLASSES] = {\
   "daisy" ,   "dandelion" ,   "roses" ,   "sunflowers" ,   "tulips"}\

/* Resizing configuration */
#define NO_RESIZE       (0)
#define INTERPOLATION_NEAREST       (1)

#define PP_RESIZING_ALGO       INTERPOLATION_NEAREST

/* Input rescaling configuration */
#define PP_OFFSET       (-1.0f)
#define PP_SCALE       (127.5f)

/* Input color format configuration */
#define RGB_FORMAT    (1)
#define BGR_FORMAT    (2)
#define GRAYSCALE_FORMAT    (3)
#define PP_COLOR_MODE    RGB_FORMAT

/* Input/Output quantization configuration */
#define UINT8_FORMAT    (1)
#define INT8_FORMAT    (2)
#define FLOAT32_FORMAT    (3)

#define QUANT_INPUT_TYPE    INT8_FORMAT
#define QUANT_OUTPUT_TYPE    FLOAT32_FORMAT

#endif      /* __AI_MODEL_CONFIG_H__  */
