/**
 ******************************************************************************
 * @file    CircularBuffer.h
 * @author  SRA - MCD
 * @brief  Circular buffer implementation specialized for the producer /
 * consumer design pattern.
 * This class allocates and manage a set of user defined type items
 * (::CBItemData) in a circular way. The user get a new free item from the
 * head of the buffer (to produce its content), and a he get a ready item from
 * the tail (to consume its content).
 * This class is specialized for the producer /consumer design pattern.
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

#ifndef USER_INC_CIRCULARBUFFER_H_
#define USER_INC_CIRCULARBUFFER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systp.h"
#include "services/sysmem.h"
#include "services/syscs.h"


#ifndef SYS_NO_ERROR_CODE
#define SYS_NO_ERROR_CODE                                 0
#endif
#ifndef SYS_CB_BASE_ERROR_CODE
#define SYS_CB_BASE_ERROR_CODE                            1
#endif
#define SYS_CB_INVALID_ITEM_ERROR_CODE                    SYS_CB_BASE_ERROR_CODE + 1
#define SYS_CB_FULL_ERROR_CODE                            SYS_CB_BASE_ERROR_CODE + 2
#define SYS_CB_NO_READY_ITEM_ERROR_CODE                   SYS_CB_BASE_ERROR_CODE + 3
#define SYS_CB_ERROR_CODE_COUNT                           3


/**
 * Create a type name for _CircularBuffer
 */
typedef struct _CircularBuffer CircularBuffer;

/**
 * Create a type name for _CBItem
 */
typedef struct _CBItem CBItem;


// Public API declaration
// **********************

/**
 * Allocate an object of ::CircularBuffer type. This allocator implement the singleton design pattern,
 * so there is only one instance of circular buffer.
 * A new allocated object must be initialized before use it.
 *
 * @param [IN] nItemCount specifies the maximum number of items that is possible to store in the buffer.
 * @return a pointer to new allocated circular buffer object.
 */
CircularBuffer *CB_Alloc(uint16_t item_count);

/**
 * Deallocate the ::CircularBuffer object.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 */
void CB_Free(CircularBuffer *_this);

/**
 * Initialize a circular buffer object. The application allocate the data buffer.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @param p_items_buffer [IN] specifies the memory buffer where the data are stored.
 * @param item_size [IN] specifies the size in byte of an item.
 * @return SYS_NO_ERROR_CODE
 */
uint16_t CB_Init(CircularBuffer *_this, void *p_items_buffer, uint16_t item_size);

/**
 * Check if the circular buffer is empty.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @return `true` if the circular buffer is empty, `false` otherwise
 */
bool CB_IsEmpty(CircularBuffer *_this);

/**
 * Check if the circular buffer is full.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @return `true` if the circular buffer is full, `false` otherwise
 */
bool CB_IsFull(CircularBuffer *_this);

/**
 * Get the number of allocated (NEW or READY) items.
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @return the number of items in the buffer that are NEW or READY.
 */
uint32_t CB_GetUsedItemsCount(CircularBuffer *_this);

/**
 * Get the number of items.
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @return the number of items in the buffer that are NEW or READY.
 */
uint32_t CB_GetItemsCount(CircularBuffer *_this);

/**
 * Get the items size for the specified Circular Buffer.
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @return the size of the items.
 */
uint16_t CB_GetItemSize(CircularBuffer *_this);

/**
 * Get a free item from the head of the buffer. A free item can be used by the caller to produce its content.
 * When the item is ready the caller must call CBSetItemReady() to mark the item a ready to be consumed.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @param p_item [OUT] pointer to the new circular buffer item object. If the operation fails the pointer will be set to NULL.
 * @return SYS_NO_ERROR_CODE if success, SYS_CB_FULL_ERROR_CODE if the buffer is full.
 */
uint16_t CB_GetFreeItemFromHead(CircularBuffer *_this, CBItem **p_item);

/**
 * Get a ready item from the tail of the buffer. A ready item can be consumed by the caller.
 * After the item is consumed the caller must call CBReleaseItem() in order to free the item.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @param p_item [OUT] pointer to the ready circular buffer item object. If the operation fails the pointer will be set to NULL.
 * @return SYS_NO_ERROR_CODE if success, SYS_CB_NO_READY_ITEM_ERROR_CODE if there are not ready item in the tail of the buffer.
 */
uint16_t CB_GetReadyItemFromTail(CircularBuffer *_this, CBItem **p_item);

/**
 * Release an item. After an item has been consumed it must be released so it is marked as free,
 * and avoid the buffer to become full. If the item is new, that means it has been allocate but it is not ready yet,
 * the function fails.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @param p_item [IN] specifies a pointer to the item to be released.
 * @return SYS_NO_ERROR_CODE if success, SYS_CB_INVALID_ITEM_ERROR_CODE otherwise.
 */
uint16_t CB_ReleaseItem(CircularBuffer *_this, CBItem *p_item);

/**
 * Mark an item as ready. When a new item is ready to be consumed it must be marked as ready.
 * If the item has not been allocated, and it is free, the function fails.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object.
 * @param p_item [IN] specifies a pointer to the item to be marked as ready.
 * @return SYS_NO_ERROR_CODE if success, SYS_CB_INVALID_ITEM_ERROR_CODE otherwise.
 */
uint16_t CB_SetItemReady(CircularBuffer *_this, CBItem *p_item);

/**
 * Get a pointer to the user data wrapped inside a circular buffer item.
 *
 * @param p_item [IN] specifies a pointer to a circular buffer item
 * @return a pointer to the user data wrapped inside a circular buffer item.
 */
void *CB_GetItemData(CBItem *p_item);

/**
 * Get a pointer to the data buffer.
 *
 * @param pItem [IN] specifies a pointer to a circular buffer item
 * @return a pointer to the data buffer.
 */
void *CB_GetItemsBuffer(CircularBuffer *_this);

/**
 * Given an item, this method return the next item in the buffer without modifying the status
 * of the circular buffer. If the input item is doesn't belong to the circular buffer,
 * then the method returns NULL.
 *
 * @param _this [IN] specifies a pointer to a ::CircularBuffer object
 * @param pItem [IN] specifies a pointer to a circular buffer item
 * @return the item in the buffer at the next position respect to pItem,
 *         or NULL if pItem doesn't belong to the buffer.
 */
CBItem *CB_PeekNextItem(CircularBuffer *_this, CBItem *p_item);


#ifdef __cplusplus
}
#endif

#endif /* USER_INC_CIRCULARBUFFER_H_ */
