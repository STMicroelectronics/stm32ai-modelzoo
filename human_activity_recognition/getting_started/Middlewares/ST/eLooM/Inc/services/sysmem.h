/**
 ******************************************************************************
 * @file    sysmem.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 1.0.0
 * @date    Nov 11, 2020
 *
 * @brief   System memory management.
 *
 * This file declares API function to alloc and release block of memory.
 * The application can use its own memory allocation strategy.
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2020 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
 
#ifndef INCLUDE_SERVICES_SYSMEM_H_
#define INCLUDE_SERVICES_SYSMEM_H_

#include "services/systp.h"
#include "services/systypes.h"


/**
 * Allocate a block of memory of a specific size.
 *
 * @param nSize [IN] specifies the size in byte of the requested memory.
 * @return a pointer to the allocated memory if success, NULL otherwise.
 */
void *SysAlloc(size_t nSize);

/**
 * Release a block of memory.
 *
 * @param pvData [IN] specifies the start of teh block of memory to release.
 */
void SysFree(void *pvData);

#endif /* INCLUDE_SERVICES_SYSMEM_H_ */
