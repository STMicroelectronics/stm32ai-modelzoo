/**
 ******************************************************************************
 * @file    em_data_fortmat.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    Apr 4, 2022
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

#include "services/em_data_format.h"
#include <stdbool.h>

#define EM_IS_SUPPORTED_DATA_TYPE(_dt)     (((_dt) <= E_EM_FLOAT))
#define EM_IS_SUPPORTED_DATA_MODE(_dm)     (((_dm) == E_EM_MODE_LINEAR) || ((_dm) == E_EM_MODE_INTERLEAVED) || ((_dm) == E_EM_MODE_NONE))

typedef struct _EMDataClass
{
  size_t platform_data_size[EM_N_KNOWN_DATA_TYPE];
}EMDataClass;


static const EMDataClass s_TheClass = {
    {
        sizeof(uint8_t),
        sizeof(int8_t),
        sizeof(uint16_t),
        sizeof(int16_t),
        sizeof(uint32_t),
        sizeof(int32_t),
        sizeof(float),
#if 0
        sizeof(uint64_t),
        sizeof(int64_t),
        sizeof(double)
#endif
    }
};


/* Public API definition */
/*************************/

sys_error_code_t EMD_Init(EMData_t *p_data, uint8_t *p_payload, uint16_t type, uint8_t mode, uint8_t dimensions, ...)
{
  assert_param(p_data != NULL);
  assert_param((dimensions > 0) && (dimensions <= EM_DATA_CFG_MAX_SHAPE));
  assert_param(EM_IS_SUPPORTED_DATA_TYPE(type));
  assert_param(EM_IS_SUPPORTED_DATA_MODE(mode));
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /* parameter validation */
  if (dimensions == 1 && mode != E_EM_MODE_LINEAR)
  {
    res = SYS_EM_DATA_INVALID_MODE_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_EM_DATA_INVALID_MODE_ERROR_CODE);
    return res;
  }

  p_data->p_payload = p_payload;
  p_data->type = type;
  p_data->mode = mode;
  p_data->element_size = s_TheClass.platform_data_size[type];


  if((dimensions > 0) && (dimensions <= EM_DATA_CFG_MAX_SHAPE))
  {
    p_data->dimensions = dimensions;
    va_list valist;
    /* initialize valist for dimensions number of arguments */
    va_start(valist, dimensions);
    for(uint8_t i=0; i<dimensions; ++i)
    {
      p_data->shapes[i] = (uint16_t)va_arg(valist, int);
      if (p_data->shapes[i] == 0)
      {
        res = SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE);
        break;
      }
    }
    /* clean memory reserved for valist */
    va_end(valist);
  }
  else
  {
    res = SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE);
  }

  return res;
}

sys_error_code_t EMD_InitWithCustomType(EMData_t *p_data, uint8_t *p_payload, uint16_t type, uint16_t element_size, uint8_t mode, uint8_t dimensions, ...)
{
  assert_param(p_data != NULL);
  assert_param((dimensions > 0) && (dimensions <= EM_DATA_CFG_MAX_SHAPE));
  assert_param(EM_IS_SUPPORTED_DATA_MODE(mode));
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  /* parameter validation */
  if (dimensions == 1 && mode != E_EM_MODE_LINEAR)
  {
    res = SYS_EM_DATA_INVALID_MODE_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_EM_DATA_INVALID_MODE_ERROR_CODE);
    return res;
  }

  p_data->p_payload = p_payload;
  p_data->type = type;
  p_data->mode = mode;
  p_data->element_size = element_size;


  if((dimensions > 0) && (dimensions <= EM_DATA_CFG_MAX_SHAPE))
  {
    p_data->dimensions = dimensions;
    va_list valist;
    /* initialize valist for dimensions number of arguments */
    va_start(valist, dimensions);
    for(uint8_t i=0; i<dimensions; ++i)
    {
      p_data->shapes[i] = (uint16_t)va_arg(valist, int);
      if (p_data->shapes[i] == 0)
      {
        res = SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE;
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE);
        break;
      }
    }
    /* clean memory reserved for valist */
    va_end(valist);
  }
  else
  {
    res = SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE);
  }

  return res;
}

size_t EMD_GetPayloadSize(const EMData_t *p_data)
{
  assert_param(p_data != NULL);
  size_t payload_size = 1;
  for (uint8_t i=0; i<p_data->dimensions; ++i)
  {
    payload_size *= p_data->shapes[i];
  }

  payload_size *= EMD_GetElementSize(p_data);

  return payload_size;
}

