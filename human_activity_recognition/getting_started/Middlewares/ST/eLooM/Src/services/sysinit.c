/**
 ******************************************************************************
 * @file    sysinit.c
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Sep 6, 2016
 * @brief   System global initialization
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

#include "services/sysinit.h"
#include "services/syslowpower.h"
#include "services/sysdebug.h"
#include "services/NullErrorDelegate.h"
#include "services/SysDefPowerModeHelper.h"
#include "services/SysTimestamp.h"
/* MISRA messages linked to ThreadX include are ignored */
/*cstat -MISRAC2012-* */
#include "tx_api.h"
#include "tx_timer.h"
/*cstat +MISRAC2012-* */
#include <string.h>

#ifndef INIT_TASK_CFG_STACK_SIZE
#define INIT_TASK_CFG_STACK_SIZE               (140U)
#endif
#define INIT_TASK_CFG_PRIORITY                 (0) // with ThreadX the task priority are from MAX=0 to MIN=app_defined
#define INIT_TASK_CFG_QUEUE_ITEM_SIZE          sizeof(SysEvent)
#ifndef INIT_TASK_CFG_QUEUE_LENGTH
#define INIT_TASK_CFG_QUEUE_LENGTH             16
#endif
#define INIT_TASK_CFG_PM_SWITCH_DELAY_MS       50

#ifndef INIT_TASK_CFG_HEAP_SIZE
#define INIT_TASK_CFG_HEAP_SIZE                4096
#endif

#ifndef INIT_TASK_CFG_POST_EVENT_TIMEOUT_MS
#define INIT_TASK_CFG_POST_EVENT_TIMEOUT_MS    (50U)
#endif

#define INIT_IS_KIND_OF_AMTEX(pxTask)           ((pxTask)->m_xStatus.nReserved == 1)

#define SYS_DEBUGF(level, message) 			        SYS_DEBUGF3(SYS_DBG_INIT, level, message)

/**
 * Create a type name for _System.
 */
typedef struct _System System;

/**
 * The eLooM framework provides its services through the System object. It is an abstraction of an embedded application.
 */
struct _System{
  /**
   * Specifies the INIT task handle.
   */
  TX_THREAD m_xInitTask;

  /**
   * Specifies the queue used to serialize the system request made by the application tasks.
   * The supported requests are:
   * - Power Mode Switch.
   * - Error.
   */
  TX_QUEUE m_xSysQueue;

  /**
   * Specifies the application specific error manager delegate object.
   */
  IApplicationErrorDelegate *m_pxAppErrorDelegate;

  /**
   * Specifies the application specific power mode helper object.
   */
  IAppPowerModeHelper *m_pxAppPowerModeHelper;

  /**
   * Specifies the address of the first unused memory as reported by the linker.
   */
  void *pvFirstUnusedMemory;

#if (SYS_TS_CFG_ENABLE_SERVICE == 1)
  SysTimestamp_t m_xTimestampSrv;
#endif


#if INIT_TASK_CFG_ENABLE_BOOT_IF == 1
  /**
   * Specifies the application specific boot interface object.
   */
  IBoot *m_pxAppBootIF;
#endif

  /**
   * System memory pool control block.
   */
  TX_BYTE_POOL m_xSysMemPool;

  /**
   * System heap. This memory block is used to create the system byte pool.
   * This is a convenient way to handle the memory allocation at application level.
   */
  uint8_t m_pnHeap[INIT_TASK_CFG_HEAP_SIZE];
};


/* Private variables for the Init Task. */
/****************************************/

/**
 * The only instance of System object.
 */
static System s_xTheSystem;



/* Private function declaration */
/********************************/

/**
 * System Clock configuration procedure. It is provided by the CubeMX project.
 */
extern void SystemClock_Config(void);

/**
 * Configure the unused PIN in analog to minimize the power consumption, and enable the ultra low power mode.
 */
extern void SysPowerConfig(void);

/**
 * Initialize the system timestamp service. This function, even if it is not static, is not declared in the header file
 * because it should be used only by the INIT task.
 *
 * @param _this  [IN] specifies a system timestamp object.
 * @param pxDrvCfg [IN] specify the configuration structure of an hardware timer or SYS_TS_USE_SW_TSDRIVER to use the RTOS tick.
 * @return SYS_NO_ERROR_CODE if success, SYS_TS_SERVICE_ISSUE_ERROR_CODE otherwise.
 */
