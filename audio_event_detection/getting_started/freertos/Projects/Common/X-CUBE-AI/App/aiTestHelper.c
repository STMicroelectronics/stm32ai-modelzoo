/**
 ******************************************************************************
 * @file    aiTestUtility.c
 * @author  MCD/AIS Team
 * @brief   STM32 Helper functions for STM32 AI test application
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; Copyright (c) 2019,2021 STMicroelectronics.
 * All rights reserved.</center></h2>
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

/*
 * Description:
 *
 *
 * History:
 *  - v1.0 - Initial version (from initial aiSystemPerformance file v5.0)
 *  - v2.0 - Update aiPrintNetworkInfo() to use new report with support of
 *           fragmented activations/weights buffer
 *           Update buffer description for binary 32b-packet tensor
 */

#include <stdio.h>
#include <string.h>
//#include "logging_levels.h"
///* define LOG_LEVEL here if you want to modify the logging level from the default */
//#define LOG_LEVEL    LOG_INFO
//#include "logging.h"

#if !defined(TFLM_RUNTIME)

#include <aiTestHelper.h>
//#include <aiTestUtility.h>
//#define LC_PRINT(...)   vLoggingPrintf( "INF", 0 , 0, __VA_ARGS__ )
#define LC_PRINT(...)   fprintf(stdout,__VA_ARGS__)

#include <ai_platform_interface.h>


void aiPlatformVersion(void)
{
  const ai_platform_version rt_ver = ai_platform_runtime_get_version();

  LC_PRINT("\r\nAI platform (API %d.%d.%d - RUNTIME %d.%d.%d)\r\n",
      AI_PLATFORM_API_MAJOR,
      AI_PLATFORM_API_MINOR,
      AI_PLATFORM_API_MICRO,
      rt_ver.major,
      rt_ver.minor,
      rt_ver.micro);
}

void aiLogErr(const ai_error err, const char *fct)
{
  if (fct)
    LC_PRINT("E: AI error (%s) - type=0x%02x code=0x%02x\r\n", fct,
        err.type, err.code);
  else
    LC_PRINT("E: AI error - type=0x%02x code=0x%02x\r\n", err.type, err.code);
}


static inline void aiPrintDataType(const ai_buffer_format fmt)
{
    if (AI_BUFFER_FMT_GET_TYPE(fmt) == AI_BUFFER_FMT_TYPE_FLOAT)
      LC_PRINT("float%d", (int)AI_BUFFER_FMT_GET_BITS(fmt));
    else if (AI_BUFFER_FMT_GET_TYPE(fmt) == AI_BUFFER_FMT_TYPE_BOOL) {
      LC_PRINT("bool%d", (int)AI_BUFFER_FMT_GET_BITS(fmt));
    } else { /* integer type */
      LC_PRINT("%s%d", AI_BUFFER_FMT_GET_SIGN(fmt)?"i":"u",
            (int)AI_BUFFER_FMT_GET_BITS(fmt));
    }
}


