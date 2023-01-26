/**
 ******************************************************************************
 * @file    AppController_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 *********************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *********************************************************************************
 */
#ifndef INC_APPCONTROLLER_VTBL_H_
#define INC_APPCONTROLLER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


/* AManagedTask virtual functions */
sys_error_code_t AppController_vtblHardwareInit(AManagedTask *_this, void *p_params); /*!< @sa AMTHardwareInit */
sys_error_code_t AppController_vtblOnCreateTask(AManagedTask *_this, TaskFunction_t *p_task_code, const char **p_name, unsigned short *p_stack_depth, void **p_params, UBaseType_t *p_priority); /*!< @sa AMTOnCreateTask */
sys_error_code_t AppController_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode); /*!< @sa AMTDoEnterPowerMode */
sys_error_code_t AppController_vtblHandleError(AManagedTask *_this, SysEvent error); /*!< @sa AMTHandleError */
sys_error_code_t AppController_vtblOnEnterTaskControlLoop(AManagedTask *this); ///< @sa AMTOnEnterTaskControlLoop

/* AManagedTaskEx virtual functions */
sys_error_code_t AppController_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode active_power_mode); /*!< @sa AMTExForceExecuteStep */
sys_error_code_t AppController_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode); /*!< @sa AMTExOnEnterPowerMode */

/* IListener virtual functions */
sys_error_code_t ACProcEvtListener_vtblOnStatusChange(IListener *_this);                                          ///< @sa IListenerOnStatusChange
/* IEventListener virtual functions */
void ACProcEvtListener_vtblSetOwner(IEventListener *_this, void *pxOwner);                                        ///< @sa IEventListenerSetOwner
void *ACProcEvtListener_vtblGetOwner(IEventListener *_this);                                                      ///< @sa IEventListenerGetOwner
/* IEventListener virtual functions */
sys_error_code_t ACProcEvtListener_vtblOnProcessedDataReady(IEventListener *_this, const ProcessEvent *pxEvt);   ///< @sa ISensorEventListenerOnNewDataReady

#ifdef __cplusplus
}
#endif

#endif /* INC_APPCONTROLLER_VTBL_H_ */
