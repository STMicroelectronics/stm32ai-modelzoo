/**
  ******************************************************************************
  * @file    ISensorMlc_vtbl.h
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

#ifndef INCLUDE_ISENSORMLC_VTBL_H_
#define INCLUDE_ISENSORMLC_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/**
  * Create a type name for ISensorMlc_vtbl.
  */
typedef struct _ISensorMlc_vtbl ISensorMlc_vtbl;


struct _ISensorMlc_vtbl
{
  sys_error_code_t (*SensorMlcLoadUcf)(ISensorMlc_t *_this, uint32_t size, const char *ucf);
  boolean_t (*SensorMlcIsEnabled)(ISensorMlc_t *_this);
};


struct _ISensorMlc_t
{
  /**
    * Pointer to the virtual table for the class.
    */
  const ISensorMlc_vtbl *vptr;
};


// Inline functions definition
// ***************************
static inline sys_error_code_t ISensorMlcLoadUcf(ISensorMlc_t *_this, uint32_t size, const char *ucf)
{
  return _this->vptr->SensorMlcLoadUcf(_this, size, ucf);
}

static inline boolean_t ISensorMlcIsEnabled(ISensorMlc_t *_this)
{
  return _this->vptr->SensorMlcIsEnabled(_this);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISENSORMLC_VTBL_H_ */
