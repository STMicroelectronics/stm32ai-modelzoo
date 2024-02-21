/**
 ******************************************************************************
 * @file    app_display.c
 * @author  MCD Application Team
 * @brief   Library to manage LCD display through DMA2D
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2019 STMicroelectronics.
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
#include "app_display.h"
#include "app_utility.h"
#include "stlogo.h"
#include "cube_ai_logo.h"
#include "stm32h7logo.h"

/* Private defines -----------------------------------------------------------*/
#define AVAILABLE_LABELS 36
/* Private macros ------------------------------------------------------------*/
#define MAX(x, y) ((x > y) ? x : y)

/* Global variables ----------------------------------------------------------*/

const uint32_t colors_table[AVAILABLE_LABELS] = {
    UTIL_LCD_COLOR_ST_BLUE,
    UTIL_LCD_COLOR_ST_BLUE_LIGHT,
    UTIL_LCD_COLOR_ST_BLUE_DARK,
    UTIL_LCD_COLOR_ST_YELLOW,
    UTIL_LCD_COLOR_ST_BROWN,
    UTIL_LCD_COLOR_ST_PINK,
    UTIL_LCD_COLOR_ST_PURPLE,
    UTIL_LCD_COLOR_ST_GRAY_DARK,
    UTIL_LCD_COLOR_ST_GRAY,
    UTIL_LCD_COLOR_ST_GRAY_LIGHT,
    UTIL_LCD_COLOR_ST_GREEN_LIGHT,
    UTIL_LCD_COLOR_ST_GREEN_DARK,
    UTIL_LCD_COLOR_GREEN,
    UTIL_LCD_COLOR_RED,
    UTIL_LCD_COLOR_CYAN,
    UTIL_LCD_COLOR_MAGENTA,
    UTIL_LCD_COLOR_YELLOW,
    UTIL_LCD_COLOR_LIGHTBLUE,
    UTIL_LCD_COLOR_LIGHTGREEN,
    UTIL_LCD_COLOR_LIGHTRED,
    UTIL_LCD_COLOR_LIGHTCYAN,
    UTIL_LCD_COLOR_LIGHTMAGENTA,
    UTIL_LCD_COLOR_LIGHTYELLOW,
    UTIL_LCD_COLOR_DARKBLUE,
    UTIL_LCD_COLOR_DARKGREEN,
    UTIL_LCD_COLOR_DARKRED,
    UTIL_LCD_COLOR_DARKCYAN,
    UTIL_LCD_COLOR_DARKMAGENTA,
    UTIL_LCD_COLOR_DARKYELLOW,
    UTIL_LCD_COLOR_LIGHTGRAY,
    UTIL_LCD_COLOR_GRAY,
    UTIL_LCD_COLOR_DARKGRAY,
    UTIL_LCD_COLOR_BLACK,
    UTIL_LCD_COLOR_BROWN,
    UTIL_LCD_COLOR_BLUE,
    UTIL_LCD_COLOR_ORANGE
};

/* Private function prototypes -----------------------------------------------*/
static void Display_CameraCaptureBuffer_upscale(AppConfig_TypeDef *App_Config_Ptr, uint16_t* cam_buffer);
static void Display_Refresh(AppConfig_TypeDef* App_Config_Ptr);
static void Display_DrawBBox(float x_center, float y_center, float width, float height, float confidence, const char* class_name, uint32_t color);

/* Functions Definition ------------------------------------------------------*/

/**
 * @brief  Display Initialization
 * @param App_Config_Ptr pointer to application context
 * @retval None
 */
 void Display_Init(AppConfig_TypeDef *App_Config_Ptr)  
{
  MX_LTDC_LayerConfig_t config;

  /*
   * Disable FMC Bank1 to prevent CPU speculative read accesses
   * AN4861: 4.6.1 Disable FMC bank1 if not used.
   */
  __FMC_NORSRAM_DISABLE(FMC_Bank1_R, FMC_NORSRAM_BANK1);

  BSP_LCD_Init(0, LCD_ORIENTATION_LANDSCAPE);/*by default, 0xD0000000 is used as start address for lcd frame buffer*/

  config.X0          = 0;
  config.X1          = LCD_DEFAULT_WIDTH;
  config.Y0          = 0;
  config.Y1          = LCD_DEFAULT_HEIGHT;
  config.PixelFormat = LTDC_PIXEL_FORMAT_ARGB8888;
  config.Address     = (uint32_t)App_Config_Ptr->lcd_frame_read_buff;/*lcd_frame_read_buff buffer used as lcd frame buffer*/
  BSP_LCD_ConfigLayer(0, 0, &config);//overwrite config 
  
  UTIL_LCD_SetFuncDriver(&LCD_Driver);
  UTIL_LCD_SetLayer(0);
  
  UTIL_LCD_SetBackColor(UTIL_LCD_COLOR_BLACK);
  UTIL_LCD_SetTextColor(UTIL_LCD_COLOR_WHITE);
  UTIL_LCD_SetFont(&Font24);
  
  /*Use lcd_frame_write_buff buffer for display composition*/
  hlcd_ltdc.LayerCfg[Lcd_Ctx[0].ActiveLayer].FBStartAdress=(uint32_t)App_Config_Ptr->lcd_frame_write_buff;
  
  /*LCD sync: set LTDCreload type to vertical blanking*/
  HAL_LTDC_Reload(&hlcd_ltdc, LTDC_RELOAD_VERTICAL_BLANKING);
}

