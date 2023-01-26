/**
  ******************************************************************************
  * @file   IDPU.c
  * @author  SRA - MCD
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
  
#include "IDPU.h"
#include "IDPUVtbl.h"


// GCC requires one function forward declaration in only one .c source
// in order to manage the inline.
// See also http://stackoverflow.com/questions/26503235/c-inline-function-and-gcc
#if defined (__GNUC__) || defined (__ICCARM__)
extern sys_error_code_t IDPU_Init(IDPU *_this);
extern sys_error_code_t IDPU_AttachToSensor(IDPU *_this, ISourceObservable *s, void *buffer);
extern sys_error_code_t IDPU_DetachFromSensor(IDPU *_this, ISourceObservable *s);
extern sys_error_code_t IDPU_AttachInputDPU(IDPU *_this, IDPU *in_adpu, void *buffer);
extern sys_error_code_t IDPU_DetachFromDPU(IDPU *_this);
extern sys_error_code_t IDPU_DispatchEvents(IDPU *_this,  ProcessEvent *pxEvt);
extern sys_error_code_t IDPU_RegisterNotifyCallback(IDPU *_this, DPU_ReadyToProcessCallback_t callback, void *p_param);
extern sys_error_code_t IDPU_Process(IDPU *_this);
#endif
