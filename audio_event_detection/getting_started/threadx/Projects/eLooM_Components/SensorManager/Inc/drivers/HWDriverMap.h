/**
 ******************************************************************************
 * @file    HWDriverMap.h
 * @author  SRA - GPM
 * @brief   This class manages a map between a driver Instance and it's
 *          parameters
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 *
 ******************************************************************************
 */
#ifndef INCLUDE_HWDRIVERMAP_H_
#define INCLUDE_HWDRIVERMAP_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "drivers/IDriver.h"
#include "drivers/IDriver_vtbl.h"


typedef struct _HWDriverMapElement
{
  /**
   * Pointer to the driver instance
   */
  IDriver *p_driver_obj;

  /**
   * Unique key to identify the peripheral
   */
  uint32_t key;

  /**
   * Generic pointer to the static parameters of the specific implementation
   */
  void *p_static_param;
} HWDriverMapElement_t;


typedef struct _HWDriverMap
{
  /**
   * Pointer to the map instance
   */
  HWDriverMapElement_t *p_elements;

  /**
   * Map size, number of elements
   */
  uint16_t size;
} HWDriverMap_t;

/**
 * Initialize the Driver map.
 *
 * @param _this [IN] pointer to a valid ::HWDriverMap_t object.
 * @param p_elements [IN] pointer to a valid ::HWDriverMapElement_t array.
 * @param size [IN] size of the elements array
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t HWDriverMap_Init(HWDriverMap_t *_this, HWDriverMapElement_t *p_elements, uint16_t size)
{
  assert_param(_this != NULL);
  assert_param(p_elements != NULL);
  assert_param(p_elements != 0U);
  uint32_t i = 0U;

  _this->p_elements = p_elements;
  _this->size = size;

  /* initialize all elements to NULL */
  for(i = 0; i < size; i++)
  {
    p_elements[i].p_driver_obj = NULL;
    p_elements[i].key = 0;
    p_elements[i].p_static_param = NULL;
  }

  return SYS_NO_ERROR_CODE;
}

/**
 * Searches the map for an element with a the corresponding key
 *
 * @param _this [IN] pointer to a valid ::HWDriverMap_t object.
 * @param key [IN] key to be searched.
 * @return The corresponding ::HWDriverMapElement_t if found, NULL otherwise.
 */
static inline HWDriverMapElement_t *HWDriverMap_FindByKey(HWDriverMap_t *_this, uint32_t key)
{
  assert_param(_this != NULL);
  uint32_t i = 0U;

  while(_this->p_elements[i].key != key)
  {
    i++;
    if(i >= _this->size)
    {
      return NULL;
    }
  }
  return &_this->p_elements[i];
}

/**
 * Searches the map for an element containing the corresponding instance
 *
 * @param _this [IN] pointer to a valid ::HWDriverMap_t object.
 * @param instance [IN] key to be searched.
 * @return The corresponding ::HWDriverMapElement_t, if found, NULL otherwise.
 */
static inline HWDriverMapElement_t *HWDriverMap_FindByInstance(HWDriverMap_t *_this, IDriver *p_instance)
{
  assert_param(_this != NULL);
  assert_param(p_instance != NULL);
  uint32_t i = 0U;

  /* Find the instance of the driver */
  while(_this->p_elements[i].p_driver_obj != p_instance)
  {
    i++;
    if(i >= _this->size)
    {
      return NULL;
    }
  }
  return &_this->p_elements[i];
}

/**
 * Searches the map for the next free element
 *
 * @param _this [IN] pointer to a valid ::HWDriverMap_t object.
 * @return The first available ::HWDriverMapElement_t, if any, NULL otherwise.
 */
static inline HWDriverMapElement_t *HWDriverMap_GetFreeElement(HWDriverMap_t *_this)
{
  assert_param(_this != NULL);
  uint32_t i = 0U;

  while(_this->p_elements[i].p_driver_obj != NULL)
  {
    i++;
    if(i >= _this->size)
    {
      return NULL;
    }
  }
  return &_this->p_elements[i];
}

/**
 * Release the element from the map.
 *
 * @param _this [IN] pointer to a valid ::HWDriverMap_t object.
 * @param p_element [IN] pointer to a valid ::HWDriverMapElement_t of the provided map.
 * @return true in case of success, false otherwise.
 */
static inline bool HWDriverMap_Release(HWDriverMap_t *_this, HWDriverMapElement_t *p_element)
{
  assert_param(_this != NULL);
  assert_param(p_element != NULL);
  uint32_t i = 0U;

  while((&_this->p_elements[i]) != p_element)
  {
    i++;
    if(i >= _this->size)
    {
      return false;
    }
  }
  _this->p_elements[i].p_driver_obj = NULL;
  _this->p_elements[i].key = 0;
  _this->p_elements[i].p_static_param = NULL;

  return true;
}

/**
 * Release the element with the corresponding key from the map.
 *
 * @param _this [IN] pointer to a valid ::HWDriverMap_t object.
 * @param key [IN] key to be searched.
 * @return true in case of success, false otherwise.
 */
static inline bool HWDriverMap_ReleaseByKey(HWDriverMap_t *_this, uint32_t key)
{
  assert_param(_this != NULL);
  uint32_t i = 0U;

  while(_this->p_elements[i].key != key)
  {
    i++;
    if(i >= _this->size)
    {
      return false;
    }
  }
  _this->p_elements[i].p_driver_obj = NULL;
  _this->p_elements[i].key = 0;
  _this->p_elements[i].p_static_param = NULL;

  return true;
}

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_HWDRIVERMAP_H_ */
