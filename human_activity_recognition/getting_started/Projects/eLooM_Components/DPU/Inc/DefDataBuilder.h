/**
 ******************************************************************************
 * @file    DefDataBuilder.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    Jun 17, 2022
 *
 * @brief
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef DPU_DEFDATABUILDER_H_
#define DPU_DEFDATABUILDER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "IDataBuilder.h"
#include "IDataBuilder_vtbl.h"


/**
 * Create  type name for struct _DefDataBuilder
 */
typedef struct _DefDataBuilder DefDataBuilder_t;

/**
 * DefDataBuilder_t internal state.
 */
struct _DefDataBuilder
{
  /**
   * Base interface.
   */
  IDataBuilder_t super;

  /**
   * Index used to how many elements in the target data have been built.
   */
  uint16_t index;

  /**
   * Store the data build context passed by the object that use the data build interface.
   */
  void *p_data_build_context;
};


/* Public API declaration */
/**************************/

IDataBuilder_t *DefDB_Alloc(void);

IDataBuilder_t *DefDB_AllocStatic(DefDataBuilder_t *_this);


/* Inline functions definition */
/*******************************/



#ifdef __cplusplus
}
#endif

#endif /* DPU_DEFDATABUILDER_H_ */
