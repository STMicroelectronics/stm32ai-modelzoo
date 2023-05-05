/**
  ******************************************************************************
  * @file    ADPU.c
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

#include "ADPU2.h"
#include "ADPU2_vtbl.h"
#include "services/sysmem.h"
#include "services/syscs.h"
#include "services/SysTimestamp.h"
#include <string.h>

#include "services/sysdebug.h"


#define SYS_DEBUGF(level, message)                   SYS_DEBUGF3(SYS_DBG_DPU, level, message)


/**
 * Class object declaration.
 */
typedef struct _ADPU2Class {
  /**
   * ADPU2_t class virtual table.
   */
  IDPU2_vtbl vtbl;

  /**
   * IDataEventListener_t virtual table.
   */
  IDataEventListener_vtbl if_data_evt_listener_vtbl;
} ADPU2Class_t;


/* Objects instance */
/********************/

/**
 * The class object.
 */
static const ADPU2Class_t sTheClass = {
    /* class virtual table */
    {
        ADPU2_vtblAttachToDataSource,
        ADPU2_vtblDetachFromDataSource,
        ADPU2_vtblAttachToDPU,
        ADPU2_vtblDetachFromDPU,
        ADPU2_vtblDispatchEvents,
        ADPU2_vtblRegisterNotifyCallback,
        NULL
    },

    /*IDataEventListener virtual table*/
    {
        ADPU2_vtblOnStatusChange,
        ADPU2_vtblSetOwner,
        ADPU2_vtblGetOwner,
        ADPU2_vtblOnNewDataReady
    }
};


/* Private functions declaration */
/*********************************/

/**
 * Initialize an empty attached data source observed item.
 *
 * @param _this [IN] specifies a pointer to an object.
 * @return SYS_NO_ERROR_CODE.
 */
static sys_error_code_t ASOItemInit(AttachedSourceObservedItem_t *_this);

/**
 * Find a specific data source (::ISourceObservable) in a AOS List.
 *
 * @param p_list_head [IN] specifies the head of the list where to search.
 * @param p_data_src [IN] specified the data source to search for.
 * @return a pointer to the list item if the data source has been found, NULL if the data source is not in the list.
 */
static AttachedSourceObservedItem_t *ASOListFindItem(AttachedSourceObservedItem_t *p_list_head, ISourceObservable *p_data_src);

/**
 * Find a specific data source (::ISourceObservable) in a AOS List.
 *
 * @param p_list_head [IN] specifies the head of the list where to search.
 * @param data_src_id [IN] specified the ID of the data source to search for.
 * @return a pointer to the list item if the data source has been found, NULL if the data source is not in the list.
 */
static AttachedSourceObservedItem_t *ASOListFindItemBySrcID(AttachedSourceObservedItem_t *p_list_head, uint16_t data_src_id);

/**
 * Find a specific data source (::ISourceObservable) in a AOS List.
 *
 * @param p_list_head [IN] specifies the head of the list where to search.
 * @param p_data_builder [IN] specified the data builder to search for.
 * @return a pointer to the list item if the data source has been found, NULL if the data source is not in the list.
 */
static AttachedSourceObservedItem_t *ASOListFindItemByDataBuilder(AttachedSourceObservedItem_t *p_list_head, IDataBuilder_t *p_data_builder);

/**
 * Add an item in the head of the Attached Source Observable list. The function doesn't check if
 * the embedded ::ISourceObservable is already in the list.
 *
 * @param p_list_head [IN] specifies the head of the list.
 * @param p_item [IN] specifies the item to add into the list.
 */
static inline void ASOListAddItem(AttachedSourceObservedItem_t *p_list_head, AttachedSourceObservedItem_t *p_item);

/**
 * Remove an item from the attached source observable list.
 *
 * @param p_list_head [IN] specifies the head of the list.
 * @param p_item [IN] specifies the item to add into the list.
 */
