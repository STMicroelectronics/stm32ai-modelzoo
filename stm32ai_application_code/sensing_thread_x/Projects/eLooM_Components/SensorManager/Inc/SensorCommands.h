/**
  ******************************************************************************
  * @file    SensorCommands.h
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
#ifndef SENSORCOMMANDS_H_
#define SENSORCOMMANDS_H_

#ifdef __cplusplus
extern "C" {
#endif

// Command ID. These are all commands supported by a sensor task.
#define SENSOR_CMD_ID_INIT          ((uint16_t)0x0001)              ///< START command ID.
#define SENSOR_CMD_ID_SET_ODR       ((uint16_t)0x0002)              ///< SET ODR command ID.
#define SENSOR_CMD_ID_SET_FS        ((uint16_t)0x0003)              ///< SET FS command ID.
#define SENSOR_CMD_ID_SET_FIFO_WM   ((uint16_t)0x0006)              ///< SET Fifo WM command ID.
#define SENSOR_CMD_ID_ENABLE        ((uint16_t)0x0004)              ///< ENABLE command ID.
#define SENSOR_CMD_ID_DISABLE       ((uint16_t)0x0005)              ///< DISABLE command ID.

#ifdef __cplusplus
}
#endif

#endif /* SENSORCOMMANDS_H_ */
