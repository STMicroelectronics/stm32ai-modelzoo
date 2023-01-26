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

#include "CircularBuffer.h"
#include <stdlib.h>

#define CB_ITEM_FREE   0x00  ///< Status of a circular buffer item: FREE.
#define CB_ITEM_NEW    0x01  ///< Status of a circular buffer item: NEW
#define CB_ITEM_READY  0x02  ///< Status of a circular buffer item: READY

#define CB_INCREMENT_IDX(pCB, idx)   (((idx) + 1) % (pCB)->itemCount)
#define CB_IS_EMPTY(pCB)              (((pCB)->headIdx == (pCB)->tailIdx) && ((pCB)->pItems[(pCB)->headIdx].status.status == CB_ITEM_FREE) ? 1 : 0)
#define CB_IS_FULL(pCB)               (((pCB)->headIdx == (pCB)->tailIdx) && ((pCB)->pItems[(pCB)->headIdx].status.status != CB_ITEM_FREE) ? 1 : 0)

#ifndef SYS_IS_CALLED_FROM_ISR
#define SYS_IS_CALLED_FROM_ISR() ((SCB->ICSR & SCB_ICSR_VECTACTIVE_Msk) != 0 ? 1 : 0)
#endif

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
  void *pData;
  
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
  uint16_t tailIdx;
  
  /**
  * Specifies the index of the circular buffer head.
  */
  uint16_t headIdx;
  
  /**
  * Specifies the maximum number of items that is possible to store in the buffer.
  */
  uint16_t itemCount;
  
  /**
  * Specifies the item size.
  */
  uint16_t itemSize;
  
  /**
  * Specified the buffer of items managed as a circular buffer.
  */
  CBItem *pItems;
};

// Private functions declarations
// ******************************

/**
* Start a critical section to protect the circular buffer object from multi-task access.
*/
static inline void CB_EnterCritical(void);

/**
*  End a critical section to allow other tasks to use the circular buffer object.
*/
static inline void CB_ExitCritical(void);

// Public API definition
// **********************

CircularBuffer* CB_Alloc(uint16_t ItemCount)
{
  CircularBuffer *pObj = CB_HEAP_ALLOC(sizeof(CircularBuffer));
  if(pObj != NULL)
  {
    pObj->pItems = CB_HEAP_ALLOC(sizeof(CBItem) * ItemCount);
    
    if(pObj->pItems == NULL)
    {
      /* release the memory */
      CB_HEAP_FREE(pObj);
      pObj = NULL;
    }
    else
    {
      pObj->itemCount = ItemCount;
    }
  }
  return pObj;
}

void CB_Free(CircularBuffer *_this)
{
  assert_param(_this);
  
  CB_HEAP_FREE(_this->pItems);
  CB_HEAP_FREE(_this);
}

uint32_t CB_Init(CircularBuffer *_this, void *pItemsBuffer, uint16_t ItemSize)
{
  assert_param(_this);
  assert_param(pItemsBuffer);
  uint32_t ret = CB_NO_ERROR_CODE;
  
  _this->headIdx = 0;
  _this->tailIdx = 0;
  _this->itemSize = ItemSize;
  uint32_t pData = (uint32_t) pItemsBuffer;
  for(uint32_t i = 0; i < _this->itemCount; ++i)
  {
    _this->pItems[i].pData = (void*) pData;
    _this->pItems[i].status.status = CB_ITEM_FREE;
    _this->pItems[i].status.reserved = 0;
    pData += ItemSize;
  }
  
  return ret;
}

uint8_t CB_IsEmpty(CircularBuffer *_this)
{
  assert_param(_this);
  uint8_t ret = 0;
  
  CB_EnterCritical();
  ret = CB_IS_EMPTY(_this);
  CB_ExitCritical();
  
  return ret;
}

uint8_t CB_IsFull(CircularBuffer *_this)
{
  assert_param(_this);
  uint8_t ret = 0;
  
  CB_EnterCritical();
  ret = CB_IS_FULL(_this);
  CB_ExitCritical();
  
  return ret;
}

uint32_t CB_GetUsedItemsCount(CircularBuffer *_this)
{
  assert_param(_this != NULL);
  uint32_t items = 0;
  
  CB_EnterCritical();
  if(!CB_IS_EMPTY(_this))
  {
    if(_this->headIdx > _this->tailIdx)
    {
      items = _this->headIdx - _this->tailIdx;
    }
    else
    {
      items = _this->itemCount - (_this->tailIdx - _this->headIdx);
    }
  }
  CB_ExitCritical();
  
  return items;
}

