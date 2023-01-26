/**
 ******************************************************************************
 * @file    sysinit_mx.c
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 1.2.1
 * @date    Nov 13, 2017
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#include "services/systp.h"
#include "services/syserror.h"
#include "mx.h"

#define SystemClock_Config_MX SystemClock_Config

/**
 * This type group together the components of the clock three to be modified during
 * a power mode change.
 */
typedef struct _system_clock_t{
	uint32_t latency;
	RCC_OscInitTypeDef osc;
	RCC_ClkInitTypeDef clock;
	RCC_PeriphCLKInitTypeDef periph_clock;
} system_clock_t;

/**
 * It is used to save and restore the system clock during the power mode switch.
 */
static system_clock_t system_clock;

// Private member function declaration
// ***********************************


// Public API definition
// *********************

void SystemClock_Config_MX(void) {
	RCC_OscInitTypeDef RCC_OscInitStruct = {0};
	RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
	RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

	/** Configure the main internal regulator output voltage
	 */
	if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1_BOOST) != HAL_OK)
	{
		sys_error_handler();
	}
	/** Configure LSE Drive Capability
	 */
	HAL_PWR_EnableBkUpAccess();
	__HAL_RCC_LSEDRIVE_CONFIG(RCC_LSEDRIVE_LOW);
	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE|RCC_OSCILLATORTYPE_LSE|RCC_OSCILLATORTYPE_HSI48;
	RCC_OscInitStruct.HSEState = RCC_HSE_ON;
	RCC_OscInitStruct.HSI48State = RCC_HSI48_ON;
	RCC_OscInitStruct.LSEState = RCC_LSE_ON;
	RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
	RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
	RCC_OscInitStruct.PLL.PLLM = 2;
	RCC_OscInitStruct.PLL.PLLN = 30;
	RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
	RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
	RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
	{
		sys_error_handler();
	}
	/** Initializes the CPU, AHB and APB busses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
			|RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
	{
		sys_error_handler();
	}
	PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_RTC|RCC_PERIPHCLK_USART2
			|RCC_PERIPHCLK_I2C2|RCC_PERIPHCLK_DFSDM1
			|RCC_PERIPHCLK_ADC|RCC_PERIPHCLK_USB;
	PeriphClkInit.Usart2ClockSelection = RCC_USART2CLKSOURCE_PCLK1;
	PeriphClkInit.I2c2ClockSelection = RCC_I2C2CLKSOURCE_PCLK1;
	PeriphClkInit.AdcClockSelection = RCC_ADCCLKSOURCE_PLLSAI1;
	PeriphClkInit.Dfsdm1ClockSelection = RCC_DFSDM1CLKSOURCE_PCLK;
	PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_HSI48;
	PeriphClkInit.RTCClockSelection = RCC_RTCCLKSOURCE_LSE;
	PeriphClkInit.PLLSAI1.PLLSAI1Source = RCC_PLLSOURCE_HSE;
	PeriphClkInit.PLLSAI1.PLLSAI1M = 5;
	PeriphClkInit.PLLSAI1.PLLSAI1N = 96;
	PeriphClkInit.PLLSAI1.PLLSAI1P = RCC_PLLP_DIV25;
	PeriphClkInit.PLLSAI1.PLLSAI1Q = RCC_PLLQ_DIV4;
	PeriphClkInit.PLLSAI1.PLLSAI1R = RCC_PLLR_DIV4;
	PeriphClkInit.PLLSAI1.PLLSAI1ClockOut = RCC_PLLSAI1_ADC1CLK;
	if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
	{
		sys_error_handler();
	}

	__HAL_RCC_PWR_CLK_ENABLE();
}

void SystemClock_Backup(void)
{
	HAL_RCC_GetOscConfig(&(system_clock.osc));
	HAL_RCC_GetClockConfig(&(system_clock.clock), &(system_clock.latency));
	HAL_RCCEx_GetPeriphCLKConfig(&(system_clock.periph_clock));
}

/**
 * @brief  Restore original clock parameters
 * @retval Process result
 *         @arg SMPS_OK or SMPS_KO
 */
void SystemClock_Restore(void)
{
	/* SEQUENCE:
	 *   1. Set PWR regulator to SCALE1_BOOST
	 *   2. PLL ON
	 *   3. Set SYSCLK source to PLL
	 *
	 * NOTE:
	 *   Do not change or update the base-clock source (e.g. MSI and LSE)
	 */

	if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1_BOOST) != HAL_OK) {
		sys_error_handler();
	}

	if (__HAL_RCC_GET_SYSCLK_SOURCE() != RCC_CFGR_SWS_PLL) {
		if (HAL_RCC_OscConfig(&(system_clock.osc)) != HAL_OK) {
			sys_error_handler();
		}
	}

	if (HAL_RCC_ClockConfig(&(system_clock.clock), system_clock.latency) != HAL_OK) {
		sys_error_handler();
	}
}