/**
 * @brief Displays a Welcome screen
 *        with information about the memory and camera configuration.
 *        Also test for WakeUp button input in order to start the magic menu.
 *
 * @param App_Config_Ptr pointer to application context
 * @return int boolean value, 1 if WakeUp button has been pressed, 0 otherwise
 */
void Display_WelcomeScreen(AppConfig_TypeDef *App_Config_Ptr)
{
  UTIL_LCD_Clear(UTIL_LCD_COLOR_BLACK);
  
  /* Draw logos.*/
  BSP_LCD_DrawBitmap(0, 50, 77, (uint8_t *)stlogo);
  BSP_LCD_DrawBitmap(0, 620, 85, (uint8_t *)stm32h7logo);
  
  /*Display welcome message*/
  UTIL_LCD_DisplayStringAt(0, LINE(5), (uint8_t *)"OBJECT DETECTION", CENTER_MODE);
  UTIL_LCD_DisplayStringAt(0, LINE(6), (uint8_t *)" GETTING STARTED", CENTER_MODE);
  UTIL_LCD_DisplayStringAt(0, LINE(10), (uint8_t *)WELCOME_MSG_0, CENTER_MODE);
  UTIL_LCD_DisplayStringAt(0, LINE(13), (uint8_t *)WELCOME_MSG_1, CENTER_MODE);
  UTIL_LCD_DisplayStringAt(0, LINE(14), (uint8_t *)WELCOME_MSG_2, CENTER_MODE);
  UTIL_LCD_DisplayStringAt(0, LINE(15), (uint8_t *)WELCOME_MSG_3, CENTER_MODE);
  UTIL_LCD_DisplayStringAt(0, LINE(16), (uint8_t *)WELCOME_MSG_4, CENTER_MODE);
  
  Display_Refresh(App_Config_Ptr);
  
  HAL_Delay(4000);
  
  UTIL_LCD_Clear(UTIL_LCD_COLOR_BLACK);
}

/**
 * @brief Display camera preview on LCD display
 *
 * @param App_Config_Ptr pointer to application context
 */
void Display_CameraPreview(AppConfig_TypeDef *App_Config_Ptr)
{
#if ASPECT_RATIO_MODE == ASPECT_RATIO_PADDING
  uint8_t *camera_capture_buffer = App_Config_Ptr->camera_capture_buffer_no_borders;
#else
  uint8_t *camera_capture_buffer = App_Config_Ptr->camera_capture_buffer;
#endif
  
  /*Coherency purpose: invalidate the camera_capture_buffer area in L1 D-Cache before CPU reading*/
  Utility_DCache_Coherency_Maintenance((void*)camera_capture_buffer,
                                     CAM_FRAME_BUFFER_SIZE, INVALIDATE);
  
  /*Clear LCD display*/
  UTIL_LCD_Clear(UTIL_LCD_COLOR_BLACK);

  /* Copy and upscale from camera frame buffer to LCD write buffer */
  Display_CameraCaptureBuffer_upscale(App_Config_Ptr, (uint16_t *)camera_capture_buffer);
}

/**
 * @brief Upscale and display image to LCD write buffer (centered)
 *
 * @param App_Config_Ptr pointer to application context
 * @param cam_buff pointer to the buffer to display
 */
