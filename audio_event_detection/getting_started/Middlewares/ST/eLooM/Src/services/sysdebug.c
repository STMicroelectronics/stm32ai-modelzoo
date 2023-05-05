/**
 ******************************************************************************
 * @file    sysdebug.c
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Oct 10, 2016
 * @brief
 *
 * TODO - insert here the file description
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

#include "services/sysdebug.h"
#include <stdio.h>
#include <stdint.h>
#include "tx_api.h"

#ifndef SYS_DBG_LEVEL
#define SYS_DBG_LEVEL    SYS_DBG_LEVEL_VERBOSE
#endif


/**
 * Select the system wide debug level. Valid value are:
 * - SYS_DBG_LEVEL_ALL
 * - SYS_DBG_LEVEL_VERBOSE
 * - SYS_DBG_LEVEL_LLA
 * - SYS_DBG_LEVEL_SL
 * - SYS_DBG_LEVEL_DEFAULT
 * - SYS_DBG_LEVEL_WARNING
 * - SYS_DBG_LEVEL_SEVERE
 */
uint8_t g_sys_dbg_min_level = SYS_DBG_LEVEL;


#ifdef SYS_DEBUG

/**
 * To redirect the Debug log using printf and semihosting.
 */
#define  SysDebugLowLevelPutchar __io_putchar

/**
 * Check if the current code is inside an ISR or not.
 */
#define SYS_DBG_IS_CALLED_FROM_ISR() ((SCB->ICSR & SCB_ICSR_VECTACTIVE_Msk) != 0 ? 1 : 0)

static TX_SEMAPHORE s_xMutex;

void null_lockfn(void);
void SysDebugLock(void);
void SysDebugUnlock(void);

extern void sys_error_handler(void);


xDebugLockUnlockFnType xSysDebugLockFn = null_lockfn;
xDebugLockUnlockFnType xSysDebugUnlockFn = null_lockfn;

DebugPrintfFn xSysDebugPrintfFn = printf;

int SysDebugInit() {
  // hardware initialization
  SysDebugHardwareInit();

  // software initialization.
  UINT xResult = tx_semaphore_create(&s_xMutex, "DBG_S", 1);

  if (xResult != TX_SUCCESS) {
    return 1;
  }

  xSysDebugUnlockFn = SysDebugUnlock;
  xSysDebugLockFn = SysDebugLock;

  return 0;
}

void null_lockfn()
{
  return;
}

void SysDebugLock() {
  UINT xResult = TX_SUCCESS;
  if (SYS_DBG_IS_CALLED_FROM_ISR()) {
    xResult = tx_semaphore_get(&s_xMutex, TX_NO_WAIT);
  }
  else {
    xResult = tx_semaphore_get(&s_xMutex, TX_WAIT_FOREVER);
    }
  assert_param(xResult == TX_SUCCESS);
}

void SysDebugUnlock() {
  tx_semaphore_put(&s_xMutex);
}

#if defined ( __ICCARM__ )
__weak
#else
__attribute__((weak))
#endif
int SysDebugHardwareInit() {

  SYS_DBG_UART_INIT();

  return 0;
}

int SysDebugLowLevelPutchar(int x) {
  if(HAL_UART_Transmit(&SYS_DBG_UART, (uint8_t*)&x, 1, SYS_DBG_UART_TIMEOUT_MS)!= HAL_OK) {
    return -1;
  }

//  ITM_SendChar(x);

  return x;
}

#endif // SYS_DEBUG

