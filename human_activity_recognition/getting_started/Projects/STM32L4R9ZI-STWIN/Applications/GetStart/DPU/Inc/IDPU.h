/**
  ******************************************************************************
  * @file    IDPU.h
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
 
#ifndef INCLUDE_IDPU_H_
#define INCLUDE_IDPU_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/ProcessEvent.h"
#include "events/ISourceObservable.h"
#include "events/ISourceObservable_vtbl.h"
#include "events/ISensorEventListener.h"
#include "events/ISensorEventListener_vtbl.h"

/**
 * Create  type name for IDPU.
 */
typedef struct _IDPU IDPU;

/**
 * Create  type name for ready to process callback.
 */
typedef void (*DPU_ReadyToProcessCallback_t)(IDPU *_this, void *param);

// Public API declaration
//***********************

/**
 * Initialize the IDPU object
 *
 * @param _this [IN] specifies a pointer to a IDPU object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
inline sys_error_code_t IDPU_Init(IDPU *_this);

/**
 * Attach an ISourceObservable object to the IDPU object.
 *
 * @param _this [IN] specifies a pointer to a IDPU object.
 * @param s [IN] specifies a pointer to a ISourceObservable object.
 * @param buffer [IN][OPTIONAL] specifies a pointer to a buffer used to allocate the circular buffer for the source attached.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
inline sys_error_code_t IDPU_AttachToSensor(IDPU *_this, ISourceObservable *s, void *buffer);

/**
 * Detach the ISourceObservable object to the IDPU object.
 *
 * @param _this [IN] specifies a pointer to a IDPU object.
 * @param s [IN] specifies a pointer to a ISourceObservable object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
inline sys_error_code_t IDPU_DetachFromSensor(IDPU *_this, ISourceObservable *s);

/**
 * Attach an IDPU object to the IDPU object.
 *
 * @param _this [IN] specifies a pointer to a IDPU object.
 * @param in_adpu [IN] specifies a pointer to a IDPU object that you want attach to DPU object.
 * @param buffer [IN][OPTIONAL] specifies a pointer to a buffer used to allocate the circular buffer for the dpu attached.
 *
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
inline sys_error_code_t IDPU_AttachInputDPU(IDPU *_this, IDPU *in_adpu, void *buffer);

/**
 * Detach the IDPU object attached to object.
 * Note: there is always only one IDPU attached at the same time.
 *
 * @param _this [IN] specifies a pointer to a IDPU object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
inline sys_error_code_t IDPU_DetachFromDPU(IDPU *_this);

/**
 * Dispatch a data ready event to all listeners and IDPU attached to the IDPU object.
 *
 * @param _this [IN] specifies a pointer to a IDPU object.
 * @param pxEvt [IN] specifies a pointer to the initializes ProcessEvent to dispatch.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
inline sys_error_code_t IDPU_DispatchEvents(IDPU *_this,  ProcessEvent *pxEvt);

/**
 * Register an user notify callback used to notify the application the IDPU is ready to process the data.
 * The application should be invoke the IDPU_Process function in order to perform processing.
 * Note: THis step is optional. If there is no one callback registered the IDPU performs the processing as soon as
 * the input data are available.
 *
 * @param _this [IN] it specifies a pointer to a IDPU object.
 * @param callback [IN] it specifies a pointer to the notify callback.
 * @param p_param [IN] it specifies an application generic parameter used in the callback.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
inline sys_error_code_t IDPU_RegisterNotifyCallback(IDPU *_this, DPU_ReadyToProcessCallback_t callback, void *p_param);

/**
 * Perform the IDPU specific processing. After the processing is completed an IDPU_DispatchEvents() is called in order
 * to notify the listeners about the complete processing.
 * Note: The IDPU_Process function is automatically called if the user doesn't register the callback otherwise the user must call
 * it to perform the processing.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * or NULL if out of memory error occurs.
 */
inline sys_error_code_t IDPU_Process(IDPU *_this);


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISENSOR_H_ */
