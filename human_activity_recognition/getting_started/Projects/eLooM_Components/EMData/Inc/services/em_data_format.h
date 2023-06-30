/**
 ******************************************************************************
 * @file    em_data_fortmat.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    Apr 4, 2022
 *
 * @brief   Data format.
 *
 * Common data format used to store and manipulate the data in memory by
 * eLooM components.
 * The data are multidimensional array of homogeneous type, stored in
 * row-major order.
 *
 * \anchor fig43 \image html 43_emd_row-major_order.png "Fig.43 - Row-major order"
 *
 * In this context the dimension are called also shape. The maximum number of
 * shape is specified by the macro
 * `EM_DATA_CFG_MAX_SHAPE`.
 *
 * A data object is composed by a **payload**, that is a
 * pointer to a contiguous memory location that store the values of the data,
 * and a metadata that are additional information describing how the value
 * are organized in memory.
 *
 * The supported type are:
 * - E_EM_INT8
 * - E_EM_UINT8
 * - E_EM_INT16
 * - E_EM_UINT16
 * - E_EM_INT32
 * - E_EM_UINT32
 * - E_EM_FLOAT
 *
 * The `mode` specifies how the data are stored in memory. It can be:
 * - E_EM_MODE_NONE
 * - E_EM_MODE_INTERLEAVED
 * - E_EM_MODE_LINEAR
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
#ifndef INC_SERVICES_EM_DATA_EM_DATA_FORTMAT_H_
#define INC_SERVICES_EM_DATA_EM_DATA_FORTMAT_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
#include <string.h>
#include "services/systp.h"
#include "services/syserror.h"

#ifndef EM_DATA_CFG_MAX_SHAPE
#define EM_DATA_CFG_MAX_SHAPE          3
#endif

/* Error Code */
/**************/
#ifndef SYS_BASE_EM_DATA_ERROR_CODE
#define SYS_BASE_EM_DATA_ERROR_CODE            APP_BASE_ERROR_CODE
#endif
#define SYS_EM_DATA_INVALID_MODE_ERROR_CODE    SYS_BASE_EM_DATA_ERROR_CODE + 1
#define SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE  SYS_BASE_EM_DATA_ERROR_CODE + 2

 /*
  * Known data type.
  */

#define E_EM_UINT8                     0x00  /**< E_EM_UINT8  */
#define E_EM_INT8                      0x01  /**< E_EM_INT8   */
#define E_EM_UINT16                    0x02  /**< E_EM_UINT16 */
#define E_EM_INT16                     0x03  /**< E_EM_INT16  */
#define E_EM_UINT32                    0x04  /**< E_EM_UINT32 */
#define E_EM_INT32                     0x05  /**< E_EM_INT32  */
#define E_EM_FLOAT                     0x06  /**< E_EM_FLOAT  */
#if 0
#define E_EM_UINT64                    0x08  /**< E_EM_UINT64 */
#define E_EM_INT64                     0x09  /**< E_EM_INT64  */
#define E_EM_DOUBLE                    0x0A  /**< E_EM_DOUBLE */
#endif
#define EM_N_KNOWN_DATA_TYPE       7    /** Specifies the number of data type well known in the framework.*/

/*
 * Specifies how the data are stored in memory.
 */

#define E_EM_MODE_NONE                 0x20  /**< E_EM_MODE_NONE        */
#define E_EM_MODE_LINEAR               0x40  /**< E_EM_MODE_LINEAR      */
#define E_EM_MODE_INTERLEAVED          0x80  /**< E_EM_MODE_INTERLEAVED */


typedef enum _EMComapre
{
  E_EM_DATA_SAME_KIND,
  E_EM_DATA_BIGGER_SHAPE,
  E_EM_DATA_SMALLER_SHAPE,
  E_EM_DATA_SAME_KIND_BUT_TYPE,
  E_EM_DATA_NOT_SAME_KIND
} EMCompare_t;