extern sys_error_code_t SysTsInit(SysTimestamp_t *_this, const void *pxDrvCfg);

/**
 * INIT task control loop. The INIT task is in charge of the system initialization.
 *
 * @param thread_input not used.
 */
static void InitTaskRun(ULONG thread_input);

#if defined(DEBUG) && !defined(SYS_TP_MCU_STM32U5)
/* Used in DEBUG to check for stack overflow */
static void SysThreadxStackErrorHandler(TX_THREAD *thread_ptr);
#endif


/**
 * Execute the power mode transaction for all managed tasks belonging to a given PMClass.
 *
 * @param pxContext [IN] specifies the Application Context.
 * @param ePowerModeClass [IN] specifies the a power mode class.
 * @param eActivePowerMode [IN] specifies the current power mode of the system.
 * @param eNewPowerMode [IN] specifies the new power mode that is to be activated by the system.
 * @return the number of tasks that did the PM transaction.
 */
static uint16_t InitTaskDoEnterPowerModeForPMClass(ApplicationContext *pxContext, EPMClass ePowerModeClass, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);


/* Public API definition */
/*************************/

__weak sys_error_code_t SysLoadApplicationContext(ApplicationContext *pAppContext) {
  UNUSED(pAppContext);
  SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_TASK_INVALID_CALL_ERROR_CODE);
  return SYS_TASK_INVALID_CALL_ERROR_CODE;
}

__weak sys_error_code_t SysOnStartApplication(ApplicationContext *pAppContext) {
  UNUSED(pAppContext);
  SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_TASK_INVALID_CALL_ERROR_CODE);
  return SYS_TASK_INVALID_CALL_ERROR_CODE;
}

sys_error_code_t SysInit(boolean_t bEnableBootIF) {
  /* First step: initialize the minimum set of resources before passing the control
   to the RTOS.*/

  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  /* Reset of all peripherals, Initializes the Flash interface and the Systick.*/
  if ( HAL_OK != HAL_Init()) {
    sys_error_handler();
  }

  /* Configure the system clock.*/
  SystemClock_Config();
  SysPowerConfig();

#if( configAPPLICATION_ALLOCATED_HEAP == 1 )
  // initialize the FreeRTOS heap.
  memset(ucHeap, 0, configTOTAL_HEAP_SIZE );
#endif

#if INIT_TASK_CFG_ENABLE_BOOT_IF == 1

  if (bEnableBootIF) {
    s_xTheSystem.m_pxAppBootIF = SysGetBootIF();
    if (s_xTheSystem.m_pxAppBootIF != NULL) {
      /* initialize the BootIF*/
      xRes = IBootInit(s_xTheSystem.m_pxAppBootIF);
      // check the trigger condition
      if (!IBootCheckDFUTrigger(s_xTheSystem.m_pxAppBootIF)) {
        /* prepare to jump to the main application*/
       uint32_t nAppAddress = IBootGetAppAdderss(s_xTheSystem.m_pxAppBootIF);
       xRes = IBootOnJampToApp(s_xTheSystem.m_pxAppBootIF, nAppAddress);
        if (!SYS_IS_ERROR_CODE(xRes) &&
            (((*(__IO uint32_t*)nAppAddress) & 0x2FFE0000 ) == 0x20000000)) {
          typedef void (*pFunction)(void);
          volatile uint32_t JumpAddress = *(__IO uint32_t*) (nAppAddress + 4);
          volatile pFunction JumpToApplication = (pFunction) JumpAddress;
          /* initialize user application's Stack Pointer */
          __set_MSP(*(__IO uint32_t*) nAppAddress);
          /* jump to the user application*/
          JumpToApplication();
        }
      }
    }
  }

#endif  /* INIT_TASK_CFG_ENABLE_BOOT_IF */

#ifdef SYS_DEBUG
  if (SysDebugInit() != 0) {
    sys_error_handler();
  }
#ifdef DEBUG
  HAL_DBGMCU_EnableDBGStopMode();
  __HAL_DBGMCU_FREEZE_WWDG();
#endif /* DEBUG */
#endif /* SYS_DEBUG */

  /* Clear the global error.*/
  SYS_CLEAR_ERROR();

  /* Create the INIT task to complete the system initialization
   after RTOS is started.*/

#ifdef SYS_TP_RTOS_FREERTOS
  if (xTaskCreate(InitTaskRun, "INIT", INIT_TASK_CFG_STACK_SIZE, NULL, INIT_TASK_CFG_PRIORITY, &s_xTheSystem.m_xInitTask) != pdPASS) {
    xRes = SYS_OUT_OF_MEMORY_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(xRes);
  }

  // ThreadX use a different approach. After the scheduler is started, it will call the following function
  // that the application code must overwrite:
  // void tx_application_define(void *first_unused_memory)
#endif

  return xRes;
}

