/**
 ******************************************************************************
 * @file    DefDataBuilder_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    Jun 17, 2022
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
#ifndef DPU_DEFDATABUILDER_VTBL_H_
#define DPU_DEFDATABUILDER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

/* IDataBuilder_t virtual functions */
sys_error_code_t DefDB_vtblOnReset(IDataBuilder_t *_this, void *p_data_build_context);                                                                                                           ///< @sa IDataBuilder_Reset
sys_error_code_t DefDB_vtblOnNewInData(IDataBuilder_t *_this, EMData_t *p_target_data, const EMData_t *p_new_in_data, IDB_BuildStrategy_e build_strategy, DataBuffAllocator_f data_buff_alloc);  ///< @sa IDataBuilder_OnNewInData

#ifdef __cplusplus
}
#endif

#endif /* DPU_DEFDATABUILDER_VTBL_H_ */