/**
 * eLooM generic data type. It describes a multidimensional data like, for example, matrix.
 * The base type of all elements is one of ::EMDataType_t. This means the data is homogeneous.
 * The elements are stored in memory according to one of the supported ::EMDataMode_t.
 */
typedef struct _EMData
{
  /**
   * Pointer to memory region where the data are stored.
   */
  uint8_t *p_payload;

  /**
   * It specifies the number of items for each shape.
   */
  uint16_t shapes[EM_DATA_CFG_MAX_SHAPE];


  /**
   * Specifies the data type of the of each elements.
   */
  uint16_t type;

  /**
   * Specifies the number of padding bytes there are between each element of the data.
   */
//  uint8_t padding; //TODO: do we need this? Maybe in case of custom type like struct.

  uint16_t element_size;

  /**
   * Specifies how the elements of the data are stored in memory.
   */
  uint8_t mode;

  /**
   * Specifies the number of dimensions (or shape) of the data. Valid value are in the range [1, EM_DATA_MAX_SHAPE].
   */
  uint8_t dimensions;

}EMData_t;


/* Public API declaration */
/**************************/

/**
 * Initialize a data object using a payload and the parameters that specify the shape of the payload for a known element type.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param p_payload [IN] specifies a pointer to a contiguous memory location that store the values of the data.
 * It can be NULL, and in this case the data object is useful to get information about the data.
 * @param type [IN] specifies the type of the values of the data. Valid value are:
 *   - E_EM_INT8
 *   - E_EM_UINT8
 *   - E_EM_INT16
 *   - E_EM_UINT16
 *   - E_EM_INT32
 *   - E_EM_UINT32
 *   - E_EM_FLOAT
 *
 *   To use a new application defined type use the initialization function EMD_InitWithCustomType().
 * @param mode [IN] specifies how the data value are stored / interpreted. Valid value:
 *   - E_EM_MODE_NONE
 *   - E_EM_MODE_LINEAR
 *   - E_EM_MODE_INTERLEAVED
 * @param dimensions [IN] specifies the number of shape of the data. After `dimensions` there must be
 *   dimensions parameters specifying the numbers of element for each shape (or dimension).
 * @return SYS_NO_ERROR_CODE if success, SYS_EM_DATA_INVALID_MODE_ERROR_CODE if dimensions is 1 and mode is not E_EM_MODE_LINEAR,
 *   or SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE if the format is not valid
 */
sys_error_code_t EMD_Init(EMData_t *p_data, uint8_t *p_payload, uint16_t type, uint8_t mode, uint8_t dimensions, ...);

/**
 * Initialize a data object using a payload and the parameters that specify the shape of the payload for an application defined element type.
 * The application can define its own element type by providing a unique `type` and the size in byte of the element type.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param p_payload [IN] specifies a pointer to a contiguous memory location that store the values of the data.
 * It can be NULL, and in this case the data object is useful to get information about the data.
 * @param type [IN] specifies an unique id for the application defined type.
 * @param element_size [IN] specifies the size in byte of type of element defined by the application.
 * @param mode [IN] specifies how the data value are stored / interpreted. Valid value:
 *   - E_EM_MODE_NONE
 *   - E_EM_MODE_LINEAR
 *   - E_EM_MODE_INTERLEAVED
 * @param dimensions [IN] specifies the number of shape of the data. After `dimensions` there must be
 *   dimensions parameters specifying the numbers of element for each shape (or dimension).
 * @return SYS_NO_ERROR_CODE if success, SYS_EM_DATA_INVALID_MODE_ERROR_CODE if dimensions is 1 and mode is not E_EM_MODE_LINEAR,
 *   or SYS_EM_DATA_INVALID_FORMAT_ERROR_CODE if the format is not valid
 */
sys_error_code_t EMD_InitWithCustomType(EMData_t *p_data, uint8_t *p_payload, uint16_t type, uint16_t element_size, uint8_t mode, uint8_t dimensions, ...);

