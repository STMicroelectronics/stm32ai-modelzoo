/**
 ******************************************************************************
 * @file    app_camera.c
 * @author  MDG Application Team
 * @brief   Library to manage camera related operation
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
#include "app_camera.h"
#include "app_utility.h"
#include "ai_model_config.h"

/* Global variables ----------------------------------------------------------*/

/* Private defines -----------------------------------------------------------*/

/* Private variables ---------------------------------------------------------*/

/* Private function prototypes -----------------------------------------------*/
/**
 * @brief Get the subsequent frame available
 * @param App_Config_Ptr pointer to application context
 */
void Camera_GetNextReadyFrame(AppConfig_TypeDef *App_Config_Ptr)
{ 
#if CAMERA_INTERFACE == CAMERA_INTERFACE_USB
  if (BSP_CAMERA_USB_WaitForFrame() != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#else
  /* Wait for current camera acquisition to complete*/
  while(App_Config_Ptr->new_frame_ready == 0);
#endif
}

/**
 * @brief Start the camera acquisition of the subsequent frame
 * @param App_Config_Ptr pointer to application context
 */
void Camera_StartNewFrameAcquisition(AppConfig_TypeDef *App_Config_Ptr)
{ 
  App_Config_Ptr->new_frame_ready = 0;
  
  /***Resume the camera capture in NOMINAL mode****/
#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  if (BSP_CAMERA_DCMI_Resume() != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
  if (BSP_CAMERA_USB_StartCapture() != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
  SPI_Cam_Take_Picture();
  SPI_Cam_Fetch_Data();
  SPI_Cam_Swap_Bytes();
#else
#error "Selected camera interface is not supported"
#endif
}

/**
 * @brief  CAMERA Initialization
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Camera_Init(AppConfig_TypeDef *App_Config_Ptr)
{
#if ASPECT_RATIO_MODE == ASPECT_RATIO_PADDING
  uint8_t *camera_capture_buffer = App_Config_Ptr->camera_capture_buffer_no_borders;
#else
  uint8_t *camera_capture_buffer = App_Config_Ptr->camera_capture_buffer;
#endif

  /* Reset and power down camera to be sure camera is Off prior start */
#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  if (BSP_CAMERA_DCMI_PwrDown() != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
#else
#error "Selected camera interface is not supported"
#endif
  
  /* Wait delay */ 
  HAL_Delay(200);
  
  /* Initialize the Camera */
#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  if (BSP_CAMERA_DCMI_Init(CAMERA_R320x240, CAMERA_PF_RGB565) != BSP_ERROR_NONE) 
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
  if (BSP_CAMERA_USB_Init(camera_capture_buffer, &(App_Config_Ptr->new_frame_ready)) != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
  SPI_Cam_Init_Begin(camera_capture_buffer);
#else
#error "Selected camera interface is not supported"
#endif

#ifdef TEST_MODE
  Camera_Enable_TestBar_Mode();
#endif

  /* Set camera mirror / flip configuration */
  Camera_Set_MirrorFlip(App_Config_Ptr->mirror_flip);
  
  HAL_Delay(100);

#if ASPECT_RATIO_MODE == ASPECT_RATIO_CROP

#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  if (BSP_CAMERA_DCMI_Set_Crop() != BSP_ERROR_NONE) 
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
#else
#error "Selected camera interface is not supported"
#endif

  /* Wait for the camera initialization after HW reset */ 
  HAL_Delay(200);
#endif
  
  /*
  * Clean the camera buffer and start the Camera Capture
  */
  memset(App_Config_Ptr->camera_capture_buffer, 0x00, CAM_FRAME_BUFFER_SIZE + 32 - (CAM_FRAME_BUFFER_SIZE%32));

  /* Coherency purpose: clean the camera_capture_buffer area in L1 D-Cache */
  Utility_DCache_Coherency_Maintenance((void *)(App_Config_Ptr->camera_capture_buffer),
                                    CAM_FRAME_BUFFER_SIZE + 32 - (CAM_FRAME_BUFFER_SIZE%32), CLEAN);

#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  if (BSP_CAMERA_DCMI_StartCapture(camera_capture_buffer) != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
  if (BSP_CAMERA_USB_StartCapture() != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
  // Take a first picture in order to set the App_Config.new_frame_ready flag to 1
  SPI_Cam_Take_Picture();
  SPI_Cam_Fetch_Data(camera_capture_buffer);
  SPI_Cam_Swap_Bytes(camera_capture_buffer);
#else
#error "Selected camera interface is not supported"
#endif
  
  /* Wait for the camera initialization after HW reset */
  HAL_Delay(200);
}

/**
 * @brief Set the camera Mirror/Flip.
 * @param  MirrorFlip CAMERA_MIRRORFLIP_NONE or any combination of
 *                    CAMERA_MIRRORFLIP_FLIP and CAMERA_MIRRORFLIP_MIRROR
 * @retval None
 */
void Camera_Set_MirrorFlip(uint32_t MirrorFlip)
{
#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  if (BSP_CAMERA_DCMI_Set_MirrorFlip(MirrorFlip) != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
#else
#error "Selected camera interface is not supported"
#endif
}

/**
 * @brief  CAMERA enable test bar mode
 * @param  None
 * @retval None
 */
void Camera_Enable_TestBar_Mode(void)
{ 
#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  if (BSP_CAMERA_DCMI_Set_TestBar(1) != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
#else
#error "Selected camera interface is not supported"
#endif
  
  HAL_Delay(500);
}

/**
 * @brief  CAMERA disable test bar mode
 * @param  None
 * @retval None
 */
void Camera_Disable_TestBar_Mode(void)
{ 
#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  if (BSP_CAMERA_DCMI_Set_TestBar(0) != BSP_ERROR_NONE)
  {
    Error_Handler();
  }
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
#else
#error "Selected camera interface is not supported"
#endif
  
  HAL_Delay(500);
}
