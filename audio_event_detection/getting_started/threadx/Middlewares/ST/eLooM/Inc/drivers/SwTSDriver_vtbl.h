/**
 ******************************************************************************
 * @file    SwTSDriver_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 4.0.0
 * @date    Mar 21, 2022
 *
 * @brief   Virtual functions implemented by the driver.
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
#ifndef ELOOM_INC_DRIVERS_SWTSDRIVER_VTBL_H_
#define ELOOM_INC_DRIVERS_SWTSDRIVER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/**
 * @sa IDrvInit
 */
sys_error_code_t SwTSDriver_vtblInit(IDriver *_this, void *p_params);

/**
 * @sa IDrvStart
 */
sys_error_code_t SwTSDriver_vtblStart(IDriver *_this);

/**
 * @sa IDrvStop
 */
sys_error_code_t SwTSDriver_vtblStop(IDriver *_this);

/**
 *
 * @sa IDrvDoEnterPowerMode
 */
sys_error_code_t SwTSDriver_vtblDoEnterPowerMode(IDriver *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode);

/**
 * @sa IDrvReset
 */
sys_error_code_t SwTSDriver_vtblReset(IDriver *_this, void *p_params);

/**
 * @sa ITSDrvGetTimeStamp
 */
uint64_t SwTSDriver_vtblGetTimestamp(ITSDriver_t *_this);

#ifdef __cplusplus
}
#endif

#endif /* ELOOM_INC_DRIVERS_SWTSDRIVER_VTBL_H_ */
