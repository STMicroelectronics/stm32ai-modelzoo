/**
  ******************************************************************************
  * @file    CircularBuffer.c
  * @author  SRA - MCD
  * @brief   definition of the CircularBuffer.  *
  * For more information look at the CircularBuffer.h file.
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

#include "services/CircularBuffer.h"
#include <stdlib.h>

#define CB_ITEM_FREE   0x00  ///< Status of a circular buffer item: FREE.
#define CB_ITEM_NEW    0x01  ///< Status of a circular buffer item: NEW
#define CB_ITEM_READY  0x02  ///< Status of a circular buffer item: READY

#define CB_INCREMENT_IDX(p_cb, idx)    (((idx) + 1) % (p_cb)->item_count)
#define CB_IS_EMPTY(p_cb)              (((p_cb)->head_idx == (p_cb)->tail_idx) && ((p_cb)->p_items[(p_cb)->head_idx].status.status == CB_ITEM_FREE) ? 1 : 0)
#define CB_IS_FULL(p_cb)               (((p_cb)->head_idx == (p_cb)->tail_idx) && ((p_cb)->p_items[(p_cb)->head_idx].status.status != CB_ITEM_FREE) ? 1 : 0)

/**
* Specifies the status of a ::CBItem. An item can be:
* - FREE: an item is free if it is not allocated and it cannot be used by the application.
* - NEW: an item is new if it allocated and can be used by the application to produce its content.
* - READY: an item is ready if the application has produced its content and it can be consumed.
*/
typedef struct _CBItemStatus
{
  /**
  * Status bit.
  */
  uint8_t status :2;

  /**
  * reserved. Must be set to zero.
  */
  uint8_t reserved :6;
} CBItemStatus;

/**
* ::CBItem internal state.
*/
struct _CBItem
{
  /**
  * Specifies the user defined data managed by the circular buffer.
  */
  void *p_data;

  /**
  * Specifies a status flag added to each item. It is used to manage the item.
  */
  CBItemStatus status;
};

/**
* ::CircularBuffer internal state.
*/
struct _CircularBuffer
{

  /**
  * Specifies the index of the circular buffer tail.
  */
  uint16_t tail_idx;

  /**
  * Specifies the index of the circular buffer head.
  */
  uint16_t head_idx;

  /**
  * Specifies the maximum number of items that is possible to store in the buffer.
  */
  uint16_t item_count;

  /**
  * Specifies the item size.
  */
  uint16_t item_size;

  /**
  * Specified the buffer of items managed as a circular buffer.
  */
  CBItem *p_items;
};

// Private functions declarations
// ******************************


// Public API definition
// **********************

CircularBuffer* CB_Alloc(uint16_t item_count)
{
  CircularBuffer *p_obj = SysAlloc(sizeof(CircularBuffer));
  if(p_obj != NULL)
  {
    p_obj->p_items = SysAlloc(sizeof(CBItem) * item_count);

    if(p_obj->p_items == NULL)
    {
      /* release the memory */
      SysFree(p_obj);
      p_obj = NULL;
    }
    else
    {
      p_obj->item_count = item_count;
    }
  }
  return p_obj;
}

void CB_Free(CircularBuffer *_this)
{
  assert_param(_this);

  SysFree(_this->p_items);
  SysFree(_this);
}

uint16_t CB_Init(CircularBuffer *_this, void *p_items_buffer, uint16_t item_size)
{
  assert_param(_this);
  assert_param(p_items_buffer);
  uint16_t res = SYS_NO_ERROR_CODE;

  _this->head_idx = 0;
  _this->tail_idx = 0;
  _this->item_size = item_size;
  uint32_t pData = (uint32_t) p_items_buffer;
  for(uint32_t i = 0; i < _this->item_count; ++i)
  {
    _this->p_items[i].p_data = (void*) pData;
    _this->p_items[i].status.status = CB_ITEM_FREE;
    _this->p_items[i].status.reserved = 0;
    pData += item_size;
  }

  return res;
}

bool CB_IsEmpty(CircularBuffer *_this)
{
  assert_param(_this);
  bool res = false;
  SYS_DECLARE_CS(cs);

  SYS_ENTER_CRITICAL(cs);
  res = CB_IS_EMPTY(_this);
  SYS_EXIT_CRITICAL(cs);

  return res;
}

bool CB_IsFull(CircularBuffer *_this)
{
  assert_param(_this);
  bool res = false;
  SYS_DECLARE_CS(cs);

  SYS_ENTER_CRITICAL(cs);
  res = CB_IS_FULL(_this);
  SYS_EXIT_CRITICAL(cs);

  return res;
}

uint32_t CB_GetUsedItemsCount(CircularBuffer *_this)
{
  assert_param(_this != NULL);
  uint32_t items = 0;
  SYS_DECLARE_CS(cs);

  SYS_ENTER_CRITICAL(cs);
  if(!CB_IS_EMPTY(_this))
  {
    if(_this->head_idx > _this->tail_idx)
    {
      items = _this->head_idx - _this->tail_idx;
    }
    else
    {
      items = _this->item_count - (_this->tail_idx - _this->head_idx);
    }
  }
  SYS_EXIT_CRITICAL(cs);

  return items;
}

