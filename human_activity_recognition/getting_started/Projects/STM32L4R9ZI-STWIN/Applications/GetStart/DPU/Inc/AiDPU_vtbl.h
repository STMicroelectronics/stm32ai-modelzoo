/**
  ******************************************************************************
  * @file    AiDPU_vtbl.h
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
  
#ifndef DPU_INC_AIDPU_VTBL_H_
#define DPU_INC_AIDPU_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systp.h"
#include "services/systypes.h"
#include "services/syserror.h"


/* IDPU virtual functions */
  sys_error_code_t AiDPU_vtblProcess(IDPU *_this); /*!< @sa IDPU_Process */
  sys_error_code_t AiDPU_vtblInit(IDPU *_this); /*!< @sa IDPU_Init */



#ifdef __cplusplus
}
#endif

#endif /* DPU_INC_AIDPU_VTBL_H_ */
