/**
 ******************************************************************************
 * @file    config.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
 * @brief   Configure the getting started functionality
 *
 * Each logic module of the application should define a DEBUG control byte
 * used to turn on/off the log for the module.
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

#ifndef CONFIG_H_
#define CONFIG_H_

#ifdef __cplusplus
extern "C" {
#endif

#define CTRL_AI_CLASS_DISTRIBUTION (1U)
#define CTRL_AI_CLASS_IDX          (2U)
#define CTRL_AI_GRAV_ROT_SUPPR     (3U)
#define CTRL_AI_GRAV_ROT           (4U)
#define CTRL_AI_BYPASS             (5U)

#include "ai_model_config.h"
#ifndef CTRL_AI_HW_SELECT
#define CTRL_AI_HW_SELECT                              STWIN1B
#endif

#ifndef CTRL_SEQUENCE
#define CTRL_SEQUENCE                          {CTRL_CMD_PARAM_AI,0}
#endif

#ifndef CTRL_X_CUBE_AI_MODE_NAME
#define CTRL_X_CUBE_AI_MODE_NAME                       "X-CUBE-AI HAR"
#endif
#ifndef CTRL_X_CUBE_AI_MODE_NETWORK_MODEL_NAME
#define CTRL_X_CUBE_AI_MODE_NETWORK_MODEL_NAME         "network"
#endif

#ifndef CTRL_X_CUBE_AI_MODE_NB_OUTPUT
#define CTRL_X_CUBE_AI_MODE_NB_OUTPUT                  (1U)
#endif
#ifndef CTRL_X_CUBE_AI_MODE_OUTPUT_1
#define CTRL_X_CUBE_AI_MODE_OUTPUT_1                   CTRL_AI_CLASS_DISTRIBUTION
#endif
#ifndef CTRL_X_CUBE_AI_MODE_CLASS_NUMBER
#define CTRL_X_CUBE_AI_MODE_CLASS_NUMBER               (4U)
#endif
#ifndef CTRL_X_CUBE_AI_MODE_CLASS_LIST
#define CTRL_X_CUBE_AI_MODE_CLASS_LIST                 {"Stationary","Walking","Jogging","Biking"}
#endif
#ifndef CTRL_X_CUBE_AI_SENSOR_NAME
#define CTRL_X_CUBE_AI_SENSOR_NAME                     "ism330dhcx"
#endif
#ifndef CTRL_X_CUBE_AI_SENSOR_TYPE
#define CTRL_X_CUBE_AI_SENSOR_TYPE                     (COM_TYPE_ACC)
#endif
#ifndef CTRL_X_CUBE_AI_SENSOR_ODR
#define CTRL_X_CUBE_AI_SENSOR_ODR                      (26.0F)
#endif
#ifndef CTRL_X_CUBE_AI_SENSOR_FS
#define CTRL_X_CUBE_AI_SENSOR_FS                       (4.0F)
#endif
#ifndef CTRL_X_CUBE_AI_NB_SAMPLES
#define CTRL_X_CUBE_AI_NB_SAMPLES                      (20U)
#endif
#ifndef CTRL_X_CUBE_AI_PREPROC
#define CTRL_X_CUBE_AI_PREPROC                          CTRL_AI_GRAV_ROT_SUPPR
#endif


#ifdef __cplusplus
}
#endif

#endif /* CONFIG_H_ */

