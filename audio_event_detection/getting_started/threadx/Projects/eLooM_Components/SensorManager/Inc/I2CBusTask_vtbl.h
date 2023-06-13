/**
  ******************************************************************************
  * @file    I2CBusTask_vtbl.h
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
#ifndef I2CBUSTASK_VTBL_H_
#define I2CBUSTASK_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/* AManagedTask virtual functions */
sys_error_code_t I2CBusTask_vtblHardwareInit(AManagedTask *_this, void *pParams); ///< @sa AMTHardwareInit
sys_error_code_t I2CBusTask_vtblOnCreateTask(AManagedTask *_this, tx_entry_function_t *pvTaskCode, CHAR **pcName,
                                             VOID **pvStackStart, ULONG *pnStackSize, UINT *pnPriority, UINT *pnPreemptThreshold, ULONG *pnTimeSlice,
                                             ULONG *pnAutoStart, ULONG *pnParams); ///< @sa AMTOnCreateTask
sys_error_code_t I2CBusTask_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode eActivePowerMode,
                                                 const EPowerMode eNewPowerMode); ///< @sa AMTDoEnterPowerMode
sys_error_code_t I2CBusTask_vtblHandleError(AManagedTask *_this, SysEvent xError); ///< @sa AMTHandleError
sys_error_code_t I2CBusTask_vtblOnEnterTaskControlLoop(AManagedTask *this); ///< @sa AMTOnEnterTaskControlLoop

/* AManagedTaskEx virtual functions */
sys_error_code_t I2CBusTask_vtblForceExecuteStep(AManagedTaskEx *_this,
                                                 EPowerMode eActivePowerMode); ///< @sa AMTExForceExecuteStep
sys_error_code_t I2CBusTask_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode eActivePowerMode,
                                                 const EPowerMode eNewPowerMode); ///< @sa AMTExOnEnterPowerMode

/* IBus virtual functions */
sys_error_code_t I2CBusTask_vtblCtrl(IBus *_this, EBusCtrlCmd eCtrlCmd, uint32_t nParams); ///< @sa IBusCtr
sys_error_code_t I2CBusTask_vtblConnectDevice(IBus *_this, ABusIF *pxBusIF);  ///< @sa IBusConnectDevice
sys_error_code_t I2CBusTask_vtblDisconnectDevice(IBus *_this, ABusIF *pxBusIF);  ///< @sa IbusDisconnectDevice

#ifdef __cplusplus
}
#endif

#endif /* I2CBUSTASK_VTBL_H_ */
