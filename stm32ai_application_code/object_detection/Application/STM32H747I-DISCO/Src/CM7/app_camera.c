/**
 ******************************************************************************
 * @file    app_camera.c
 * @author  MCD Application Team
 * @brief   Library to manage camera related operation
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
#include "app_camera.h"
#include "ai_model_config.h"

/* Global variables ----------------------------------------------------------*/
MDMA_HandleTypeDef hmdma;

/* Private defines -----------------------------------------------------------*/

/* Private variables ---------------------------------------------------------*/
static uint8_t pCameraLineBuffer[CAM_LINE_SIZE] __attribute__ ((section(".camera_line_buffer")));

/* Private function prototypes -----------------------------------------------*/
HAL_StatusTypeDef HAL_DCMIEx_Start_DMA_MDMA(DCMI_HandleTypeDef *hdcmi, uint32_t DCMI_Mode, uint8_t *pData,
                                            uint32_t line_size, uint32_t num_lines);
static void DCMI_DMALineXferCplt(DMA_HandleTypeDef *hdma);
static void DCMI_DMAError(DMA_HandleTypeDef *hdma);
static void DCMI_MDMAFrameXferCplt(MDMA_HandleTypeDef *hmdma);
static void DCMI_MDMAError(MDMA_HandleTypeDef *hmdma);

/**
 * @brief Get the subsequent frame available
 * @param App_Config_Ptr pointer to application context
 */
void Camera_GetNextReadyFrame(AppConfig_TypeDef *App_Config_Ptr)
{ 
  /* Wait for current camera acquisition to complete*/
  while(App_Config_Ptr->new_frame_ready == 0);
}

/**
 * @brief Start the camera acquisition of the subsequent frame
 * @param App_Config_Ptr pointer to application context
 */
void Camera_StartNewFrameAcquisition(AppConfig_TypeDef *App_Config_Ptr)
{ 
  App_Config_Ptr->new_frame_ready = 0;
  
  /***Resume the camera capture in NOMINAL mode****/
  BSP_CAMERA_Resume(0);
}

/**
 * @brief  CAMERA Initialization
 * @param  App_Config_Ptr Pointer to application context
 * @retval None
 */
