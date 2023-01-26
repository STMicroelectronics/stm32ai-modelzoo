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

#include "services/systp.h"
#include "services/sysdebug.h"
#include <stdio.h>
#include <stdint.h>
/* MISRA messages linked to FreeRTOS include are ignored */
/*cstat -MISRAC2012-* */
#include "FreeRTOS.h"
#include "semphr.h"
#include "task.h"
/*cstat +MISRAC2012-* */

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

static SemaphoreHandle_t s_xMutex = NULL;

uint32_t g_ulHighFrequencyTimerTicks = 0;

static void SysDebugSetupRunTimeStatsTimer(void);

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
  s_xMutex = xSemaphoreCreateMutex();

  if (s_xMutex == NULL) {
    return 1;
  }

  xSysDebugUnlockFn = SysDebugUnlock;
  xSysDebugLockFn = SysDebugLock;

#ifdef DEBUG
  vQueueAddToRegistry(s_xMutex, "DBG");
#endif
  return 0;
}

void SysDebugToggleLed(uint8_t nLed) {
  UNUSED(nLed);

  HAL_GPIO_TogglePin(SYS_DBG_TP1_PORT, SYS_DBG_TP1_PIN);
}

void SysDebugLedOn(uint8_t nLed) {
  UNUSED(nLed);

  HAL_GPIO_WritePin(SYS_DBG_TP1_PORT, SYS_DBG_TP1_PIN, GPIO_PIN_SET);
}

void SysDebugLedOff(uint8_t nLed) {
  UNUSED(nLed);

  HAL_GPIO_WritePin(SYS_DBG_TP1_PORT, SYS_DBG_TP1_PIN, GPIO_PIN_RESET);
}

void null_lockfn()
{
  return;
}

void SysDebugLock() {
  if (SYS_DBG_IS_CALLED_FROM_ISR()) {
    xSemaphoreTakeFromISR(s_xMutex, NULL);
  }
  else {
    if (xTaskGetSchedulerState() == taskSCHEDULER_SUSPENDED) {
      xSemaphoreTake(s_xMutex, 0);
    }
    else {
      xSemaphoreTake(s_xMutex, portMAX_DELAY);
    }
  }
}

void SysDebugUnlock() {
  if (SYS_DBG_IS_CALLED_FROM_ISR()) {
    xSemaphoreGiveFromISR(s_xMutex, NULL);
  }
  else {
    xSemaphoreGive(s_xMutex);
  }
}

#if defined ( __ICCARM__ )
__weak
#else
__attribute__((weak))
#endif
int SysDebugHardwareInit() {

  SYS_DBG_UART_INIT();

#ifdef DEBUG
  // Debug TP1 and TP2 configuration
  GPIO_InitTypeDef GPIO_InitStruct;
  SYS_DBG_TP1_CLK_ENABLE();
  SYS_DBG_TP2_CLK_ENABLE();

  HAL_GPIO_WritePin(SYS_DBG_TP1_PORT, SYS_DBG_TP1_PIN, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(SYS_DBG_TP2_PORT, SYS_DBG_TP2_PIN, GPIO_PIN_RESET);
  GPIO_InitStruct.Pin = SYS_DBG_TP1_PIN;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(SYS_DBG_TP1_PORT, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = SYS_DBG_TP2_PIN;
  HAL_GPIO_Init(SYS_DBG_TP2_PORT, &GPIO_InitStruct);

  SysDebugSetupRunTimeStatsTimer();
#endif

  return 0;
}

void SysDebugSetupRunTimeStatsTimer() {
  SYS_DBG_TIM_INIT();
}

void SysDebugStartRunTimeStatsTimer() {
  HAL_NVIC_EnableIRQ(SYS_DBG_TIM_IRQ_N);
  HAL_TIM_Base_Start_IT(&SYS_DBG_TIM);
}

int SysDebugLowLevelPutchar(int x) {
  if(HAL_UART_Transmit(&SYS_DBG_UART, (uint8_t*)&x, 1, SYS_DBG_UART_TIMEOUT_MS)!= HAL_OK) {
    return -1;
  }

//  ITM_SendChar(x);

  return x;
}

// CubeMx integration
// ******************

void SYS_DBG_TIM_IRQ_HANDLER(void) {
    // TIM Update event
  if(__HAL_TIM_GET_FLAG(&SYS_DBG_TIM, TIM_FLAG_UPDATE) != RESET) {
    if(__HAL_TIM_GET_IT_SOURCE(&SYS_DBG_TIM, TIM_IT_UPDATE) != RESET) {
      __HAL_TIM_CLEAR_IT(&SYS_DBG_TIM, TIM_IT_UPDATE);
      // handle the update event.
      g_ulHighFrequencyTimerTicks++;
    }
  }
}

#endif // SYS_DEBUG

