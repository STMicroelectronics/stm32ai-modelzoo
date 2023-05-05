/**
 ******************************************************************************
 * @file    DataEventSrc_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    May 13, 2022
 *
 * @brief
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef EMDATA_INC_EVENTS_DATAEVENTSRC_VTBL_H_
#define EMDATA_INC_EVENTS_DATAEVENTSRC_VTBL_H_

/* IEventSrc virtual functions */

sys_error_code_t DataEventSrc_vtblSendEvent(const IEventSrc *_this, const IEvent *p_event, void *p_params); ///<< @sa IEventSrcSendEvent


#endif /* EMDATA_INC_EVENTS_DATAEVENTSRC_VTBL_H_ */