void Camera_Init(AppConfig_TypeDef *App_Config_Ptr)
{
  __HAL_RCC_MDMA_CLK_ENABLE();

  /* Init MDMA for camera line buffer to frame buffer copy */
  hmdma.Instance = MDMA_Channel0;
  hmdma.Init.Request                  = MDMA_REQUEST_SW;
  hmdma.Init.TransferTriggerMode      = MDMA_BLOCK_TRANSFER;
  hmdma.Init.Priority                 = MDMA_PRIORITY_HIGH;
  hmdma.Init.Endianness               = MDMA_LITTLE_ENDIANNESS_PRESERVE;
  hmdma.Init.SourceInc                = MDMA_SRC_INC_WORD;
  hmdma.Init.DestinationInc           = MDMA_DEST_INC_WORD;
  hmdma.Init.SourceDataSize           = MDMA_SRC_DATASIZE_WORD;
  hmdma.Init.DestDataSize             = MDMA_DEST_DATASIZE_WORD;
  hmdma.Init.DataAlignment            = MDMA_DATAALIGN_PACKENABLE;
  hmdma.Init.SourceBurst              = MDMA_DEST_BURST_SINGLE;
  hmdma.Init.DestBurst                = MDMA_DEST_BURST_16BEATS;
  hmdma.Init.BufferTransferLength     = 128;
  hmdma.Init.SourceBlockAddressOffset = 0;
  hmdma.Init.DestBlockAddressOffset   = 0;

#if ASPECT_RATIO_MODE == ASPECT_RATIO_PADDING
  uint8_t *camera_capture_buffer = App_Config_Ptr->camera_capture_buffer_no_borders;
#else
  uint8_t *camera_capture_buffer = App_Config_Ptr->camera_capture_buffer;
#endif
  if (HAL_MDMA_Init(&hmdma) != HAL_OK)
  {
    Error_Handler();
  }

  /* NVIC configuration for MDMA transfer complete interrupt */
  HAL_NVIC_SetPriority(MDMA_IRQn, 15U, 0);
  HAL_NVIC_EnableIRQ(MDMA_IRQn);

  /* Reset and power down camera to be sure camera is Off prior start */
  BSP_CAMERA_PwrDown(0);
  
  /* Wait delay */ 
  HAL_Delay(200);
  
  /* Initialize the Camera */
  if (BSP_CAMERA_Init(0, CAMERA_RESOLUTION, CAMERA_PF_RGB565) != BSP_ERROR_NONE)
  {
    Error_Handler();
  }

#ifdef TEST_MODE
  Camera_Enable_TestBar_Mode();
#endif
  
  /* Modify DMA2_Stream3 configuration so to increase its priority and its 
  memory transfer size: purpose is to avoid DCMI overflow */
  MODIFY_REG(DMA2_Stream3->CR, DMA_SxCR_PL, DMA_PRIORITY_VERY_HIGH);
  MODIFY_REG(DMA2_Stream3->CR, DMA_SxCR_MBURST, DMA_MBURST_INC4);
  
  /* Set OV5640 pixel clock (PCLK) to 48MHz and get a 30fps camera frame rate */
  if (Camera_Ctx[0].CameraId == OV5640_ID)
  {
    OV5640_Object_t *pObj = Camera_CompObj;
    uint8_t tmp = 0xC0; /* Bits[7:0]: PLL multiplier */
    if (ov5640_write_reg(&pObj->Ctx, OV5640_SC_PLL_CONTRL2,  &tmp, 1) != OV5640_OK)
    {
      while(1);
    }
  }
  
  /* Set camera mirror / flip configuration */
  Camera_Set_MirrorFlip(App_Config_Ptr->mirror_flip);
  
  HAL_Delay(100);

#if ASPECT_RATIO_MODE == ASPECT_RATIO_CROP
  /* Center-crop the 320x240 frame to 240x240 */
  const uint32_t x0 = (CAM_RES_WIDTH - CAM_RES_HEIGHT) / 2;
  const uint32_t y0 = 0;
  
  /* Note: 1 px every 2 DCMI_PXCLK (8-bit interface in RGB565) */
  HAL_DCMI_ConfigCrop(&hcamera_dcmi,
                      x0 * 2,
                      y0,
                      CAM_RES_WIDTH * 2 - 1,
                      CAM_RES_HEIGHT - 1);
  
  HAL_DCMI_EnableCrop(&hcamera_dcmi);
  /* Wait for the camera initialization after HW reset */ 
  HAL_Delay(200);
#endif
  
  /*
  * Start the Camera Capture
  * Using intermediate line buffer in D2-AHB domain to support high pixel clocks.
  */
  if (HAL_DCMIEx_Start_DMA_MDMA(&hcamera_dcmi, CAMERA_MODE_CONTINUOUS,
                                camera_capture_buffer,
                                CAM_LINE_SIZE, CAM_RES_HEIGHT) != HAL_OK)
  {
    while(1);
  }
  
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
  if (BSP_CAMERA_SetMirrorFlip(0, MirrorFlip) != BSP_ERROR_NONE)
  {
    while(1);
  }
}

/**
 * @brief  CAMERA enable test bar mode
 * @param  None
 * @retval None
 */
void Camera_Enable_TestBar_Mode(void)
{ 
  uint32_t camera_id = Camera_Ctx[0].CameraId;
  
  /* Send I2C command(s) to configure the camera in test color bar mode */
  if ((camera_id == OV9655_ID) || (camera_id == OV9655_ID_2))
  {
    uint8_t tmp;
    OV9655_Object_t *pObj = Camera_CompObj;
    ov9655_read_reg(&pObj->Ctx, OV9655_COMMON_CTRL20, &tmp, 1);
    tmp |= 0x10; /* Set bit[4]: Color bar test mode */
    ov9655_write_reg(&pObj->Ctx, OV9655_COMMON_CTRL20, &tmp, 1);
  }
  else
  {
    OV5640_Object_t *pObj = Camera_CompObj;
    if (OV5640_ColorbarModeConfig(pObj, COLORBAR_MODE_ENABLE) != OV5640_OK)
    {
      while(1);
    }
  }
  
  HAL_Delay(500);
}

