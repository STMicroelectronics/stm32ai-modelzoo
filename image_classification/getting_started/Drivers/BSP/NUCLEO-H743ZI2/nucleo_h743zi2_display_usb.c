/**
 ******************************************************************************
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
#include "usb_otg.h"
#include "usb_disp.h"

/* Private variables ---------------------------------------------------------*/
uint8_t                  *display_buffer;
USB_DISP_Hdl_t           disp_hdl;

void (*cb_ptr)(uint8_t *p_frame, void *cb_args);

/* Private functions prototypes-----------------------------------------------*/
static void BSP_DISPLAY_USB_ConfigLayer(BSP_LCD_LayerConfig_t *Config);

extern void USB_DISP_FormatRgb565ToYuv422(uint8_t *p_dst, uint8_t *p_src, int width, int height);

/* Private functions ---------------------------------------------------------*/
/**
 * @brief Upscale and display image to LCD write buffer (centered)
 * @param lcd_buffer pointer to LCD write buffer
  * @retval BSP status
 */
static void BSP_DISPLAY_USB_ConfigLayer(BSP_LCD_LayerConfig_t *Config)
{
  LcdLayerCfg[0] = *Config;
}

/* Public functions ----------------------------------------------------------*/
/**
  * @brief  Initializes the LCD in default mode.
  * @param  Orientation LCD_ORIENTATION_LANDSCAPE
  * @retval BSP status
  */
int BSP_DISPLAY_USB_Init(BSP_LCD_LayerConfig_t *Config, uint32_t Orientation, void (*cb)(uint8_t *p_frame, void *cb_args))
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

    /* Initialize the USB driver */
    BSP_DISPLAY_USB_ConfigLayer(Config);

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
 * @brief Upscale and display image to LCD write buffer (centered)
 * @param lcd_buffer pointer to LCD write buffer
 * @param cam_buffer pointer to camera buffer
 */
void BSP_DISPLAY_USB_CameraCaptureBuffer(uint32_t *lcd_buffer, uint16_t *cam_buffer)
{
  // memcpy((uint8_t *) lcd_buffer, (uint8_t *) cam_buffer, CAM_RES_WIDTH * CAM_RES_HEIGHT * RGB_565_BPP/4);

  int rowlcd = 0;
  int collcd = (LCD_RES_WIDTH-CAM_RES_WIDTH)/2;
  uint16_t *lcd_buffer_ = (uint16_t *) lcd_buffer;

  /* Upscale to VGA, centered for display */
  for (int row = 0; row < CAM_RES_HEIGHT; row++)
  {
    for (int col = 0; col < CAM_RES_WIDTH; col++)
    {
      uint16_t pixel = *cam_buffer++;
      lcd_buffer_[rowlcd * LCD_RES_WIDTH + collcd] = pixel;

      collcd += 1;
    }
    collcd = (LCD_RES_WIDTH-CAM_RES_WIDTH)/2;
    rowlcd += 1;
  }
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