static inline void ASOListRemoveItem(AttachedSourceObservedItem_t *p_list_head, AttachedSourceObservedItem_t *p_item);

/**
 * Extract, from the ::CircularBuffer_t, a new buffer used to build a new input data for the DPU, and reset all the
 * ::DataBuilder_t IF linked to the data sources of the DPU.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param p_no_reset_item [IN] specifies an item that is not reset. It can be NULL.
 * @return SYS_NO_ERROR_CODE if success, an application specific error code otherwise.
 */
static sys_error_code_t ADPU2_PrepareToBuildNewData(ADPU2_t *_this, AttachedSourceObservedItem_t *p_no_reset_item);

/**
 * Callback called by a ::IDataBuilder_t object when a new data is ready.
 *
 * @param _this [IN] specifies a data builder object.
 * @param p_data_build_context [IN] specifies a data build context.
 */
static uint8_t *ADPU2_DataBuffAlloc(IDataBuilder_t *_this, void *p_data_build_context);

/**
 * This function implements the DPU chain. It is used to dispatch a process data to the next DPU.
 *
 * @param _this [IN] specifies a pointer to the object. It is the DPU that receives the data to be processed.
 * @param p_evt [IN] specifies a pointer to a data event.
 * @param p_src_dpu [IN] specifies the DPU that has generated the data.
 * @return SYS_NO_ERROR_CODE if success, an application specific error code otherwise.
 */
static sys_error_code_t ADPU2_OnNewInputDataFromDPU(ADPU2_t *_this,  DataEvent_t *p_evt, ADPU2_t *p_src_dpu);


/* IDPU2 virtual functions definition */
/**************************************/

sys_error_code_t ADPU2_vtblAttachToDataSource(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy)
{
  assert_param(_this != NULL);
  assert_param(p_data_source != NULL);
  assert_param(p_builder != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  ADPU2_t *p_obj = (ADPU2_t*)_this;

  if (p_obj->is_chained_as_next)
  {
    /* a DPU can have n data sources or one DPU attached as input data source, but not to both.*/
    res = SYS_INVALID_FUNC_CALL_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_FUNC_CALL_ERROR_CODE);

    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("ADPU2: error DPU chained, in AttachToDataSource!\r\n"));
  }

  if (!SYS_IS_ERROR_CODE(res))
  {
    AttachedSourceObservedItem_t *p_list_item = ASOListFindItem(&p_obj->attached_data_src_list, p_data_source);
    if (p_list_item != NULL)
    {
      /* DPU is already attached to this data source*/
      res = SYS_ADPU2_DATA_SRC_ALREADY_ATTACHED;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_ADPU2_DATA_SRC_ALREADY_ATTACHED);
    }
    else
    {
      p_list_item = SysAlloc(sizeof(AttachedSourceObservedItem_t));
      if (p_list_item != NULL)
      {
        p_list_item->p_data_source = p_data_source;
        p_list_item->build_strategy = build_strategy;
        p_list_item->p_builder = p_builder;
        ASOListAddItem(&p_obj->attached_data_src_list, p_list_item);
      }
      else
      {
        res = SYS_OUT_OF_MEMORY_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
      }
    }
  }

  if (!SYS_IS_ERROR_CODE(res))
  {
    /* register the DPU as a listener of the data source.*/
    IEventSrc *p_event_src = ISourceGetEventSrcIF(p_data_source);
    res = IEventSrcAddEventListener(p_event_src, ADPU2_GetEventListenerIF(p_obj));
    if (SYS_IS_ERROR_CODE(res))
    {
      sys_error_handler();
    }
  }

  return res;
}