static void Display_CameraCaptureBuffer_upscale(AppConfig_TypeDef *App_Config_Ptr, uint16_t* cam_buffer)
{
  uint32_t *lcd_buffer = (uint32_t *) App_Config_Ptr->lcd_frame_write_buff;
  int rowlcd = 0;
  int collcd = 0;

  /*Upscale to VGA, centered for display*/
  for (int row = 0; row < CAM_RES_HEIGHT; row++)
  {
    for (int col = 0; col < CAM_RES_WIDTH; col++)
    {
      uint8_t r8;
      uint8_t g8;
      uint8_t b8;

      uint16_t pixel = *cam_buffer++;
      /* Extract R:5 G:6 B:5 components */
      uint32_t red   = ((pixel & 0xf800u) >> 11);
      uint32_t green = ((pixel & 0x07e0u) >>  5);
      uint32_t blue  = ((pixel & 0x001fu) >>  0);

      /* Convert */
      /* Left shift and copy MSBs to LSBs to improve conversion linearity */
      red   = (red   << 3) | (red   >> 2);
      green = (green << 2) | (green >> 4);
      blue  = (blue  << 3) | (blue  >> 2);
      r8 = (uint8_t) red;
      g8 = (uint8_t) green;
      b8 = (uint8_t) blue;

      uint32_t argb_pix = 0xFF000000 | (r8 << 16) | (g8 << 8) | b8;
      lcd_buffer[rowlcd * LCD_RES_WIDTH + collcd] = argb_pix;
#if CAMERA_RESOLUTION == CAMERA_R320x240
      lcd_buffer[rowlcd * LCD_RES_WIDTH + collcd + 1] = argb_pix;
      lcd_buffer[(rowlcd + 1) * LCD_RES_WIDTH + collcd] = argb_pix;
      lcd_buffer[(rowlcd + 1) * LCD_RES_WIDTH + collcd + 1] = argb_pix;
      collcd += 2;
    }
    collcd = 0;
    rowlcd += 2;
#else
      collcd += 1;
    }
    collcd = 0;
    rowlcd += 1;
#endif
  }
     
}

/**
* @brief Display Neural Network output classification results as well as other performances informations
*
* @param App_Config_Ptr pointer to application context
*/
void Display_NetworkOutput(AppConfig_TypeDef *App_Config_Ptr)
{
  char msg[70];

  postprocess_outBuffer_t *pOutBuff = App_Config_Ptr->output.pOutBuff;

  int32_t nb_objects = 0;
  for (int32_t i = 0; i < App_Config_Ptr->output.nb_detect; ++i)
  {
    if (pOutBuff->class_index < AVAILABLE_LABELS)
    {
      Display_DrawBBox(pOutBuff->x_center, pOutBuff->y_center, pOutBuff->width, pOutBuff->height, pOutBuff->conf,
                       App_Config_Ptr->nn_output_labels[pOutBuff->class_index], colors_table[pOutBuff->class_index]);
    }
    else
    {
      Display_DrawBBox(pOutBuff->x_center, pOutBuff->y_center, pOutBuff->width, pOutBuff->height, pOutBuff->conf,
                       App_Config_Ptr->nn_output_labels[pOutBuff->class_index], colors_table[AVAILABLE_LABELS-1]);
    }
    BSP_LED_Off(LED_RED);
    BSP_LED_On(LED_GREEN);
    nb_objects++;
    pOutBuff++;
  }

  /* Reset DMA2D RB-Swap as it is not configured in BSP_LCD_DrawBitmap */
  hlcd_dma2d.LayerCfg[1].RedBlueSwap = DMA2D_RB_REGULAR;

  BSP_LCD_DrawBitmap(0, 640, 15, (uint8_t *)stlogo);
  BSP_LCD_DrawBitmap(0, 640, 200, (uint8_t *)cubeai_logo);
  UTIL_LCD_SetTextColor(UTIL_LCD_COLOR_WHITE);

  if (nb_objects > 1)
  {
    sprintf(msg, "%ld objects", nb_objects);
    UTIL_LCD_DisplayStringAt(320, LINE(16), (uint8_t *)msg, CENTER_MODE);
  }
  else
  {
    sprintf(msg, "%ld object", nb_objects);
    UTIL_LCD_DisplayStringAt(320, LINE(16), (uint8_t *)msg, CENTER_MODE);
  }

  UTIL_LCD_SetTextColor(UTIL_LCD_COLOR_WHITE);

  sprintf(msg, "Fps: %.1f", 1000.0F / (float)(App_Config_Ptr->Tfps_stop - App_Config_Ptr->Tfps_start));
  UTIL_LCD_DisplayStringAt(320, LINE(18), (uint8_t *)msg, CENTER_MODE);

  Display_Refresh(App_Config_Ptr);
}

/**
 * @brief Refreshes LCD screen
 *        by performing a DMA transfer from lcd write buffer to lcd read buffer
 *
 * @param App_Config_Ptr pointer to application context
 */
