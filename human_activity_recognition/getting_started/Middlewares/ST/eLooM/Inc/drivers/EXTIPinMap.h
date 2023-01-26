/**
 ******************************************************************************
 * @file    EXTIPinMap.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Dec 8, 2016
 * @brief   External Interrupt callback declaration.
 *
 * This file declares a set of macro that the application use to define the
 * pin to callback map for the external interrupt.
 *
 * Each entry has two values that are:
 * - GPIO pin.
 * - Callback function.
 *
 * To access the map from an application source file:
 * - Include the EXTIPinMap.h
 * - use the EXTI_DECLARE_PIN2F_MAP() macro to declare the map.
 * - use the EXTI_GET_PIN2F_MAP() to get a pointer to the first element
 *   of the map.
 *
 * The application has the responsibility to define the map according to the
 * PIN used as external interrupt source.
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

#ifndef INCLUDE_DRIVERS_EXTIPINMAP_H_
#define INCLUDE_DRIVERS_EXTIPINMAP_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include "services/systp.h"

#define EXTI_DECLARE_PIN2F_MAP() \
		extern const EXTIMapEntry g_xExtiPin2FMap[];

#define EXTI_GET_P2F_MAP() g_xExtiPin2FMap

#define EXTI_BEGIN_P2F_MAP() \
  const EXTIMapEntry g_xExtiPin2FMap[] = {

#define EXTI_P2F_MAP_ENTRY(pin, callbackF) \
    { (pin), (callbackF) },

#define EXTI_END_P2F_MAP() \
    { 0, 0 }\
  };

typedef void ExtiCallbackF(uint16_t nPin);

struct _EXTIMapEntry {
	/**
	 * a GPIO_Pin. Valid value are GPIO_PINx with x in [0, 15].
	 */
	uint16_t nPin;

	/**
	 * Pointer to the callback called when the IRQ for the PIN nPin is triggered.
	 */
	ExtiCallbackF *pfCallback;
};

typedef struct _EXTIMapEntry EXTIMapEntry;

typedef const EXTIMapEntry* EXTIPin2CallbckMap;


#ifdef __cplusplus
}
#endif


#endif /* INCLUDE_DRIVERS_EXTIPINMAP_H_ */
