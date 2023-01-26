/**
 ******************************************************************************
 * @file    ISourceObservable_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 3.0.0
 * @date    Jun 8, 2021
 *
 * @brief   Definition of the stream data source generic interface.
 *
 * This file define the virtual table for the ::ISourceObservable Interface.
 *
 ******************************************************************************
 * @attention
 *
 * <h2><center>COPYRIGHT &copy; 2021 STMicroelectronics</center></h2>
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#ifndef INCLUDE_ISOURCEOBSERVER_VTBL_H_
#define INCLUDE_ISOURCEOBSERVER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/IEvent.h"


/**
 * Create a type name for ::ISourceObservable_vtbl.
 */
typedef struct _ISourceObservable_vtbl ISourceObservable_vtbl;

/**
 * Specifies the virtual table for the interface.
 */
struct _ISourceObservable_vtbl {

  uint8_t             (*GetId)(ISourceObservable *_this); /** @sa ISourceGetId() */
  IEventSrc*          (*GetEventSourceIF)(ISourceObservable *_this); /** @sa ISourceGetEventSrcIF() */
  sys_error_code_t    (*SourceGetODR)(ISourceObservable *_this, float *p_measured, float *p_nominal); /** @sa ISourceGetODR() */
  float               (*SourceGetFS)(ISourceObservable *_this); /** @sa ISourceGetFS() */
  float               (*SourceGetSensitivity)(ISourceObservable *_this); /** @sa ISourceGetSensitivity() */
};

/**
 * Internal state of the Source Observable IF.
 */
struct _ISourceObservable {
  /**
   * Pointer to the virtual table for the class.
   */
  const ISourceObservable_vtbl *vptr;
};


// Inline functions definition
// ***************************

/**
 * @sa ISourceGetId()
 */
static inline uint8_t ISourceGetId(ISourceObservable *_this) {
  return _this->    vptr->GetId(_this );
}

/**
 * @sa ISourceGetEventSrcIF()
 */
static inline IEventSrc * ISourceGetEventSrcIF(ISourceObservable *_this) {
  return _this->vptr->GetEventSourceIF(_this );
}

/**
 * @sa ISourceGetODR()
 */
static inline sys_error_code_t ISourceGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal) {
  return _this->vptr->SourceGetODR(_this, p_measured, p_nominal );
}

/**
 * @sa ISourceGetFS()
 */
static inline float ISourceGetFS(ISourceObservable *_this) {
  return _this->vptr->SourceGetFS(_this );
}

/**
 * @sa ISourceGetSensitivity()
 */
static inline float ISourceGetSensitivity(ISourceObservable *_this) {
  return _this->vptr->SourceGetSensitivity(_this );
}




#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISOURCEOBSERVER_VTBL_H_ */