static void Display_Refresh(AppConfig_TypeDef *App_Config_Ptr)
{
  /*LCD sync: wait for next VSYNC event before refreshing, i.e. before updating the content of the buffer that will be read by the LTDC for display. 
  The refresh occurs during the blanking period => this sync mecanism should enable to avoid tearing effect*/
  App_Config_Ptr->lcd_sync =0;
  while(App_Config_Ptr->lcd_sync==0);
  
  /*Coherency purpose: clean the lcd_frame_write_buff area in L1 D-Cache before DMA2D reading*/
  Utility_DCache_Coherency_Maintenance((void *)App_Config_Ptr->lcd_frame_write_buff, LCD_FRAME_BUFFER_SIZE, CLEAN);
  
  Utility_Dma2d_Memcpy((uint32_t *)(App_Config_Ptr->lcd_frame_write_buff), (uint32_t *)(App_Config_Ptr->lcd_frame_read_buff), 0, 0, LCD_RES_WIDTH,
                     LCD_RES_HEIGHT, LCD_RES_WIDTH, DMA2D_INPUT_ARGB8888, DMA2D_OUTPUT_ARGB8888, 0, 0);
}

void HAL_LTDC_ReloadEventCallback(LTDC_HandleTypeDef *hltdc)
{
  App_Config.lcd_sync=1;
  
  /*Set LTDCreload type to vertical blanking*/
  HAL_LTDC_Reload(hltdc, LTDC_RELOAD_VERTICAL_BLANKING);
}

/**
 * @brief Draw bounding box with center to LCD
 *
 * @param x_center Normalized box center x coordinate
 * @param y_center Normalized box center y coordinate
 * @param width Normalized box width
 * @param height Normalized box height
 * @param class_name Class name to display 
 * @param color Color of the BBox
 */
static void Display_DrawBBox(float x_center, float y_center, float width, float height, float confidence, const char* class_name, uint32_t color)
{
uint32_t res_display_width = VGA_RES_WIDTH; 
uint32_t res_display_height = VGA_RES_HEIGHT;

  /* Scale normalized coordinates to display resolution */
#if ASPECT_RATIO_MODE == ASPECT_RATIO_PADDING
  uint32_t box_center_x = (uint32_t) (x_center * res_display_width);
  uint32_t box_center_y = (uint32_t) (y_center * res_display_width - (CAM_RES_WIDTH-CAM_RES_HEIGHT));
  uint32_t box_w = (uint32_t) (width * res_display_width) ;
  uint32_t box_h = (uint32_t) (height * res_display_width) ;
  uint32_t box_x = box_center_x - (box_w / 2) ;
  uint32_t box_y = box_center_y - (box_h / 2) ;
#else
   uint32_t box_center_x = (uint32_t) (x_center * res_display_width);
   uint32_t box_center_y = (uint32_t) (y_center * res_display_height);
   uint32_t box_w = (uint32_t) (width * res_display_width) ;
   uint32_t box_h = (uint32_t) (height * res_display_height) ;
   uint32_t box_x = box_center_x - (box_w / 2) ;
   uint32_t box_y = box_center_y - (box_h / 2) ;
#endif

   /* Draw box */
  UTIL_LCD_DrawRect(box_x, box_y, box_w, box_h, color);

   /* Draw box center */
  UTIL_LCD_DrawHLine(box_center_x - 5, box_center_y, 10, color);
  UTIL_LCD_DrawVLine(box_center_x, box_center_y - 5, 10, color);
  UTIL_LCD_SetBackColor(color);

  uint8_t red = (color & 0x00FF0000) >> 16;
  uint8_t green = (color & 0x0000FF00) >> 8;
  uint8_t blue = color & 0x000000FF;
  uint32_t brightness = red + green + blue;

  /* Increase lisibility by setting black for dark colors, white otherwise. */
  if (brightness < 0x17E) /* lower than mid value */ 
  {
    UTIL_LCD_SetTextColor(UTIL_LCD_COLOR_WHITE);
  }
  else
  {
    UTIL_LCD_SetTextColor(UTIL_LCD_COLOR_BLACK);
  }
  char confidence_as_char[5];
  snprintf(confidence_as_char, sizeof(confidence_as_char), "%0.2f", confidence);
  sFONT *tmpFontSize = UTIL_LCD_GetFont();
  UTIL_LCD_DisplayStringAt(box_x, box_y, (uint8_t*)class_name, LEFT_MODE);
  UTIL_LCD_DisplayStringAt(box_x + strlen(class_name)*tmpFontSize->Width+1, box_y, (unsigned char *)confidence_as_char, LEFT_MODE);
  UTIL_LCD_SetBackColor(UTIL_LCD_COLOR_BLACK);
}

