/**
 ******************************************************************************
 * @file    systypes.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Sep 6, 2016
 * @brief   Common type declaration
 *
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2016 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#ifndef SYSTYPES_H_
#define SYSTYPES_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "stdbool.h"

/* redefine the boolean_t to use the standard C bool for backward compatibility */

#define boolean_t bool

#ifndef TRUE
#define TRUE true
#endif

#ifndef FALSE
#define FALSE false
#endif

typedef void (*tx_entry_function_t)(unsigned long nParam);

#ifdef __cplusplus
}
#endif


#endif /* SYSTYPES_H_ */
