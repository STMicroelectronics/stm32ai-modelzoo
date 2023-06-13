/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
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
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32u5xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define WRLS_FLOW_Pin GPIO_PIN_15
#define WRLS_FLOW_GPIO_Port GPIOG
#define WRLS_UART4_RX_Pin GPIO_PIN_11
#define WRLS_UART4_RX_GPIO_Port GPIOC
#define USB_UCPD_CC1_Pin GPIO_PIN_15
#define USB_UCPD_CC1_GPIO_Port GPIOA
#define OCTOSPI_F_NCS_Pin GPIO_PIN_5
#define OCTOSPI_F_NCS_GPIO_Port GPIOI
#define OCTOSPI_R_IO5_Pin GPIO_PIN_0
#define OCTOSPI_R_IO5_GPIO_Port GPIOI
#define OCTOSPI_F_IO7_Pin GPIO_PIN_12
#define OCTOSPI_F_IO7_GPIO_Port GPIOH
#define PH3_BOOT0_Pin GPIO_PIN_3
#define PH3_BOOT0_GPIO_Port GPIOH
#define UCPD_PWR_Pin GPIO_PIN_5
#define UCPD_PWR_GPIO_Port GPIOB
#define WRLS_SPI2_MOSI_Pin GPIO_PIN_4
#define WRLS_SPI2_MOSI_GPIO_Port GPIOD
#define WRLS_UART4_TX_Pin GPIO_PIN_10
#define WRLS_UART4_TX_GPIO_Port GPIOC
#define T_SWCLK_Pin GPIO_PIN_14
#define T_SWCLK_GPIO_Port GPIOA
#define OCTOSPI_F_IO5_Pin GPIO_PIN_10
#define OCTOSPI_F_IO5_GPIO_Port GPIOH
#define PC14_OSC32_IN_Pin GPIO_PIN_14
#define PC14_OSC32_IN_GPIO_Port GPIOC
#define OCTOSPI_R_DQS_Pin GPIO_PIN_3
#define OCTOSPI_R_DQS_GPIO_Port GPIOE
#define T_SWO_Pin GPIO_PIN_3
#define T_SWO_GPIO_Port GPIOB
#define OCTOSPI_R_IO7_Pin GPIO_PIN_7
#define OCTOSPI_R_IO7_GPIO_Port GPIOD
#define WRLS_SPI2_MISO_Pin GPIO_PIN_3
#define WRLS_SPI2_MISO_GPIO_Port GPIOD
#define OCTOSPI_F_IO6_Pin GPIO_PIN_11
#define OCTOSPI_F_IO6_GPIO_Port GPIOH
#define PC15_OSC32_OUT_Pin GPIO_PIN_15
#define PC15_OSC32_OUT_GPIO_Port GPIOC
#define OCTOSPI_F_IO0_Pin GPIO_PIN_0
#define OCTOSPI_F_IO0_GPIO_Port GPIOF
#define USER_Button_Pin GPIO_PIN_13
#define USER_Button_GPIO_Port GPIOC
#define OCTOSPI_F_IO4_Pin GPIO_PIN_9
#define OCTOSPI_F_IO4_GPIO_Port GPIOH
#define LED_RED_Pin GPIO_PIN_6
#define LED_RED_GPIO_Port GPIOH
#define OCTOSPI_R_IO0_Pin GPIO_PIN_8
#define OCTOSPI_R_IO0_GPIO_Port GPIOF
#define OCTOSPI_F_IO1_Pin GPIO_PIN_1
#define OCTOSPI_F_IO1_GPIO_Port GPIOF
#define OCTOSPI_F_IO2_Pin GPIO_PIN_2
#define OCTOSPI_F_IO2_GPIO_Port GPIOF
#define WRLS_SPI2_SCK_Pin GPIO_PIN_1
#define WRLS_SPI2_SCK_GPIO_Port GPIOD
#define LED_GREEN_Pin GPIO_PIN_7
#define LED_GREEN_GPIO_Port GPIOH
#define OCTOSPI_R_IO4_Pin GPIO_PIN_2
#define OCTOSPI_R_IO4_GPIO_Port GPIOH
#define T_VCP_RX_Pin GPIO_PIN_10
#define T_VCP_RX_GPIO_Port GPIOA
#define T_SWDIO_Pin GPIO_PIN_13
#define T_SWDIO_GPIO_Port GPIOA
#define USB_C_P_Pin GPIO_PIN_12
#define USB_C_P_GPIO_Port GPIOA
#define OCTOSPI_R_IO2_Pin GPIO_PIN_7
#define OCTOSPI_R_IO2_GPIO_Port GPIOF
#define OCTOSPI_R_IO1_Pin GPIO_PIN_9
#define OCTOSPI_R_IO1_GPIO_Port GPIOF
#define OCTOSPI_F_IO3_Pin GPIO_PIN_3
#define OCTOSPI_F_IO3_GPIO_Port GPIOF
#define OCTOSPI_F_CLK_P_Pin GPIO_PIN_4
#define OCTOSPI_F_CLK_P_GPIO_Port GPIOF
#define T_VCP_TX_Pin GPIO_PIN_9
#define T_VCP_TX_GPIO_Port GPIOA
#define USB_C_PA11_Pin GPIO_PIN_11
#define USB_C_PA11_GPIO_Port GPIOA
#define MIC_CCK1_Pin GPIO_PIN_10
#define MIC_CCK1_GPIO_Port GPIOF
#define OCTOSPI_R_IO3_Pin GPIO_PIN_6
#define OCTOSPI_R_IO3_GPIO_Port GPIOF
#define MIC_SDINx_Pin GPIO_PIN_10
#define MIC_SDINx_GPIO_Port GPIOE
#define WRLS_WKUP_B_Pin GPIO_PIN_6
#define WRLS_WKUP_B_GPIO_Port GPIOG
#define Mems_VL53_xshut_Pin GPIO_PIN_1
#define Mems_VL53_xshut_GPIO_Port GPIOH
#define MIC_CCK0_Pin GPIO_PIN_9
#define MIC_CCK0_GPIO_Port GPIOE
#define Mems_VLX_GPIO_Pin GPIO_PIN_5
#define Mems_VLX_GPIO_GPIO_Port GPIOG
#define WRLS_NOTIFY_Pin GPIO_PIN_14
#define WRLS_NOTIFY_GPIO_Port GPIOD
#define OCTOSPI_R_IO6_Pin GPIO_PIN_3
#define OCTOSPI_R_IO6_GPIO_Port GPIOC
#define OCTOSPI_F_DQS_Pin GPIO_PIN_12
#define OCTOSPI_F_DQS_GPIO_Port GPIOF
#define USB_UCPD_FLT_Pin GPIO_PIN_8
#define USB_UCPD_FLT_GPIO_Port GPIOE
#define OCTOSPI_R_CLK_P_Pin GPIO_PIN_10
#define OCTOSPI_R_CLK_P_GPIO_Port GPIOB
#define Mems_INT_IIS2MDC_Pin GPIO_PIN_10
#define Mems_INT_IIS2MDC_GPIO_Port GPIOD
#define USB_IANA_Pin GPIO_PIN_13
#define USB_IANA_GPIO_Port GPIOD
#define Mems_INT_LPS22HH_Pin GPIO_PIN_2
#define Mems_INT_LPS22HH_GPIO_Port GPIOG
#define USB_VBUS_SENSE_Pin GPIO_PIN_14
#define USB_VBUS_SENSE_GPIO_Port GPIOF
#define OCTOSPI_R_NCS_Pin GPIO_PIN_11
#define OCTOSPI_R_NCS_GPIO_Port GPIOB
#define WRLS_SPI2_NSS_Pin GPIO_PIN_12
#define WRLS_SPI2_NSS_GPIO_Port GPIOB
#define USB_UCPD_CC2_Pin GPIO_PIN_15
#define USB_UCPD_CC2_GPIO_Port GPIOB
#define Mems_STSAFE_RESET_Pin GPIO_PIN_11
#define Mems_STSAFE_RESET_GPIO_Port GPIOF
#define Mems_ISM330DLC_INT1_Pin GPIO_PIN_11
#define Mems_ISM330DLC_INT1_GPIO_Port GPIOE
#define MIC_SDIN0_Pin GPIO_PIN_1
#define MIC_SDIN0_GPIO_Port GPIOB
#define WRLS_WKUP_W_Pin GPIO_PIN_15
#define WRLS_WKUP_W_GPIO_Port GPIOF

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
