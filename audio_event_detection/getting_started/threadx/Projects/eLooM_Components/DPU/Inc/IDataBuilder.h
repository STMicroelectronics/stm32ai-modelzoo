/**
 ******************************************************************************
 * @file    IDataBuilder.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 1.0.0
 * @date    May 20, 2022
 *
 * @brief   Interface to build an input data (::EMData_t) for a DPU.
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
#ifndef DPU_IDATABUILDER_H_
#define DPU_IDATABUILDER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/em_data_format.h"


#define SYS_IDB_NO_ERROR_CODE                                  0
#ifndef SYS_IDB_BASE_ERROR_CODE
#define SYS_IDB_BASE_ERROR_CODE                                1
#endif
#define SYS_IDB_DATA_NOT_READY_ERROR_CODE                      SYS_IDB_BASE_ERROR_CODE + 1
#define SYS_IDB_DATA_READY_ERROR_CODE                          SYS_IDB_BASE_ERROR_CODE + 2
#define SYS_IDB_UNSUPPORTED_STRATEGY_ERROR_CODE                SYS_IDB_BASE_ERROR_CODE + 3
#define SYS_IDB_ERROR_CODE_COUNT                               3

/**
 * Specifies the build strategy. //TODO: STF - to specify more!!
 */
typedef enum _IDB_BuildStrategy
{
  E_IDB_NO_DATA_LOSS,    /**< E_IDB_NODATA_LOSS */
  E_IDB_SKIP_DATA,       /**< E_IDB_SKIP_DATA */
}IDB_BuildStrategy_e;

/**
 * Create  type name for struct _IDataBuilder_t.
 */
typedef struct _IDataBuilder IDataBuilder_t;

/**
 * Allocator used by the data builder to allocate a new buffer in the build context.
 * It is used during the new input data processing when all these conditions are true:
 * - The target data is ready.
 * - There are element in the input data not processed.
 * - The build strategy is E_IDB_NO_DATA_LOSS.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param p_data_build_context [IN] specifies a context for the data build operation. This parameter is not used
 *                             by the data builders IF, but is for exclusive use of the caller.
 * @return a new data buffer if success, NULL otherwise.
 */
typedef uint8_t* (*DataBuffAllocator_f)(IDataBuilder_t *_this, void *p_data_build_context);


/* Public API declaration */
/**************************/

/**
 * Reset the interface. Called at the beginning of a new data creation.
 * The object reset its internal state to get ready to receive new input data
 * used to build the target data.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param p_data_build_context [IN] specifies a build context. It is provide by the object that uses the data builder interface.
 *                                  The interface must use this context when it calls the data ready callback.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IDataBuilder_Reset(IDataBuilder_t *_this, void *p_data_build_context);

/**
 *
 * @param _this  [IN] specifies a pointer to the object.
 * @param p_target_data [IN] specify the target data to build.
 * @param p_new_in_data [IN] specifies a new input data used to build the target data.
 * @param build_strategy [IN] specifies a build strategy.
 * @param data_buff_alloc [IN] specifies an allocator function.
 * @return  - IDB_DATA_READY_ERROR_CODE if the builder has finished its contribution for the new target data.
 *          - IDB_DATA_NOT_READY_ERROR_CODE if the builder has not finished its contribution for the new target data, and it needs more new input dta.
 */
static inline sys_error_code_t IDataBuilder_OnNewInData(IDataBuilder_t *_this, EMData_t *p_target_data, const EMData_t *p_new_in_data, IDB_BuildStrategy_e build_strategy, DataBuffAllocator_f data_buff_alloc);


/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* DPU_IDATABUILDER_H_ */
