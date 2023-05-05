/**
 ******************************************************************************
 * @file    HwTSDriver.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    Mar 15, 2022
 *
 * @brief
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights xReserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#include "drivers/HwTSDriver.h"
#include "drivers/HwTSDriver_vtbl.h"
/* MISRA messages linked to ThreadX include are ignored */
/*cstat -MISRAC2012-* */
#include "tx_api.h"
/*cstat +MISRAC2012-* */
#include "services/sysdebug.h"

#if (SYS_TS_CFG_ENABLE_SERVICE == 1)

#ifndef HW_TS_DRV_IRQ_PRIORITY
#define HW_TS_DRV_IRQ_PRIORITY          0xE
#endif

#define SYS_DEBUGF(level, message)      SYS_DEBUGF3(SYS_DBG_DRIVERS, level, message)

/**
 * Define the resource shared between the eLooM low level driver and the HAL driver.
 * The members of this structure are used by ISR callback and by the eLooM driver.
 * We use this structure to model a relation between HAL and eLooM driver
 */
typedef struct _HwDriverResources
{
  /**
   * Specifies the timestamp in tick.
   */
  uint64_t m_nTimestampTick;
} HwDriverResources_t;

/**
 * HwTSDriver Driver virtual table.
 */
static const ITSDriver_vtbl sHwTSDriver_vtbl = {
    HwTSDriver_vtblInit,
    HwTSDriver_vtblStart,
    HwTSDriver_vtblStop,
    HwTSDriver_vtblDoEnterPowerMode,
    HwTSDriver_vtblReset,
    HwTSDriver_vtblGetTimestamp
};


/**
 * The only instance of the hardware resource for this driver.
 */
volatile static HwDriverResources_t s_xHwResources;


/* Private member function declaration */
/***************************************/

static void HwTSDriver_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim);


/* Public API definition */
/*************************/


/* IDriver virtual functions definition */
/****************************************/

IDriver *HwTSDriverAlloc(void) {
  ITSDriver_t *pxNewObj = (ITSDriver_t*)SysAlloc(sizeof(HwTSDriver_t));

  if (pxNewObj == NULL) {
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_OUT_OF_MEMORY_ERROR_CODE);
    SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("HwTSDriver - alloc failed.\r\n"));
  }
  else {
    pxNewObj->vptr = &sHwTSDriver_vtbl;
  }

  return (IDriver*)pxNewObj;
}

