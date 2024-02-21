/**
  ******************************************************************************
  * @file    IDPU2_vtbl.h
  * @author  SRA - MCD
  * @brief
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
  */

#ifndef INCLUDE_IDPU2_VTBL_H_
#define INCLUDE_IDPU2_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/**
 * Create a type name for IDPU2_vtbl.
 */
typedef struct _IDPU2_vtbl IDPU2_vtbl;


/**
 * Specifies the virtual table for the  class.
 */
struct _IDPU2_vtbl {
  sys_error_code_t (*AttachToDataSource)(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t * p_builder, IDB_BuildStrategy_e build_strategy);
  sys_error_code_t (*DetachFromDataSource)(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t **p_data_builder);
  sys_error_code_t (*AttachToDPU)(IDPU2_t *_this, IDPU2_t *p_next_dpu, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy);
  sys_error_code_t (*DetachFromDPU)(IDPU2_t *_this, IDataBuilder_t **p_data_builder);
  sys_error_code_t (*DispatchEvents)(IDPU2_t *_this,  DataEvent_t *p_evt);
  sys_error_code_t (*RegisterNotifyCallback)(IDPU2_t *_this, DPU2_ReadyToProcessCallback_t callback, void *p_param);
  sys_error_code_t (*Process)(IDPU2_t *_this, EMData_t in_data, EMData_t out_data);
};

struct _IDPU2{
  /**
   * Pointer to the virtual table for the class.
   */
  const IDPU2_vtbl *vptr;
};


// Inline virtual functions definition
// ***********************************

static inline
sys_error_code_t IDPU2_AttachToDataSource(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy)
{
  return _this->vptr->AttachToDataSource(_this, p_data_source, p_builder, build_strategy);
}

static inline
sys_error_code_t IDPU2_DetachFromDataSource(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t **p_data_builder)
{
  return _this->vptr->DetachFromDataSource(_this, p_data_source, p_data_builder);
}

static inline
sys_error_code_t IDPU2_AttachToDPU(IDPU2_t *_this, IDPU2_t *p_next_dpu, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy)
{
  return _this->vptr->AttachToDPU(_this, p_next_dpu, p_builder, build_strategy);
}

static inline
sys_error_code_t IDPU2_DetachFromDPU(IDPU2_t *_this, IDataBuilder_t **p_data_builder)
{
  return _this->vptr->DetachFromDPU(_this, p_data_builder);
}

static inline
sys_error_code_t IDPU2_DispatchEvents(IDPU2_t *_this,  DataEvent_t *p_evt)
{
  return _this->vptr->DispatchEvents(_this, p_evt);
}

static inline
sys_error_code_t IDPU2_RegisterNotifyCallback(IDPU2_t *_this, DPU2_ReadyToProcessCallback_t callback, void *p_param)
{
  return _this->vptr->RegisterNotifyCallback(_this, callback, p_param);
}

static inline
sys_error_code_t IDPU2_Process(IDPU2_t *_this, EMData_t in_data, EMData_t out_data)
{
  return _this->vptr->Process(_this, in_data, out_data);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_IDPU2_VTBL_H_ */
