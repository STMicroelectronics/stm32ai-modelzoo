/**
  ******************************************************************************
  * @file    IDPU2.h
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

#ifndef INCLUDE_IDPU2_H_
#define INCLUDE_IDPU2_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/IDataEventListener.h"
#include "events/IDataEventListener_vtbl.h"
#include "services/ISourceObservable.h"
#include "services/ISourceObservable_vtbl.h"
#include "IDataBuilder.h"
#include "IDataBuilder_vtbl.h"

/**
 * Create  type name for IDPU2.
 */
typedef struct _IDPU2 IDPU2_t;


/**
 * Create  type name for ready to process callback.
 */
typedef void (*DPU2_ReadyToProcessCallback_t)(IDPU2_t *_this, void *param);

// Public API declaration
//***********************

/**
 * Attach an ISourceObservable object to the IDPU2 object.
 *
 * @param _this [IN] specifies a pointer to a IDPU2 object.
 * @param p_data_source [IN] specifies a pointer to a ISourceObservable object.
 * @param p_builder [IN] specifies a data builder object used to convert the data from the format of the p_data_source object
 *        to the input format of the DPU.
 * @param build_strategy [IN] specifies a build strategy.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IDPU2_AttachToDataSource(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy);

/**
 * Detach the ISourceObservable object to the IDPU2 object. If
 *
 * @param _this [IN] specifies a pointer to a IDPU2 object.
 * @param p_data_source [IN] specifies a pointer to a ISourceObservable object.
 * @param p_data_builder [OUT] specifies a pointer to the data builder associated with the data source. It can be NULL.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IDPU2_DetachFromDataSource(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t **p_data_builder);

/**
 * Attach an IDPU2 object to the IDPU2 object.
 *
 * @param _this [IN] specifies a pointer to a IDPU2 object.
 * @param p_next_dpu [IN] specifies a pointer to a IDPU2 object that become the next to the DPU chain.
 * @param p_builder [IN] specifies a data builder object used to convert the data from the format of this DPU
 *        to the input format of the p_next_dpu.
 * @param build_strategy [IN] specifies a build strategy.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IDPU2_AttachToDPU(IDPU2_t *_this, IDPU2_t *p_next_dpu, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy);

/**
 * Detach the IDPU2 object attached to object.
 * Note: there is always only one IDPU2 attached at the same time.
 *
 * @param _this [IN] specifies a pointer to a IDPU2 object.
 * @param p_data_builder [OUT] specifies a pointer to the data builder associated with the chained DPU. It can be NULL.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
static inline sys_error_code_t IDPU2_DetachFromDPU(IDPU2_t *_this, IDataBuilder_t **p_data_builder);

/**
 * Dispatch a data ready event to all listeners and IDPU2 attached to the IDPU2 object.
 *
 * @param _this [IN] specifies a pointer to a IDPU2 object.
 * @param p_evt [IN] specifies a pointer to the initializes ProcessEvent to dispatch.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
static inline sys_error_code_t IDPU2_DispatchEvents(IDPU2_t *_this,  DataEvent_t *p_evt);

/**
 * Register an user notify callback used to notify the application the IDPU2 is ready to process the data.
 * The application should be invoke the IDPU2_Process function in order to perform processing.
 * Note: THis step is optional. If there is no one callback registered the IDPU2 performs the processing as soon as
 * the input data are available.
 *
 * @param _this [IN] it specifies a pointer to a IDPU2 object.
 * @param callback [IN] it specifies a pointer to the notify callback.
 * @param p_param [IN] it specifies an application generic parameter used in the callback.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
static inline sys_error_code_t IDPU2_RegisterNotifyCallback(IDPU2_t *_this, DPU2_ReadyToProcessCallback_t callback, void *p_param);

/**
 * Perform the IDPU2 specific processing. After the processing is completed an IDPU2_DispatchEvents() is called in order
 * to notify the listeners about the complete processing.
 * Note: The IDPU2_Process function is automatically called if the user doesn't register the callback otherwise the user must call
 * it to perform the processing.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @param in_data [IN] specifies the input data to process.
 * @param out_data [IN] specifies the output data (TODO: STF - what if we want to process on the fly?).
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
static inline sys_error_code_t IDPU2_Process(IDPU2_t *_this, EMData_t in_data, EMData_t out_data);


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISENSOR_H_ */
