/**
  ******************************************************************************
  * @file    AI_MessagesDef.h
  * @author  STMicroelectronics - AIS - MCD Team
  * @version $Version$
  * @date    $Date$
  *
  * @brief   AI HAR task commands ID
  *
  * This file declares the commands ID for the AI_Task.
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
#ifndef INC_AIHARMESSAGESDEF_H_
#define INC_AIHARMESSAGESDEF_H_

#ifdef __cplusplus
extern "C" {
#endif

/* Exported constants --------------------------------------------------------*/
#define AI_CMD_ALLOC_DATA_BUFF           (0x01U)
#define AI_CMD_LOAD_MODEL                (0x02U)
#define AI_CMD_UNLOAD_MODEL              (0x03U)

#ifdef __cplusplus
}
#endif

#endif /* INC_AIHARMESSAGESDEF_H_ */