sys_error_code_t HwTSDriver_vtblInit(IDriver *_this, void *pxParams) {
  assert_param(_this != NULL);
  assert_param(pxParams != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  HwTSDriver_t *pxObj = (HwTSDriver_t*)_this;
  HwTSDriverParams_t *pxInitParams = (HwTSDriverParams_t*)pxParams;
  pxObj->m_xHwHandle.pxTimParams = pxInitParams->pxTimParams;

  /* Initialize the timer for the timestamp  */
  pxObj->m_xHwHandle.pxTimParams->pMxInitF();

  TIM_HandleTypeDef *pxTim = pxObj->m_xHwHandle.pxTimParams->pxTim;
  HAL_StatusTypeDef hal_res = HAL_TIM_RegisterCallback(pxTim, HAL_TIM_PERIOD_ELAPSED_CB_ID, HwTSDriver_TIM_PeriodElapsedCallback);
  UNUSED(hal_res);

  /* TIM interrupt Init */
  HAL_NVIC_SetPriority(pxObj->m_xHwHandle.pxTimParams->nIrq, HW_TS_DRV_IRQ_PRIORITY, 0);

  /* Initialize the hardware resources.*/
  s_xHwResources.m_nTimestampTick = 0U;

  return xRes;
}

sys_error_code_t HwTSDriver_vtblStart(IDriver *_this) {
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  HwTSDriver_t *pxObj = (HwTSDriver_t*)_this;
  TIM_HandleTypeDef *pxTim = pxObj->m_xHwHandle.pxTimParams->pxTim;
  UINT nPosture = TX_INT_ENABLE;

  nPosture = tx_interrupt_control(TX_INT_DISABLE);
  HAL_NVIC_EnableIRQ(pxObj->m_xHwHandle.pxTimParams->nIrq);
  LL_TIM_ClearFlag_UPDATE(pxTim->Instance);
  if(HAL_TIM_Base_Start_IT(pxTim) != HAL_OK) {
    tx_interrupt_control(nPosture);
    xRes = SYS_UNDEFINED_ERROR_CODE;
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    sys_error_handler();
  }
  tx_interrupt_control(nPosture);

  return xRes;
}

sys_error_code_t HwTSDriver_vtblStop(IDriver *_this) {
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  HwTSDriver_t *pxObj = (HwTSDriver_t*)_this;
  TIM_HandleTypeDef *pxTim = pxObj->m_xHwHandle.pxTimParams->pxTim;
  UINT nPosture = TX_INT_ENABLE;

  nPosture = tx_interrupt_control(TX_INT_DISABLE);
  HAL_NVIC_DisableIRQ(pxObj->m_xHwHandle.pxTimParams->nIrq);
  if(HAL_TIM_Base_Stop_IT(pxTim) != HAL_OK) {
    tx_interrupt_control(nPosture);
    xRes = SYS_UNDEFINED_ERROR_CODE;
    SYS_SET_LOW_LEVEL_ERROR_CODE(SYS_UNDEFINED_ERROR_CODE);
    sys_error_handler();
  }
  tx_interrupt_control(nPosture);

  return xRes;
}

sys_error_code_t HwTSDriver_vtblDoEnterPowerMode(IDriver *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
/*  HwTSDriver_t *pxObj = (HwTSDriver_t*)_this; */

  SYS_DEBUGF(SYS_DBG_LEVEL_WARNING, ("HwTsDrv: not implemented\r\n"));

  return xRes;
}

sys_error_code_t HwTSDriver_vtblReset(IDriver *_this, void *pxParams)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  HwTSDriver_t *pxObj = (HwTSDriver_t*)_this;
  UINT nPosture = TX_INT_ENABLE;

  nPosture = tx_interrupt_control(TX_INT_DISABLE);
  LL_TIM_SetCounter(pxObj->m_xHwHandle.pxTimParams->pxTim->Instance, 0);
  s_xHwResources.m_nTimestampTick = 0U;
  tx_interrupt_control(nPosture);

  return xRes;
}

uint64_t HwTSDriver_vtblGetTimestamp(ITSDriver_t *_this)
{
  assert_param(_this != NULL);
  HwTSDriver_t *pxObj = (HwTSDriver_t*)_this;
  uint32_t nPeriod;
  uint64_t nCounter;
  uint64_t nTimestamp;
  TIM_HandleTypeDef *pxTim;
  UINT nPosture = TX_INT_ENABLE;

  /* Enter a critical section*/
  nPosture = tx_interrupt_control(TX_INT_DISABLE);

  pxTim = pxObj->m_xHwHandle.pxTimParams->pxTim;
  nCounter = LL_TIM_GetCounter(pxTim->Instance);
  nPeriod = LL_TIM_GetAutoReload(pxTim->Instance) + 1U;
  if(__HAL_TIM_GET_FLAG(pxTim, TIM_FLAG_UPDATE)) {
    /* Update Event happened while already in critical section */
    /* Evaluate if the timer was read before or after the "UPDATE" event */
    if (nCounter < (nPeriod/(uint64_t)2)) {
      /* After*/
      nTimestamp = s_xHwResources.m_nTimestampTick + nCounter + nPeriod;
    }
    else {
      /* Before*/
      nTimestamp = s_xHwResources.m_nTimestampTick + nCounter;
    }
  }
  else {
    // No Update Event, just sum the timer value to the global TimeStamp
    nTimestamp = s_xHwResources.m_nTimestampTick + nCounter;
  }

  /* Exit the critical section*/
  tx_interrupt_control(nPosture);

  return nTimestamp;
}


/* Private function definition */
/*******************************/
static void HwTSDriver_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  uint64_t nPeriod = LL_TIM_GetAutoReload(htim->Instance);
  s_xHwResources.m_nTimestampTick += nPeriod + 1U;
}

#endif // (SYS_TS_CFG_ENABLE_SERVICE == 1)
