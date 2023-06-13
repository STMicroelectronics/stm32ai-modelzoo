/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    stm32u5xx_it.c
  * @brief   Interrupt Service Routines.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32u5xx_it.h"
#include "drivers/EXTIPinMap.h"
#include "tx_port.h"
#include "tx_execution_profile.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN TD */

/* USER CODE END TD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/* External variables --------------------------------------------------------*/
extern TIM_HandleTypeDef htim6;
extern TIM_HandleTypeDef htim7;
extern DMA_HandleTypeDef handle_GPDMA1_Channel3;
extern DMA_HandleTypeDef handle_GPDMA1_Channel2;
extern DMA_HandleTypeDef handle_GPDMA1_Channel5;
extern I2C_HandleTypeDef hi2c2;
extern UART_HandleTypeDef huart1;

/* USER CODE BEGIN EV */
// Forward function declarations
// ****************************

/**
 * Map one EXTI to n callback based on the GPIO PIN.
 */
static inline void ExtiDefISR(void);


// External variables
// ******************

EXTI_DECLARE_PIN2F_MAP()

// Private function definition
// ***************************

void ExtiDefISR() {
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
	_tx_execution_isr_enter();             // Call the ISR enter function
#endif
  EXTIPin2CallbckMap xMap = EXTI_GET_P2F_MAP();
  for (int i=0; xMap[i].pfCallback != NULL; i++) {
    if (__HAL_GPIO_EXTI_GET_IT(xMap[i].nPin)) {
      /* EXTI line interrupt detected */
      __HAL_GPIO_EXTI_CLEAR_IT(xMap[i].nPin);
      xMap[i].pfCallback(xMap[i].nPin);
    }
  }
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
    _tx_execution_isr_exit();              // Call the ISR exit function
#endif
}
/* USER CODE END EV */

/******************************************************************************/
/*           Cortex Processor Interruption and Exception Handlers          */
/******************************************************************************/
/**
  * @brief This function handles Non maskable interrupt.
  */
void NMI_Handler(void)
{
  /* USER CODE BEGIN NonMaskableInt_IRQn 0 */

  /* USER CODE END NonMaskableInt_IRQn 0 */
  /* USER CODE BEGIN NonMaskableInt_IRQn 1 */
  while (1)
  {
  }
  /* USER CODE END NonMaskableInt_IRQn 1 */
}

/**
  * @brief This function handles Hard fault interrupt.
  */
void HardFault_Handler(void)
{
  /* USER CODE BEGIN HardFault_IRQn 0 */

  /* USER CODE END HardFault_IRQn 0 */
  while (1)
  {
    /* USER CODE BEGIN W1_HardFault_IRQn 0 */
    /* USER CODE END W1_HardFault_IRQn 0 */
  }
}

/**
  * @brief This function handles Memory management fault.
  */
void MemManage_Handler(void)
{
  /* USER CODE BEGIN MemoryManagement_IRQn 0 */

  /* USER CODE END MemoryManagement_IRQn 0 */
  while (1)
  {
    /* USER CODE BEGIN W1_MemoryManagement_IRQn 0 */
    /* USER CODE END W1_MemoryManagement_IRQn 0 */
  }
}

/**
  * @brief This function handles Prefetch fault, memory access fault.
  */
void BusFault_Handler(void)
{
  /* USER CODE BEGIN BusFault_IRQn 0 */

  /* USER CODE END BusFault_IRQn 0 */
  while (1)
  {
    /* USER CODE BEGIN W1_BusFault_IRQn 0 */
    /* USER CODE END W1_BusFault_IRQn 0 */
  }
}

/**
  * @brief This function handles Undefined instruction or illegal state.
  */
void UsageFault_Handler(void)
{
  /* USER CODE BEGIN UsageFault_IRQn 0 */

  /* USER CODE END UsageFault_IRQn 0 */
  while (1)
  {
    /* USER CODE BEGIN W1_UsageFault_IRQn 0 */
    /* USER CODE END W1_UsageFault_IRQn 0 */
  }
}

/**
  * @brief This function handles Debug monitor.
  */