sys_error_code_t ADPU2_vtblDetachFromDataSource(IDPU2_t *_this, ISourceObservable *p_data_source, IDataBuilder_t **p_data_builder)
{
  assert_param(_this != NULL);
  assert_param(p_data_source != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  ADPU2_t *p_obj = (ADPU2_t*)_this;

  /*check if the data source is attached to this DPU*/
  AttachedSourceObservedItem_t *p_item = ASOListFindItem(&p_obj->attached_data_src_list, p_data_source);
  if (p_item != NULL)
  {
    /* remove the item from the list.*/
    ASOListRemoveItem(&p_obj->attached_data_src_list, p_item);

    /* remove the DPU as listener from the data source.*/
    IEventSrc *p_evenr_src = ISourceGetEventSrcIF(p_data_source);
    res = IEventSrcRemoveEventListener(p_evenr_src, ADPU2_GetEventListenerIF(p_obj));
    if(SYS_IS_ERROR_CODE(res))
    {
      sys_error_handler();
    }

    if (p_data_builder != NULL)
    {
      *p_data_builder = p_item->p_builder;
    }

    /*release the memory of the item*/
    SysFree(p_item);
  }
  else
  {
    if (p_data_builder != NULL){
      *p_data_builder = NULL;
    }
  }

  return res;
}

sys_error_code_t ADPU2_vtblAttachToDPU(IDPU2_t *_this, IDPU2_t *p_next_dpu, IDataBuilder_t *p_builder, IDB_BuildStrategy_e build_strategy)
{
  assert_param(_this != NULL);
  assert_param(p_next_dpu != NULL);
  assert_param(p_builder != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  ADPU2_t *p_obj = (ADPU2_t*)_this;

  if (ADPU2_IsAttachedToDPU(p_obj) || ADPU2_IsAttachedToDPU((ADPU2_t*)p_next_dpu))
  {
    res = SYS_ADPU2_ALREADY_ATTACHED;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_ADPU2_ALREADY_ATTACHED);

    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("ADPU2: error DPU attached, in AttachToDPU!\r\n"));
  }
  else
  {
    p_obj->next_dpu.p_next = (ADPU2_t*)p_next_dpu;
    p_obj->next_dpu.build_strategy = build_strategy;
    p_obj->next_dpu.p_builder = p_builder;
    p_obj->next_dpu.p_next->is_chained_as_next = true;
  }

  return res;
}

sys_error_code_t ADPU2_vtblDetachFromDPU(IDPU2_t *_this, IDataBuilder_t **p_data_builder)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  ADPU2_t *p_obj = (ADPU2_t*)_this;

  if (p_obj->next_dpu.p_next != NULL)
  {
    p_obj->next_dpu.p_next->is_chained_as_next = false;
    p_obj->next_dpu.p_next = NULL;
    if (p_data_builder != NULL)
    {
      *p_data_builder = p_obj->next_dpu.p_builder;
    }
    p_obj->next_dpu.p_builder = NULL;
  }
  else
  {
    *p_data_builder = NULL;
    res = SYS_ADPU2_NOT_CHAINED;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_ADPU2_NOT_CHAINED);
  }

  return res;
}

sys_error_code_t ADPU2_vtblDispatchEvents(IDPU2_t *_this,  DataEvent_t *p_evt)
{
  assert_param(_this != NULL);
  assert_param(p_evt != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  ADPU2_t *p_obj = (ADPU2_t*)_this;

  /* first notify the listeners.*/
  res = IEventSrcSendEvent((IEventSrc *)&p_obj->data_evt_src_if, (IEvent *) p_evt, NULL);
  if(SYS_IS_ERROR_CODE(res))
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);

    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("ADPU2: error during evt dispatching!\r\n"));
  }
  else
  {
    /* then propagate the data into DPU2 chain*/
    if(p_obj->next_dpu.p_next != NULL)
    {
      res = ADPU2_OnNewInputDataFromDPU(p_obj->next_dpu.p_next, p_evt, p_obj);

      if (res == SYS_IDB_DATA_READY_ERROR_CODE)
      {
        res = SYS_NO_ERROR_CODE;
      }
    }

    if(SYS_IS_ERROR_CODE(res))
    {
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);

      SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("ADPU2: error during DPU chaining!\r\n"));
    }
  }

  return res;
}