/**
 * @brief  CAMERA disable test bar mode
 * @param  None
 * @retval None
 */
void Camera_Disable_TestBar_Mode(void)
{ 
  uint32_t camera_id = Camera_Ctx[0].CameraId;
  
  /* Send I2C command(s) to configure the camera in test color bar mode */
  if ((camera_id == OV9655_ID) || (camera_id == OV9655_ID_2))
  {
    uint8_t tmp;
    OV9655_Object_t *pObj = Camera_CompObj;
    tmp=0x00;
    
    ov9655_write_reg(&pObj->Ctx, OV9655_COMMON_CTRL20, &tmp, 1);
    HAL_Delay(300);
    
    ov9655_write_reg(&pObj->Ctx, OV9655_COMMON_CTRL3, &tmp, 1);
    HAL_Delay(300);
  }
  else
  {
    OV5640_Object_t *pObj = Camera_CompObj;
    if (OV5640_ColorbarModeConfig(pObj, COLORBAR_MODE_DISABLE) != OV5640_OK)
    {
      while(1);
    }
  }
  
  HAL_Delay(500);
}

/**
 * @brief Frame Event callback
 * @param Instance Camera instance
 */
void BSP_CAMERA_FrameEventCallback(uint32_t Instance)
{
  
  __disable_irq();
  
  /*Notifies the backgound task about new frame available for processing*/
  App_Config.new_frame_ready = 1;
  
  /*Suspend acquisition of the data stream coming from camera*/
  BSP_CAMERA_Suspend(0);
  
  __enable_irq();
}

/**
 * @brief VSYNC Event callback
 * @param Instance Camera instance
 */
void BSP_CAMERA_VsyncEventCallback(uint32_t Instance)
{   
  __disable_irq();

  __enable_irq();
}

/**
  * @brief  Error callback.
  * @param  Instance Camera instance.
  * @retval None
  */
void BSP_CAMERA_ErrorCallback(uint32_t Instance)
{
  Error_Handler();
}

/**
 * @brief Start DCMI capture intermediate line buffer
 *
 * Line capture using DMA from DCMI to intermediate line buffer. Line buffer is
 * then accumulated into final destination frame buffer using MDMA.
 *
 * @param hdcmi     Pointer to a DCMI_HandleTypeDef structure that contains
 *                  the configuration information for DCMI.
 * @param DCMI_Mode DCMI capture mode snapshot or continuous grab.
 * @param pData     Pointer to destination frame buffer.
 * @param line_size Horizontal frame size in bytes.
 * @param num_lines Vertical frame size in pixels.
 * @retval HAL status
 */
HAL_StatusTypeDef HAL_DCMIEx_Start_DMA_MDMA(DCMI_HandleTypeDef *hdcmi, uint32_t DCMI_Mode, uint8_t *pData,
                                            uint32_t line_size, uint32_t num_lines)
{
  /* Check function parameters */
  assert_param(IS_DCMI_CAPTURE_MODE(DCMI_Mode));

  /* Process Locked */
  __HAL_LOCK(hdcmi);

  /* Lock the DCMI peripheral state */
  hdcmi->State = HAL_DCMI_STATE_BUSY;

  /* Enable DCMI by setting DCMIEN bit */
  __HAL_DCMI_ENABLE(hdcmi);

  /* Configure the DCMI Mode */
  hdcmi->Instance->CR &= ~(DCMI_CR_CM);
  hdcmi->Instance->CR |= (uint32_t)(DCMI_Mode);

  /* Set DMA callbacks */
  hdcmi->DMA_Handle->XferCpltCallback = DCMI_DMALineXferCplt;
  hdcmi->DMA_Handle->XferErrorCallback = DCMI_DMAError;
  hdcmi->DMA_Handle->XferAbortCallback = NULL;

  /* Set MDMA callbacks */
  hmdma.XferCpltCallback = DCMI_MDMAFrameXferCplt;
  hmdma.XferErrorCallback = DCMI_MDMAError;

  hdcmi->XferCount = 0;
  hdcmi->XferTransferNumber = num_lines;
  hdcmi->XferSize = line_size / 4U;
  hdcmi->pBuffPtr = (uint32_t) pData;

  /* Enable the DMA Stream */
  uint32_t pLineData = (uint32_t) pCameraLineBuffer;
  if (HAL_DMA_Start_IT(hdcmi->DMA_Handle, (uint32_t)&hdcmi->Instance->DR, pLineData, hdcmi->XferSize) != HAL_OK)
  {
    /* Set Error Code */
    hdcmi->ErrorCode = HAL_DCMI_ERROR_DMA;
    /* Change DCMI state */
    hdcmi->State = HAL_DCMI_STATE_READY;
    /* Release Lock */
    __HAL_UNLOCK(hdcmi);
    /* Return function status */
    return HAL_ERROR;
  }

  /* Enable Capture */
  hdcmi->Instance->CR |= DCMI_CR_CAPTURE;

  /* Release Lock */
  __HAL_UNLOCK(hdcmi);

  /* Return function status */
  return HAL_OK;
}

