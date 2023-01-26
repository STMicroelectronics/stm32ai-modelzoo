/**
 ******************************************************************************
 * @file    App.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
 *
 * @brief   Define the Application main entry points
 *
 * The framework `weak` function are redefined in this file and they link
 * the application specific code with the framework.
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

#include "services/sysdebug.h"
#include "services/ApplicationContext.h"
#include "AppPowerModeHelper.h"
#include "SPIBusTask.h"
#include "ISM330DHCXTask.h"
#include "IIS3DWBTask.h"
#include "AITask.h"
#include "AppController.h"
#include "mx.h"

/**
 * SPI bus task object.
 */
static AManagedTaskEx *spSPIBusObj = NULL;

/**
 * Sensor task object.
 */
static AManagedTaskEx *spISM330DHCXObj = NULL;

/**
 * Sensor task object.
 */
static AManagedTaskEx *spIIS3DWBObj = NULL;

/**
 * CubeAI task object.
 */
static AManagedTaskEx *spAIObj = NULL;

/**
 * Application controller object.
 */
static AManagedTaskEx *spControllerObj = NULL;

/**
 * specifies the map (PM_APP, PM_SM). It re-map the state of the application into the state of the Sensor Manager.
 */
static EPowerMode spAppPMState2SMPMStateMap[] = {
    E_POWER_MODE_STATE1,
    E_POWER_MODE_SLEEP_1,
    E_POWER_MODE_SENSORS_ACTIVE,
    E_POWER_MODE_SENSORS_ACTIVE,
};

/* Private functions declaration */
/*********************************/

/**
 * Re-map the PM State Machine of the Sensor Manager managed tasks used in the application according to the following map:
 *
 * | App State                      | Sensor Manager State         |
 * | :----------------------------- | ---------------------------: |
 * | E_POWER_MODE_STATE1            | E_POWER_MODE_STATE1          |
 * | E_POWER_MODE_SLEEP_1           | E_POWER_MODE_SLEEP_1         |
 * | E_POWER_MODE_X_CUBE_AI_ACTIVE  | E_POWER_MODE_SENSORS_ACTIVE  |
 *
 * @param pPMState2PMStateMap [IN] specifies the map (PM_APP, PM_SM).
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static sys_error_code_t SensorManagerStateMachineRemap(EPowerMode *pPMState2PMStateMap);


/* eLooM framework entry points definition */
/*******************************************/

sys_error_code_t SysLoadApplicationContext(ApplicationContext *pAppContext)
{
  assert_param(pAppContext);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  // Allocate the task objects
  spSPIBusObj     = SPIBusTaskAlloc(&MX_SPI3InitParams);
  spISM330DHCXObj = ISM330DHCXTaskAlloc();
  spIIS3DWBObj    = IIS3DWBTaskAlloc();
  spAIObj         = AITaskAlloc();
  spControllerObj = AppControllerAlloc();

  // Add the task object to the context.
  xRes = ACAddTask(pAppContext, (AManagedTask*)spSPIBusObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*)spISM330DHCXObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*)spIIS3DWBObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*)spAIObj);
  xRes = ACAddTask(pAppContext, (AManagedTask*)spControllerObj);
  return xRes;
}

sys_error_code_t SysOnStartApplication(ApplicationContext *pAppContext)
{
  UNUSED(pAppContext);

  /* Re-map the state machine of the Sensor Manager tasks */
  SensorManagerStateMachineRemap(spAppPMState2SMPMStateMap);

  /* connect the sensors task to the SPI bus. */
  SPIBusTaskConnectDevice((SPIBusTask*)spSPIBusObj, ISM330DHCXTaskGetSensorIF((ISM330DHCXTask*)spISM330DHCXObj));
  SPIBusTaskConnectDevice((SPIBusTask*)spSPIBusObj, IIS3DWBTaskGetSensorIF((IIS3DWBTask*)spIIS3DWBObj));

  /* register AI processing with the application controller. */
  QueueHandle_t queueAi   = AITaskGetInQueue((AITask_t*)spAIObj);
  AppControllerSetAIProcessesInQueue((AppController_t*)spControllerObj, queueAi /*,queueNeai*/ );

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


/* Private function definition */
/*******************************/

static sys_error_code_t SensorManagerStateMachineRemap(EPowerMode *pPMState2PMStateMap)
{
  assert_param(pPMState2PMStateMap != NULL);

  AMTSetPMStateRemapFunc((AManagedTask*)spSPIBusObj, pPMState2PMStateMap);
  AMTSetPMStateRemapFunc((AManagedTask*)spISM330DHCXObj, pPMState2PMStateMap);
  AMTSetPMStateRemapFunc((AManagedTask*)spIIS3DWBObj, pPMState2PMStateMap);

  return SYS_NO_ERROR_CODE;
}
