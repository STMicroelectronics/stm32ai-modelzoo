/**
  ******************************************************************************
  * @file    ADPU2.h
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

#ifndef INCLUDE_ADPU2_H_
#define INCLUDE_ADPU2_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "IDPU2.h"
#include "IDPU2_vtbl.h"
#include "events/IDataEventListener.h"
#include "events/IDataEventListener_vtbl.h"
#include "events/DataEventSrc.h"
#include "events/DataEventSrc_vtbl.h"
#include "services/CircularBuffer.h"
#include "IDataBuilder.h"
#include "IDataBuilder_vtbl.h"


/* ADPU ERROR CODE */
/*******************/

#define ADPU2_NO_ERROR_CODE                      0
#ifndef SYS_ADPU2_BASE_ERROR_CODE
#define SYS_ADPU2_BASE_ERROR_CODE                1  ///<< the base error code is used to remap ADPU error codes at application level in the file apperror.h
#endif
#define SYS_ADPU2_DATA_SRC_ALREADY_ATTACHED      SYS_ADPU2_BASE_ERROR_CODE + 1
#define SYS_ADPU2_ALREADY_ATTACHED               SYS_ADPU2_BASE_ERROR_CODE + 2
#define SYS_ADPU2_NOT_ATTACHED                   SYS_ADPU2_BASE_ERROR_CODE + 3
#define SYS_ADPU2_NOT_CHAINED                    SYS_ADPU2_BASE_ERROR_CODE + 4
#define SYS_ADPU2_NOT_IMPLEMENTED                SYS_ADPU2_BASE_ERROR_CODE + 5
#define SYS_ADPU2_NO_READY_ITEM_ERROR_CODE       SYS_ADPU2_BASE_ERROR_CODE + 6
#define SYS_ADPU2_PROC_ERROR_ERROR_CODE          SYS_ADPU2_BASE_ERROR_CODE + 7
#define SYS_ADPU2_PROC_DATA_NOT_READY_ERROR_CODE SYS_ADPU2_BASE_ERROR_CODE + 8
#define SYS_ADPU2_INIT_ERROR_ERROR_CODE          SYS_ADPU2_BASE_ERROR_CODE + 9


/**
 * Create  type name for struct _ADPU2.
 */
typedef struct _ADPU2 ADPU2_t;

/**
 * Describe the struct used to manage the CB
 */
typedef struct _CBHandle2
{
  /*
   * Circular buffer used to manage multiple data. The DPU has only one Circular buffer. The application must allocate the buffer
   * using the ADPU2_SetDataBuffer() function.
   */
  CircularBuffer *p_cb;

  /**
   * Specifies the ::CBItem used to produce an new input data.
   */
  CBItem *p_producer_data_buff;
}CBHandle2_t;

/**
 * This struct model the relation between ::ADPU2_t and an attached ISourceObservable.
 */
typedef struct _AttachedSourceObservedItem
{
  /**
   * Data source attached to the DPU.
   */
  ISourceObservable *p_data_source;

  /**
   * Data builder used to build the data coming this data source.
   */
  IDataBuilder_t *p_builder;

  /**
   * Build strategy... TODO:// STF - to specify better.
   */
  IDB_BuildStrategy_e build_strategy;

  /**
   * Points to the next data source. It is used to manage all data source attached to the DPU as a linked list.
   */
  struct _AttachedSourceObservedItem *p_next;
} AttachedSourceObservedItem_t;

/**
 * This struct model the relation between ::ADPU2_t and the next attached ::ADPU_t.
 */
typedef struct _AttachedDPU
{
  /**
   * Data builder used to build the data ...
   */
  IDataBuilder_t *p_builder;

  /**
   * Build strategy... TODO:// STF - to specify better.
   */
  IDB_BuildStrategy_e build_strategy;

  /**
   * Points to the next attached DPU.
   */
  ADPU2_t *p_next;
} AttachedDPU;


/**
 * ADPU2_t internal state.
 */
struct _ADPU2 {

  /**
   * Base interface.
   */
  IDPU2_t super;

  /**
   * Interface to listen the DataEvent_t from the attached
   */
  IDataEventListener_t data_evt_listener_if;
  void *p_owner;

  /**
   * Interface to dispatch ::DataEvent_t events.
   */
  DataEventSrc_t data_evt_src_if;

  /**
   * Head to the ::ISourceObservable list attached to the DPU.
   */
  AttachedSourceObservedItem_t attached_data_src_list;

