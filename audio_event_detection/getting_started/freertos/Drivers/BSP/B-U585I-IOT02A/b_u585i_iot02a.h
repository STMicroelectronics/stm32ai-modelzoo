/**
  ******************************************************************************
  * @file    b_u585i_iot02a.h
  * @author  MCD Application Team
  * @brief   This file contains definitions for b_u585i_iot02a.c:
  *          LEDs
  *          USER push-button
  *          COM port
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef B_U585I_IOT02A_H
#define B_U585I_IOT02A_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "b_u585i_iot02a_conf.h"
#include "b_u585i_iot02a_errno.h"

#if (USE_BSP_COM_FEATURE > 0)
#if (USE_COM_LOG > 0)
#ifndef __GNUC__
#include "stdio.h"
#endif /* __GNUC__ */
#endif /* USE_COM_LOG */
#endif /* USE_BSP_COM_FEATURE */

/** @addtogroup BSP
  * @{
  */

/** @addtogroup B_U585I_IOT02A
  * @{
  */

/** @addtogroup B_U585I_IOT02A_LOW_LEVEL
  * @{
  */

/** @defgroup B_U585I_IOT02A_LOW_LEVEL_Exported_Types LOW LEVEL Exported Types
  * @{
  */
typedef enum
{
  LED6 = 0U,
  LED_RED = LED6,
  LED7 = 1U,
  LED_GREEN = LED7,
  LEDn
} Led_TypeDef;

typedef enum
{
  BUTTON_USER = 0U,
  BUTTONn
} Button_TypeDef;

typedef enum
{
  BUTTON_MODE_GPIO = 0U,
  BUTTON_MODE_EXTI = 1U
} ButtonMode_TypeDef;

#if (USE_BSP_COM_FEATURE > 0)
typedef enum
{
  COM1 = 0U,
  COMn
} COM_TypeDef;

typedef enum
{
  COM_STOPBITS_1     =   UART_STOPBITS_1,
} COM_StopBitsTypeDef;

typedef enum
{
  COM_PARITY_NONE     =  UART_PARITY_NONE,
  COM_PARITY_EVEN     =  UART_PARITY_EVEN,
  COM_PARITY_ODD      =  UART_PARITY_ODD,
} COM_ParityTypeDef;

typedef enum
{
  COM_HWCONTROL_NONE    =  UART_HWCONTROL_NONE,
  COM_HWCONTROL_RTS     =  UART_HWCONTROL_RTS,
  COM_HWCONTROL_CTS     =  UART_HWCONTROL_CTS,
  COM_HWCONTROL_RTS_CTS =  UART_HWCONTROL_RTS_CTS,
} COM_HwFlowCtlTypeDef;

typedef enum
{
  COM_WORDLENGTH_7B = UART_WORDLENGTH_7B,
  COM_WORDLENGTH_8B = UART_WORDLENGTH_8B,
  COM_WORDLENGTH_9B = UART_WORDLENGTH_9B,
} COM_WordLengthTypeDef;

typedef struct
{
  uint32_t              BaudRate;
  COM_WordLengthTypeDef WordLength;
  COM_StopBitsTypeDef   StopBits;
  COM_ParityTypeDef     Parity;
  COM_HwFlowCtlTypeDef  HwFlowCtl;
} COM_InitTypeDef;

#define MX_UART_InitTypeDef COM_InitTypeDef

#endif /* (USE_BSP_COM_FEATURE > 0) */

#if (USE_HAL_UART_REGISTER_CALLBACKS == 1)
typedef struct
{
  void (* pMspInitCb)(UART_HandleTypeDef *);
  void (* pMspDeInitCb)(UART_HandleTypeDef *);
} BSP_COM_Cb_t;
#endif /* (USE_HAL_UART_REGISTER_CALLBACKS == 1) */

/**
  * @}
  */

/** @defgroup B_U585I_IOT02A_LOW_LEVEL_Exported_Constants LOW LEVEL Exported Constants
  * @{
  */
/**
  * @brief  Define for B_U585I_IOT02A board
  */
#if !defined (USE_B_U585I_IOT02A)
#define USE_B_U585I_IOT02A
#endif /* USE_B_U585I_IOT02A */

/**
  * @brief B_U585I_IOT02A BSP Driver version number V1.0.0
  */
#define B_U585I_IOT02A_BSP_VERSION_MAIN   (uint32_t)(0x01U) /*!< [31:24] main version */
#define B_U585I_IOT02A_BSP_VERSION_SUB1   (uint32_t)(0x00U) /*!< [23:16] sub1 version */
#define B_U585I_IOT02A_BSP_VERSION_SUB2   (uint32_t)(0x00U) /*!< [15:8]  sub2 version */
#define B_U585I_IOT02A_BSP_VERSION_RC     (uint32_t)(0x00U) /*!< [7:0]  release candidate */
#define B_U585I_IOT02A_BSP_VERSION        ((B_U585I_IOT02A_BSP_VERSION_MAIN << 24)\
                                           |(B_U585I_IOT02A_BSP_VERSION_SUB1 << 16)\
                                           |(B_U585I_IOT02A_BSP_VERSION_SUB2 << 8 )\
                                           |(B_U585I_IOT02A_BSP_VERSION_RC))

#define B_U585I_IOT02A_BSP_BOARD_NAME  "B_U585I_IOT02A";
#define B_U585I_IOT02A_BSP_BOARD_ID    "MB1551A";

/** @defgroup B_U585I_IOT02A_LOW_LEVEL_LED LOW LEVEL LED
  * @{
  */
#define LED6_GPIO_PORT                   GPIOH
#define LED6_GPIO_CLK_ENABLE()           __HAL_RCC_GPIOH_CLK_ENABLE()
#define LED6_GPIO_CLK_DISABLE()          __HAL_RCC_GPIOH_CLK_DISABLE()
#define LED6_PIN                         GPIO_PIN_6

