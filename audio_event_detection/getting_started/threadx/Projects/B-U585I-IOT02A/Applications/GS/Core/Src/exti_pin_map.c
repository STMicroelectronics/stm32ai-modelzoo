/**
 ******************************************************************************
 * @file    exti_pin_map.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
 * @brief   Application level file. It defines the PIN to callback
 *          mapping function for the external interrupt.
 *
 * TODO - insert here the file description
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

#include "drivers/EXTIPinMap.h"

// Forward function declaration.
void ISM330DHCXTask_EXTI_Callback(uint16_t nPin);

EXTI_BEGIN_P2F_MAP()

  EXTI_P2F_MAP_ENTRY(GPIO_PIN_11, ISM330DHCXTask_EXTI_Callback)

EXTI_END_P2F_MAP()