sys_error_code_t SysPostEvent(SysEvent xEvent) {
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  UINT xResult = TX_SUCCESS;

  if (SYS_IS_ERROR_EVENT(xEvent)) {
    /* notify the error delegate to allow a first response to critical errors.*/
    xRes = IAEDOnNewErrEvent(s_xTheSystem.m_pxAppErrorDelegate, xEvent);
  }

  ULONG wait_option = TX_NO_WAIT;

  if (!SYS_IS_CALLED_FROM_ISR()) {
    /* check if we are in the system timer thread*/
    TX_THREAD *p_current_thread = tx_thread_identify();
    if (p_current_thread != &_tx_timer_thread) {
      wait_option = SYS_MS_TO_TICKS(INIT_TASK_CFG_POST_EVENT_TIMEOUT_MS);
    }
  }

  xResult = tx_queue_send(&s_xTheSystem.m_xSysQueue, &xEvent, wait_option);

  if (xResult != TX_SUCCESS) {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INIT_TASK_POWER_MODE_NOT_ENABLE_ERROR_CODE);
    xRes = SYS_INIT_TASK_POWER_MODE_NOT_ENABLE_ERROR_CODE;
  }

  return xRes;
}

EPowerMode SysGetPowerMode(void) {
  return IapmhGetActivePowerMode(s_xTheSystem.m_pxAppPowerModeHelper);
}

sys_error_code_t SysTaskErrorHandler(AManagedTask *pxTask) {
  assert_param(pxTask != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  /* TODO: STF - how to handle the shutdown of the task?*/

  tx_thread_suspend(&pxTask->m_xTaskHandle);

  return xRes;
}

SysPowerStatus SysGetPowerStatus(void) {
  return IapmhGetPowerStatus(s_xTheSystem.m_pxAppPowerModeHelper);
}

void SysResetAEDCounter(void) {
  IAEDResetCounter(s_xTheSystem.m_pxAppErrorDelegate);
}

boolean_t SysEventsPending(void) {
  ULONG nEnqueued = 0;
  UINT xResult = tx_queue_info_get(&s_xTheSystem.m_xSysQueue, TX_NULL, &nEnqueued, TX_NULL, TX_NULL, TX_NULL, TX_NULL);
#ifdef USE_FULL_ASSERT
  assert_param(xResult == TX_SUCCESS);
#else
  UNUSED(xResult);
#endif

  return nEnqueued > 0;
}

void *SysAlloc(size_t nSize) {
  void *pcMemory = NULL;
  if (TX_SUCCESS != tx_byte_allocate(&s_xTheSystem.m_xSysMemPool, (VOID **)&pcMemory, nSize, TX_NO_WAIT)) {
    pcMemory = NULL;
  }
  return pcMemory;
  }

void SysFree(void *pvData) {
  tx_byte_release(pvData);
}

__weak IApplicationErrorDelegate *SysGetErrorDelegate(void) {

  return NullAEDAlloc();
}

__weak IBoot *SysGetBootIF(void) {
  return NULL;
}

__weak IAppPowerModeHelper *SysGetPowerModeHelper(void) {

  return SysDefPowerModeHelperAlloc();
}

#if (SYS_TS_CFG_ENABLE_SERVICE == 1)
SysTimestamp_t *SysGetTimestampSrv(void) {
  return &s_xTheSystem.m_xTimestampSrv;
}
#endif

/* Private functions definition */
/********************************/

/**
 * INIT task control function.
 * The INIT task is the first created and running task. It is responsible to complete
 * the system initialization and to create all other system task.
 *
 * @param pParams not used
 */
static void InitTaskRun(ULONG thread_input) {
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  UINT nRtosRes = TX_SUCCESS;
  UNUSED(thread_input);

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("System Initialization\r\n"));

#if defined(DEBUG) && !defined(SYS_TP_MCU_STM32U5)
  tx_thread_stack_error_notify(SysThreadxStackErrorHandler);
#endif


//  vTaskSuspendAll();
  // to suspend all tasks, they are created with auto_start set to 0.
  // At the end of the system initialization all tasks with auto_start set to 1 are resumed.

  // allocate the system memory pool
  if (TX_SUCCESS != tx_byte_pool_create(&s_xTheSystem.m_xSysMemPool, "SYS_MEM_POOL", s_xTheSystem.m_pnHeap, INIT_TASK_CFG_HEAP_SIZE)) {
    // if the memory pool allocation fails then the execution is blocked
    sys_error_handler();
  }

  CHAR *pcMemory = NULL;
  // Create the queue for the system messages.
  if (TX_SUCCESS != tx_byte_allocate(&s_xTheSystem.m_xSysMemPool, (VOID **)&pcMemory, INIT_TASK_CFG_QUEUE_ITEM_SIZE * INIT_TASK_CFG_QUEUE_LENGTH, TX_NO_WAIT)) {
    sys_error_handler();
  }
  tx_queue_create(&s_xTheSystem.m_xSysQueue, "SYS_Q", INIT_TASK_CFG_QUEUE_ITEM_SIZE / sizeof(uint32_t), pcMemory, INIT_TASK_CFG_QUEUE_ITEM_SIZE * INIT_TASK_CFG_QUEUE_LENGTH);

  /* Check if the system has resumed from WWDG reset*/
  if (__HAL_RCC_GET_FLAG(RCC_FLAG_WWDGRST) != RESET) {
    __NOP();

    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("INIT: start after WWDG reset!\r\n"));
  }
  /* Check if the system has resumed from the Option Byte loading occurred*/
  if (__HAL_RCC_GET_FLAG(RCC_FLAG_OBLRST) != RESET) {
    HAL_FLASH_OB_Lock();
    HAL_FLASH_Lock();

    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("INIT: start after OB reset!\r\n"));
  }

  /* check the reset flags*/
  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("INIT: reset flags: 0x%x\r\n", READ_BIT(RCC->CSR, 0xFF000000U)));

  /* Clear reset flags in any case*/
  __HAL_RCC_CLEAR_RESET_FLAGS();

