/**
 ********************************************************************************
 * @file    DProcessTask1MessagesDef.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 1.0.0
 * @date    Aug 1, 2022
 *
 * @brief
 *
 * <ADD_FILE_DESCRIPTION>
 *
 ********************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ********************************************************************************
 */
#ifndef CORE_INC_DPROCESSTASK1MESSAGESDEF_H_
#define CORE_INC_DPROCESSTASK1MESSAGESDEF_H_

#ifdef __cplusplus
extern "C" {
#endif

#define DPT1_CMD_SUSPEND_DPU               (0x01U)
#define DPT1_CMD_RESUME_DPU                (0x02U)
#define DPT1_CMD_RESET_DPU                 (0x03U)
#define DPT1_CMD_NEW_IN_DATA_READY         (0x04U)
#define DPT1_CMD_STOP_PROCESSING           (0x05U)

#ifdef __cplusplus
}
#endif

#endif /* CORE_INC_DPROCESSTASK1MESSAGESDEF_H_ */