  /**
   * Handle of the chained DPU. It specifies the next DPU in the processing chain.
   */
  AttachedDPU next_dpu;

  /**
   * Callback to notify data are ready to be processed.
   */
  DPU2_ReadyToProcessCallback_t notify_data_ready_f;

  /**
   * Specifies the parameter passed to the callback when new data are ready to be processed.
   */
  void *p_data_ready_callback_param;

  /**
   * Describes the input data format required by the DPU.
   */
  EMData_t in_data;

  /**
   * Describes the output data format produced by the DPU.
   */
  EMData_t out_data;

  /**
   * Handle of the ::CircularBuffer used by the DPU to store the input data.
   */
  CBHandle2_t cbh;

  /**
   * Specifies an application specific tag that can be set with the method ADPU2_SetTag()
   * and read the method ADPU2_GetTag().
   */
  uint32_t tag;

  /**
   * Specifies the number of remaining data builder (::IDataBuilder_t) objects to complete the data.
   */
  uint16_t data_builder_to_complete;

  /**
   * Specifies if the DPU is active. When the DPU is active:
   * - it handles the input data
   * - it process the data when ready
   * - it dispatch data event.
   *
   * When the DPU is not active all input data are skipped.
   */
  bool active;

  /**
   * Specifies if this DPU is attached to another DPU as next one.
   */
  bool is_chained_as_next;
};


/* Public API declaration */
/**************************/

/**
 * Initialize the DPU.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param in_data [IN] specifies the input data format required by the DPU.
 * @param out_data [IN] specifies the output data format produced by the DPU.
 * @return SYS_NO_ERROR_CODE if success, an application error code otherwise.
 */
sys_error_code_t ADPU2_Init(ADPU2_t *_this, EMData_t in_data, EMData_t out_data);

/**
 * Get the event listener interface of the DPU. It actual type is ::IDataEventListener_t.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return a pointer to the event listener interface of the DPU.
 */
IEventListener *ADPU2_GetEventListenerIF(ADPU2_t *_this);

/**
 * Get the event source interface of the DPU. It actual type is ::IDataEventSource_t.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return a pointer to the event source interface of the DPU.
 */
IEventSrc *ADPU2_GetEventSrcIF(ADPU2_t * _this);

/**
 * Set the tag value to ADPU2 object
 * Note: This function is optional but useful to distinguish a specific ADPU2 among several ADPU2s
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param tag [IN] specifies a tag value to be set.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t ADPU2_SetTag(ADPU2_t *_this, uint32_t tag) ;

/**
  * Get the tag value to the ADPU2 object
  *
  * @param _this [IN] specifies a pointer to the object.
  * @return the tag value set with ADPU2_SetTag().
  */
uint32_t ADPU2_GetTag(ADPU2_t *_this) ;


/**
  * Reset the ADPU2 object. All circular buffers are reinitialized, as well as the ADPU2 resources.
  *
  * @param _this [IN] specifies a pointer to the object.
  * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
  */
sys_error_code_t ADPU2_Reset(ADPU2_t *_this);

/**
 * Suspend the DPU. When the DPU is suspended all the incoming data produced by the attached data source are skipped.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE
 */
sys_error_code_t ADPU2_Suspend(ADPU2_t *_this);

/**
 * Resume the normal DPU processing flow. When the DPU is resumed it process the input data to produce the output data
 * and notify the listener and the attached DPU.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE
 */
sys_error_code_t ADPU2_Resume(ADPU2_t *_this);

/**
 * Set the memory buffer used by the DPU to manage the input data. It must be big enough to store
 * the payload of one or more input data. To know the size in byte of the payload of one input data, it is
 * possible to use the method ADPU2_GetInDataPayloadSize(). If the DPU has already an input buffer,
 * then it is released and replaced with the new one.
 *
 * If `buffer_size` is equal to zero then the DPU releases the buffer resources.
 *
 * If the DPU has no input data buffer then its behavior, when it receive new data, is not defined.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param p_buffer [IN] specifies a buffer .
 * @param buffer_size [IN] specifies the size in byte of the buffer.
 * @return SYS_NO_ERROR_CODE if success, SYS_OUT_OF_MEMORY_ERROR_CODE otherwise.
 */
sys_error_code_t ADPU2_SetInDataBuffer(ADPU2_t *_this, uint8_t *p_buffer, uint32_t buffer_size);