/**
 * Initialize a data object using a payload and the parameters that specify the shape of the payload for a known element type.
 * This is a version of EMD_1dInit() specialized for one dimensional data (1D). In this case the mode is fixed as E_EM_MODE_LINEAR.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param p_payload [IN] specifies a pointer to a contiguous memory location that store the values of the data.
 * It can be NULL, and in this case the data object is useful to get information about the data.
 * @param type [IN] specifies the type of the values of the data. Valid value are:
 *   - E_EM_INT8
 *   - E_EM_UINT8
 *   - E_EM_INT16
 *   - E_EM_UINT16
 *   - E_EM_INT32
 *   - E_EM_UINT32
 *   - E_EM_FLOAT
 *
 *   To use a new application defined type use the initialization function EMD_InitWithCustomType().
 * @param elements [IN] specifies the numbers of element for shape[0] (or dimension).
 * @return SYS_NO_ERROR_CODE
 */
sys_error_code_t EMD_1dInit(EMData_t *p_data, uint8_t *p_payload, uint16_t type, uint16_t elements);

/**
 * Initialize a data object using a payload and the parameters that specify the shape of the payload for an application defined element type.
 * The application can define its own element type by providing a unique `type` and the size in byte of the element type.
 * This is a version of EMD_1dInit() specialized for one dimensional data (1D). In this case the mode is fixed as E_EM_MODE_LINEAR.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param p_payload [IN] specifies a pointer to a contiguous memory location that store the values of the data.
 * It can be NULL, and in this case the data object is useful to get information about the data.
 * @param type [IN] specifies an unique id for the application defined type.
 * @param element_size [IN] specifies the size in byte of type of element defined by the application.
 * @param elements [IN] specifies the numbers of element for each shape[0] (or dimension).
 * @return SYS_NO_ERROR_CODE
 */
sys_error_code_t EMD_1dInitWithCustomType(EMData_t *p_data, uint8_t *p_payload, uint16_t type, uint16_t element_size, uint16_t elements);


/**
 * Compute the size in byte of the payload.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @return the size in byte of the payload
 */
size_t EMD_GetPayloadSize(const EMData_t *p_data);

/**
 * Compute the size in byte of the type of an element of the data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @return the size in byte of the type of an element of the data.
 */
static inline
size_t EMD_GetElementSize(const EMData_t *p_data);

/**
 * Get the type of the data. It is one of:
 *   - E_EM_INT8
 *   - E_EM_UINT8
 *   - E_EM_INT16
 *   - E_EM_UINT16
 *   - E_EM_INT32
 *   - E_EM_UINT32
 *   - E_EM_FLOAT
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @return the type of the data.
 */
static inline
uint16_t EMD_GetType(const EMData_t *p_data);

/**
 * Get the mode of the data. It is one of:
 *   - E_EM_MODE_NONE
 *   - E_EM_MODE_LINEAR
 *   - E_EM_MODE_INTERLEAVED
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @return the mode of the data.
 */
static inline
uint8_t EMD_GetMode(const EMData_t *p_data);

/**
 * Get the dimension (that is the number of shapes) of the data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @return the number of shape of the data
 */
static inline
uint8_t EMD_GetDimensions(const EMData_t *p_data);

/**
 * Get the number of element in a given shape (or dimension) of the data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param dimension [IN] specifies the 0 based index of a shape of the data.
 * @return the number of element in a given shape (or dimension) of the data.
 */
static inline
uint16_t EMD_GetShape(const EMData_t *p_data, uint8_t dimension);

/**
 * Get the number of elements of the data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @return the number of elements of the data.
 */
static inline
uint32_t EMD_GetElementsCount(const EMData_t *p_data);

/**
 * Check if the two data are compatible. The result can be one of:
 * - E_EM_DATA_SAME_KIND: data1 and data2 have the same metadata.
 * - E_EM_DATA_BIGGER_SHAPE: data1 and data 2 have the same metadata but data1 has bigger dimensions in each shape.
 * - E_EM_DATA_SMALLER_SHAPE: data1 and data 2 have the same metadata but data1 has smaller dimensions in each shape.
 * - E_EM_DATA_SAME_KIND_BUT_TYPE: data1 and data 2 have the same metadata but 'type' is different.
 * - E_EM_DATA_NOT_SAME_KIND: data1 and data2 have different metadata.
 *
 * @param p_data1 [IN] specifies a pointer to the first data object to compare.
 * @param p_data2 [IN] specifies a pointer to the second data object to compare.
 * @return the result of the comparison between the two data objects.
 */
