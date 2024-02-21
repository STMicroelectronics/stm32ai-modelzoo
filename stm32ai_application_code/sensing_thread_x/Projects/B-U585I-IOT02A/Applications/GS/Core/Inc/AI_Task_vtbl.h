/**
  ******************************************************************************
  * @file    AI_Task_vtbl.h
  * @author  STMicroelectronics - AIS - MCD Team
  * @version $Version$
  * @date    $Date$
  *
  * @brief
  *
  * <DESCRIPTIOM>
  *
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef SRC_AI_TASK_VTBL_H_
#define SRC_AI_TASK_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

/* Exported functions --------------------------------------------------------*/
/* AManagedTask virtual functions */
sys_error_code_t AI_Task_vtblOnCreateTask(AManagedTask *_this, tx_entry_function_t *pTaskCode, CHAR **pName, VOID **pStackStart, ULONG *pStackDepth, UINT *pPriority, UINT *pPreemptThreshold, ULONG *pTimeSlice, ULONG *pAutoStart, ULONG *pParams); ///< @sa AMTOnCreateTask

/* AManagedTaskEx virtual functions */

#ifdef __cplusplus
}
#endif

#endif /* SRC_AI_TASK_VTBL_H_ */