sys_error_code_t ADPU2_vtblRegisterNotifyCallback(IDPU2_t *_this, DPU2_ReadyToProcessCallback_t callback, void *p_param)
{
  assert_param(_this != NULL);
  assert_param(callback != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  ADPU2_t *p_obj = (ADPU2_t*)_this;

  p_obj->notify_data_ready_f = callback;
  p_obj->p_data_ready_callback_param = p_param;

  return xRes;
}


/* IListener virtual functions definition */
/******************************************/

sys_error_code_t ADPU2_vtblOnStatusChange(IListener *_this)
{
  assert_param(_this != NULL);

  SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("DPU: warning - IListener::OnStatusChange not implemented.\r\n"));

  return SYS_INVALID_FUNC_CALL_ERROR_CODE;
}


/* IEventListener virtual functions definition */
/***********************************************/

void ADPU2_vtblSetOwner(IEventListener *_this, void *p_owner)
{
  assert_param(_this != NULL);
  assert_param(p_owner != NULL);
  ADPU2_t* p_obj = (ADPU2_t*) ((uint32_t) _this - offsetof (ADPU2_t , data_evt_listener_if));

  p_obj->p_owner = p_owner;
}

void *ADPU2_vtblGetOwner(IEventListener *_this)
{
  assert_param(_this != NULL);
  ADPU2_t* p_obj = (ADPU2_t*) ((uint32_t) _this - offsetof (ADPU2_t , data_evt_listener_if));

  return p_obj->p_owner;
}


/* IDataEventListener_t virtual functions */
/******************************************/

