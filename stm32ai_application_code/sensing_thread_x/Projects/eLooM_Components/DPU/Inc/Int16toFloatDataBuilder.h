/**
 ******************************************************************************
 * @file    Int16toFloatDataBuilder.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    May 21, 2022
 *
 * @brief   Data builder that convert int16_t value into float.
 *
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
#ifndef DPU_INC_INT16TOFLOATDATABUILDER_H_
#define DPU_INC_INT16TOFLOATDATABUILDER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "IDataBuilder.h"
#include "IDataBuilder_vtbl.h"


/**
 * Create  type name for struct _Int16toFloatDataBuilder
 */
typedef struct _Int16toFloatDataBuilder Int16toFloatDataBuilder_t;

/**
 * Int16toFloatDataBuilder_t internal state.
 */
struct _Int16toFloatDataBuilder
{
  /**
   * Base interface.
   */
  IDataBuilder_t super;

  /**
   * Index used to count how many elements in the target data have been built.
   */
  uint16_t index;

  /**
   * Store the data build context passed by the object that use the data build interface.
   */
  void *p_data_build_context;
};

/* Public API declaration */
/**************************/

/**
 * Alloc an object from the system heap.
 *
 * @return a pointer to the new created object if success, NULL if an out of memory error occur.
 */
IDataBuilder_t *Int16ToFloatDB_Alloc(void);

/**
 * Pseudo allocator to perform the basic object initialization (to assign the class virtual table to the new instance)
 * to an object instance allocate buy the application.
 *
 * @param _this [IN] object instance allocated by the application.
 * @return a pointer to the new created object if success, NULL if an out of memory error occur.
 */
IDataBuilder_t *Int16ToFloatDB_AllocStatic(Int16toFloatDataBuilder_t *_this);


/* Inline functions definition */
/********************************/

#ifdef __cplusplus
}
#endif

#endif /* DPU_INC_INT16TOFLOATDATABUILDER_H_ */