uint32_t CB_GetItemsCount(CircularBuffer *_this)
{
  assert_param(_this != NULL);
  uint32_t ret =0;
  
  CB_EnterCritical();
  ret = _this->itemCount;
  CB_ExitCritical();
  
  return  ret;
}

uint16_t CB_GetItemSize(CircularBuffer *_this)
{
  assert_param(_this);  
  uint16_t ret =0;
  
  CB_EnterCritical();
  ret = _this->itemSize;
  CB_ExitCritical();
  
  return ret;
}

uint32_t CB_GetFreeItemFromHead(CircularBuffer *_this, CBItem **pItem)
{
  assert_param(_this);
  assert_param(pItem);
  uint32_t ret = CB_NO_ERROR_CODE;
  
  CB_EnterCritical();
  if(_this->pItems[_this->headIdx].status.status == CB_ITEM_FREE)
  {
    *pItem = &_this->pItems[_this->headIdx];
    /* Mark the item as NEW */
    (*pItem)->status.status = CB_ITEM_NEW;
    /* Increment the head pointer */
    _this->headIdx = CB_INCREMENT_IDX(_this, _this->headIdx);
  }
  else
  {
    *pItem = NULL;
    ret = CB_FULL_ERROR_CODE;
  }
  CB_ExitCritical();
  
  return ret;
}

uint32_t CB_GetReadyItemFromTail(CircularBuffer *_this, CBItem **pItem)
{
  assert_param(_this);
  assert_param(pItem);
  uint32_t ret = CB_NO_ERROR_CODE;
  
  CB_EnterCritical();
  if(_this->pItems[_this->tailIdx].status.status == CB_ITEM_READY)
  {
    *pItem = &_this->pItems[_this->tailIdx];
    /* increment the tail pointer */
    _this->tailIdx = CB_INCREMENT_IDX(_this, _this->tailIdx);
  }
  else
  {
    *pItem = NULL;
    ret = CB_NO_READY_ITEM_ERROR_CODE;
  }
  CB_ExitCritical();
  
  return ret;
}

uint32_t CB_ReleaseItem(CircularBuffer *_this, CBItem *pItem)
{
  assert_param(_this);
  assert_param(pItem);
  uint32_t xRes = CB_NO_ERROR_CODE;
  
  UNUSED(_this);
  
  CB_EnterCritical();
  if(pItem->status.status == CB_ITEM_NEW)
  {
    /* the item is not valid because it has been only allocated but not produced. */
    xRes = CB_INVALID_ITEM_ERROR_CODE;
  }
  else
  {
    /* item is already FREE or READY, so I can release it. */
    pItem->status.status = CB_ITEM_FREE;
  }
  CB_ExitCritical();
  
  return xRes;
}

uint32_t CB_SetItemReady(CircularBuffer *_this, CBItem *pItem)
{
  assert_param(_this);
  assert_param(pItem);
  uint32_t xRes = CB_NO_ERROR_CODE;
  
  UNUSED(_this);
  
  CB_EnterCritical();
  if(pItem->status.status == CB_ITEM_FREE)
  {
    /* the item is not valid because it has not been allocated */
    xRes = CB_INVALID_ITEM_ERROR_CODE;
  }
  else
  {
    /* the item is already READY or NEW, so I can mark as READY. */
    pItem->status.status = CB_ITEM_READY;
  }
  CB_ExitCritical();
  
  return xRes;
}

void* CB_GetItemData(CBItem *pItem)
{
  assert_param(pItem);
  
  return pItem->pData;
}

void* CB_GetItemsBuffer(CircularBuffer *_this)
{
  assert_param(_this);
  
  return _this->pItems[0].pData;
}

CBItem* CB_PeekNextItem(CircularBuffer *_this, CBItem *pItem)
{
  assert_param(_this);
  assert_param(pItem);
  CBItem *pNextItem = NULL;
  
  /* find pItem in the buffer */
  uint16_t index = 0;
  uint8_t found = 0;
  while(!found && (index < _this->itemCount))
  {
    if(&_this->pItems[index] == pItem)
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
    pNextItem = &_this->pItems[CB_INCREMENT_IDX(_this, index)];
  }
  
  return pNextItem;
}

// Private functions definition
// ****************************

static inline void CB_EnterCritical(void)
{
  if(SYS_IS_CALLED_FROM_ISR())
  {
    taskENTER_CRITICAL_FROM_ISR();
  }
  else
  {
    taskENTER_CRITICAL();
  }
}

static inline void CB_ExitCritical(void)
{
  if(SYS_IS_CALLED_FROM_ISR())
  {
    taskEXIT_CRITICAL_FROM_ISR(0);
  }
  else
  {
    taskEXIT_CRITICAL();
  }
}


