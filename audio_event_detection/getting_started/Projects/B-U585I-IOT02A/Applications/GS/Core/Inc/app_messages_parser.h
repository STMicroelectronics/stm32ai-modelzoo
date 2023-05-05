/**
  ******************************************************************************
  * @file    app_messages_parser.h
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
#ifndef APP_REPORT_PARSER_H_
#define APP_REPORT_PARSER_H_

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "services/syserror.h"
#include "services/ISourceObservable.h"
#include "services/ISourceObservable_vtbl.h"
#include "IDPU2.h"
#include "IDPU2_vtbl.h"
#include "IDataBuilder.h"
#include "IDataBuilder_vtbl.h"

/* Exported types ------------------------------------------------------------*/
typedef union _AppMsg{
  uint8_t msg_id;

  //--------------------------------------------------------------------------------
  //  internalReport 0A (MCU) - generic message
  //--------------------------------------------------------------------------------

  struct genericMsg_t
  {
    uint8_t   msg_id;                               /* Message ID = 0x0A (10) */
    uint8_t   sparam;                               /* optional small parameter */
    uint16_t  cmd_id;                               /* command ID */
    uint32_t  param;                                /* optional parameter. */
  } generic_msg;

  //--------------------------------------------------------------------------------
  //  CtrlMessage 0x14
  //--------------------------------------------------------------------------------

  struct CtrlMessage_t
  {
    uint8_t  msg_id;                                /* Message ID = 0x14 (20) */
    uint8_t  sparam;                                /* small parameter */
    uint16_t cmd_id;                                /* AppController task command ID */
    uint32_t param;                                 /* command parameter */
    uint8_t data[32];                               /* CLI data buff. Used only with the CMD_ID CTRL_CMD_NEW_CHAR*/
  } ctrl_msg;

  //--------------------------------------------------------------------------------
  //  DPU_MESSAGE_ID_ATTACH_TO_DPU 0x12 | DPU_MESSAGE_ID_ATTACH_TO_DATA_SRC 0x13
  //--------------------------------------------------------------------------------

  struct DPU_MSG_Attach_t
  {
    uint8_t  msg_id;                                /* Message ID = 0x12, 0x13 */
    uint8_t padding[3];                             /* reserved */
    IDataBuilder_t *p_data_builder;                 /* data builder object */
    IDB_BuildStrategy_e build_strategy;             /* build strategy */
    union
    {
      ISourceObservable *p_data_source;             /* data source */
      IDPU2_t *p_next_dpu;                          /* next DPU in the DPU chain */
    }p_data_obj;
  } dpu_msg_attach;

  //--------------------------------------------------------------------------------
  //  DPU_MESSAGE_ID_DETACH_FROM_DPU 0x14 | DPU_MESSAGE_ID_DETACH_FROM_DATA_SRC 0x15
  //--------------------------------------------------------------------------------

  struct DPU_MSG_Detach_t
  {
    uint8_t  msg_id;                                /* Message ID = 0x14, 0x15 */
    bool release_data_builder;                      /* if true the memory of related data source object is released (SysFree). */
    uint8_t padding[2];                             /* reserved */
    ISourceObservable *p_data_source;               /* data source. Not used if msg_id == DPU_MESSAGE_ID_DETACH_FROM_DPU */
  } dpu_msg_detach;

  //--------------------------------------------------------------------------------
  //  DPU_MESSAGE_ID_ADD_LISTENER 0x16 | DPU_MESSAGE_ID_REMOVE_LISTENER 0x17
  //--------------------------------------------------------------------------------

  struct DPU_MSG_AddRemoveListener_t
  {
    uint8_t  msg_id;                                /* Message ID = 0x16, 0x17 */
    uint8_t padding[3];                             /* reserved */
    IDataEventListener_t *p_listener;               /* data event listener object */
  } dpu_msg_add_remove_listener;

  //--------------------------------------------------------------------------------
  //  DPU_MESSAGE_ID_SET_IN_BUFFER 0x18 | DPU_MESSAGE_ID_SET_OUT_BUFFER 0x19
  //--------------------------------------------------------------------------------
  struct DPU_MSG_SetBuffer_t
  {
    uint8_t msg_id;                                /* Message ID = 0x18, 0x19 */
    uint8_t reserved[3];                           /* reserved. */
    uint8_t *p_buffer;                             /* data buffer. */
    uint32_t buffer_size;                          /* size in byte of the buffer. */
  }dpu_msg_set_buff;

  //--------------------------------------------------------------------------------
  //  DPU_MESSAGE_ID_CMD 0xA0
  //--------------------------------------------------------------------------------
  struct DPU_MSG_Cmd_t
  {
    uint8_t msg_id;                                /* Message ID = 0xA0 */
    uint8_t cmd_id;                                /* command ID. */
    uint8_t reserved[2];                           /* reserved. */
  }dpu_msg_cmd;

  //--------------------------------------------------------------------------------
  //  internalReport (MCU)
  //--------------------------------------------------------------------------------

  struct internalReportFE_t
  {
    uint8_t  msg_id;                                 /* Message ID = 0xFE */
    uint8_t  data;                                   /* reserved. It can be ignored */
  } internalReportFE;

}AppMsg_t;