#define LED7_GPIO_PORT                   GPIOH
#define LED7_GPIO_CLK_ENABLE()           __HAL_RCC_GPIOH_CLK_ENABLE()
#define LED7_GPIO_CLK_DISABLE()          __HAL_RCC_GPIOH_CLK_DISABLE()
#define LED7_PIN                         GPIO_PIN_7

/**
  * @}
  */
/** @defgroup B_U585I_IOT02A_LOW_LEVEL_BUTTON LOW LEVEL BUTTON
  * @{
  */
/* Button state */
#define BUTTON_RELEASED                    0U
#define BUTTON_PRESSED                     1U

/**
  * @brief User push-button
  */
#define BUTTON_USER_PIN                       GPIO_PIN_13
#define BUTTON_USER_GPIO_PORT                 GPIOC
#define BUTTON_USER_GPIO_CLK_ENABLE()         __HAL_RCC_GPIOC_CLK_ENABLE()
#define BUTTON_USER_GPIO_CLK_DISABLE()        __HAL_RCC_GPIOC_CLK_DISABLE()
#define BUTTON_USER_EXTI_IRQn                 EXTI13_IRQn
#define BUTTON_USER_EXTI_LINE                 EXTI_LINE_13
/**
  * @}
  */

/** @defgroup B_U585I_IOT02A_LOW_LEVEL_COM LOW LEVEL COM
  * @{
  */
#ifndef USE_BSP_COM_FEATURE
#define USE_BSP_COM_FEATURE    0U
#endif /* USE_BSP_COM_FEATURE */
#if (USE_BSP_COM_FEATURE > 0)
/**
  * @brief Definition for COM port1, connected to USART1
  */
#define COM1_UART                     USART1
#define COM1_CLK_ENABLE()             __HAL_RCC_USART1_CLK_ENABLE()
#define COM1_CLK_DISABLE()            __HAL_RCC_USART1_CLK_DISABLE()

#define COM1_TX_PIN                   GPIO_PIN_9
#define COM1_TX_GPIO_PORT             GPIOA
#define COM1_TX_GPIO_CLK_ENABLE()     __HAL_RCC_GPIOA_CLK_ENABLE()
#define COM1_TX_GPIO_CLK_DISABLE()    __HAL_RCC_GPIOA_CLK_DISABLE()
#define COM1_TX_AF                    GPIO_AF7_USART1

#define COM1_RX_PIN                   GPIO_PIN_10
#define COM1_RX_GPIO_PORT             GPIOA
#define COM1_RX_GPIO_CLK_ENABLE()     __HAL_RCC_GPIOA_CLK_ENABLE()
#define COM1_RX_GPIO_CLK_DISABLE()    __HAL_RCC_GPIOA_CLK_DISABLE()
#define COM1_RX_AF                    GPIO_AF7_USART1

#define COM_POLL_TIMEOUT              1000U
#endif /* (USE_BSP_COM_FEATURE > 0) */
/**
  * @}
  */

/**
  * @}
  */

/** @addtogroup B_U585I_IOT02A_LOW_LEVEL_Exported_Variables
  * @{
  */
extern EXTI_HandleTypeDef hpb_exti[];
#if (USE_BSP_COM_FEATURE > 0)
extern UART_HandleTypeDef hcom_uart[];
extern USART_TypeDef *COM_UART[];
#endif /* USE_BSP_COM_FEATURE */
/**
  * @}
  */

/** @addtogroup B_U585I_IOT02A_LOW_LEVEL_Exported_Functions
  * @{
  */
int32_t  BSP_GetVersion(void);
const uint8_t *BSP_GetBoardName(void);
const uint8_t *BSP_GetBoardID(void);

int32_t  BSP_LED_Init(Led_TypeDef Led);
int32_t  BSP_LED_DeInit(Led_TypeDef Led);
int32_t  BSP_LED_On(Led_TypeDef Led);
int32_t  BSP_LED_Off(Led_TypeDef Led);
int32_t  BSP_LED_Toggle(Led_TypeDef Led);
int32_t  BSP_LED_GetState(Led_TypeDef Led);

int32_t  BSP_PB_Init(Button_TypeDef Button, ButtonMode_TypeDef ButtonMode);
int32_t  BSP_PB_DeInit(Button_TypeDef Button);
int32_t  BSP_PB_GetState(Button_TypeDef Button);
void     BSP_PB_Callback(Button_TypeDef Button);
void     BSP_PB_IRQHandler(Button_TypeDef Button);

#if (USE_BSP_COM_FEATURE > 0)
int32_t  BSP_COM_Init(COM_TypeDef COM, COM_InitTypeDef *COM_Init);
int32_t  BSP_COM_DeInit(COM_TypeDef COM);
#if (USE_COM_LOG > 0)
int32_t  BSP_COM_SelectLogPort(COM_TypeDef COM);
#endif /* USE_COM_LOG */

#if (USE_HAL_UART_REGISTER_CALLBACKS > 0)
int32_t BSP_COM_RegisterDefaultMspCallbacks(COM_TypeDef COM);
int32_t BSP_COM_RegisterMspCallbacks(COM_TypeDef COM, BSP_COM_Cb_t *Callback);
#endif /* USE_HAL_UART_REGISTER_CALLBACKS */
HAL_StatusTypeDef MX_USART1_Init(UART_HandleTypeDef *huart, MX_UART_InitTypeDef *COM_Init);
#endif /* USE_BSP_COM_FEATURE */

/**
  * @}
  */
/**
  * @}
  */

/**
  * @}
  */

/**
  * @}
  */

#ifdef __cplusplus
}
#endif
#endif /* B_U585I_IOT02A_H */
