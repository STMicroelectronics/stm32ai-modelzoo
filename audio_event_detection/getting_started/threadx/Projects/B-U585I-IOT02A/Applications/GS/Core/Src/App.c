/**
  ******************************************************************************
  * @file    App.c
  * @author  STMicroelectronics - AIS - MCD Team
  * @version $Version$
  * @date    $Date$
  *
  * @brief   Define the Application main entry points
  *
  * ## Introduction
  *
  * This file is the main entry point for the user code.
  *
  * The framework `weak` functions are redefined in this file and they link
  * the application specific code with the framework:
  * - SysLoadApplicationContext(): it is the first application defined function
  *   called by the framework. Here we define all managed tasks. A managed task
  *   implements one or more application specific feature.
  * - SysOnStartApplication(): this function is called by the framework
  *   when the system is initialized (all managed task objects have been
  *   initialized), and before the INIT task release the control. Here we
  *   link the application objects according to the application design.
  *
  * The execution time  between the two above functions is called
  * *system initialization*. During this period only the INIT task is running.
  *
  * Each managed task will be activated in turn to initialize its hardware
  * resources, if any - MyTask_vtblHardwareInit() - and its software
  * resources - MyTask_vtblOnCreateTask().
  *
  * ## About this demo
  *
  * ## How to use the demo
  *
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

#include "services/sysdebug.h"
#include "services/ApplicationContext.h"
#include "AppPowerModeHelper.h"
#include "AI_Task.h"
#include "PreProc_Task.h"
#include "mx.h"
#include "crc.h"
#include "ISM330DHCXTask.h"
#include "IMP34DT05Task.h"
#include "I2CBusTask.h"
#include "AppController.h"

/**
 * Application controller object.
 */
static AManagedTaskEx *spControllerObj = NULL;
/**
 * AI CubeAI task object.
 */
static AI_Task_t sAiObj = {0};

/**
 * PreProc task object.
 */
static PreProc_Task_t sPreProcObj = {0};

/**
 * Sensor tasks objects
 */

static AManagedTaskEx *spISM330DHCXObj = NULL;
static AManagedTaskEx *spIMP34DT05Obj  = NULL;
/**
 * I2C bus task object
 */

static AManagedTaskEx *spI2CBusObj = NULL;

/**
 * specifies the map (PM_APP, PM_SM). It re-map the state of the application into the state of the Sensor Manager.
 */
static EPowerMode spAppPMState2SMPMStateMap[] = {
    E_POWER_MODE_STATE1,
    E_POWER_MODE_SLEEP_1,
    E_POWER_MODE_SENSORS_ACTIVE,
    E_POWER_MODE_SENSORS_ACTIVE,
};

/**
 * specifies the map (PM_APP, PM_SM). It re-map the state of the application into the state of the AI_Task.
 */
static const EPowerMode spAiTaskPMState2PMStateMap[] = {
    E_POWER_MODE_STATE1,
    E_POWER_MODE_SLEEP_1,
    E_POWER_MODE_SENSORS_ACTIVE,
    E_POWER_MODE_SENSORS_ACTIVE,
};

/* eLooM framework entry points definition */
/*******************************************/

sys_error_code_t SysLoadApplicationContext(ApplicationContext *pAppContext)
{
  assert_param(pAppContext);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  /* Enable CRC IP clock required by X-CUBE-AI. */
  /**
   * Initialize the CRC IP required by X-CUBE-AI. Must be called before any usage of the
   * ai library API. The beginning of the SysLoadApplicationContext() is a good place
   * because no other application code is called before.
   */
  __HAL_RCC_CRC_CLK_ENABLE();
  MX_CRC_Init();

  /** Enable instruction cache (default 2-ways set associative cache)
  */
  if (HAL_ICACHE_Enable() != HAL_OK)
  {
    Error_Handler();
  }

  /* Allocate the task objects */
  spControllerObj = AppControllerAlloc();
  (void) AI_StaticAlloc(&sAiObj);
  (void) PreProc_TaskStaticAlloc(&sPreProcObj);
  spI2CBusObj     = I2CBusTaskAlloc(&MX_I2C2InitParams);
  spISM330DHCXObj = ISM330DHCXTaskAlloc(&MX_GPIO_PE11InitParams, NULL, NULL);
  spIMP34DT05Obj  = IMP34DT05TaskAlloc(&MX_ADF1InitParams);

  /* Add the task object to the context. */
  xRes = ACAddTask(pAppContext, (AManagedTask*) spControllerObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*) &sAiObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*) &sPreProcObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*) spI2CBusObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*) spISM330DHCXObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*) spIMP34DT05Obj);

  return xRes;
}

sys_error_code_t SysOnStartApplication(ApplicationContext *pAppContext)
{
  UNUSED(pAppContext);

  /* Re-map the state machine of the Sensor Manager tasks */
  (void)AMTSetPMStateRemapFunc((AManagedTask*)spI2CBusObj     , spAppPMState2SMPMStateMap);
  (void)AMTSetPMStateRemapFunc((AManagedTask*)spISM330DHCXObj , spAppPMState2SMPMStateMap);
  (void)AMTSetPMStateRemapFunc((AManagedTask*)spIMP34DT05Obj  , spAppPMState2SMPMStateMap);

  /* Re-map the state machine of the AI process tasks */
  (void)AMTSetPMStateRemapFunc((AManagedTask*) &sAiObj  , spAiTaskPMState2PMStateMap);
  (void)AMTSetPMStateRemapFunc((AManagedTask*) &sPreProcObj, spAiTaskPMState2PMStateMap);

  /* Connect the sensors to the I2C bus*/
  I2CBusTaskConnectDevice((I2CBusTask*) spI2CBusObj, (I2CBusIF*)ISM330DHCXTaskGetSensorIF((ISM330DHCXTask*)spISM330DHCXObj));

  /* register AI processing with the application controller.
   * The application controller can communicate with those tasks in two way:
   * - Using messages posted in the task input message queue. The message structure are defined in the app_message_parser.c file
   * and the command ID specific for each task are defined in the respective [XXX]MessagesDef.h file.
   * - Using their public API. this is the way used in this application.
   */
  (void) AppControllerConnectAppTasks((AppController_t*)spControllerObj, &sAiObj, &sPreProcObj);

  return SYS_NO_ERROR_CODE;
}

IAppPowerModeHelper *SysGetPowerModeHelper(void)
{
  // Install the application power mode helper.
  static IAppPowerModeHelper *s_pxPowerModeHelper = NULL;
  if (s_pxPowerModeHelper == NULL) {
    s_pxPowerModeHelper = AppPowerModeHelperAlloc();
  }

  return s_pxPowerModeHelper;
}