sys_error_code_t ADPU2_vtblOnNewDataReady(IEventListener *_this, const DataEvent_t *p_evt)
{
  assert_param(_this != NULL);
  assert_param(p_evt != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  ADPU2_t* p_obj = (ADPU2_t*) ((uint32_t) _this - offsetof (ADPU2_t , data_evt_listener_if));
  SYS_DECLARE_CS(cs);

  if (p_obj->active)
  {
    /* search for the data source.*/
    AttachedSourceObservedItem_t *p_aso_item = ASOListFindItemBySrcID(&p_obj->attached_data_src_list, p_evt->tag);

    /* Check if we are start building a new data.*/
    SYS_ENTER_CRITICAL(cs);
    if (p_obj->cbh.p_producer_data_buff == NULL)
    {
      SYS_EXIT_CRITICAL(cs);
      /* we start to build a new data.*/
      res = ADPU2_PrepareToBuildNewData(p_obj, NULL);
      if (SYS_IS_ERROR_CODE(res))
      {
        /* no free cb item or there is a data source without a data builder. Check the build strategy...*/
        if (p_aso_item->build_strategy != E_IDB_SKIP_DATA)
        {
          /* unable to build the IN data.*/
          sys_error_handler();
        }
        else
        {
          /* build_strategy == E_IDB_SKIP_DATA */
          return SYS_NO_ERROR_CODE;
        }
      }
    }
    else
    {
      SYS_EXIT_CRITICAL(cs);
    }

    res = IDataBuilder_OnNewInData(p_aso_item->p_builder, &p_obj->in_data, p_evt->p_data, p_aso_item->build_strategy, ADPU2_DataBuffAlloc);

    if (res == SYS_IDB_DATA_READY_ERROR_CODE)
    {
      if (!--p_obj->data_builder_to_complete)
      {
        /*a new data is ready*/
        CB_SetItemReady(p_obj->cbh.p_cb, p_obj->cbh.p_producer_data_buff);
        SYS_ENTER_CRITICAL(cs);
        p_obj->cbh.p_producer_data_buff = NULL;
        SYS_EXIT_CRITICAL(cs);
        if(p_obj->notify_data_ready_f)
        {
          /* I do not process inline the new data, but I notify the app.
           * It will be responsibility of the app to call ADPU2_ProcessAndDispatch or manually
           * do the Process&Dispatch */
          p_obj->notify_data_ready_f((IDPU2_t*)p_obj, p_obj->p_data_ready_callback_param);
        }
        else
        {
          res = ADPU2_ProcessAndDispatch(p_obj);
        }

        SYS_DEBUGF(SYS_DBG_LEVEL_ALL, ("ADPU2: new data ready\r\n"));
      }
    }
  }

  return res;
}


/* Public functions definition */
/*******************************/

sys_error_code_t ADPU2_Init(ADPU2_t *_this, EMData_t in_data, EMData_t out_data)
{
  assert_param(_this);
  ADPU2_t *p_obj = (ADPU2_t*)_this;
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /* The DPU vtbl has been initialized during the allocation of the derived DPU,
   * so we have to initialize only the listener IF
   */
  p_obj->data_evt_listener_if.vptr = &sTheClass.if_data_evt_listener_vtbl;
  IEventListenerSetOwner((IEventListener*)&p_obj->data_evt_listener_if, p_obj);

  /* Initialize the data event source IF*/
  (void)DataEventSrcAllocStatic(&p_obj->data_evt_src_if);
  (void)IEventSrcInit((IEventSrc*)&p_obj->data_evt_src_if);

  /* Initialize the list of attached data source*/
  (void)ASOItemInit(&p_obj->attached_data_src_list);

  p_obj->active = true;
  p_obj->notify_data_ready_f = NULL;
  p_obj->p_data_ready_callback_param = NULL;
  p_obj->tag = 0U;
  p_obj->data_builder_to_complete = 0;
  p_obj->in_data = in_data;
  p_obj->out_data = out_data;
  p_obj->cbh.p_cb = NULL;
  p_obj->cbh.p_producer_data_buff = NULL;
  p_obj->next_dpu.p_next = NULL;
  p_obj->next_dpu.p_builder = NULL;
  p_obj->is_chained_as_next = false;

  return res;
}

IEventListener *ADPU2_GetEventListenerIF(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  return (IEventListener*) &_this->data_evt_listener_if;
}

IEventSrc *ADPU2_GetEventSrcIF(ADPU2_t * _this)
{
  assert_param(_this != NULL);

  return (IEventSrc*) &_this->data_evt_src_if;
}

sys_error_code_t ADPU2_SetTag(ADPU2_t *_this, uint32_t tag)
{
  assert_param(_this != NULL);

  _this->tag = tag;

  return SYS_NO_ERROR_CODE;
}

uint32_t ADPU2_GetTag(ADPU2_t *_this)
{
  assert_param(_this != NULL);

  return _this->tag;
}

sys_error_code_t ADPU2_Reset(ADPU2_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /*check if the DPU has already a cb.*/
  if (_this->cbh.p_cb != NULL)
  {
    /* reset the Circular Buffer handler.*/
    (void)CB_Init(_this->cbh.p_cb, CB_GetItemsBuffer(_this->cbh.p_cb), CB_GetItemSize(_this->cbh.p_cb));
    _this->cbh.p_producer_data_buff = NULL;
    /*the above code line will trigger a data builders reset when the DPU receives new data,*/
    /*so we do not need to reset the data builder here explicitly.*/
  }

  /*check if the DPU has another DPU chained as next.*/
  if (_this->next_dpu.p_next != NULL)
  {
    /*reset the next DPU handler.*/
    (void)IDataBuilder_Reset(_this->next_dpu.p_builder, _this);

    //TODO: STF - shall I reset all the DPU in the chain ?
//    ADPU2_Reset(_this->next_dpu.p_next);
  }

  return res;
}

sys_error_code_t ADPU2_Resume(ADPU2_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  _this->active = true;

  return res;
}

sys_error_code_t ADPU2_Suspend(ADPU2_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  _this->active = false;

  return res;
}

sys_error_code_t ADPU2_SetInDataBuffer(ADPU2_t *_this, uint8_t *p_buffer, uint32_t buffer_size)
{
  assert_param(_this != NULL);
  assert_param((p_buffer != NULL) || (buffer_size == 0));
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /*check if the DPU has already a cb.*/
  if (_this->cbh.p_cb != NULL)
  {
    /*release the cb*/
    CB_Free(_this->cbh.p_cb);
    _this->cbh.p_cb = NULL;
    _this->cbh.p_producer_data_buff = NULL;
  }

  if (buffer_size > 0)
  {
    size_t payload_size = EMD_GetPayloadSize(&_this->in_data);
    uint16_t cb_items = buffer_size / payload_size;
    _this->cbh.p_cb = CB_Alloc(cb_items);
    if (_this->cbh.p_cb != NULL)
    {
      (void)CB_Init(_this->cbh.p_cb, p_buffer, payload_size);
    }
    else
    {
      res = SYS_OUT_OF_MEMORY_ERROR_CODE;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(res);
    }
  }

  return res;
}

sys_error_code_t ADPU2_SetOutDataBuffer(ADPU2_t *_this, uint8_t *p_buffer, uint32_t buffer_size)
{
  assert_param(_this != NULL);
  assert_param(p_buffer != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  _this->out_data.p_payload = NULL;

  if (buffer_size > 0)
  {
    size_t payload_size = EMD_GetPayloadSize(&_this->out_data);
    if (payload_size > buffer_size)
    {
      res = SYS_INVALID_PARAMETER_ERROR_CODE;
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);

      SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("ADPU2: error - out buffer size too small!\r\n"));
    }
    else
    {
      _this->out_data.p_payload = p_buffer;
    }
  }

  return res;
}


