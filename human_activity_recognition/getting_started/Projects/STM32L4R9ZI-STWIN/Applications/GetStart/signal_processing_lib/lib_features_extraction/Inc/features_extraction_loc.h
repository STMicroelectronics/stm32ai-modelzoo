/**
 ******************************************************************************
 * @file    features_extraction_loc.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
 *
 * @brief   local header file for features extraction routines
 *
 * <DESCRIPTIOM>
 *
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
 */
  
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __FEAT_EXTRACT_LOC_H__
#define __FEAT_EXTRACT_LOC_H__


#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "arm_math.h"
#include "features_extraction_if.h"


/* Exported constants --------------------------------------------------------*/
/* Exported defines ----------------------------------------------------------*/
#define AI_SP_EPSILON                 (0.000001f)
#define AI_SP_SPECTRAL_PEAK_SNR_MAX   (100)
#define AI_SP_SPECTRAL_PEAK_MIN       (-6.0)


/* Exported macros -----------------------------------------------------------*/
#define MACRO_COMMENT(ignored)

#define  AI_SP_GENERIC_PROCESS_INIT()   \
  uint32_t i;   \
  uint16_t  mode = pInput->mode;    \
  int32_t error = AI_SP_ERROR_NO;   \
  ai_logging_packet_t packetIn = pInput->packet;    \
  ai_logging_packet_t packetOut = pOutput->packet;  \
  uint16_t data_width_in;   \
  uint16_t data_height_in;  \
  uint32_t inner_data_loop; \
  uint32_t outer_data_loop; \
  uint32_t inner_data_stride;   \
  uint32_t outer_data_stride;   \
  const float32_t *pDataIn; \
  uint32_t fmt_in;  \
  uint32_t fmt_out; \
  data_width_in = packetIn.shape.shapes[AI_LOGGING_SHAPES_WIDTH];   \
  data_height_in = (packetIn.shape.n_shape == 1) ? 1 : packetIn.shape.shapes[AI_LOGGING_SHAPES_HEIGHT]; \
  MACRO_COMMENT((/* First check that the format is currently supported :    */))    \
  MACRO_COMMENT((/*     - I/O are (signed) floating point 32 bits           */))    \
  AI_SP_PACKET_FMT_FLOAT32_CHECK(packetIn,   \
                                 packetOut); \
  MACRO_COMMENT((/* Initializes inner/outer loop counters and strides values depending  */))    \
  MACRO_COMMENT((/* on mode processing chosen.                                          */))    \
  AI_SP_LOOPCNT_INIT(mode,  \
                     data_width_in, \
                     data_height_in);

#define  AI_SP_ADPU_PROCESS_INIT()   \
  uint16_t  mode = pInput->mode;    \
  ai_logging_packet_t packetIn = pInput->packet;    \
  uint16_t data_width_in;   \
  uint16_t data_height_in;  \
  uint32_t inner_data_loop; \
  uint32_t outer_data_loop; \
  uint32_t inner_data_stride;   \
  uint32_t outer_data_stride;   \
  data_width_in = packetIn.shape.shapes[AI_LOGGING_SHAPES_WIDTH];   \
  data_height_in = (packetIn.shape.n_shape == 1) ? 1 : packetIn.shape.shapes[AI_LOGGING_SHAPES_HEIGHT]; \
  MACRO_COMMENT((/* First check that the format is currently supported :    */))    \
  MACRO_COMMENT((/*     - I/O are (signed) floating point 32 bits           */))    \
  MACRO_COMMENT((/* Initializes inner/outer loop counters and strides values depending  */))    \
  MACRO_COMMENT((/* on mode processing chosen.                                          */))    \
  AI_SP_LOOPCNT_INIT(mode,  \
                     data_width_in, \
                     data_height_in);

#define  AI_SP_PACKET_FMT_FLOAT32_CHECK(packetIn,    \
                                        packetOut)   \
  if ((packetIn.payload_type != AI_FMT) ||  \
      (packetOut.payload_type != AI_FMT))   \
  { \
    return (AI_SP_ERROR_UNSUPPORTED_FMT);   \
  } \
  else  \
  { \
    fmt_in = packetIn.payload_fmt;  \
    fmt_out = packetOut.payload_fmt;    \
    error = fmtCheckFloat32(fmt_in,   \
                            fmt_out); \
    if (error != AI_SP_ERROR_NO)    \
    {   \
      return (error);   \
    }   \
  }


#define  AI_SP_LOOPCNT_INIT(mode, \
                            data_width_in, \
                            data_height_in)   \
  if (mode == AI_SP_MODE_FULL) \
  { \
    inner_data_loop = data_width_in * data_height_in;   \
    outer_data_loop = 1;    \
    inner_data_stride = 1;  \
    outer_data_stride = inner_data_loop;    \
  } \
  else if (mode == AI_SP_MODE_LINE)    \
  { \
    inner_data_loop = data_width_in;    \
    outer_data_loop = data_height_in;   \
    inner_data_stride = 1;  \
    outer_data_stride = inner_data_loop;    \
  } \
  else if (mode == AI_SP_MODE_COLUMN)  \
  { \
    inner_data_loop = data_height_in;   \
    outer_data_loop = data_width_in;    \
    inner_data_stride = outer_data_loop;    \
    outer_data_stride = 1;  \
  } \
  else  \
  { \
    return (AI_SP_ERROR_UNSUPPORTED_FMT);   \
  }



/* Exported types ------------------------------------------------------------*/
/* External variables --------------------------------------------------------*/
/* Exported functions ------------------------------------------------------- */


#ifdef __cplusplus
}
#endif

#endif   /*  __FEAT_EXTRACT_LOC_H__  */