#if (SYS_TS_CFG_ENABLE_SERVICE == 1)
  /* Initialize the System Timestamp service*/
  xRes = SysTsInit(&s_xTheSystem.m_xTimestampSrv, SYS_TS_CFG_TSDRIVER_PARAMS);
  if (SYS_IS_ERROR_CODE(xRes)) {
    __NOP();
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("INIT: error during timestamp srv initialization.\r\n"));
  }
#endif

  /* Get the default application error manager delegate*/
  s_xTheSystem.m_pxAppErrorDelegate = SysGetErrorDelegate();
  /* initialize the application error manager delegate*/
  xRes = IAEDInit(s_xTheSystem.m_pxAppErrorDelegate, NULL);
  if (SYS_IS_ERROR_CODE(xRes)) {
    sys_error_handler();
  }

  /* Get the default Power Mode Helper object*/
  s_xTheSystem.m_pxAppPowerModeHelper = SysGetPowerModeHelper();
  /* Initialize the Power Mode Helper object*/
  xRes = IapmhInit(s_xTheSystem.m_pxAppPowerModeHelper);
  if (SYS_IS_ERROR_CODE(xRes)) {
    sys_error_handler();
  }

  /* Allocate the global application context*/
  ApplicationContext xContext;
  /* Initialize the context*/
  xRes = ACInit(&xContext);

  UNUSED(xRes); /* at the moment ACInit() return always SYS_NO_ERROR_CODE */

  xRes = SysLoadApplicationContext(&xContext);
  if (xRes != SYS_NO_ERROR_CODE) {
    /* it seems that there is no application to run!!!*/
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("INIT: no application tasks loaded!\r\n"));
    sys_error_handler();
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("INIT: added %i managed tasks.\r\n", ACGetTaskCount(&xContext)));

  /* Initialize the hardware resource for all tasks*/
  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("INIT: task hardware initialization.\r\n"));

  AManagedTask *pxTask = ACGetFirstTask(&xContext);
  while (pxTask != NULL && !SYS_IS_ERROR_CODE(xRes)) {
    xRes = AMTHardwareInit(pxTask, NULL);
    if (SYS_IS_ERROR_CODE(xRes)) {
       SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INIT_TASK_FAILURE_ERROR_CODE);
       SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("\r\nINIT: system failure.\r\n"));
    }
    else {
      pxTask = ACGetNextTask(&xContext, pxTask);

      SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("...\r\n"));
    }
  }

  SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("DONE.\r\n"));

  /* Create the application tasks*/
  tx_entry_function_t pvTaskCode;
  CHAR *pcName;
  VOID *pvStackStart;
  ULONG nStackSize;
  UINT nPriority;
  UINT nPreemptThreshold;
  ULONG nTimeSlice;
  ULONG nAutoStart;
  ULONG nParams;

  pxTask = ACGetFirstTask(&xContext);
  while ((pxTask != NULL) && !SYS_IS_ERROR_CODE(xRes)) {
    xRes = AMTOnCreateTask(pxTask, &pvTaskCode, &pcName, &pvStackStart, &nStackSize, &nPriority, &nPreemptThreshold, &nTimeSlice, &nAutoStart, &nParams);
    if (SYS_IS_ERROR_CODE(xRes)) {
      SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INIT_TASK_FAILURE_ERROR_CODE);
      SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("INIT: system failure.\r\n"));
    } else {
      if(pvStackStart == NULL) {
        // allocate the task stack in the system memory pool
        nRtosRes = tx_byte_allocate(&s_xTheSystem.m_xSysMemPool, &pvStackStart, nStackSize, TX_NO_WAIT);
      }
      if (nRtosRes == TX_SUCCESS) {
        if (nAutoStart == TX_AUTO_START) {
          pxTask->m_xStatus.nAutoStart = 1;
        }
        nRtosRes = tx_thread_create(&pxTask->m_xTaskHandle, pcName, pvTaskCode, nParams, pvStackStart, nStackSize,
            nPriority, nPreemptThreshold, nTimeSlice, TX_DONT_START);
      }
      if(nRtosRes != TX_SUCCESS) {
        SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INIT_TASK_FAILURE_ERROR_CODE);
        SYS_DEBUGF(SYS_DBG_LEVEL_SEVERE, ("INIT: unable to create task %s.\r\n", pcName));
      }
    }
    pxTask = ACGetNextTask(&xContext, pxTask);
  }

  SysOnStartApplication(&xContext);
  IAEDOnStartApplication(s_xTheSystem.m_pxAppErrorDelegate, &xContext);

  SYS_DEBUGF(SYS_DBG_LEVEL_SL, ("INIT: system initialized.\r\n"));

