/**
 ******************************************************************************
 * @file    free_rtos_hooks.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
 *
 * @brief
 *
 * <DESCRIPTIOM>
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

#include "FreeRTOS.h"
#include "task.h"
#include "services/sysdebug.h"
#include "stm32l4xx_hal.h"

#define SYS_DEBUGF(level, message)      SYS_DEBUGF3(SYS_DBG_APP, level, message)


// Private member function declaration
// ***********************************


// Public API definition
// *********************

void vApplicationStackOverflowHook( TaskHandle_t pxTask, char *pcTaskName )
{
  ( void ) pcTaskName;
  ( void ) pxTask;

  /* Run time stack overflow checking is performed if
  configCHECK_FOR_STACK_OVERFLOW is defined to 1 or 2.  This hook
  function is called if a stack overflow is detected. */
  taskDISABLE_INTERRUPTS();
  for( ;; );
}

void vApplicationMallocFailedHook( void )
{
  /* vApplicationMallocFailedHook() will only be called if
  configUSE_MALLOC_FAILED_HOOK is set to 1 in FreeRTOSConfig.h.  It is a hook
  function that will get called if a call to pvPortMalloc() fails.
  pvPortMalloc() is called internally by the kernel whenever a task, queue,
  timer or semaphore is created.  It is also called by various parts of the
  demo application.  If heap_1.c or heap_2.c are used, then the size of the
  heap available to pvPortMalloc() is defined by configTOTAL_HEAP_SIZE in
  FreeRTOSConfig.h, and the xPortGetFreeHeapSize() API function can be used
  to query the size of free heap space that remains (although it does not
  provide information on how the remaining heap might be fragmented). */
  taskDISABLE_INTERRUPTS();

//  SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("FreeRTOS: malloc failed\r\n"));

  for( ;; );
}

/**
 * This function block the program execution if an exception occurs in the FreeRTOS kernel code.
 * See bugTabs4 #5265 (WDGID 201289)
 *
 * @param ulLine [IN] specifies the code line that has triggered the exception.
 * @param pcFileName [IN] specifies the full path of the file that has triggered the exception.
 */
void vFreeRTOSAssertCalled( unsigned long ulLine, const char * const pcFileName )
{
  /* Parameters are not used. */
  ( void ) ulLine;
  ( void ) pcFileName;

#ifdef FREERTOS_CONFIG_ASSERT_MUST_BLOCK
  //TODO: STF.Port - add the code to block.
#else
volatile unsigned long ulSetToNonZeroInDebuggerToContinue = 0;


  taskENTER_CRITICAL();
  {
    while( ulSetToNonZeroInDebuggerToContinue == 0 )
    {
      /* Use the debugger to set ulSetToNonZeroInDebuggerToContinue to a
      non zero value to step out of this function to the point that raised
      this assert(). */
      __asm volatile( "NOP" );
      __asm volatile( "NOP" );
    }
  }
  taskEXIT_CRITICAL();
#endif
}

void vApplicationIdleHook( void ) {

#if !(SYS_DBG_ENABLE_TA4>=1)
  // Enter Sleep Mode.
  HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
#endif
}
