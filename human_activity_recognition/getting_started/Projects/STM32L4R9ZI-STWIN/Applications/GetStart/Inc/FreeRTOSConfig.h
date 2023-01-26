/*
 * FreeRTOS V202107.00
 * Copyright (C) 2020 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * http://www.FreeRTOS.org
 * http://aws.amazon.com/freertos
 *
 * 1 tab == 4 spaces!
 */

#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

/*-----------------------------------------------------------
 * Application specific definitions.
 *
 * These definitions should be adjusted for your particular hardware and
 * application requirements.
 *
 * THESE PARAMETERS ARE DESCRIBED WITHIN THE 'CONFIGURATION' SECTION OF THE
 * FreeRTOS API DOCUMENTATION AVAILABLE ON THE FreeRTOS.org WEB SITE.
 *
 * See http://www.freertos.org/a00110.html.
 *----------------------------------------------------------*/

/* Ensure stdint is only used by the compiler, and not the assembler. */
#if defined(__ICCARM__) || defined(__CC_ARM) || defined(__GNUC__)
 #include <stdint.h>
 #include "stm32l4xx.h"
 extern uint32_t SystemCoreClock;
 #define CORE_CLOCK_RSHIFT (8)
#endif
#define configUSE_PREEMPTION                     1
#define configUSE_PORT_OPTIMISED_TASK_SELECTION  0
#define configUSE_TICKLESS_IDLE                  0
#define configCPU_CLOCK_HZ                       ( SystemCoreClock )
#define configTICK_RATE_HZ                       ((TickType_t)1000)
#define configMAX_PRIORITIES                     ( 7 )
#define configMAX_TASK_NAME_LEN                  ( 8 )
#define configMINIMAL_STACK_SIZE                 ((uint16_t)70)
#define configUSE_16_BIT_TICKS                   0
#define configIDLE_SHOULD_YIELD                  1
#define configUSE_TASK_NOTIFICATIONS             0
#if defined(DEBUG) || defined(SYS_DEBUG)
#define configUSE_MUTEXES                        1
#else
#define configUSE_MUTEXES                        0
#endif
#define configUSE_RECURSIVE_MUTEXES              0
#define configUSE_COUNTING_SEMAPHORES            0
#if defined(DEBUG) || defined(SYS_DEBUG)
#define configQUEUE_REGISTRY_SIZE                20
#else
#define configQUEUE_REGISTRY_SIZE                1
#endif
#define configUSE_QUEUE_SETS                     0
#define configENABLE_BACKWARD_COMPATIBILITY      0
#define configNUM_THREAD_LOCAL_STORAGE_POINTERS  0
#if defined(__ICCARM__)|| defined(__CC_ARM)
#define configUSE_NEWLIB_REENTRANT               0
#elif  defined(__GNUC__)
#define configUSE_NEWLIB_REENTRANT               0
#endif

/* Memory allocation related definitions. */
#define configSUPPORT_STATIC_ALLOCATION          0
#define configSUPPORT_DYNAMIC_ALLOCATION         1
#if defined(DEBUG) || (SYS_DBG_ENABLE_TA4>=1)
#define configTOTAL_HEAP_SIZE                    ((size_t)(150*1024))
#else
#define configTOTAL_HEAP_SIZE                    ((size_t)(140*1024))
#endif
#define configAPPLICATION_ALLOCATED_HEAP         1

/* Hook function related definitions. */
#define configUSE_IDLE_HOOK                      1
#define configUSE_TICK_HOOK                      0
#ifdef DEBUG
#define configCHECK_FOR_STACK_OVERFLOW           2
#else
#define configCHECK_FOR_STACK_OVERFLOW           0
#endif
#ifdef DEBUG
#define configUSE_MALLOC_FAILED_HOOK             1
#else
#define configUSE_MALLOC_FAILED_HOOK             0
#endif
#define configUSE_DAEMON_TASK_STARTUP_HOOK       0

/* Run time and task stats gathering related definitions. */
#define configGENERATE_RUN_TIME_STATS            1
#define configUSE_STATS_FORMATTING_FUNCTIONS     1
#define configUSE_TRACE_FACILITY                 1

 /* Co-routine definitions. */
#define configUSE_CO_ROUTINES                    0
#define configMAX_CO_ROUTINE_PRIORITIES          ( 2 )

/* Software timer related definitions. */
#define configUSE_TIMERS                         1
#define configTIMER_TASK_PRIORITY                3
#define configTIMER_QUEUE_LENGTH                 10
#define configTIMER_TASK_STACK_DEPTH             (3*configMINIMAL_STACK_SIZE)

/* Other. */
#define configUSE_APPLICATION_TASK_TAG           0

/* Set the following definitions to 1 to include the API function, or zero
to exclude the API function. */
#define INCLUDE_vTaskPrioritySet                 0
#define INCLUDE_uxTaskPriorityGet                0
#define INCLUDE_vTaskDelete                      0
#define INCLUDE_vTaskSuspend                     1
#define INCLUDE_vTaskDelayUntil                  0
#define INCLUDE_vTaskDelay                       1
#define INCLUDE_vTaskCleanUpResources            0
#define INCLUDE_xTaskGetSchedulerState           1
#define INCLUDE_xTaskGetCurrentTaskHandle        1
#define INCLUDE_uxTaskGetStackHighWaterMark      1
#define INCLUDE_xTaskGetIdleTaskHandle           0
#define INCLUDE_eTaskGetState                    0
#define INCLUDE_xEventGroupSetBitFromISR         0
#define INCLUDE_xTimerPendFunctionCall           0
#define INCLUDE_xTaskAbortDelay                  1
#define INCLUDE_xTaskGetHandle                   0
#define INCLUDE_xTaskResumeFromISR               1

