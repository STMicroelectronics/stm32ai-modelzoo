/**
  ******************************************************************************
  * @file    ai_lite_inspect.h
  * @author  AST Embedded Analytics Research Platform
  * @brief   Definitions and implementations of runtime-lite inspection routines
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
  @endverbatim
  ******************************************************************************
  */
#ifndef AI_LITE_INSPECT_H
#define AI_LITE_INSPECT_H
#pragma once 
#include "ai_platform.h"

//#define HAS_LITE_INSPECT

AI_API_DECLARE_BEGIN

/* Types needed by inspect callback signature */
typedef ai_i32 ai_data_format;
typedef ai_i32 ai_data_id;

/* Lite inspect callback definition */
typedef void (*ai_lite_inspect_cb)(
  const ai_handle cookie,
  const ai_data_id node_id,
  const ai_handle data, const ai_size data_size,
  const ai_data_format data_fmt, const ai_data_id data_id);


#ifdef HAS_LITE_INSPECT

#define LITE_INSPECT_CB(_node_id, _data, _data_size, _data_fmt, _data_id) { \
  if (graph->cb) { \
    graph->cb(graph->cb_cookie, \
              (ai_data_id)(_node_id), (ai_handle)(_data), (ai_size)(_data_size), \
              (ai_data_format)(_data_fmt), (ai_data_id)(_data_id)); \
  } \
}

#else

#define LITE_INSPECT_CB(_node_id, _data, _data_size, _data_fmt, _data_id) { \
  do { /* LITE_INSPECT_CB() */ } while (0); \
}

#endif    /* HAS_LITE_INSPECT */

AI_API_DECLARE_END

#endif    /* AI_LITE_INSPECT_H */
