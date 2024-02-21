/**
  ******************************************************************************
  * @file    core_datatypes.h
  * @author  AST Embedded Analytics Research Platform
  * @brief   header file of core module private defines and datatypes
  * to public nor codegen tool
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2018 STMicroelectronics.
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

#ifndef AI_CORE_DATATYPES_H
#define AI_CORE_DATATYPES_H
#pragma once
#include <stdint.h>

/*!
 * @defgroup Core Module Datatypes
 * @brief Data structures and defines used by core module
 */

/*!
 * @brief platform runtime core library version
 */
#define AI_PLATFORM_RUNTIME_MAJOR    7
#define AI_PLATFORM_RUNTIME_MINOR    3
#define AI_PLATFORM_RUNTIME_MICRO    0

#define AI_MAGIC_CONTEXT_TOKEN       (0xA1C00100)   /*!< AI Cool! Magic Token */

#define AI_MAGIC_INSPECTOR_TOKEN     (0xA1C00101)   /*!< AI Cool! Magic Token */


#define AI_ID_OBJ(id) \
  ((ai_id_obj)(id))

#define AI_C_ARRAY_COUNT(array_) \
  ( sizeof(array_) / sizeof((array_)[0]) )

#define AI_C_ARRAY_BYTE_SIZE(array_) \
  ( sizeof(array_) )


/*!
 * @typedef ai_id_obj
 * @ingroup core_datatypes
 * @brief numeric identifier for generic object instances (e.g. layers, 
 * operators, etc.) It is used by codegen tool to keep tracks of specific
 * instances created 
 */
typedef uint16_t ai_id_obj;

#endif    /*AI_CORE_DATATYPES_H*/