sys_error_code_t ADPU2_ProcessAndDispatch(ADPU2_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  CBItem *p_ready_item;
  CB_GetReadyItemFromTail(_this->cbh.p_cb, &p_ready_item);
  if (p_ready_item == NULL)
  {
    res = SYS_ADPU2_NO_READY_ITEM_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_ADPU2_NO_READY_ITEM_ERROR_CODE);
    return res;
  }

  EMData_t in_data = _this->in_data;
  in_data.p_payload = CB_GetItemData(p_ready_item);
  res = IDPU2_Process((IDPU2_t*)_this, in_data, _this->out_data);
  CB_ReleaseItem(_this->cbh.p_cb, p_ready_item);
  double timestamp = SysTsGetTimestampF(SysGetTimestampSrv());
  if (!SYS_IS_ERROR_CODE(res))
  {
    DataEvent_t data_evt;
    DataEventInit((IEvent*)&data_evt, (IEventSrc*)&_this->data_evt_src_if, &_this->out_data, timestamp, _this->tag);
    res = IDPU2_DispatchEvents((IDPU2_t*)_this, &data_evt);
  }

  return res;
}


/* Private functions definition */
/********************************/

static sys_error_code_t ASOItemInit(AttachedSourceObservedItem_t *_this)
{
  assert_param(_this != NULL);

  _this->p_data_source = NULL;
  _this->p_next = NULL;
  _this->p_builder = NULL;

  return SYS_NO_ERROR_CODE;
}

static AttachedSourceObservedItem_t *ASOListFindItem(AttachedSourceObservedItem_t *p_list_head, ISourceObservable *p_data_src)
{
  assert_param(p_data_src != NULL);

  return ASOListFindItemBySrcID(p_list_head, ISourceGetId(p_data_src));
}

static AttachedSourceObservedItem_t *ASOListFindItemByDataBuilder(AttachedSourceObservedItem_t *p_list_head, IDataBuilder_t *p_data_builder)
{
  assert_param(p_data_builder != NULL);

  AttachedSourceObservedItem_t *p_tmp = p_list_head->p_next;
  bool found = false;
  while (!found && (p_tmp != NULL))
  {
    if (p_tmp->p_builder == p_data_builder)
    {
      /* data source is already in the list of attached data source.*/
      found = true;
    }
    else
    {
      /*move to the next list item.*/
      p_tmp = p_tmp->p_next;
    }
  }

  return p_tmp;
}

