/**
 ******************************************************************************
 * @file    ai_logging.h
 * @brief   AILogging library prototypes.
 * AILogging is used to send and received data between STM32 
 * and Computer in Machine Learning projects.
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
 *
 * @brief
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

#ifndef AI_LOGGING_H
#define AI_LOGGING_H


#ifdef __cplusplus
extern "C" {
#endif

#include "stdint.h"

#ifndef AI_LOGGING_MAX_N_SHAPES
#define AI_LOGGING_MAX_N_SHAPES 8
#endif

#define   AI_LOGGING_SHAPES_WIDTH     (0)
#define   AI_LOGGING_SHAPES_HEIGHT    (1)
#define   AI_LOGGING_SHAPES_DEPTH     (2)




typedef enum {//This has to be aligned with Python constants
  // "System constants"
  AI_NONE = (uint8_t)0x00,
  AI_RESERVED_1 = (uint8_t)0x01,  // AI_COMMAND=(uint8_t)0x01,
  AI_RESERVED_2 = (uint8_t)0x02,  // AI_SHAPE=(uint8_t)0x02,
  AI_RESERVED_3 = (uint8_t)0x03,  // AI_TIMESTAMP=(uint8_t)0x03,

  // Data type constants
  AI_INT16=(uint8_t)0x5,
  AI_UINT16=(uint8_t)0x6,
  AI_INT32=(uint8_t) 0x7,
  AI_UINT32=(uint8_t) 0x8,
  AI_STR=(uint8_t)0x9,
  AI_INT8=(uint8_t)0xA,
  AI_UINT8=(uint8_t)0xB,
  AI_FLOAT=(uint8_t)0xC, // This is an example of a Custom data type that can be defined by user
  AI_FMT=(uint8_t)0xD

} ai_logging_payload_type;


typedef struct {
  uint16_t n_shape;
  uint16_t shapes[AI_LOGGING_MAX_N_SHAPES];
} ai_logging_shape;

typedef struct {
  ai_logging_payload_type payload_type;
  uint8_t *payload;
  uint32_t payload_fmt;
  uint32_t payload_size;

  ai_logging_shape shape;

  int32_t timestamp;
} ai_logging_packet_t;



// External Helpers
/**
 * Helpers function that helps you to fill your shape data into ai_logging_shape.
 */
/// @{
void  ai_logging_create_shape_0d(ai_logging_shape *shape);
void  ai_logging_create_shape_1d(ai_logging_shape *shape, uint16_t dim_x);
void  ai_logging_create_shape_2d(ai_logging_shape *shape, uint16_t dim_x, uint16_t dim_y);
void  ai_logging_create_shape_3d(ai_logging_shape *shape, uint16_t dim_x, uint16_t dim_y, uint16_t dim_z);
/// @}


#ifdef __cplusplus
}
#endif

#endif