void DebugMon_Handler(void)
{
  /* USER CODE BEGIN DebugMonitor_IRQn 0 */

  /* USER CODE END DebugMonitor_IRQn 0 */
  /* USER CODE BEGIN DebugMonitor_IRQn 1 */

  /* USER CODE END DebugMonitor_IRQn 1 */
}

/******************************************************************************/
/* STM32U5xx Peripheral Interrupt Handlers                                    */
/* Add here the Interrupt Handlers for the used peripherals.                  */
/* For the available peripheral interrupt handler names,                      */
/* please refer to the startup file (startup_stm32u5xx.s).                    */
/******************************************************************************/

/**
  * @brief This function handles TIM6 global interrupt.
  */
void TIM6_IRQHandler(void)
{
  /* USER CODE BEGIN TIM6_IRQn 0 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
	_tx_execution_isr_enter();             // Call the ISR enter function
#endif
  /* USER CODE END TIM6_IRQn 0 */
  HAL_TIM_IRQHandler(&htim6);
  /* USER CODE BEGIN TIM6_IRQn 1 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
    _tx_execution_isr_exit();              // Call the ISR exit function
#endif
  /* USER CODE END TIM6_IRQn 1 */
}

/* USER CODE BEGIN 1 */
void TIM7_IRQHandler(void)
{
  /* USER CODE BEGIN TIM6_IRQn 0 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
	_tx_execution_isr_enter();             // Call the ISR enter function
#endif
  /* USER CODE END TIM6_IRQn 0 */
  HAL_TIM_IRQHandler(&htim7);
  /* USER CODE BEGIN TIM6_IRQn 1 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
    _tx_execution_isr_exit();              // Call the ISR exit function
#endif
  /* USER CODE END TIM6_IRQn 1 */
}

void GPDMA1_Channel2_IRQHandler(void)
{
  /* USER CODE BEGIN DMA1_Channel2_IRQn 0 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
	_tx_execution_isr_enter();             // Call the ISR enter function
#endif
  /* USER CODE END DMA1_Channel2_IRQn 0 */
  HAL_DMA_IRQHandler(&handle_GPDMA1_Channel2);
  /* USER CODE BEGIN DMA1_Channel2_IRQn 1 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
    _tx_execution_isr_exit();              // Call the ISR exit function
#endif
  /* USER CODE END DMA1_Channel2_IRQn 1 */
}

void GPDMA1_Channel3_IRQHandler(void)
{
  /* USER CODE BEGIN DMA1_Channel3_IRQn 0 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
	_tx_execution_isr_enter();             // Call the ISR enter function
#endif
  /* USER CODE END DMA1_Channel3_IRQn 0 */
  HAL_DMA_IRQHandler(&handle_GPDMA1_Channel3);
  /* USER CODE BEGIN DMA1_Channel3_IRQn 1 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
    _tx_execution_isr_exit();              // Call the ISR exit function
#endif
  /* USER CODE END DMA1_Channel3_IRQn 1 */
}

/**
  * @brief This function handles GPDMA1 Channel 5 global interrupt.
  */
void GPDMA1_Channel5_IRQHandler(void)
{
  /* USER CODE BEGIN GPDMA1_Channel5_IRQn 0 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
	_tx_execution_isr_enter();             // Call the ISR enter function
#endif
  /* USER CODE END GPDMA1_Channel5_IRQn 0 */
  HAL_DMA_IRQHandler(&handle_GPDMA1_Channel5);
  /* USER CODE BEGIN GPDMA1_Channel5_IRQn 1 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
    _tx_execution_isr_exit();              // Call the ISR exit function
#endif
  /* USER CODE END GPDMA1_Channel5_IRQn 1 */
}

/* USER CODE END 1 */

/**
  * @brief This function handles I2C2 Event interrupt.
  */