#if defined(DEBUG) || defined(SYS_DEBUG)
  if (SYS_DBG_LEVEL_SL >= g_sys_dbg_min_level) {
    ULONG nFreeHeapSize = 0;
    tx_byte_pool_info_get(&s_xTheSystem.m_xSysMemPool, TX_NULL, &nFreeHeapSize, TX_NULL, TX_NULL, TX_NULL, TX_NULL);
    SYS_DEBUGF(SYS_DBG_LEVEL_SL, ("INIT: free heap = %i.\r\n", nFreeHeapSize));
    SYS_DEBUGF(SYS_DBG_LEVEL_SL, ("INIT: SystemCoreClock = %iHz.\r\n", SystemCoreClock));
  }
#endif

  /*Resume all tasks created with auto_start set to 1.*/
  pxTask = ACGetFirstTask(&xContext);
  while (pxTask != NULL && !SYS_IS_ERROR_CODE(xRes)) {
    if (pxTask->m_xStatus.nAutoStart) {
      tx_thread_resume(&pxTask->m_xTaskHandle);
    }
    pxTask = ACGetNextTask(&xContext, pxTask);
  }

  // After the system initialization the INIT task is used to implement some system call
  // because it is the owner of the Application Context.
  // At the moment this is an initial implementation of a system level Power Management:
  // wait for a system level power mode request
  SysEvent xEvent;
  for (;;) {
    if (TX_SUCCESS == tx_queue_receive(&s_xTheSystem.m_xSysQueue, &xEvent, TX_WAIT_FOREVER)) {
      EPowerMode eActivePowerMode = IapmhGetActivePowerMode(s_xTheSystem.m_pxAppPowerModeHelper);
      /* check if it is a system error event*/
      if (SYS_IS_ERROR_EVENT(xEvent)) {
        IAEDProcessEvent(s_xTheSystem.m_pxAppErrorDelegate, &xContext, xEvent);
        // check if the system is in low power mode and it was waked up by a strange IRQ.
        if (IapmhIsLowPowerMode(s_xTheSystem.m_pxAppPowerModeHelper, eActivePowerMode)) {
          // if the system was wake up due to an error event, then wait the error is recovered before put the MCU in STOP
          if (!IAEDIsLastErrorPending(s_xTheSystem.m_pxAppErrorDelegate)) {
            // then put the system again in low power mode.
            IapmhDidEnterPowerMode(s_xTheSystem.m_pxAppPowerModeHelper, eActivePowerMode);
          }
        }
      }
      else {
        /* it is a power mode event*/
        EPowerMode ePowerMode = IapmhComputeNewPowerMode(s_xTheSystem.m_pxAppPowerModeHelper, xEvent);
        if (ePowerMode != eActivePowerMode) {
          IapmhCheckPowerModeTransaction(s_xTheSystem.m_pxAppPowerModeHelper, eActivePowerMode, ePowerMode);

          SYS_DEBUGF(SYS_DBG_LEVEL_VERBOSE, ("INIT: evt:src=%x evt:param=%x\r\n", xEvent.xEvent.nSource, xEvent.xEvent.nParam));

          /* first inform the AmanagedTaskEx that a transaction in the power mode state machine
           is going to begin.*/
          pxTask = ACGetFirstTask(&xContext);
          for (; pxTask!=NULL; pxTask=ACGetNextTask(&xContext, pxTask)) {
            if (INIT_IS_KIND_OF_AMTEX(pxTask)) {
              xRes = AMTExOnEnterPowerMode((AManagedTaskEx*)pxTask, eActivePowerMode, ePowerMode);
              if (SYS_IS_ERROR_CODE(xRes)) {
                sys_error_handler();
              }
            }
          }

          uint16_t nTaskToDoPMSwitch = ACGetTaskCount(&xContext);
          /* then we do the power mode transaction for the task belonging to CLASS_0*/
          nTaskToDoPMSwitch -= InitTaskDoEnterPowerModeForPMClass(&xContext, E_PM_CLASS_0, eActivePowerMode, ePowerMode);
          if (nTaskToDoPMSwitch > 0U) {
            /* then we do the power mode transaction for the task belonging to CLASS_1*/
            nTaskToDoPMSwitch -= InitTaskDoEnterPowerModeForPMClass(&xContext, E_PM_CLASS_1, eActivePowerMode, ePowerMode);
          }
          if (nTaskToDoPMSwitch > 0U) {
            /* then we do the power mode transaction for the task belonging to CLASS_2*/
            nTaskToDoPMSwitch -= InitTaskDoEnterPowerModeForPMClass(&xContext, E_PM_CLASS_2, eActivePowerMode, ePowerMode);
          }

          /* Enter the specified power mode*/
          IapmhDidEnterPowerMode(s_xTheSystem.m_pxAppPowerModeHelper, ePowerMode);

#if defined(DEBUG) || defined(SYS_DEBUG)
          if (SYS_DBG_LEVEL_SL >= g_sys_dbg_min_level) {
            ULONG nFreeHeapSize = 0;
            tx_byte_pool_info_get(&s_xTheSystem.m_xSysMemPool, TX_NULL, &nFreeHeapSize, TX_NULL, TX_NULL, TX_NULL, TX_NULL);
            SYS_DEBUGF(SYS_DBG_LEVEL_SL, ("INIT: free heap = %i.\r\n", nFreeHeapSize));
          }
#endif

          pxTask = ACGetFirstTask(&xContext);
          for (; pxTask!=NULL; pxTask=ACGetNextTask(&xContext, pxTask)) {
            pxTask->m_xStatus.nPowerModeSwitchDone = 0;
            pxTask->m_xStatus.nPowerModeSwitchPending = 0;
            tx_thread_resume(&pxTask->m_xTaskHandle);
          }
        }
        else {
          /* check if the system is in a low power mode and it was waked up by a strange IRQ.*/
          if (IapmhIsLowPowerMode(s_xTheSystem.m_pxAppPowerModeHelper, eActivePowerMode)) {
            /* then put the system again in low power mode.*/
            IapmhDidEnterPowerMode(s_xTheSystem.m_pxAppPowerModeHelper, ePowerMode);
          }
        }
      }
    }
  }
}

