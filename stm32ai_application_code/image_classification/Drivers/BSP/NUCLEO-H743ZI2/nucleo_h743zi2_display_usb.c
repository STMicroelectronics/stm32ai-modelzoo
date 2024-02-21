 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_display_usb.c
 * @author  MDG Application Team
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
#include "nucleo_h743zi2_display_usb.h"
#include "usb_disp.h"
#include "main.h"

/* Private variables ---------------------------------------------------------*/
static USB_DISP_Hdl_t           disp_hdl;
PCD_HandleTypeDef               hpcd_USB_OTG_FS;

void (*cb_ptr)(uint8_t *p_frame, void *cb_args);

/* Private functions prototypes ----------------------------------------------*/
extern void USB_DISP_FormatRgb565ToYuv422(uint8_t *p_dst, uint8_t *p_src, int width, int height);
static void MX_USB_OTG_FS_PCD_Init(void);
void HAL_PCD_MspInit(PCD_HandleTypeDef* pcdHandle);

/* Private functions definitions ---------------------------------------------*/
/* USB_OTG_FS init function */
static void MX_USB_OTG_FS_PCD_Init(void)
{
  hpcd_USB_OTG_FS.Instance = USB_OTG_FS;
  hpcd_USB_OTG_FS.Init.dev_endpoints = 9;
  hpcd_USB_OTG_FS.Init.speed = PCD_SPEED_FULL;
  hpcd_USB_OTG_FS.Init.dma_enable = DISABLE;
  hpcd_USB_OTG_FS.Init.phy_itface = PCD_PHY_EMBEDDED;
  hpcd_USB_OTG_FS.Init.Sof_enable = DISABLE;
  hpcd_USB_OTG_FS.Init.low_power_enable = DISABLE;
  hpcd_USB_OTG_FS.Init.lpm_enable = DISABLE;
  hpcd_USB_OTG_FS.Init.battery_charging_enable = DISABLE;
  hpcd_USB_OTG_FS.Init.vbus_sensing_enable = DISABLE;
  hpcd_USB_OTG_FS.Init.use_dedicated_ep1 = DISABLE;
  if (HAL_PCD_Init(&hpcd_USB_OTG_FS) != HAL_OK)
  {
    Error_Handler();
  }
}

void HAL_PCD_MspInit(PCD_HandleTypeDef* pcdHandle)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInitStruct = {0};
  if(pcdHandle->Instance==USB_OTG_FS)
  {
  /** Initializes the peripherals clock
  */
    PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_USB;
    PeriphClkInitStruct.PLL3.PLL3M = 1;
    PeriphClkInitStruct.PLL3.PLL3N = 24;
    PeriphClkInitStruct.PLL3.PLL3P = 2;
    PeriphClkInitStruct.PLL3.PLL3Q = 4;
    PeriphClkInitStruct.PLL3.PLL3R = 2;
    PeriphClkInitStruct.PLL3.PLL3RGE = RCC_PLL3VCIRANGE_3;
    PeriphClkInitStruct.PLL3.PLL3FRACN = 0.0;
    PeriphClkInitStruct.UsbClockSelection = RCC_USBCLKSOURCE_PLL3;
    if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct) != HAL_OK)
    {
      Error_Handler();
    }

  /** Enable USB Voltage detector
  */
    HAL_PWREx_EnableUSBVoltageDetector();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    /**USB_OTG_FS GPIO Configuration
    PA8     ------> USB_OTG_FS_SOF
    PA9     ------> USB_OTG_FS_VBUS
    PA11     ------> USB_OTG_FS_DM
    PA12     ------> USB_OTG_FS_DP
    */
    GPIO_InitStruct.Pin = GPIO_PIN_8|GPIO_PIN_11|GPIO_PIN_12;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    GPIO_InitStruct.Alternate = GPIO_AF10_OTG1_FS;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* USB_OTG_FS clock enable */
    __HAL_RCC_USB_OTG_FS_CLK_ENABLE();

    /* USB_OTG_FS interrupt Init */
    HAL_NVIC_SetPriority(OTG_FS_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(OTG_FS_IRQn);
  }
}

/* Public functions ----------------------------------------------------------*/
/**
  * @brief  Initializes the LCD in default mode.
  * @param  Orientation LCD_ORIENTATION_LANDSCAPE
  * @retval BSP status
  */
int BSP_DISPLAY_USB_Init(uint32_t Orientation, void (*cb)(uint8_t *p_frame, void *cb_args))
{
  /* USB display configuration */
  int ret = BSP_ERROR_NONE;
  USB_DISP_Conf_t USB_config = {
    &hpcd_USB_OTG_FS,
    NULL,
    0,
    LCD_DEFAULT_WIDTH,
    LCD_DEFAULT_HEIGHT,
    30,
    LCD_DEFAULT_WIDTH * LCD_DEFAULT_HEIGHT * LCD_BPP,
    {NULL, NULL},
    USB_DISP_MODE_RAW,
    USB_DISP_PAYLOAD_UNCOMPRESSED,
    USB_DISP_INPUT_FORMAT_UNKNOWN,
    NULL
  };

  cb_ptr = cb;

  /* Configure LCD instance */
  Lcd_Ctx.BppFactor = 2;
  Lcd_Ctx.PixelFormat = LCD_PIXEL_FORMAT_RGB565;
  Lcd_Ctx.XSize = LCD_DEFAULT_WIDTH;
  Lcd_Ctx.YSize = LCD_DEFAULT_HEIGHT;

  if (Orientation != LCD_ORIENTATION_LANDSCAPE)
  {
    ret = BSP_ERROR_WRONG_PARAM;
  }
  else
  {
    /* Initializes peripherals instance value */
    hlcd_dma2d.Instance = DMA2D;

    DMA2D_MspInit(&hlcd_dma2d);

    MX_USB_OTG_FS_PCD_Init();

    disp_hdl = USB_DISP_Init(&USB_config);
    if (0 == disp_hdl)
    {
      ret = BSP_ERROR_PERIPH_FAILURE;
    }
  }

  return ret;
}

/**
 * @brief Upscale and display image to LCD read buffer. The conversion from RGB565 to YUV422 is done in place.
 * @param lcd_buffer pointer to buffer to write
 * @retval return 1 if frame will be displayed else return 0 is frame is dropped
 */
int BSP_DISPLAY_USB_ImageBufferRGB565(uint8_t *buffer)
{
  /* Convert buffer from RGB565 to YUV422 before it is sent through USB */
  USB_DISP_FormatRgb565ToYuv422(buffer, buffer, LCD_DEFAULT_WIDTH, LCD_DEFAULT_HEIGHT);

  /* Sent buffer */
  return USB_DISP_ShowRaw(disp_hdl, buffer, LCD_DEFAULT_WIDTH * LCD_DEFAULT_HEIGHT * LCD_BPP, cb_ptr, NULL);
}

/**
 * @brief Upscale and display image to LCD read buffer. No conversion is done.
 * @param lcd_buffer pointer to buffer to write
 * @retval return 1 if frame will be displayed else return 0 is frame is dropped
 */
int BSP_DISPLAY_USB_ImageBufferYUV422(uint8_t *buffer)
{
  /* Sent buffer */
  return USB_DISP_ShowRaw(disp_hdl, buffer, LCD_DEFAULT_WIDTH * LCD_DEFAULT_HEIGHT * LCD_BPP, cb_ptr, NULL);
}
