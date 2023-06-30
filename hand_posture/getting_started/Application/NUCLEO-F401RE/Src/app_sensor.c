/**
 ******************************************************************************
 * @file    app_sensor.c
 * @author  MCD Application Team
 * @brief   Library to manage TOF sensor related operation
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

/* Includes ------------------------------------------------------------------*/
#include "app_sensor.h"
#include "vl53lmz_plugin_xtalk.h"

/* Global variables ----------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;

/* Private defines -----------------------------------------------------------*/

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c1;

/* Private function prototypes -----------------------------------------------*/
static uint8_t apps_layer_vl53lmz_Configure(AppConfig_TypeDef *App_Config);

/* Private function definitions ----------------------------------------------*/

/**
 * @brief Configure the VL53LMZ sensor
 * @param (AppConfig_TypeDef) *App_Config : configuration to be applied
 * @return (int) status : 0 if OK
 */
static uint8_t apps_layer_vl53lmz_Configure(AppConfig_TypeDef *App_Config)
{
  uint8_t status = 0;

  status = vl53lmz_set_resolution(&(App_Config->ToFDev),
      App_Config->Params.Resolution==RESOLUTION_16 ? VL53LMZ_RESOLUTION_4X4 : VL53LMZ_RESOLUTION_8X8);
  if (status != VL53LMZ_STATUS_OK){
    printf("ERROR at %s(%d) : vl53lmz_set_resolution failed : %d\n",__func__, __LINE__,status);
    return(status);
  }

  status = vl53lmz_set_ranging_frequency_hz(&(App_Config->ToFDev), (MILLIHERTZ_TO_HERTZ/App_Config->Params.RangingPeriod));
  if (status != VL53LMZ_STATUS_OK){
    printf("ERROR at %s(%d) : vl53lmz_set_ranging_period_ms failed : %d\n",__func__, __LINE__,status);
    return(status);
  }

  status = vl53lmz_set_integration_time_ms(&(App_Config->ToFDev), App_Config->Params.IntegrationTime);
  if (status != VL53LMZ_STATUS_OK){
    printf("ERROR at %s(%d) : vl53lmz_set_integration_time_ms failed : %d\n",__func__, __LINE__,status);
    return(status);
  }

  status = vl53lmz_set_xtalk_margin(&(App_Config->ToFDev), XTALK_MARGIN);
  if (status != VL53LMZ_STATUS_OK){
    printf("ERROR at %s(%d) : vl53lmz_set_xtalk_margin failed : %d\n",__func__, __LINE__,status);
    return(status);
  }

  /* Set Closest target first */
  status = vl53lmz_set_target_order(&(App_Config->ToFDev), VL53LMZ_TARGET_ORDER_CLOSEST);
  if (status != VL53LMZ_STATUS_OK){
    printf("ERROR at %s(%d) : vl53lmz_set_target_order failed : %d\n",__func__, __LINE__,status);
    return(status);
  }

  /* Sharpener sets to 5 */
  status = vl53lmz_set_sharpener_percent(&(App_Config->ToFDev), 5);
  if (status != VL53LMZ_STATUS_OK){
    printf("ERROR at %s(%d) : vl53lmz_set_sharpener_percent failed : %d\n",__func__, __LINE__,status);
    return(status);
  }

  /* Reset the flag indicating the parameters has been modified */
  App_Config->params_modif = false;

  return(status);
}

/* Public function definitions -----------------------------------------------*/

/**
 * @brief  SENSOR Initialization
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Sensor_Init(AppConfig_TypeDef *App_Config)
{
  /* I2C1 Initialization */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 1000000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    printf("I2C init failed\n");
    Error_Handler();
  }

  /* Initialize the sensor platform */
  if (LMZ_platform_init(&(App_Config->ToFDev.platform)) < 0)
  {
    printf("LMZ_platform_init failed\n");
    Error_Handler();
  }

  /* Initialize the sensor */
  if (vl53lmz_init(&(App_Config->ToFDev)) != VL53LMZ_STATUS_OK)
  {
    printf("vl53lmz_init failed\n");
    Error_Handler();
  }

}

/**
 * @brief  SENSOR Start ranging
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Sensor_StartRanging(AppConfig_TypeDef *App_Config)
{
  /* If parameters has been modified */
  if (App_Config->params_modif)
  {
    /* Configure the sensor */
    if (apps_layer_vl53lmz_Configure(App_Config) != VL53LMZ_STATUS_OK)
    {
      printf("VL53LMZ_Configure failed\n");
      Error_Handler();
    }
  }

  /* Start the sensor */
  if (vl53lmz_start_ranging(&(App_Config->ToFDev)) != VL53LMZ_STATUS_OK)
  {
    printf("vl53lmz_start_ranging failed\n");
    Error_Handler();
  }

  /* Set the LED */
  HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_SET);

}

/**
 * @brief  SENSOR Get ranging data
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Sensor_GetRangingData(AppConfig_TypeDef *App_Config)
{
  /* If parameters has been modified */
  if (App_Config->params_modif)
  {
    /* Configure the sensor */
    if (apps_layer_vl53lmz_Configure(App_Config) != VL53LMZ_STATUS_OK)
    {
      printf("VL53LMZ_Configure failed\n");
      Error_Handler();
    }
  }

  /* Wait for the sensor to get data */
  if (wait_for_ToF_interrupt(&(App_Config->ToFDev.platform), &(App_Config->IntrCount)) == 0)
  {
    /* Get data from the sensor */
    if (vl53lmz_get_ranging_data(&(App_Config->ToFDev), &(App_Config->RangingData)) != VL53LMZ_STATUS_OK)
    {
      printf("vl53lmz_get_ranging_data failed\n");
      Error_Handler();
    }
    /* Set the flat indicating a new data has been received */
    App_Config->new_data_received = true;
  }
  else
  {
    /* Reset the flag indicating a new data has been received */
    App_Config->new_data_received = false;
  }

}

/**
 * @brief  SENSOR Stop ranging
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Sensor_StopRanging(AppConfig_TypeDef *App_Config)
{
  /* If the application is running */
  if (App_Config->app_run)
  {
    /* Stop the sensor */
    if (vl53lmz_stop_ranging(&(App_Config->ToFDev)) != VL53LMZ_STATUS_OK)
    {
      printf("vl53lmz_stop_ranging failed\n");
      Error_Handler();
    }
  }

  /* Reset the LED */
  HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

}

/**
 * @brief  SENSOR GPIO interrupt handler
 * @param  GPIO_Pin GPIO pin number
 * @retval None
 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  if (GPIO_Pin == INT_C_Pin)
  {
    App_Config.IntrCount++;
  }

}
