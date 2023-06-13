/**
  ******************************************************************************
  * @file    PreProc_MessagesDef.h
  * @author  STMicroelectronics - AIS - MCD Team
  * @version $Version$
  * @date    $Date$
  *
  * @brief   PreProc task commands ID
  *
  * This file declares the commands ID for the PreProc_Task.
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
#ifndef INC_PREPROC_MESSAGESDEF_H_
#define INC_PREPROC_MESSAGESDEF_H_

#ifdef __cplusplus
extern "C" {
#endif

/* Exported constants --------------------------------------------------------*/
#define PREPROC_CMD_STOP_PROCESSING           (0x02U)
#define PREPROC_CMD_SET_IN_BUFF               (0x05U) /*!< msg.param = input_signals_count, valid value are [0..0xFFFFFFFF] */
#define PREPROC_CMD_SET_SPECTROGRAM_TYPE      (0x06U) /*!< msg.param = input_signals_count, valid value are [0..0xFFFFFFFF] */

#ifdef __cplusplus
}
#endif

#endif /* INC_PREPROC_MESSAGESDEF_H_ */