/**
 * Set the memory buffer used by the DPU to manage the output data. It must be big enough to store
 * the payload of one output data. To know the size in byte of the payload of one output data, it is
 * possible to use the method ADPU2_GetOutDataPayloadSize().
 *
 * If `buffer_size` is equal to zero then the DPU releases the buffer resources.
 *
 * If the DPU has no output data buffer then its behavior, when it process input data, is not defined.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param p_buffer [IN] specifies a buffer .
 * @param buffer_size [IN] specifies the size in byte of the buffer.
 * @return SYS_NO_ERROR_CODE if success, SYS_INVALID_PARAMETER_ERROR_CODE otherwise.
 */
sys_error_code_t ADPU2_SetOutDataBuffer(ADPU2_t *_this, uint8_t *p_buffer, uint32_t buffer_size);

/**
 * Process an input data when it is ready, and dispatch the processed data: first all listeners are notified about the new data,
 * then the new data is sent to the next DPU of the chain for further processing.
 *
 * This method is called automatically by the DPU if it has not notify callback registered, otherwise it is
 * responsibility of the application to call this method start the processing of the input data.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE if success,
 *         SYS_ADPU2_NO_READY_ITEM_ERROR_CODE if there are no input data ready to be processed,
 *         others error code otherwise.
 */
sys_error_code_t ADPU2_ProcessAndDispatch(ADPU2_t *_this);

/**
 * Get information about the input data format of the DPU.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return an ::EMData_t object for the input data of the DPU.
 */
static inline EMData_t ADPU2_GetInDataInfo(ADPU2_t *_this);

/**
 * Get information about the output data format of the DPU.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return an ::EMData_t object for the output data of the DPU.
 */
static inline EMData_t ADPU2_GetOutDataInfo(ADPU2_t *_this);

/**
 * Get the size in byte of the payload of the input data of the DPU.
 * It is equivalent to EMD_GetPayloadSize(ADPU2_GetInDataInfo(p_dpu)).
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return size in byte of the payload of the input data of the DPU.
 */
static inline size_t ADPU2_GetInDataPayloadSize(ADPU2_t *_this);

/**
 * Get the size in byte of the payload of the output data of the DPU.
 * It is equivalent to EMD_GetPayloadSize(ADPU2_GetOutDataInfo(p_dpu)).
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return size in byte of the payload of the output data of the DPU.
 */
static inline size_t ADPU2_GetOutDataPayloadSize(ADPU2_t *_this);

/**
 * Check if the DPU is attached to at least one data source.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return `true` if the DPU is attached to at least one data source, `false` otherwise.
 */
static inline bool ADPU2_IsAttachedToDataSource(ADPU2_t *_this);

/**
 * Check if the DPU is chained to another DPU.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return `true` if the DPU belongs to a DPU chain, `false` otherwise.
 */
static inline bool ADPU2_IsAttachedToDPU(ADPU2_t *_this);

/**
 * Get a pointer to the next DPU if _this DPU belong to a DPU chain.
 * @param _this [IN] specifies a pointer to the object.
 * @return a pointer to the next DPU if _this DPU belong to a DPU chain,
 *         NULL if it is the last DPU in the chain or if it doesn't belong to a DPU chain.
 */
static inline ADPU2_t *ADPU2_GetNextDPU(ADPU2_t *_this);


/* Inline function definition */
/*****************************/

static inline
EMData_t ADPU2_GetInDataInfo(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  EMData_t tmp_data = _this->in_data;
  tmp_data.p_payload = NULL;

  return tmp_data;
}

static inline
EMData_t ADPU2_GetOutDataInfo(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  EMData_t tmp_data = _this->out_data;
  tmp_data.p_payload = NULL;

  return tmp_data;
}

static inline
size_t ADPU2_GetInDataPayloadSize(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  return EMD_GetPayloadSize(&_this->in_data);
}

static inline
size_t ADPU2_GetOutDataPayloadSize(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  return EMD_GetPayloadSize(&_this->out_data);
}

static inline bool ADPU2_IsAttachedToDataSource(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  return (_this->attached_data_src_list.p_next != NULL);
}

static inline bool ADPU2_IsAttachedToDPU(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  return (_this->next_dpu.p_next != NULL) || (_this->is_chained_as_next);
}

static inline ADPU2_t *ADPU2_GetNextDPU(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  return _this->next_dpu.p_next;
}

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ADPU2_H_ */