EMCompare_t EMD_Compare(const EMData_t *p_data1, const EMData_t *p_data2);

/**
 * Get the vale of the data at a given index. `dimension` must be equal to the number of shapes of the data, and it is used
 * to specify the number of optional arguments.
 *
 * For example, in a bidimensional data [4 x 2], the call EMD_GetValueAt(&data, 2, 2, 1) get the value at index (2, 1).
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param p_val [OUT] specifies a buffer provided by the caller to store the value. It size must be greater that EMD_GetElementSize(p_data).
 * @param dimensions must be equal to the number of shapes of the data. It is used to specify the number of optional arguments.
 * @return the value of the data at a given index. If the index is not well formed, then the value is undefined.
 */
sys_error_code_t EMD_GetValueAt(const EMData_t *p_data, void *p_val, uint8_t dimensions, ...);

/**
 * Get the address of the vale of the data at a given address. `dimension` must be equal to the number of shapes of the data, and it is used
 * to specify the number of optional arguments. This address can be used to set the value of the data at a given index (d1, .. dn).
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param dimensions must be equal to the number of shapes of the data. It is used to specify the number of optional arguments.
 * @return the address of the value of the data at a given index. If the index is not well formed, then the address is undefined.
 */
uint8_t *EMD_DataAt(EMData_t *p_data, uint8_t dimensions, ...);

/**
 * Get the payload of the data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @return the payload of the data.
 */
static inline
uint8_t *EMD_Data(const EMData_t *p_data);

/**
 * This is a version of EMD_GetValueAt() specialized for bidimensional (2d) data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param p_val [OUT] specifies a buffer provided by the caller to store the value. It size must be greater that EMD_GetElementSize(p_data).
 * @param d1_idx specifies the zero based index for the first dimension. It must less than `p_data->shape[0]`.
 * @param d2_idx specifies the zero based index for the second dimension. It must less than `p_data->shape[1]`.
 * @return the value of the data at the index (d1_idx, d2_idx). If the index is not well formed, then the value is undefined.
 */
static inline
sys_error_code_t EMD_2dGetValueAt(const EMData_t *p_data, void *p_val, uint16_t d1_idx, uint16_t d2_idx);

/**
 * This is a version of EMD_DataAt() specialized for bidimensional (2d) data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param d1_idx specifies the zero based index for the first dimension. It must less than `p_data->shape[0]`.
 * @param d2_idx specifies the zero based index for the second dimension. It must less than `p_data->shape[1]`.
 * @return the address of the value of the index (d1_idx, d2_idx). If the index is not well formed, then the address is undefined.
 */
static inline
uint8_t *EMD_2dDataAt(EMData_t *p_data, uint16_t d1_idx, uint16_t d2_idx);

/**
 * This is a version of EMD_GetValueAt() specialized for monodimensional (1d) data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param p_val [OUT] specifies a buffer provided by the caller to store the value. It size must be greater that EMD_GetElementSize(p_data).
 * @param d1_idx specifies the zero based index for the first dimension. It must less than `p_data->shape[0]`.
 * @return the value of the data at the index (d1_idx). If the index is not well formed, then the value is undefined.
 */
static inline
sys_error_code_t EMD_1dGetValueAt(const EMData_t *p_data, void *p_val, uint16_t d1_idx);

/**
 * This is a version of EMD_DataAt() specialized for monodimensional (1d) data.
 *
 * @param p_data [IN] specifies a pointer to a data object.
 * @param d1_idx specifies the zero based index for the first dimension. It must less than `p_data->shape[0]`.
 * @return the address of the value of the index (d1_idx). If the index is not well formed, then the address is undefined.
 */