static AttachedSourceObservedItem_t *ASOListFindItemBySrcID(AttachedSourceObservedItem_t *p_list_head, uint16_t data_src_id)
{
  assert_param(p_list_head != NULL);

  AttachedSourceObservedItem_t *p_tmp = p_list_head->p_next;
  bool found = false;
  while (!found && (p_tmp != NULL))
  {
    if (ISourceGetId(p_tmp->p_data_source) == data_src_id)
    {
      /* data source is already in the list of attached data source.*/
      found = true;
    }
    else
    {
      /*move to the next list item.*/
      p_tmp = p_tmp->p_next;
    }
  }

  return p_tmp;
}

static inline
void ASOListAddItem(AttachedSourceObservedItem_t *p_list_head, AttachedSourceObservedItem_t *p_item)
{
  assert_param(p_list_head != NULL);

  if(p_item != NULL)
  {
    p_item->p_next = p_list_head->p_next;
    p_list_head->p_next = p_item;
  }
}

static inline
void ASOListRemoveItem(AttachedSourceObservedItem_t *p_list_head, AttachedSourceObservedItem_t *p_item)
{
  assert_param(p_list_head != NULL);

  if (p_item != NULL)
  {
    /*find the item in the list*/
    AttachedSourceObservedItem_t *p_tmp = p_list_head;
    while ((p_tmp != NULL) && (p_tmp->p_next != p_item))
    {
      p_tmp = p_tmp->p_next;
    }

    /*if the item is in the list then remove it*/
    if (p_tmp != NULL)
    {
      AttachedSourceObservedItem_t *p_removed_item = p_tmp->p_next;
      p_tmp->p_next = p_removed_item->p_next;
      /*eventually disconnect the removed item from the list.*/
      p_removed_item->p_next = NULL;
    }
  }
}

