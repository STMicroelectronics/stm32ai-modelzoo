/**
  ******************************************************************************
  * @file    ISensorLL_vtbl.h
  * @author  SRA - MCD
  * @brief
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

#ifndef INCLUDE_ISENSORLL_VTBL_H_
#define INCLUDE_ISENSORLL_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/**
  * Create a type name for ISensorLL_vtbl.
  */
typedef struct _ISensorLL_vtbl ISensorLL_vtbl;


struct _ISensorLL_vtbl
{
  sys_error_code_t (*SensorReadReg)(ISensorLL_t *_this, uint16_t reg, uint8_t *data, uint16_t len);
  sys_error_code_t (*SensorWriteReg)(ISensorLL_t *_this, uint16_t reg, const uint8_t *data, uint16_t len);
  sys_error_code_t (*SensorSyncModel)(ISensorLL_t *_this);
};


struct _ISensorLL_t
{
  /**
    * Pointer to the virtual table for the class.
    */
  const ISensorLL_vtbl *vptr;
};


// Inline functions definition
// ***************************
static inline sys_error_code_t ISensorReadReg(ISensorLL_t *_this, uint16_t reg, uint8_t *data, uint16_t len)
{
  return _this->vptr->SensorReadReg(_this, reg, data, len);
}

static inline sys_error_code_t ISensorWriteReg(ISensorLL_t *_this, uint16_t reg, const uint8_t *data, uint16_t len)
{
  return _this->vptr->SensorWriteReg(_this, reg, data, len);
}

static inline sys_error_code_t ISensorSyncModel(ISensorLL_t *_this)
{
  return _this->vptr->SensorSyncModel(_this);
}

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISENSORLL_VTBL_H_ */