void aiPrintBufferInfo(const ai_buffer *buffer)
{
  const ai_buffer_format fmt = buffer->format;

  /* shape + nb elem */
  LC_PRINT("(%ld,%ld,%ld,",
     AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_BATCH),
     AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_HEIGHT),
     AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_WIDTH));

  if (AI_BUFFER_SHAPE_SIZE(buffer) == 5)
  {
    LC_PRINT("%d,%d)",
        (int)AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_DEPTH),
        (int)AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_CHANNEL));
  }
  else if (AI_BUFFER_SHAPE_SIZE(buffer) == 6)
  {
    LC_PRINT("%d,%d,%d)",
        (int)AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_DEPTH),
        (int)AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_EXTENSION),
        (int)AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_CHANNEL));
  } else
  {
    LC_PRINT("%d)", (int)AI_BUFFER_SHAPE_ELEM(buffer, AI_SHAPE_CHANNEL));
  }

  LC_PRINT("%d/", (int)AI_BUFFER_SIZE(buffer));

  /* type (+meta_data) */
  aiPrintDataType(fmt);
  /* quantized info if available */
  if (AI_BUFFER_FMT_GET_TYPE(fmt) == AI_BUFFER_FMT_TYPE_Q) {
    if (AI_BUFFER_META_INFO_INTQ(buffer->meta_info)) {
      ai_u16 s_ = AI_BUFFER_META_INFO_INTQ_GET_SIZE(buffer->meta_info);
      const int max_ = s_> 4?4:s_;
      LC_PRINT(" %d:", s_);
      for (int idx=0; idx<max_; idx++) {
        ai_float scale = AI_BUFFER_META_INFO_INTQ_GET_SCALE(buffer->meta_info, idx);
        int zero_point = AI_BUFFER_META_INFO_INTQ_GET_ZEROPOINT(buffer->meta_info, idx);
        LC_PRINT("(%f,%d),", scale, zero_point);
      }
      	  if (s_ > max_) {
      		  LC_PRINT("..");
      	  }
    } else if (AI_BUFFER_FMT_GET_BITS(fmt) < 8) {
      /* lower of 8b format */
      LC_PRINT(" int32-%db", (int)AI_BUFFER_FMT_GET_BITS(fmt));
    } else {
      LC_PRINT(" Q%d.%d",
          (int)AI_BUFFER_FMT_GET_BITS(fmt) - ((int)AI_BUFFER_FMT_GET_FBITS(fmt) + (int)AI_BUFFER_FMT_GET_SIGN(fmt)),
          AI_BUFFER_FMT_GET_FBITS(fmt)
      );
    }
  }
  /* @ + size in bytes */
  if (buffer->data)
    LC_PRINT(" @0x%X/%d",
        (int)buffer->data,
        (int)AI_BUFFER_BYTE_SIZE(AI_BUFFER_SIZE(buffer), fmt)
    );
  else
    LC_PRINT(" (User Domain)/%d",
        (int)AI_BUFFER_BYTE_SIZE(AI_BUFFER_SIZE(buffer), fmt)
    );
}

void aiPrintNetworkInfo(const ai_network_report* report)
{
  LC_PRINT("Network informations...\r\n");
  LC_PRINT(" model name         : %s\r\n", report->model_name);
  LC_PRINT(" model signature    : %s\r\n", report->model_signature);
  LC_PRINT(" model datetime     : %s\r\n", report->model_datetime);
  LC_PRINT(" compile datetime   : %s\r\n", report->compile_datetime);
  LC_PRINT(" runtime version    : %d.%d.%d\r\n",
      report->runtime_version.major,
      report->runtime_version.minor,
      report->runtime_version.micro);
  if (report->tool_revision[0])
    LC_PRINT(" Tool revision      : %s\r\n", (report->tool_revision[0])?report->tool_revision:"");
  LC_PRINT(" tools version      : %d.%d.%d\r\n",
      report->tool_version.major,
      report->tool_version.minor,
      report->tool_version.micro);
  LC_PRINT(" complexity         : %lu MACC\r\n", (unsigned long)report->n_macc);
  LC_PRINT(" c-nodes            : %d\r\n", (int)report->n_nodes);

  LC_PRINT(" map_activations    : %d\r\n", report->map_activations.size);
  for (int idx=0; idx<report->map_activations.size;idx++) {
      const ai_buffer *buffer = &report->map_activations.buffer[idx];
      LC_PRINT("  [%d] ", idx);
      aiPrintBufferInfo(buffer);
      LC_PRINT("\r\n");
  }

  LC_PRINT(" map_weights        : %d\r\n", report->map_weights.size);
  for (int idx=0; idx<report->map_weights.size;idx++) {
      const ai_buffer *buffer = &report->map_weights.buffer[idx];
      LC_PRINT("  [%d] ", idx);
      aiPrintBufferInfo(buffer);
      LC_PRINT("\r\n");
  }

  LC_PRINT(" n_inputs/n_outputs : %u/%u\r\n", report->n_inputs,
          report->n_outputs);

  for (int i=0; i<report->n_inputs; i++) {
//     LC_PRINT("  I[%d] %s\r\n", i, aiGetBufferDesc(&report->inputs[i]));
     LC_PRINT("  I[%d] ", i);
     aiPrintBufferInfo(&report->inputs[i]);
    LC_PRINT("\r\n");
  }

  for (int i=0; i<report->n_outputs; i++) {
    //LC_PRINT("  O[%d] %s\r\n", i, aiGetBufferDesc(&report->outputs[i]));
    LC_PRINT("  O[%d] ", i);
    aiPrintBufferInfo(&report->outputs[i]);
    LC_PRINT("\r\n");
  }
}

#endif /* !TFLM_RUNTIME) */