static uint16_t InitTaskDoEnterPowerModeForPMClass(ApplicationContext *pxContext, EPMClass ePowerModeClass, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode) {
  /* Forward the request to all managed tasks*/
  AManagedTask *pTask = NULL;
  EPMClass eTaskPMClass;
  boolean_t bDelayPowerModeSwitch;
  uint16_t nTaskCount = 0;

  do {
    bDelayPowerModeSwitch = FALSE;
    pTask = ACGetFirstTask(pxContext);
    for (; pTask!=NULL; pTask=ACGetNextTask(pxContext, pTask)) {

      /* check if the task is a AMTEx and, in case, if its power mode class is equal to ePowerModeClass*/
      eTaskPMClass = INIT_IS_KIND_OF_AMTEX(pTask) ? AMTExGetPMClass((AManagedTaskEx*)pTask) : E_PM_CLASS_0;
      if (eTaskPMClass == ePowerModeClass) {
        /* notify the task that the power mode is changing,
         so the task will suspend.*/
        pTask->m_xStatus.nPowerModeSwitchPending = 1;
        if (pTask->m_xStatus.nPowerModeSwitchDone == 0) {
          if ((pTask->m_xStatus.nDelayPowerModeSwitch == 0)) {

            AMTDoEnterPowerMode(pTask, eActivePowerMode, eNewPowerMode);
            pTask->m_xStatus.nPowerModeSwitchDone = 1;
            pTask->m_xStatus.nIsTaskStillRunning = 1;
            nTaskCount++;
          }
          else {
            /* check if it is an Extended Managed Task*/
            if (pTask->m_xStatus.nReserved == 1U) {
              // force the step execution to prepare the task for the power mode switch.
              AMTExForceExecuteStep((AManagedTaskEx*)pTask, eActivePowerMode);
            }
            bDelayPowerModeSwitch = TRUE;
          }
        }
      }
    }

    if (bDelayPowerModeSwitch == TRUE) {
      tx_thread_sleep(SYS_MS_TO_TICKS(INIT_TASK_CFG_PM_SWITCH_DELAY_MS));
    }

  } while (bDelayPowerModeSwitch == TRUE);

  return nTaskCount;
}