void I2C2_EV_IRQHandler(void)
{
  /* USER CODE BEGIN I2C2_EV_IRQn 0 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//	_tx_execution_isr_enter();             // Call the ISR enter function
//#endif
  /* USER CODE END I2C2_EV_IRQn 0 */
  HAL_I2C_EV_IRQHandler(&hi2c2);
  /* USER CODE BEGIN I2C2_EV_IRQn 1 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//    _tx_execution_isr_exit();              // Call the ISR exit function
//#endif
  /* USER CODE END I2C2_EV_IRQn 1 */
}

/**
  * @brief This function handles I2C2 Error interrupt.
  */
void I2C2_ER_IRQHandler(void)
{
  /* USER CODE BEGIN I2C2_ER_IRQn 0 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
	_tx_execution_isr_enter();             // Call the ISR enter function
#endif
  /* USER CODE END I2C2_ER_IRQn 0 */
  HAL_I2C_ER_IRQHandler(&hi2c2);
  /* USER CODE BEGIN I2C2_ER_IRQn 1 */
#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
    _tx_execution_isr_exit();              // Call the ISR exit function
#endif
  /* USER CODE END I2C2_ER_IRQn 1 */
}

/* USER CODE BEGIN 1 */

/* USER CODE END 1 */

/**
  * @brief This function handles EXTI Line11 interrupt.
  */
void EXTI11_IRQHandler(void)
{
  /* USER CODE BEGIN EXTI11_IRQn 0 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//	_tx_execution_isr_enter();             // Call the ISR enter function
//#endif
  /* USER CODE END EXTI11_IRQn 0 */
	ExtiDefISR();
  /* USER CODE BEGIN EXTI11_IRQn 1 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//    _tx_execution_isr_exit();              // Call the ISR exit function
//#endif
  /* USER CODE END EXTI11_IRQn 1 */
}

/**
  * @brief This function handles EXTI Line10 interrupt.
  */

void EXTI10_IRQHandler(void)
{
  /* USER CODE BEGIN EXTI10_IRQn 0 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//	_tx_execution_isr_enter();             // Call the ISR enter function
//#endif
  /* USER CODE END EXTI10_IRQn 0 */
	ExtiDefISR();
  /* USER CODE BEGIN EXTI10_IRQn 1 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//    _tx_execution_isr_exit();              // Call the ISR exit function
//#endif
  /* USER CODE END EXTI10_IRQn 1 */
}

/**
  * @brief This function handles EXTI Line2 interrupt.
  */

void EXTI2_IRQHandler(void)
{
  /* USER CODE BEGIN EXTI2_IRQn 0 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//	_tx_execution_isr_enter();             // Call the ISR enter function
//#endif
  /* USER CODE END EXTI2_IRQn 0 */
	ExtiDefISR();
  /* USER CODE BEGIN EXTI2_IRQn 1 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//    _tx_execution_isr_exit();              // Call the ISR exit function
//#endif
  /* USER CODE END EXTI2_IRQn 1 */
}

/**
  * @brief This function handles EXTI Line13 interrupt.
  */
void EXTI13_IRQHandler(void)
{
  /* USER CODE BEGIN EXTI13_IRQn 0 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//	_tx_execution_isr_enter();             // Call the ISR enter function
//#endif
  /* USER CODE END EXTI13_IRQn 0 */
	ExtiDefISR();
  /* USER CODE BEGIN EXTI13_IRQn 1 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//    _tx_execution_isr_exit();              // Call the ISR exit function
//#endif
  /* USER CODE END EXTI13_IRQn 1 */
}

/**
  * @brief This function handles USART1 global interrupt.
  */
void USART1_IRQHandler(void)
{
  /* USER CODE BEGIN USART1_IRQn 0 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//	_tx_execution_isr_enter();             // Call the ISR enter function
//#endif
  /* USER CODE END USART1_IRQn 0 */
  HAL_UART_IRQHandler(&huart1);
  /* USER CODE BEGIN USART1_IRQn 1 */
//#if (defined(TX_ENABLE_EXECUTION_CHANGE_NOTIFY) || defined(TX_EXECUTION_PROFILE_ENABLE))
//    _tx_execution_isr_exit();              // Call the ISR exit function
//#endif
  /* USER CODE END USART1_IRQn 1 */
}