void SysPowerConfig() {
	// Enable Power Clock
	__HAL_RCC_PWR_CLK_ENABLE();

	// Select MSI as system clock source after Wake Up from Stop mode
	__HAL_RCC_WAKEUPSTOP_CLK_CONFIG(RCC_STOP_WAKEUPCLOCK_MSI);


	// This function is called in the early step of the system initialization.
	// All the PINs used by the application are reconfigured later by the application tasks.

	GPIO_InitTypeDef GPIO_InitStruct = {0};

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();
	__HAL_RCC_GPIOC_CLK_ENABLE();
	__HAL_RCC_GPIOD_CLK_ENABLE();
	__HAL_RCC_GPIOE_CLK_ENABLE();

	__HAL_RCC_GPIOG_CLK_ENABLE();
	HAL_PWREx_EnableVddIO2();
	__HAL_RCC_GPIOF_CLK_ENABLE();

	GPIO_InitStruct.Pin = PA0_Pin|PA1_Pin|GPIO_PIN_2|GPIO_PIN_3|DAC1_OUT1_Pin|GPIO_PIN_6|GPIO_PIN_6
			|GPIO_PIN_7|PA9_Pin|PA10_Pin|GPIO_PIN_11|GPIO_PIN_12|GPIO_PIN_15;
	GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

	GPIO_InitStruct.Pin = CHRGB0_Pin|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7|PB8_Pin
			|PB9_Pin|GPIO_PIN_10|GPIO_PIN_11|GPIO_PIN_12|GPIO_PIN_13|PB14_Pin|GPIO_PIN_15;
	HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

	GPIO_InitStruct.Pin = GPIO_PIN_0|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3|GPIO_PIN_5|GPIO_PIN_7|GPIO_PIN_8
			|GPIO_PIN_9|GPIO_PIN_10|GPIO_PIN_11|GPIO_PIN_12|GPIO_PIN_13;
	HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

	GPIO_InitStruct.Pin = GPIO_PIN_0|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7|GPIO_PIN_8
			|GPIO_PIN_9|GPIO_PIN_10|GPIO_PIN_11|GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;
	HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);

	GPIO_InitStruct.Pin = GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7|GPIO_PIN_8
			|GPIO_PIN_9|GPIO_PIN_10|GPIO_PIN_11|GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;
	HAL_GPIO_Init(PE12_GPIO_Port, &GPIO_InitStruct);

	GPIO_InitStruct.Pin = GPIO_PIN_0|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7|GPIO_PIN_8
			|GPIO_PIN_9|GPIO_PIN_10|GPIO_PIN_11|GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;
	HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);

	GPIO_InitStruct.Pin = GPIO_PIN_0|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7|GPIO_PIN_8
			|GPIO_PIN_9|GPIO_PIN_10|GPIO_PIN_12|GPIO_PIN_13;
	HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOE_CLK_DISABLE();
	__HAL_RCC_GPIOB_CLK_DISABLE();
	__HAL_RCC_GPIOD_CLK_DISABLE();
	__HAL_RCC_GPIOC_CLK_DISABLE();
	__HAL_RCC_GPIOA_CLK_DISABLE();
	__HAL_RCC_GPIOG_CLK_DISABLE();
	__HAL_RCC_GPIOF_CLK_DISABLE();
	HAL_PWREx_DisableVddIO2();
}

/**
 * Initializes the Global MSP.
 */
void HAL_MspInit(void)
{
	__HAL_RCC_SYSCFG_CLK_ENABLE();
	__HAL_RCC_PWR_CLK_ENABLE();

	HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4);

	// System interrupt init
	// MemoryManagement_IRQn interrupt configuration
	HAL_NVIC_SetPriority(MemoryManagement_IRQn, 0, 0);
	// BusFault_IRQn interrupt configuration
	HAL_NVIC_SetPriority(BusFault_IRQn, 0, 0);
	// UsageFault_IRQn interrupt configuration
	HAL_NVIC_SetPriority(UsageFault_IRQn, 0, 0);
	// SVCall_IRQn interrupt configuration
	HAL_NVIC_SetPriority(SVCall_IRQn, 0, 0);
	// DebugMonitor_IRQn interrupt configuration
	HAL_NVIC_SetPriority(DebugMonitor_IRQn, 0, 0);
	// PendSV_IRQn interrupt configuration
	HAL_NVIC_SetPriority(PendSV_IRQn, 15, 0);
	// SysTick_IRQn interrupt configuration
	HAL_NVIC_SetPriority(SysTick_IRQn, 15, 0);
}

// Private function definition
// ***************************