static inline
uint8_t *EMD_1dDataAt(EMData_t *p_data, uint16_t d1_idx);


/* Inline function definition */
/******************************/

static inline
size_t EMD_GetElementSize(const EMData_t *p_data)
{
  assert_param(p_data != NULL);

  return p_data->element_size;
}

static inline
uint16_t EMD_GetType(const EMData_t *p_data)
{
  assert_param(p_data != NULL);

  return p_data->type;
}

static inline
uint8_t EMD_GetMode(const EMData_t *p_data)
{
  assert_param(p_data != NULL);

  return p_data->mode;
}

static inline
uint8_t EMD_GetDimensions(const EMData_t *p_data)
{
  assert_param(p_data != NULL);

  return p_data->dimensions;
}

static inline
uint8_t *EMD_Data(const EMData_t *p_data)
{
  assert_param(p_data != NULL);

  return p_data->p_payload;
}

static inline
uint16_t EMD_GetShape(const EMData_t *p_data, uint8_t dimension)
{
  assert_param(p_data != NULL);
  assert_param(dimension < p_data->dimensions);

  return p_data->shapes[dimension];
}

static inline
uint32_t EMD_GetElementsCount(const EMData_t *p_data)
{
  assert_param(p_data != NULL);
  register uint32_t element_count = 1U;

  for (uint8_t i=0; i<p_data->dimensions; ++i)
  {
    element_count *= p_data->shapes[i];
  }

  return element_count;
}

static inline
sys_error_code_t EMD_2dGetValueAt(const EMData_t *p_data, void *p_val, uint16_t d1_idx, uint16_t d2_idx)
{
  assert_param(p_data != NULL);
  assert_param(p_data->dimensions == 2);
  assert_param(d1_idx < p_data->shapes[0]);
  assert_param(d2_idx < p_data->shapes[1]);

  uint32_t val_pos = (p_data->shapes[1] * d1_idx) + d2_idx;
  uintptr_t val_addr = ((uintptr_t)p_data->p_payload) + (val_pos * EMD_GetElementSize(p_data));
  memcpy(p_val, (void*)val_addr, p_data->element_size);

  return SYS_NO_ERROR_CODE;}

static inline
uint8_t *EMD_2dDataAt(EMData_t *p_data, uint16_t d1_idx, uint16_t d2_idx)
{
  assert_param(p_data != NULL);
  assert_param(p_data->dimensions == 2);
  assert_param(d1_idx < p_data->shapes[0]);
  assert_param(d2_idx < p_data->shapes[1]);

  uint32_t val_pos = (p_data->shapes[1] * d1_idx) + d2_idx;
  uintptr_t val_addr = ((uintptr_t)p_data->p_payload) + (val_pos * EMD_GetElementSize(p_data));

  return (uint8_t*)val_addr;
}

static inline
sys_error_code_t EMD_1dGetValueAt(const EMData_t *p_data, void *p_val, uint16_t d1_idx)
{
  assert_param(p_data != NULL);
  assert_param(p_data->dimensions == 1);
  assert_param(d1_idx < p_data->shapes[0]);

  uintptr_t val_addr = ((uintptr_t)p_data->p_payload) + (d1_idx * EMD_GetElementSize(p_data));
  memcpy(p_val, (void*)val_addr, p_data->element_size);

  return SYS_NO_ERROR_CODE;
}

static inline
uint8_t *EMD_1dDataAt(EMData_t *p_data, uint16_t d1_idx)
{
  assert_param(p_data != NULL);
  assert_param(p_data->dimensions == 1);
  assert_param(d1_idx < p_data->shapes[0]);

  uintptr_t val_addr = ((uintptr_t)p_data->p_payload) + (d1_idx * EMD_GetElementSize(p_data));

  return (uint8_t*)val_addr;
}

#ifdef __cplusplus
extern }
#endif

#endif /* INC_SERVICES_EM_DATA_EM_DATA_FORTMAT_H_ */
