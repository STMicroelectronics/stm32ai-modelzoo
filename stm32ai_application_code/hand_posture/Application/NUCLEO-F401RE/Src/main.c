/**
 ******************************************************************************
 * @file    main.c
 * @author  MCD Application Team
 * @brief   This is the main program for the application
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
#include "main.h"
#include "app_comm.h"
#include "app_sensor.h"

/* Global variables ----------------------------------------------------------*/
CLASSES_TABLE;
EVK_LABEL_TABLE;

/* Application context */
AppConfig_TypeDef App_Config;

/* Private function prototypes -----------------------------------------------*/
static void Hardware_Init(AppConfig_TypeDef *);
static void Software_Init(AppConfig_TypeDef *);
void SystemClock_Config(void);
static void MX_GPIO_Init(void);

/* Private user code ---------------------------------------------------------*/


/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* Configure the system clock */
  SystemClock_Config();

  /* Enable CRC HW IP block */
  __HAL_RCC_CRC_CLK_ENABLE();

  /* Perform HW configuration (sensor) related to the application  */
  Hardware_Init(&App_Config);

  /* Perform SW configuration related to the application  */
  Software_Init(&App_Config);

  /* Initialize the Neural Network library  */
  Network_Init(&App_Config);

  /* Start communication */
  Comm_Start(&App_Config);

  /* Infinite loop */
  while (1)
  {
    /* Handle a command if one has been received */
    Comm_HandleRxCMD(&App_Config);

    if (App_Config.app_run)
    {
      /* Wait for available ranging data */
      Sensor_GetRangingData(&App_Config);
      /* Pre-process data */
      Network_Preprocess(&App_Config);
      /* Run inference */
      Network_Inference(&App_Config);
      /* Post-process data */
      Network_Postprocess(&App_Config);
      /* Print output */
      Comm_Print(&App_Config);
    }
  }
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 16;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 7;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct = {0};

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOC_CLK_ENABLE();
	__HAL_RCC_GPIOH_CLK_ENABLE();
	__HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();

	/*Configure GPIO pin Output Level */
	//Set I2C enable
	HAL_GPIO_WritePin(FLEX_SPI_I2C_N_GPIO_Port, FLEX_SPI_I2C_N_Pin, GPIO_PIN_RESET);
	// Sensor Reset
	HAL_GPIO_WritePin(PWR_EN_C_GPIO_Port, PWR_EN_C_Pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(LPn_C_GPIO_Port, LPn_C_Pin, GPIO_PIN_RESET);
	HAL_Delay(100);
	HAL_GPIO_WritePin(PWR_EN_C_GPIO_Port, PWR_EN_C_Pin, GPIO_PIN_SET);
	HAL_Delay(100);
	HAL_GPIO_WritePin(LPn_C_GPIO_Port, LPn_C_Pin, GPIO_PIN_SET);


	/*Configure GPIO pin : FLEX_SPI_I2C_N_Pin */
	GPIO_InitStruct.Pin = FLEX_SPI_I2C_N_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(FLEX_SPI_I2C_N_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : INT_C_Pin */
	GPIO_InitStruct.Pin = INT_C_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(INT_C_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pins : PWR_EN_C_Pin */
	GPIO_InitStruct.Pin = PWR_EN_C_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(PWR_EN_C_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pins : LPn_C_Pin PWR_EN_L_Pin */
	GPIO_InitStruct.Pin = LPn_C_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(LPn_C_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : LD2_Pin */
  GPIO_InitStruct.Pin = LD2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);


	/* EXTI interrupt init*/
	HAL_NVIC_SetPriority(EXTI4_IRQn, 0, 0);
	HAL_NVIC_EnableIRQ(EXTI4_IRQn);

	HAL_Delay(100);

}

/**
 * @brief Initializes the WH peripherals
 * @param App_Config_Ptr pointer to application context
 */
static void Hardware_Init(AppConfig_TypeDef *App_Config_Ptr)
{
  /* MX hardware init */
  MX_GPIO_Init();

  /* Communication init */
  Comm_Init(App_Config_Ptr);

  /* TOF sensor init */
  Sensor_Init(App_Config_Ptr);

}

/* Private functions ---------------------------------------------------------*/
/**
 * @brief Initializes the application context structure
 * @param App_Config_Ptr pointer to application context
 */
static void Software_Init(AppConfig_TypeDef *App_Config_Ptr)
{
  printf("\x1b[2J");
  printf("\x1b[1;1H");
  printf("Hand Posture Getting Started version: %s\n", HANDPOSTURE_EXAMPLE_VERSION);

  /* Initialize application context values */
  App_Config_Ptr->Uart_RxRcvIndex = 0;
  App_Config_Ptr->Uart_nOverrun = 0;
  App_Config_Ptr->UartComm_CmdReady = 0;
  App_Config_Ptr->frame_count = 0;
  App_Config_Ptr->Params.gesture_gui = 0;
  App_Config_Ptr->Params.Resolution = SENSOR__MAX_NB_OF_ZONES;
  App_Config_Ptr->Params.RangingPeriod = DEFAULT_GESTURE_APP_RANGING_PERIOD;
  App_Config_Ptr->Params.IntegrationTime = DEFAULT_GESTURE_APP_INTEGRATION_TIME;
  App_Config_Ptr->app_run = false;
  App_Config_Ptr->new_data_received = false;
  App_Config_Ptr->params_modif = true;

}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
    HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_SET);
    HAL_Delay(200);
    HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);
    HAL_Delay(200);
  }
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
}
#endif /* USE_FULL_ASSERT */
