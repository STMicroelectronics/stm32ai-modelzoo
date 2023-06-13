/**
  ******************************************************************************
  * @file    MDFDriver_vtbl.h
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
#ifndef HSDCORE_INC_DRIVERS_MDFDRIVER_VTBL_H_
#define HSDCORE_INC_DRIVERS_MDFDRIVER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/**
  * @sa IDrvInit
  */
sys_error_code_t MDFDriver_vtblInit(IDriver *_this, void *p_params);

/**
  * @sa IDrvStart
  */
sys_error_code_t MDFDriver_vtblStart(IDriver *_this);

/**
  * @sa IDrvStop
  */
sys_error_code_t MDFDriver_vtblStop(IDriver *_this);

/**
  *
  * @sa IDrvDoEnterPowerMode
  */
sys_error_code_t MDFDriver_vtblDoEnterPowerMode(IDriver *_this, const EPowerMode active_power_mode,
                                                const EPowerMode new_power_mode);

/**
  * @sa IDrvReset
  */
sys_error_code_t MDFDriver_vtblReset(IDriver *_this, void *p_params);

#ifdef __cplusplus
}
#endif

#endif /* HSDCORE_INC_DRIVERS_MDFDRIVER_VTBL_H_ */