sys_error_code_t EMD_GetValueAt(const EMData_t *p_data, void *p_val, uint8_t dimensions, ...)
{
  assert_param(p_data != NULL);
  assert_param(p_val != NULL);
  assert_param(dimensions == p_data->dimensions);
  register uint32_t val_pos = 0U;
  uint16_t index[EM_DATA_CFG_MAX_SHAPE];
  bool valid_params = true;

  if(dimensions == p_data->dimensions)
  {
    /* parameter validation*/
    va_list valist;
    /* initialize valist for dimensions number of arguments */
    va_start(valist, dimensions);
    for(uint8_t i=0; i<dimensions; ++i)
    {
      index[i] = (uint16_t)va_arg(valist, int);
      /* validate the argument */
      if (!(index[i] < p_data->shapes[i]))
      {
        valid_params = false;
        break;
      }
    }
    va_end(valist);

    if (valid_params)
    {
      /* find the data position */
      for (uint8_t i=0; i<dimensions; ++i)
      {
        register uint32_t stride = 1U;
        for (uint8_t j=i+1; j<dimensions; ++j)
        {
          stride *= p_data->shapes[j];
        }
        val_pos += stride * index[i];
      }
      uintptr_t val_addr = ((uintptr_t)p_data->p_payload) + (val_pos * p_data->element_size);

      memcpy(p_val, (void*)val_addr, p_data->element_size);
    }
  }

  return SYS_NO_ERROR_CODE;
}

uint8_t *EMD_DataAt(EMData_t *p_data, uint8_t dimensions, ...)
{
  assert_param(p_data != NULL);
  assert_param(dimensions == p_data->dimensions);
  register uint32_t val_pos = 0U;
  uint16_t index[EM_DATA_CFG_MAX_SHAPE];
  bool valid_params = true;
  uintptr_t val_addr = 0U;

  if(dimensions == p_data->dimensions)
  {
    /* parameter validation*/
    va_list valist;
    /* initialize valist for dimensions number of arguments */
    va_start(valist, dimensions);
    for(uint8_t i=0; i<dimensions; ++i)
    {
      index[i] = (uint16_t)va_arg(valist, int);
      /* validate the argument */
      if (!(index[i] < p_data->shapes[i]))
      {
        valid_params = false;
        break;
      }
    }
    va_end(valist);

    if (valid_params)
    {
      /* find the data position */
      for (uint8_t i=0; i<dimensions; ++i)
      {
        register uint32_t stride = 1U;
        for (uint8_t j=i+1; j<dimensions; ++j)
        {
          stride *= p_data->shapes[j];
        }
        val_pos += stride * index[i];
      }
    }

    //TODO: STF.Debug - on STM32 this must be uint32_t = sizeof(uint8_t*) because a pointer is 4 bytes.
    val_addr = ((uintptr_t)p_data->p_payload) + (val_pos * EMD_GetElementSize(p_data));
  }

  return (uint8_t*)val_addr;
}

EMCompare_t EMD_Compare(const EMData_t *p_data1, const EMData_t *p_data2)
{
  assert_param(p_data1 != NULL);
  assert_param(p_data2 != NULL);
  EMCompare_t res = E_EM_DATA_NOT_SAME_KIND;

  /*check the basic attribute of the data*/
  if ((p_data1->dimensions == p_data2->dimensions) &&
      (p_data1->mode == p_data2->mode) &&
      (p_data1->type == p_data2->type))
  {
    /* data are of the same kind but they can have different shapes*/
    int8_t diff_p = 0;
    int8_t diff_m = 0;
    for (uint8_t i=0; i<p_data1->dimensions; ++i)
    {
      diff_m += (p_data1->shapes[i] < p_data2->shapes[i] ? 1 : 0);
      diff_p += (p_data1->shapes[i] > p_data2->shapes[i] ? 1 : 0);
    }

    if ((diff_m == 0) && (diff_p == 0))
    {
      res = E_EM_DATA_SAME_KIND;
    }
    else if((diff_m > 0) && (diff_p == 0))
    {
      res = E_EM_DATA_SMALLER_SHAPE;
    }
    else if((diff_m == 0) && (diff_p > 0))
    {
      res = E_EM_DATA_BIGGER_SHAPE;
    }
    else {
      res = E_EM_DATA_NOT_SAME_KIND;
    }
  }

  else if ((p_data1->dimensions == p_data2->dimensions) &&
           (p_data1->mode != p_data2->mode) &&
           (p_data1->type == p_data2->type))
  {
    /* check the case E_EM_DATA_SAME_KIND_BUT_TYPE*/
    res = E_EM_DATA_SAME_KIND_BUT_TYPE;
    for (uint8_t i=0; i<p_data1->dimensions; ++i)
    {
      if(p_data1->shapes[i] != p_data2->shapes[i])
      {
        res = E_EM_DATA_NOT_SAME_KIND;
        break;
      }
    }
  }

  return res;
}

sys_error_code_t EMD_1dInit(EMData_t *p_data, uint8_t *p_payload, uint16_t type, uint16_t elements)
{
  assert_param(p_data != NULL);
  assert_param(EM_IS_SUPPORTED_DATA_TYPE(type));
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  p_data->p_payload = p_payload;
  p_data->type = type;
  p_data->mode = E_EM_MODE_LINEAR;
  p_data->element_size = s_TheClass.platform_data_size[type];
  p_data->dimensions = 1U;
  p_data->shapes[0] = elements;

  return res;
}

sys_error_code_t EMD_1dInitWithCustomType(EMData_t *p_data, uint8_t *p_payload, uint16_t type, uint16_t element_size, uint16_t elements)
{
  assert_param(p_data != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  p_data->p_payload = p_payload;
  p_data->type = type;
  p_data->mode = E_EM_MODE_LINEAR;
  p_data->element_size = element_size;
  p_data->dimensions = 1U;
  p_data->shapes[0] = elements;

  return res;
}
