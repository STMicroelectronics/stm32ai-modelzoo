/**
 ******************************************************************************
 * @file    AIMessagesDef.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
 *
 * @brief   AI task commands ID
 *
 * This file declares the commands ID for the AITask.
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
#ifndef INC_AIMESSAGESDEF_H_
#define INC_AIMESSAGESDEF_H_

#ifdef __cplusplus
extern "C" {
#endif

#define AI_CMD_NEW_DATA_READY            (0x01U)
#define AI_CMD_STOP_PROCESSING           (0x02U)
#define AI_CMD_CONNECT_TO_SENSOR         (0x03U)
#define AI_CMD_DETACH_FROM_SENSOR        (0x05U)
#define AI_CMD_ADD_DPU_LISTENER          (0x06U)
#define AI_CMD_REMOVE_DPU_LISTENER       (0x07U)
#define AI_CMD_SUSPEND_DPU               (0x08U)
#define AI_CMD_RESUME_DPU                (0x09U)
#define AI_CMD_LOAD_MODEL                (0x0AU)
#define AI_CMD_RELEASE_MODEL             (0x0BU)

#ifdef __cplusplus
}
#endif

#endif /* INC_AIMESSAGESDEF_H_ */
