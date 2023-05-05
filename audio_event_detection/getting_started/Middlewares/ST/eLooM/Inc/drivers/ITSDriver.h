/**
 ******************************************************************************
 * @file    ITSDriver.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 4.0.0
 * @date    Mar 15, 2022
 *
 * @brief   Timestamp Driver interface.
 *
 * Timestamp driver interface extends the basic ::IDriver interface with
 * get timestamp operation.
 *
 * At this level the timestamp is the raw value of the counter of the timer
 * used to implement the driver.
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

#ifndef ELOOM_INC_DRIVERS_ITSDRIVER_H_
#define ELOOM_INC_DRIVERS_ITSDRIVER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "drivers/IDriver.h"


/**
 * Create  type name for _ITSDriver_t.
 */
typedef struct _ITSDriver_t ITSDriver_t;


/** Public API declaration */
/***************************/

/**
 * Get the raw value of the counter of the timer used to implement the driver.
 *
 * @param _this [IN] specifies a pointer to a ::ITSDriver_t object.
 * @return a 32 bit value of the
 */
static inline uint64_t ITSDrvGetTimeStamp(ITSDriver_t *_this);


/** Inline functions definition */
/********************************/


#ifdef __cplusplus
}
#endif

#endif /* ELOOM_INC_DRIVERS_ITSDRIVER_H_ */
