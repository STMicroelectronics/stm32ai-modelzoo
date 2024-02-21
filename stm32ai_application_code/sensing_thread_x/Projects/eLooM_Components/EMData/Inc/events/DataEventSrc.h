/**
 ******************************************************************************
 * @file    DataEventSrc.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    May 13, 2022
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
#ifndef EMDATA_INC_EVENTS_DATAEVENTSRC_H_
#define EMDATA_INC_EVENTS_DATAEVENTSRC_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "events/AEventSrc.h"
#include "events/AEventSrc_vtbl.h"
#include "services/sysmem.h"


/**
 * Create  type name for ::_DataEventSrc.
 */
typedef struct _DataEventSrc DataEventSrc_t;

/**
 * DataEventSrc internal state.
 */
struct _DataEventSrc {
  /**
   * Base class object.
   */
  AEventSrc super;
};

/* Public API declaration */
/**************************/

/**
 * Allocate an instance of DataEventSrc.
 *
 * @return a pointer to the generic object ::IEventSrc if success,
 * or NULL if out of memory error occurs.
 */
IEventSrc *DataEventSrcAlloc(void);

/**
 * Deallocate an instance of DataEventSrc.
 *
 * @param _this [IN] specifies an object of type DataEventSrc_t.
 */
static inline
void DataEventSrcFree(IEventSrc *_this);

/**
 * This is not a real allocator. Instead given the address of a variable of type DataEventSrc_t, it
 * initializes the virtual table. In this way the object can be statically allocated by the application.
 *
 * @param _this [IN] specifies an object of type DataEventSrc_t.
 * @return a pointer to the generic object ::IEventSrc if success,
 * or NULL if out of memory error occurs.
 */
IEventSrc *DataEventSrcAllocStatic(DataEventSrc_t *_this);


/* Inline functions definition */
/*******************************/

static inline
void DataEventSrcFree(IEventSrc *_this)
{
  /* kernel deallocator already check for a NULL pointer. */
  SysFree(_this);
}


#ifdef __cplusplus
}
#endif

#endif /* EMDATA_INC_EVENTS_DATAEVENTSRC_H_ */