static sys_error_code_t ADPU2_PrepareToBuildNewData(ADPU2_t *_this, AttachedSourceObservedItem_t *p_no_reset_item)
{
  assert_param(_this != NULL);
  assert_param(_this->cbh.p_cb != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  _this->data_builder_to_complete = (p_no_reset_item == NULL ? 0U : 1U);

  /*get a new empty buffer from the circular buffer.*/
  res = (sys_error_code_t)CB_GetFreeItemFromHead(_this->cbh.p_cb, &_this->cbh.p_producer_data_buff);
  if (!SYS_IS_ERROR_CODE(res))
  {
    _this->in_data.p_payload = (uint8_t*)CB_GetItemData(_this->cbh.p_producer_data_buff);

    /* reset the data builder interface*/
    AttachedSourceObservedItem_t *p_tmp = _this->attached_data_src_list.p_next;

    while(p_tmp != NULL)
    {
      if (p_tmp->p_builder == NULL)
      {
        /* all source must have a data builder! */
        sys_error_handler();
      }
      if (p_tmp != p_no_reset_item)
      {
        (void)IDataBuilder_Reset(p_tmp->p_builder, _this);
        _this->data_builder_to_complete++;
      }
      p_tmp = p_tmp->p_next;
    }
  }

  return res;
}

static uint8_t *ADPU2_DataBuffAlloc(IDataBuilder_t *_this, void *p_data_build_context)
{
  assert_param(_this != NULL);
  assert_param(p_data_build_context != NULL);
  ADPU2_t *p_obj = (ADPU2_t*)p_data_build_context;
  uint8_t *p_buff = NULL;
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SYS_DECLARE_CS(cs);

  /*a data builder needs a new buffer because it has completed its part of the data.*/

  if (p_obj->data_builder_to_complete == 1U)
  {
    /* it is the last data builder so I can mark the data ready and allocate a new buffer.*/
    SYS_DEBUGF(SYS_DBG_LEVEL_ALL, ("ADPU2: new data ready _\r\n"));

    CB_SetItemReady(p_obj->cbh.p_cb, p_obj->cbh.p_producer_data_buff);
    SYS_ENTER_CRITICAL(cs);
    p_obj->cbh.p_producer_data_buff = NULL;
    SYS_EXIT_CRITICAL(cs);
    /* find the attached source observer list item*/
    AttachedSourceObservedItem_t *p_aso_item = ASOListFindItemByDataBuilder(&p_obj->attached_data_src_list, _this);
    res = ADPU2_PrepareToBuildNewData(p_obj, p_aso_item);
    if (!SYS_IS_ERROR_CODE(res))
    {
      p_buff = p_obj->in_data.p_payload;
    }

    /* */
    if(p_obj->notify_data_ready_f)
    {
      /* I do not process inline the new data, but I notify the app.
       * It will be responsibility of the app to call ADPU2_ProcessAndDispatch or manually
       * do the Process&Dispatch */
      p_obj->notify_data_ready_f((IDPU2_t*)p_obj, p_obj->p_data_ready_callback_param);
    }
    else
    {
      res = ADPU2_ProcessAndDispatch(p_obj);
    }
  }

  return p_buff;
}

static sys_error_code_t ADPU2_OnNewInputDataFromDPU(ADPU2_t *_this,  DataEvent_t *p_evt, ADPU2_t *p_src_dpu)
{
  assert_param(_this != NULL);
  assert_param(p_evt != NULL);
  assert_param(p_src_dpu != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  SYS_DECLARE_CS(cs);

  if (_this->active)
  {
    /* Check if we are start building a new data.*/
    SYS_ENTER_CRITICAL(cs);
    if (_this->cbh.p_producer_data_buff == NULL)
    {
      SYS_EXIT_CRITICAL(cs);
      /*get a new empty buffer from the circular buffer.*/
      res = (sys_error_code_t)CB_GetFreeItemFromHead(_this->cbh.p_cb, &_this->cbh.p_producer_data_buff);
      if (!SYS_IS_ERROR_CODE(res))
      {
        _this->in_data.p_payload = (uint8_t*)CB_GetItemData(_this->cbh.p_producer_data_buff);

        /* reset the data builder interface*/
        (void)IDataBuilder_Reset(p_src_dpu->next_dpu.p_builder, _this);
      }
      if (_this->in_data.p_payload == NULL)
      {
        /* no free cb item or there is a data source without a data builder. Check the build strategy...*/
        if (p_src_dpu->next_dpu.build_strategy != E_IDB_SKIP_DATA)
        {
          /* unable to build the IN data.*/
          sys_error_handler();
        }
        else
        {
          /* build_strategy == E_IDB_SKIP_DATA */
          return SYS_NO_ERROR_CODE;
        }
      }
    }
    else
    {
      SYS_EXIT_CRITICAL(cs);
    }

    res = IDataBuilder_OnNewInData(p_src_dpu->next_dpu.p_builder, &_this->in_data, p_evt->p_data, p_src_dpu->next_dpu.build_strategy, ADPU2_DataBuffAlloc);

    if (res == SYS_IDB_DATA_READY_ERROR_CODE)
    {
      /*a new data is ready*/
      CB_SetItemReady(_this->cbh.p_cb, _this->cbh.p_producer_data_buff);
      SYS_ENTER_CRITICAL(cs);
      _this->cbh.p_producer_data_buff = NULL;
      SYS_EXIT_CRITICAL(cs);
      if(_this->notify_data_ready_f)
      {
        /* I do not process inline the new data, but I notify the app.
         * It will be responsibility of the app to call ADPU2_ProcessAndDispatch or manually
         * do the Process&Dispatch */
        _this->notify_data_ready_f((IDPU2_t*)_this, _this->p_data_ready_callback_param);
      }
      else
      {
        res = ADPU2_ProcessAndDispatch(_this);
      }

      SYS_DEBUGF(SYS_DBG_LEVEL_ALL, ("ADPU2: new data ready\r\n"));
    }
  }

  return res;
}