#if defined(SYS_DEBUG)
void SysDebugLogFreeHeapSize(void)
{
  ULONG nFreeHeapSize = 0;
  tx_byte_pool_info_get(&s_xTheSystem.m_xSysMemPool, TX_NULL, &nFreeHeapSize, TX_NULL, TX_NULL, TX_NULL, TX_NULL);
  SYS_DEBUGF(SYS_DBG_LEVEL_SL, ("INIT: free heap = %i.\r\n", nFreeHeapSize));
}
#endif

// ThreadX integration
// *******************
#ifdef SYS_TP_RTOS_THREADX

void tx_application_define(void *first_unused_memory) {
  UINT nRes = TX_SUCCESS;
  // create the INIT task.
  s_xTheSystem.pvFirstUnusedMemory = first_unused_memory;
  nRes = tx_thread_create(&s_xTheSystem.m_xInitTask, "INIT", InitTaskRun, ELOOM_MAGIC_NUMBER, s_xTheSystem.pvFirstUnusedMemory, INIT_TASK_CFG_STACK_SIZE, INIT_TASK_CFG_PRIORITY, INIT_TASK_CFG_PRIORITY, TX_NO_TIME_SLICE, TX_AUTO_START);
  if (nRes != TX_SUCCESS) {
    sys_error_handler();
  }
  uint32_t mem = (uint32_t)(INIT_TASK_CFG_STACK_SIZE * 4);
  uint32_t p =  ((uint32_t)s_xTheSystem.pvFirstUnusedMemory) + mem;
  s_xTheSystem.pvFirstUnusedMemory = (void *) p ;
}

/* For more info check cortex_m33/tx_port.h file (look for TX_ENABLE_STACK_CHECKING) */
#if defined(DEBUG) && !defined(SYS_TP_MCU_STM32U5)
static void SysThreadxStackErrorHandler(TX_THREAD *thread_ptr) {
  tx_interrupt_control(TX_INT_DISABLE);
#ifdef DEBUG
  __asm volatile ("bkpt 0");
#else
  while (1) __NOP();
#endif
}
#endif
#endif // SYS_TP_RTOS_THREADX
