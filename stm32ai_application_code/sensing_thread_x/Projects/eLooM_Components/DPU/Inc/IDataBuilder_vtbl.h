/**
 ******************************************************************************
 * @file    IDataBuilder_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 1.0.0
 * @date    May 20, 2022
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
#ifndef DPU_IDATABUILDER_VTBL_H_
#define DPU_IDATABUILDER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systp.h"
#include "services/systypes.h"
#include "services/syserror.h"


/**
 * Create  type name for _IDataBuilder_vtbl_t.
 */
typedef struct _IDataBuilder_vtbl_t IDataBuilder_vtbl;

/**
 * Specifies the virtual table for the  class.
 */
struct _IDataBuilder_vtbl_t {
  sys_error_code_t (*Reset)(IDataBuilder_t *_this, void *p_data_build_context);
  sys_error_code_t (*OnNewInData)(IDataBuilder_t *_this, EMData_t *p_target_data, const EMData_t *p_new_in_data, IDB_BuildStrategy_e build_strategy, DataBuffAllocator_f data_buff_alloc);
};

/**
 * IF_NAME interface internal state.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _IDataBuilder {
  /**
   * Pointer to the virtual table for the class.
   */
  const IDataBuilder_vtbl *vptr;
};


/* Inline functions definition */
/*******************************/

static inline
sys_error_code_t IDataBuilder_Reset(IDataBuilder_t *_this, void *p_data_build_context) {
  return _this->vptr->Reset(_this, p_data_build_context);
}

static inline
sys_error_code_t IDataBuilder_OnNewInData(IDataBuilder_t *_this, EMData_t *p_target_data, const EMData_t *p_new_in_data, IDB_BuildStrategy_e build_strategy, DataBuffAllocator_f data_buff_alloc)
{
  return _this->vptr->OnNewInData(_this, p_target_data, p_new_in_data, build_strategy, data_buff_alloc);
}

#ifdef __cplusplus
}
#endif

#endif /* DPU_IDATABUILDER_VTBL_H_ */
