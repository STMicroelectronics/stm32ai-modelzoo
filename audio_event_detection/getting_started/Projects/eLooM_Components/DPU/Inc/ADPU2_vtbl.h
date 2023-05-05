/**
  ******************************************************************************
  * @file    ADPU_vtbl.h
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

#ifndef INCLUDE_ADPU2_VTBL_H_
#define INCLUDE_ADPU2_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/* IDPU2 virtual functions */
sys_error_code_t ADPU2_vtblAttachToDataSource(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy);    ///< @sa IDPU2_AttachToDataSource
sys_error_code_t ADPU2_vtblDetachFromDataSource(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t **p_data_builder);                                                                 ///< @sa IDPU2_DetachFromDataSource
sys_error_code_t ADPU2_vtblAttachToDPU(IDPU2_t *_this, IDPU2_t *p_next_dpu, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy);                                                            ///< @sa IDPU2_AttachToDPU
sys_error_code_t ADPU2_vtblDetachFromDPU(IDPU2_t *_this, IDataBuilder_t **p_data_builder);                                                                                                          ///< @sa IDPU2_DetachFromDPU
sys_error_code_t ADPU2_vtblDispatchEvents(IDPU2_t *_this,  DataEvent_t *p_evt);                                                                                    ///< @sa IDPU2_DispatchEvents
sys_error_code_t ADPU2_vtblRegisterNotifyCallback(IDPU2_t *_this, DPU2_ReadyToProcessCallback_t callback, void *p_param);                                          ///< @sa IDPU2_RegisterNotifyCallback

/* IListener virtual function */
sys_error_code_t ADPU2_vtblOnStatusChange(IListener *_this);                                                                                                       ///< @sa IListenerOnStatusChange

/* IEventListener virtual functions */
void *ADPU2_vtblGetOwner(IEventListener *_this);                                                                                                                   ///< @sa IEventListenerGetOwner
void ADPU2_vtblSetOwner(IEventListener *_this, void *p_owner);                                                                                                     ///< @sa IEventListenerSetOwner

/* IDataEventListener_t virtual functions */
sys_error_code_t ADPU2_vtblOnNewDataReady(IEventListener *_this, const DataEvent_t *p_evt);                                                                        ///< @sa IDataEventListenerOnNewDataReady


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ADPU2_VTBL_H_ */