uint32_t CB_GetItemsCount(CircularBuffer *_this)
{
  assert_param(_this != NULL);
  uint32_t ret = 0;
  SYS_DECLARE_CS(cs);

  SYS_ENTER_CRITICAL(cs);
  ret = _this->item_count;
  SYS_EXIT_CRITICAL(cs);

  return  ret;
}

uint16_t CB_GetItemSize(CircularBuffer *_this)
{
  assert_param(_this);
  uint16_t ret = 0;
  SYS_DECLARE_CS(cs);

  SYS_ENTER_CRITICAL(cs);
  ret = _this->item_size;
  SYS_EXIT_CRITICAL(cs);

  return ret;
}

uint16_t CB_GetFreeItemFromHead(CircularBuffer *_this, CBItem **p_item)
{
  assert_param(_this);
  assert_param(p_item);
  uint16_t res = SYS_NO_ERROR_CODE;
  SYS_DECLARE_CS(cs);

  SYS_ENTER_CRITICAL(cs);
  if(_this->p_items[_this->head_idx].status.status == CB_ITEM_FREE)
  {
    *p_item = &_this->p_items[_this->head_idx];
    /* Mark the item as NEW */
    (*p_item)->status.status = CB_ITEM_NEW;
    /* Increment the head pointer */
    _this->head_idx = CB_INCREMENT_IDX(_this, _this->head_idx);
  }
  else
  {
    *p_item = NULL;
    res = SYS_CB_FULL_ERROR_CODE;
  }
  SYS_EXIT_CRITICAL(cs);

  return res;
}

uint16_t CB_GetReadyItemFromTail(CircularBuffer *_this, CBItem **p_item)
{
  assert_param(_this);
  assert_param(p_item);
  uint16_t res = SYS_NO_ERROR_CODE;
  SYS_DECLARE_CS(cs);

  SYS_ENTER_CRITICAL(cs);
  if(_this->p_items[_this->tail_idx].status.status == CB_ITEM_READY)
  {
    *p_item = &_this->p_items[_this->tail_idx];
    /* increment the tail pointer */
    _this->tail_idx = CB_INCREMENT_IDX(_this, _this->tail_idx);
  }
  else
  {
    *p_item = NULL;
    res = SYS_CB_NO_READY_ITEM_ERROR_CODE;
  }
  SYS_EXIT_CRITICAL(cs);

  return res;
}

uint16_t CB_ReleaseItem(CircularBuffer *_this, CBItem *p_item)
{
  assert_param(_this);
  assert_param(p_item);
  uint16_t res = SYS_NO_ERROR_CODE;
  SYS_DECLARE_CS(cs);

  UNUSED(_this);

  SYS_ENTER_CRITICAL(cs);
  if(p_item->status.status == CB_ITEM_NEW)
  {
    /* the item is not valid because it has been only allocated but not produced. */
    res = SYS_CB_INVALID_ITEM_ERROR_CODE;
  }
  else
  {
    /* item is already FREE or READY, so I can release it. */
    p_item->status.status = CB_ITEM_FREE;
  }
  SYS_EXIT_CRITICAL(cs);

  return res;
}

uint16_t CB_SetItemReady(CircularBuffer *_this, CBItem *p_item)
{
  assert_param(_this);
  assert_param(p_item);
  uint16_t res = SYS_NO_ERROR_CODE;
  SYS_DECLARE_CS(cs);

  UNUSED(_this);

  SYS_ENTER_CRITICAL(cs);
  if(p_item->status.status == CB_ITEM_FREE)
  {
    /* the item is not valid because it has not been allocated */
    res = SYS_CB_INVALID_ITEM_ERROR_CODE;
  }
  else
  {
    /* the item is already READY or NEW, so I can mark as READY. */
    p_item->status.status = CB_ITEM_READY;
  }
  SYS_EXIT_CRITICAL(cs);

  return res;
}

void* CB_GetItemData(CBItem *p_item)
{
  assert_param(p_item);

  return p_item->p_data;
}

void* CB_GetItemsBuffer(CircularBuffer *_this)
{
  assert_param(_this);

  return _this->p_items[0].p_data;
}

CBItem* CB_PeekNextItem(CircularBuffer *_this, CBItem *p_item)
{
  assert_param(_this);
  assert_param(p_item);
  CBItem *pNextItem = NULL;

  /* find p_item in the buffer */
  uint16_t index = 0;
  uint8_t found = 0;
  while(!found && (index < _this->item_count))
  {
    if(&_this->p_items[index] == p_item)
    {
      found = 1;
    }
    else
    {
      index++;
    }
  }

  if(found)
  {
    pNextItem = &_this->p_items[CB_INCREMENT_IDX(_this, index)];
  }

  return pNextItem;
}

// Private functions definition
// ****************************