/* Cortex-M specific definitions. */
#ifdef __NVIC_PRIO_BITS
 /* __BVIC_PRIO_BITS will be specified when CMSIS is being used. */
 #define configPRIO_BITS                        __NVIC_PRIO_BITS
#else
 #define configPRIO_BITS                        4        /* 15 priority levels */
#endif

/* The lowest interrupt priority that can be used in a call to a "set priority"
function. */
#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY     0xf

/* The highest interrupt priority that can be used by any interrupt service
routine that makes calls to interrupt safe FreeRTOS API functions.  DO NOT CALL
INTERRUPT SAFE FREERTOS API FUNCTIONS FROM ANY INTERRUPT THAT HAS A HIGHER
PRIORITY THAN THIS! (higher priorities are lower numeric values. */
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY  2

/* Interrupt priorities used by the kernel port layer itself.  These are generic
to all Cortex-M ports, and do not rely on any particular library functions. */
#define configKERNEL_INTERRUPT_PRIORITY     ( configLIBRARY_LOWEST_INTERRUPT_PRIORITY << (8 - configPRIO_BITS) )
/* !!!! configMAX_SYSCALL_INTERRUPT_PRIORITY must not be set to zero !!!!
See http://www.FreeRTOS.org/RTOS-Cortex-M3-M4.html. */
#define configMAX_SYSCALL_INTERRUPT_PRIORITY  ( configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY << (8 - configPRIO_BITS) )

/* Normal assert() semantics without relying on the provision of an assert.h
header file. */
#if defined(__ICCARM__) || defined(__GNUC__) || defined(__CC_ARM)
    // We put the forward declaration of vFreeRTOSAssertCalled function between define in order to prevent and error from the assembly
    // when it compiles the port.asm file that include FreeTOSConfig.h.
    void vFreeRTOSAssertCalled( unsigned long ulLine, const char * const pcFileName );
#else
#define vFreeRTOSAssertCalled(line, file) { taskDISABLE_INTERRUPTS(); for( ;; ); }
#endif
#define configASSERT( x ) if ((x) == 0) vFreeRTOSAssertCalled(__LINE__, __FILE__)

/* Definitions that map the FreeRTOS port interrupt handlers to their CMSIS
   standard names. */
#define vPortSVCHandler    SVC_Handler
#define xPortPendSVHandler PendSV_Handler

/* IMPORTANT: This define MUST be commented when used with STM32Cube firmware,
              to prevent overwriting SysTick_Handler defined within STM32Cube HAL */
/* #define xPortSysTickHandler SysTick_Handler */

#if defined(__ICCARM__) || defined(__CC_ARM) || defined(__GNUC__)
void SysPreSleepProcessing(uint32_t *ulExpectedIdleTime);
void SysPostSleepProcessing(uint32_t *ulExpectedIdleTime);
#endif /* defined(__ICCARM__) || defined(__CC_ARM) || defined(__GNUC__) */

/* The configPRE_SLEEP_PROCESSING() and configPOST_SLEEP_PROCESSING() macros
allow the application writer to add additional code before and after the MCU is
placed into the low power state respectively. */
#if configUSE_TICKLESS_IDLE == 1
#define configPRE_SLEEP_PROCESSING                        SysPreSleepProcessing
#define configPOST_SLEEP_PROCESSING                       SysPostSleepProcessing
#endif /* configUSE_TICKLESS_IDLE == 1 */

// Enable the RTOS-aware debugging support provided by Atollic TruSTUDIO 8.1.0.
#if configGENERATE_RUN_TIME_STATS == 1
// forward declaration
//extern void SysDebugStartRunTimeStatsTimer(void);
//extern uint32_t g_ulHighFrequencyTimerTicks;

// see https://stackoverflow.com/questions/56703232/how-to-show-runtime-in-freertos-task-list-during-debugging
#define portREMOVE_STATIC_QUALIFIER 1

//#define portCONFIGURE_TIMER_FOR_RUN_TIME_STATS() SysDebugStartRunTimeStatsTimer()
//#define portCONFIGURE_TIMER_FOR_RUN_TIME_STATS() cyclesCounterInit()
#define portCONFIGURE_TIMER_FOR_RUN_TIME_STATS() do {CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;\
	DWT->CYCCNT = 0; \
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk | DWT_CTRL_CPIEVTENA_Msk;\
} while (0)

//#define portGET_RUN_TIME_COUNTER_VALUE() g_ulHighFrequencyTimerTicks
//#define portGET_RUN_TIME_COUNTER_VALUE() dwtGetCycles()
#define portGET_RUN_TIME_COUNTER_VALUE() (DWT->CYCCNT>>CORE_CLOCK_RSHIFT)

#endif

// Tracealyzer recorder library
#if (SYS_DBG_ENABLE_TA4>=1)
#include "trcRecorder.h"

// To fix few compiler warning due to the upgrade to Tracealyzer v4.6.1.
// Something is changed in the include chain of Tracealyzer recording library.
traceHandle xTraceSetISRProperties(const char* name, uint8_t priority);
void vTraceStoreISRBegin(traceHandle handle);
void vTraceStoreISREnd(int pendingISR);
#endif

/* The size of the global output buffer that is available for use when there
are multiple command interpreters running at once (for example, one on a UART
and one on TCP/IP).  This is done to prevent an output buffer being defined by
each implementation - which would waste RAM.  In this case, there is only one
command interpreter running, and it has its own local output buffer, so the
global buffer is just set to be one byte long as it is not used and should not
take up unnecessary RAM. */
#define configCOMMAND_INT_MAX_OUTPUT_SIZE 1

#endif /* FREERTOS_CONFIG_H */