/* Exported constants --------------------------------------------------------*/
#define APP_MESSAGE_ID_GENERIC                          0x0A  /** Message ID used for the messages generic message with two parameters:
                                                                * - sparam specifies an 8-bit parameter (s stands for small).
                                                                * - param specifies a 32-bit parameters.
                                                                */
#define APP_MESSAGE_ID_AI                               APP_MESSAGE_ID_GENERIC  ///< Previously 0x11
#define APP_MESSAGE_ID_PRE_PROC                         APP_MESSAGE_ID_GENERIC  ///< Previously 0x13
#define APP_MESSAGE_ID_CTRL                             0x11  ///< Message ID used for the messages class of AppController task.
#define DPU_MESSAGE_ID_ATTACH_TO_DPU                    0x12  ///< Message ID used for the messages class DPU attach to DPU.
#define DPU_MESSAGE_ID_ATTACH_TO_DATA_SRC               0x13  ///< Message ID used for the messages class DPU attach to data source.
#define DPU_MESSAGE_ID_DETACH_FROM_DPU                  0x14  ///< Message ID used for the messages class DPU detach from to DPU.
#define DPU_MESSAGE_ID_DETACH_FROM_DATA_SRC             0x15  ///< Message ID used for the messages class DPU detach from data source.
#define DPU_MESSAGE_ID_ADD_LISTENER                     0x16  ///< Message ID used for the messages class DPU add listener.
#define DPU_MESSAGE_ID_REMOVE_LISTENER                  0x17  ///< Message ID used for the messages class DPU remove listener.
#define DPU_MESSAGE_ID_SET_IN_BUFFER                    0x18  ///< Message ID used for the messages class DPU set input data buffer.
#define DPU_MESSAGE_ID_SET_OUT_BUFFER                   0x19  ///< Message ID used for the messages class DPU set output data buffer.
#define DPU_MESSAGE_ID_CMD                              0xA0  ///< Message ID used for the messages class DPU command.
#define APP_REPORT_ID_FORCE_STEP                        0xFE  ///< Special ID used by the INIT task to force the execution of ManagedTaskEx step.

/* Exported functions --------------------------------------------------------*/
/**
 * Get the size of the report with a specified ID
 *
 * @param message_id [IN] specifies a the id of the message
 * @return the size of the message with the specified ID or 0 if the message ID is not valid.
 */
uint16_t AppMsgGetSize(uint8_t message_id);


#ifdef __cplusplus
}
#endif


#endif /* APP_REPORT_PARSER_H_ */
