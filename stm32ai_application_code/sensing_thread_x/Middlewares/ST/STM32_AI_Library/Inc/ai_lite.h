/**
  ******************************************************************************
  * @file    ai_lite.h
  * @author  AST Embedded Analytics Research Platform
  * @brief   Definitions and implementations of runtime-lite public APIs
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
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
#ifndef AI_LITE_H
#define AI_LITE_H
#pragma once
#include "ai_platform.h"
#include "ai_lite_inspect.h"

#define LITE_API_ENTRY \
  /* LITE_API_ENTRY */

#define LITE_GRAPH_INIT(_inputs, _outputs, _activations, _weights, _cb, _cb_cookie) { \
  .inputs = (_inputs), \
  .outputs = (_outputs), \
  .activations = (_activations), \
  .weights = (const ai_handle*)(_weights), \
  .cb = ((ai_lite_inspect_cb)(_cb)), \
  .cb_cookie = ((ai_handle)(_cb_cookie)), \
}


AI_API_DECLARE_BEGIN

typedef enum {
  LITE_OK = 0,
  LITE_KO_INPUTS,
  LITE_KO_OUTPUTS,
  LITE_KO_WEIGHTS,
  LITE_KO_ACTIVATIONS,
  LITE_KO_GRAPH,
} lite_result;


typedef struct {
  ai_handle*          inputs;
  ai_handle*          outputs;
  ai_handle*          activations;
  const ai_handle*    weights;
  ai_lite_inspect_cb  cb;
  ai_handle           cb_cookie;
} lite_graph;

AI_API_DECLARE_END

#endif    /* AI_LITE_H */
