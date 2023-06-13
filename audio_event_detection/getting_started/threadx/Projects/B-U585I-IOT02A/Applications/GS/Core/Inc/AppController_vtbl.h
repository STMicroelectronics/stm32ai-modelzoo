/**
 ******************************************************************************
 * @file    AppController_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
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
sys_error_code_t AppController_vtblOnCreateTask(AManagedTask *_this, tx_entry_function_t *pTaskCode, CHAR **pName, VOID **pStackStart, ULONG *pStackDepth, UINT *pPriority, UINT *pPreemptThreshold, ULONG *pTimeSlice, ULONG *pAutoStart, ULONG *pParams); ///< @sa AMTOnCreateTask
sys_error_code_t AppController_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode); /*!< @sa AMTDoEnterPowerMode */
sys_error_code_t AppController_vtblHandleError(AManagedTask *_this, SysEvent error); /*!< @sa AMTHandleError */
sys_error_code_t AppController_vtblOnEnterTaskControlLoop(AManagedTask *this); ///< @sa AMTOnEnterTaskControlLoop

/* AManagedTaskEx virtual functions */
sys_error_code_t AppController_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode active_power_mode); /*!< @sa AMTExForceExecuteStep */
sys_error_code_t AppController_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode); /*!< @sa AMTExOnEnterPowerMode */

IEventListener* AppController_getEventListenerIF(AppController_t *_this);

/* IListener virtual functions */
sys_error_code_t AppController_vtblOnStatusChange(IListener *_this);                                          /*!< @sa IListenerOnStatusChange */

/* IEventListener virtual functions */
void AppController_vtblSetOwner(IEventListener *_this, void *p_owner);                                        /*!< @sa IEventListenerSetOwner */
void *AppController_vtblGetOwner(IEventListener *_this);                                                      /*!< @sa IEventListenerGetOwner */

/* IEventListener virtual functions */
sys_error_code_t AppController_vtblOnNewDataReady(IEventListener *_this, const DataEvent_t *p_evt);           /*!< @sa IDataEventListenerOnNewDataReady */

#ifdef __cplusplus
}
#endif

#endif /* INC_APPCONTROLLER_VTBL_H_ */