/**
  * @brief  DMA transfer complete callback.
  * @param  hdma pointer to a DMA_HandleTypeDef structure that contains
  *                the configuration information for the specified DMA module.
  * @retval None
  */
static void DCMI_DMALineXferCplt(DMA_HandleTypeDef *hdma)
{
  DCMI_HandleTypeDef *hdcmi = (DCMI_HandleTypeDef *)((DMA_HandleTypeDef *)hdma)->Parent;

  /* Copy line buffer to frame buffer using MDMA */
  uint32_t line_size =  hdcmi->XferSize * 4U;
  uint8_t *pDst = (uint8_t *) hdcmi->pBuffPtr + line_size * hdcmi->XferCount;

  if (HAL_MDMA_Start_IT(&hmdma, (uint32_t) pCameraLineBuffer, (uint32_t) pDst, line_size, 1) != HAL_OK)
  {
    Error_Handler();
  }

}

/**
  * @brief  MDMA DCMI transfer complete callback
  * @param  hmdma  MDMA handle
  * @retval None
  */
static void DCMI_MDMAFrameXferCplt(MDMA_HandleTypeDef *hmdma)
{

  DCMI_HandleTypeDef *hdcmi = &hcamera_dcmi;

  /* Disable the MDMA channel */
  __HAL_MDMA_DISABLE(hmdma);

  hdcmi->XferCount++;

  /* Check if the frame is transferred */
  if (hdcmi->XferCount == hdcmi->XferTransferNumber)
  {
    /* Enable the Frame interrupt */
    __HAL_DCMI_ENABLE_IT(hdcmi, DCMI_IT_FRAME);

    /* When snapshot mode, set dcmi state to ready */
    if ((hdcmi->Instance->CR & DCMI_CR_CM) == DCMI_MODE_SNAPSHOT)
    {
      hdcmi->State = HAL_DCMI_STATE_READY;
    }
    else
    {
      hdcmi->XferCount = 0;
    }
  }
}

/**
  * @brief  DMA error callback
  * @param  hdma pointer to a DMA_HandleTypeDef structure that contains
  *                the configuration information for the specified DMA module.
  * @retval None
  */
static void DCMI_DMAError(DMA_HandleTypeDef *hdma)
{
  DCMI_HandleTypeDef *hdcmi = (DCMI_HandleTypeDef *)((DMA_HandleTypeDef *)hdma)->Parent;

  if (hdcmi->DMA_Handle->ErrorCode != HAL_DMA_ERROR_FE)
  {
    /* Initialize the DCMI state*/
    hdcmi->State = HAL_DCMI_STATE_READY;

    /* Set DCMI Error Code */
    hdcmi->ErrorCode |= HAL_DCMI_ERROR_DMA;
  }

  Error_Handler();
}

/**
  * @brief  MDMA DCMI error callback.
  * @param  hmdma MDMA handle
  * @retval None
  */
static void DCMI_MDMAError(MDMA_HandleTypeDef *hmdma)
{
  /* Disable the MDMA channel */
  __HAL_MDMA_DISABLE(hmdma);

  Error_Handler();
}

