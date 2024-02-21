
/**
 ******************************************************************************
 * @file    main.h
 * @author  MCD Application Team
 * @brief   Header for main.c module.
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

/* Includes ------------------------------------------------------------------*/
#include "app_utils.h"
#include "app_network.h"

/* Exported macro ------------------------------------------------------------*/
#define HANDPOSTURE_EXAMPLE_VERSION "1.1.0"

/* Exported constants --------------------------------------------------------*/
/* Table of classes for the NN model */
extern const char *classes_table[NB_CLASSES];
extern const int evk_label_table[NB_CLASSES];

/* Exported variables --------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);


/* Private defines -----------------------------------------------------------*/

#define FLEX_SPI_I2C_N_Pin GPIO_PIN_13
#define FLEX_SPI_I2C_N_GPIO_Port GPIOC
#define USART_TX_Pin GPIO_PIN_2
#define USART_TX_GPIO_Port GPIOA
#define USART_RX_Pin GPIO_PIN_3
#define USART_RX_GPIO_Port GPIOA
#define INT_C_Pin GPIO_PIN_4
#define INT_C_GPIO_Port GPIOA
#define INT_C_EXTI_IRQn EXTI4_IRQn
#define PWR_EN_C_Pin GPIO_PIN_7
#define PWR_EN_C_GPIO_Port GPIOA
#define LPn_C_Pin GPIO_PIN_0
#define LPn_C_GPIO_Port GPIOB

#define LD2_Pin GPIO_PIN_5
#define LD2_GPIO_Port GPIOA


#endif /* __MAIN_H */
