/**
  ******************************************************************************
  * @file    I2CMasterDriver_vtbl.h
  * @author  SRA - MCD
  * @brief   ::I2CMAsterDriver_t virtual function declaration
  *
  * This file declare all the virtual function overridden by the class.
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
  *
  *
  ******************************************************************************
  */
#ifndef INCLUDE_DRIVERS_I2CMASTERDRIVER_VTBL_H_
#define INCLUDE_DRIVERS_I2CMASTERDRIVER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/**
  * @sa IDrvInit
  */
sys_error_code_t I2CMasterDriver_vtblInit(IDriver *_this, void *p_params);

/**
  * @sa IDrvStart
  */
sys_error_code_t I2CMasterDriver_vtblStart(IDriver *_this);

/**
  * @sa IDrvStop
  */
sys_error_code_t I2CMasterDriver_vtblStop(IDriver *_this);

/**
  *
  * @sa IDrvDoEnterPowerMode
  */
sys_error_code_t I2CMasterDriver_vtblDoEnterPowerMode(IDriver *_this, const EPowerMode active_power_mode,
                                                      const EPowerMode new_power_mode);

/**
  * @sa IDrvReset
  */
sys_error_code_t I2CMasterDriver_vtblReset(IDriver *_this, void *p_params);

/**
  * @sa IIODrvWrite
  */
sys_error_code_t I2CMasterDriver_vtblWrite(IIODriver *_this, uint8_t *p_data_buffer, uint16_t data_size,
                                           uint16_t channel);

/**
  * @sa IIODrvRead
  */
sys_error_code_t I2CMasterDriver_vtblRead(IIODriver *_this, uint8_t *p_data_buffer, uint16_t data_size,
                                          uint16_t channel);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_DRIVERS_I2CMASTERDRIVER_VTBL_H_ */
