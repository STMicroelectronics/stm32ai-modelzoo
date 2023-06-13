/**
  ******************************************************************************
  * @file    AI_DPU_vtbl.h
  * @author  STMicroelectronics - AIS - MCD Team
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
  
#ifndef AI_DPU_VTBL_H_
#define AI_DPU_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systp.h"
#include "services/systypes.h"
#include "services/syserror.h"

/* IDPU virtual functions */
sys_error_code_t AI_DPU_vtblProcess(IDPU2_t *_this, EMData_t in_data, EMData_t out_data); /*!< @sa IDPU2_Process */

#ifdef __cplusplus
}
#endif

#endif /* AI_DPU_VTBL_H_ */
