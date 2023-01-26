/**
 ******************************************************************************
 * @file    app_messages_parser.h
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
#ifndef APP_REPORT_PARSER_H_
#define APP_REPORT_PARSER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/syserror.h"

#define APP_MESSAGE_ID_AI                               0x11  ///< Message ID used for the messages class of AI task.
#define APP_MESSAGE_ID_CTRL                             0x14  ///< Message ID used for the messages class of AppController task.
#define APP_REPORT_ID_FORCE_STEP                        0xFE  ///< Special ID used by the INIT task to force the execution of ManagedTaskEx step.

typedef union _APPReport{
  uint8_t msgId;
  struct AIMessage_t
  {
    uint8_t  msgId;                                 /* Message ID */
    uint8_t  sparam;                                /* small parameter */
    uint16_t cmd_id;                                /* AI task command ID */
    uint32_t param;                                 /* command parameter */
  } aiMessage;
  struct CtrlMessage_t
  {
    uint8_t  msgId;                                 /* Message ID */
    uint8_t  sparam;                                /* small parameter */
    uint16_t cmd_id;                                /* AppController task command ID */
    uint32_t param;                                 /* command parameter */
    uint8_t data[64];                               /* CLI data buff. Used only with the CMD_ID */
  } ctrlMessage;
  struct internalReportFE_t
  {
    uint8_t  reportId;                               /* Report ID */
    uint8_t  data;                                   /* reserved. It can be ignored */
  } internalReportFE;
}APPReport;

#ifdef __cplusplus
}
#endif


#endif /* APP_REPORT_PARSER_H_ */
