 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_camera_dcmi.c
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
#include "nucleo_h743zi2_camera_dcmi.h"
#include "nucleo_h743zi2_bus.h"

/* Private variables ---------------------------------------------------------*/
MDMA_HandleTypeDef hmdma;
extern AppConfig_TypeDef App_Config;
static DCMI_HandleTypeDef hcamera_dcmi;
static uint8_t pCameraLineBuffer[CAM_LINE_SIZE] __attribute__((section(".camera_line_buffer")));
static void *Camera_CompObj = NULL;
static CAMERA_Capabilities_t Camera_Cap;
static CAMERA_Drv_t *Camera_Drv = NULL;
static CAMERA_Ctx_t Camera_Ctx;
static uint32_t CameraId;

/* Private function prototypes -----------------------------------------------*/
HAL_StatusTypeDef HAL_DCMIEx_Start_DMA_MDMA(DCMI_HandleTypeDef *hdcmi, uint32_t DCMI_Mode, uint8_t *pData,
                                            uint32_t line_size, uint32_t num_lines);
static void DCMI_DMALineXferCplt(DMA_HandleTypeDef *hdma);
static void DCMI_DMAError(DMA_HandleTypeDef *hdma);
static void DCMI_MDMAFrameXferCplt(MDMA_HandleTypeDef *hmdma);
static void DCMI_MDMAError(MDMA_HandleTypeDef *hmdma);
#if CAMERA_SENSOR == CAMERA_SENSOR_OV5640
static int DCMI_Init_OV5640(uint32_t Resolution, uint32_t PixelFormat);
static int GPIO_Init_OV5640();
static int OV5640_Probe(uint32_t Resolution, uint32_t PixelFormat);
#else
#error "Selected camera sensor is not supported"
#endif

/* Private functions Definition ----------------------------------------------*/
#if CAMERA_SENSOR == CAMERA_SENSOR_OV5640
static int DCMI_Init_OV5640(uint32_t Resolution, uint32_t PixelFormat)
{
  int ret = BSP_ERROR_NONE;

  /* DCMI Initialization */
  if (BSP_CAMERA_DCMI_HwReset() != BSP_ERROR_NONE)
  {
    ret = BSP_ERROR_PERIPH_FAILURE;
  }

  if (OV5640_Probe(Resolution, PixelFormat) != BSP_ERROR_NONE)
  {
    ret = BSP_ERROR_BUS_FAILURE;
  }

  /*** Configures the DCMI to interface with the camera module ***/
  /* DCMI configuration */
  hcamera_dcmi.Instance = DCMI;
  hcamera_dcmi.Init.CaptureRate = DCMI_CR_ALL_FRAME;
  hcamera_dcmi.Init.HSPolarity = DCMI_HSPOLARITY_HIGH;
  hcamera_dcmi.Init.SynchroMode = DCMI_SYNCHRO_HARDWARE;
  hcamera_dcmi.Init.VSPolarity = DCMI_VSPOLARITY_HIGH;
  hcamera_dcmi.Init.ExtendedDataMode = DCMI_EXTEND_DATA_8B;
  hcamera_dcmi.Init.PCKPolarity = DCMI_PCKPOLARITY_RISING;

  if (HAL_DCMI_Init(&hcamera_dcmi) != HAL_OK)
  {
    ret = BSP_ERROR_PERIPH_FAILURE;
  }

  if (BSP_CAMERA_DCMI_HwReset() != BSP_ERROR_NONE)
  {
    ret = BSP_ERROR_BUS_FAILURE;
  }

  Camera_Ctx.CameraId  = CameraId;  
  Camera_Ctx.Resolution  = Resolution;
  Camera_Ctx.PixelFormat = PixelFormat;

  /*Modify DMA2_Stream3 configuration so to increase its priority and its
  memory transfer size: purpose is to avoid DCMI overflow */
  MODIFY_REG(DMA2_Stream3->CR, DMA_SxCR_PL, DMA_PRIORITY_VERY_HIGH);
  MODIFY_REG(DMA2_Stream3->CR, DMA_SxCR_MBURST, DMA_MBURST_INC4);

  /* Set OV5640 pixel clock (PCLK) to 48MHz and get a 30fps camera frame rate */
  OV5640_Object_t *pObj = Camera_CompObj;
  uint8_t tmp = 0xC0; /* Bits[7:0]: PLL multiplier */
  if (ov5640_write_reg(&pObj->Ctx, OV5640_SC_PLL_CONTRL2,  &tmp, 1) != OV5640_OK)
  {
    while(1);
  }

  return ret;
}

static int GPIO_Init_OV5640()
{
  int ret = BSP_ERROR_NONE;

  static DMA_HandleTypeDef hdma_handler;
  GPIO_InitTypeDef gpio_init_structure;

  /* Init DCMI PWR_ENABLE Pin */
  gpio_init_structure.Pin       = CAMERA_EN_Pin;
  gpio_init_structure.Mode      = GPIO_MODE_OUTPUT_PP;
  gpio_init_structure.Pull      = GPIO_NOPULL;
  gpio_init_structure.Speed     = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(CAMERA_EN_GPIO_Port, &gpio_init_structure);

  /* De-assert the camera POWER_DOWN pin (active high) */
  HAL_GPIO_WritePin(CAMERA_EN_GPIO_Port, CAMERA_EN_Pin, GPIO_PIN_RESET);
  
  /* Init DCMI PWR_ENABLE Pin */
  gpio_init_structure.Pin       = CAMERA_RST_Pin;
  gpio_init_structure.Mode      = GPIO_MODE_OUTPUT_PP;
  gpio_init_structure.Pull      = GPIO_NOPULL;
  gpio_init_structure.Speed     = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(CAMERA_RST_GPIO_Port, &gpio_init_structure);

  /* De-assert the camera RESET pin (active low) */
  HAL_GPIO_WritePin(CAMERA_RST_GPIO_Port, CAMERA_RST_Pin, GPIO_PIN_SET);

  /*** Enable peripherals and GPIO clocks ***/
  /* Enable DCMI clock */
  __HAL_RCC_DCMI_CLK_ENABLE();

  /* Enable DMA2 clock */
  __HAL_RCC_DMA2_CLK_ENABLE();

  /* Enable GPIO clocks */
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOF_CLK_ENABLE();

  /*** Configure the GPIO ***/
  /**DCMI GPIO Configuration
  PE5     ------> DCMI_D6
  PE6     ------> DCMI_D7
  PA4     ------> DCMI_HSYNC
  PA6     ------> DCMI_PIXCLK
  PC6     ------> DCMI_D0
  PC7     ------> DCMI_D1
  PC8     ------> DCMI_D2
  PC9     ------> DCMI_D3
  PC11    ------> DCMI_D4
  PD3     ------> DCMI_D5
  PB7     ------> DCMI_VSYNC
  */
  gpio_init_structure.Pin = GPIO_PIN_5|GPIO_PIN_6;
  gpio_init_structure.Mode = GPIO_MODE_AF_PP;
  gpio_init_structure.Pull = GPIO_PULLUP;
  gpio_init_structure.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  gpio_init_structure.Alternate = GPIO_AF13_DCMI;
  HAL_GPIO_Init(GPIOE, &gpio_init_structure);

  gpio_init_structure.Pin = GPIO_PIN_4|GPIO_PIN_6;
  gpio_init_structure.Mode = GPIO_MODE_AF_PP;
  gpio_init_structure.Pull = GPIO_PULLUP;
  gpio_init_structure.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  gpio_init_structure.Alternate = GPIO_AF13_DCMI;
  HAL_GPIO_Init(GPIOA, &gpio_init_structure);

  gpio_init_structure.Pin = GPIO_PIN_6|GPIO_PIN_7|GPIO_PIN_8|GPIO_PIN_9
                        |GPIO_PIN_11;
  gpio_init_structure.Mode = GPIO_MODE_AF_PP;
  gpio_init_structure.Pull = GPIO_PULLUP;
  gpio_init_structure.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  gpio_init_structure.Alternate = GPIO_AF13_DCMI;
  HAL_GPIO_Init(GPIOC, &gpio_init_structure);

  gpio_init_structure.Pin = GPIO_PIN_3;
  gpio_init_structure.Mode = GPIO_MODE_AF_PP;
  gpio_init_structure.Pull = GPIO_PULLUP;
  gpio_init_structure.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  gpio_init_structure.Alternate = GPIO_AF13_DCMI;
  HAL_GPIO_Init(GPIOD, &gpio_init_structure);

  gpio_init_structure.Pin = GPIO_PIN_7;
  gpio_init_structure.Mode = GPIO_MODE_AF_PP;
  gpio_init_structure.Pull = GPIO_PULLUP;
  gpio_init_structure.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  gpio_init_structure.Alternate = GPIO_AF13_DCMI;
  HAL_GPIO_Init(GPIOB, &gpio_init_structure);

  /*** Configure the DMA ***/
  /* Set the parameters to be configured */
  hdma_handler.Init.Request = DMA_REQUEST_DCMI;
  hdma_handler.Init.Direction = DMA_PERIPH_TO_MEMORY;
  hdma_handler.Init.PeriphInc = DMA_PINC_DISABLE;
  hdma_handler.Init.MemInc = DMA_MINC_ENABLE;
  hdma_handler.Init.PeriphDataAlignment = DMA_PDATAALIGN_WORD;
  hdma_handler.Init.MemDataAlignment = DMA_MDATAALIGN_WORD;
  hdma_handler.Init.Mode = DMA_CIRCULAR;
  hdma_handler.Init.Priority = DMA_PRIORITY_HIGH;
  hdma_handler.Init.FIFOMode = DMA_FIFOMODE_ENABLE;
  hdma_handler.Init.FIFOThreshold = DMA_FIFO_THRESHOLD_FULL;
  hdma_handler.Init.MemBurst = DMA_MBURST_SINGLE;
  hdma_handler.Init.PeriphBurst = DMA_PBURST_SINGLE;
  hdma_handler.Instance = DMA2_Stream3;

  /* Associate the initialized DMA handle to the DCMI handle */
  __HAL_LINKDMA(&hcamera_dcmi, DMA_Handle, hdma_handler);

  /*** Configure the NVIC for DCMI and DMA ***/
  /* NVIC configuration for DCMI transfer complete interrupt */
  HAL_NVIC_SetPriority(DCMI_IRQn, BSP_CAMERA_IT_PRIORITY, 0);
  HAL_NVIC_EnableIRQ(DCMI_IRQn);

  /* NVIC configuration for DMA2D transfer complete interrupt */
  HAL_NVIC_SetPriority(DMA2_Stream3_IRQn, BSP_CAMERA_IT_PRIORITY, 0);
  HAL_NVIC_EnableIRQ(DMA2_Stream3_IRQn);

  /* Configure the DMA stream */
  (void)HAL_DMA_Init(hcamera_dcmi.DMA_Handle);

  return ret;
}

/**
  * @brief  Register Bus IOs if component ID is OK
  * @retval error status
  */
static int OV5640_Probe(uint32_t Resolution, uint32_t PixelFormat)
{
  int ret = BSP_ERROR_NONE;
  OV5640_IO_t              IOCtx;
  static OV5640_Object_t   OV5640Obj;

  /* Configure the audio driver */
  IOCtx.Address     = CAMERA_OV5640_ADDRESS;
  IOCtx.Init        = BSP_I2C1_Init;
  IOCtx.DeInit      = BSP_I2C1_DeInit;
  IOCtx.ReadReg     = BSP_I2C1_ReadReg16;
  IOCtx.WriteReg    = BSP_I2C1_WriteReg16;
  IOCtx.GetTick     = BSP_GetTick;

  if(OV5640_RegisterBusIO(&OV5640Obj, &IOCtx) != OV5640_OK)
  {
    ret = BSP_ERROR_COMPONENT_FAILURE;
  }
  else if(OV5640_ReadID(&OV5640Obj, &CameraId) != OV5640_OK)
  {
    ret = BSP_ERROR_COMPONENT_FAILURE;
  }
  else
  {
    if(CameraId != OV5640_ID)
    {
      ret = BSP_ERROR_UNKNOWN_COMPONENT;
    }
    else
    {
      Camera_Drv = (CAMERA_Drv_t *) &OV5640_CAMERA_Driver;
      Camera_CompObj = &OV5640Obj;
      if(Camera_Drv->Init(Camera_CompObj, Resolution, PixelFormat) != OV5640_OK)
      {
        ret = BSP_ERROR_COMPONENT_FAILURE;
      }
      else if(Camera_Drv->GetCapabilities(Camera_CompObj, &Camera_Cap) != OV5640_OK)
      {
        ret = BSP_ERROR_COMPONENT_FAILURE;
      }
      else
      {
        ret = BSP_ERROR_NONE;
      }
    }
  }

  return ret;
}
#else
#error "Selected camera sensor is not supported"
#endif

/**
 * @brief Frame Event callback
 * @param Instance Camera instance
 */
void BSP_CAMERA_FrameEventCallback()
{
  
  __disable_irq();
  
  /*Notifies the backgound task about new frame available for processing*/
  App_Config.new_frame_ready = 1;
  
  /*Suspend acquisition of the data stream coming from camera*/
  BSP_CAMERA_DCMI_Suspend();
  
  __enable_irq();
}

/**
  * @brief  Frame event callback
  * @param  hdcmi pointer to the DCMI handle
  * @retval None
  */
void HAL_DCMI_FrameEventCallback(DCMI_HandleTypeDef *hdcmi)
{
  /* Prevent unused argument(s) compilation warning */
  UNUSED(hdcmi);

  BSP_CAMERA_FrameEventCallback();
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
  hdcmi->pBuffPtr = (uint32_t)pData;

  /* Enable the DMA Stream */
  uint32_t pLineData = (uint32_t)pCameraLineBuffer;
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
  uint32_t line_size = hdcmi->XferSize * 4U;
  uint8_t *pDst = (uint8_t *)hdcmi->pBuffPtr + line_size * hdcmi->XferCount;

  if (HAL_MDMA_Start_IT(&hmdma, (uint32_t)pCameraLineBuffer, (uint32_t)pDst, line_size, 1) != HAL_OK)
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

/* Public functions Definition -----------------------------------------------*/
/**
 * @brief Resume the CAMERA DCMI capture
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_Resume()
{
  int32_t ret = BSP_ERROR_NONE;

  if (HAL_DCMI_Resume(&hcamera_dcmi) != HAL_OK)
  {
    ret = BSP_ERROR_PERIPH_FAILURE;
  }

  /* Return BSP status */
  return ret;
}

/**
  * @brief Suspend the CAMERA capture
  * @param  Instance Camera instance.
  */
int32_t BSP_CAMERA_DCMI_Suspend()
{
  int32_t ret;

  if(HAL_DCMI_Suspend(&hcamera_dcmi) != HAL_OK)
  {
    return BSP_ERROR_PERIPH_FAILURE;
  }
  else
  {
    ret = BSP_ERROR_NONE;
  }

  /* Return BSP status */
  return ret;
}

/**
 * @brief  CAMERA DCMI power down
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_PwrDown()
{
  int32_t ret = BSP_ERROR_NONE;
  GPIO_InitTypeDef gpio_init_structure;

  /* Init DCMI PWR_ENABLE Pin */
  gpio_init_structure.Pin       = CAMERA_EN_Pin;
  gpio_init_structure.Mode      = GPIO_MODE_OUTPUT_PP;
  gpio_init_structure.Pull      = GPIO_NOPULL;
  gpio_init_structure.Speed     = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(CAMERA_EN_GPIO_Port, &gpio_init_structure);

#if CAMERA_SENSOR == CAMERA_SENSOR_OV5640
  /* Assert the camera POWER_DOWN pin (active high) */
  HAL_GPIO_WritePin(CAMERA_EN_GPIO_Port, CAMERA_EN_Pin, GPIO_PIN_SET);
#else
#error "Selected camera sensor is not supported"
#endif

  /* Return BSP status */
  return ret;
}

/**
 * @brief  CAMERA DCMI power up
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_PwrUp()
{
  int32_t ret = BSP_ERROR_NONE;
  GPIO_InitTypeDef gpio_init_structure;

  /* Init DCMI PWR_ENABLE Pin */
  gpio_init_structure.Pin       = CAMERA_EN_Pin;
  gpio_init_structure.Mode      = GPIO_MODE_OUTPUT_PP;
  gpio_init_structure.Pull      = GPIO_NOPULL;
  gpio_init_structure.Speed     = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(CAMERA_EN_GPIO_Port, &gpio_init_structure);

#if CAMERA_SENSOR == CAMERA_SENSOR_OV5640
  /* Assert the camera POWER_DOWN pin (active high) */
  HAL_GPIO_WritePin(CAMERA_EN_GPIO_Port, CAMERA_EN_Pin, GPIO_PIN_RESET);
#else
#error "Selected camera sensor is not supported"
#endif

  /* Return BSP status */
  return ret;
}

/**
 * @brief  CAMERA DCMI hardware reset
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_HwReset()
{
  int32_t ret = BSP_ERROR_NONE;

  if (BSP_CAMERA_DCMI_PwrDown() != BSP_ERROR_NONE)
  {
    ret = BSP_ERROR_PERIPH_FAILURE;
  }

  HAL_Delay(100); /* POWER_DOWN de-asserted during 100 ms */

  /* Assert the camera POWER_DOWN pin (active high) */
  if (BSP_CAMERA_DCMI_PwrUp() != BSP_ERROR_NONE)
  {
    ret = BSP_ERROR_PERIPH_FAILURE;
  }

  HAL_Delay(200);

  /* Return BSP status */
  return ret;
}

/**
 * @brief  CAMERA DCMI intitialization
 * @param  resolution desired resolution
 * @param  pixel_format frame pixel format
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_Init(uint32_t Resolution, uint32_t Pixel_Format)
{
  int32_t ret = BSP_ERROR_NONE;

  __HAL_RCC_MDMA_CLK_ENABLE();

  /* Init MDMA for camera line buffer to frame buffer copy */
  hmdma.Instance = MDMA_Channel0;
  hmdma.Init.Request = MDMA_REQUEST_SW;
  hmdma.Init.TransferTriggerMode = MDMA_BLOCK_TRANSFER;
  hmdma.Init.Priority = MDMA_PRIORITY_HIGH;
  hmdma.Init.Endianness = MDMA_LITTLE_ENDIANNESS_PRESERVE;
  hmdma.Init.SourceInc = MDMA_SRC_INC_WORD;
  hmdma.Init.DestinationInc = MDMA_DEST_INC_WORD;
  hmdma.Init.SourceDataSize = MDMA_SRC_DATASIZE_WORD;
  hmdma.Init.DestDataSize = MDMA_DEST_DATASIZE_WORD;
  hmdma.Init.DataAlignment = MDMA_DATAALIGN_PACKENABLE;
  hmdma.Init.SourceBurst = MDMA_DEST_BURST_SINGLE;
  hmdma.Init.DestBurst = MDMA_DEST_BURST_16BEATS;
  hmdma.Init.BufferTransferLength = 128;
  hmdma.Init.SourceBlockAddressOffset = 0;
  hmdma.Init.DestBlockAddressOffset = 0;
  if (HAL_MDMA_Init(&hmdma) != HAL_OK)
  {
    Error_Handler();
  }

  /* NVIC configuration for MDMA transfer complete interrupt */
  HAL_NVIC_SetPriority(MDMA_IRQn, 15U, 0);
  HAL_NVIC_EnableIRQ(MDMA_IRQn);

#if CAMERA_SENSOR == CAMERA_SENSOR_OV5640
  if (GPIO_Init_OV5640() != BSP_ERROR_NONE)
  {
    ret = BSP_ERROR_PERIPH_FAILURE;
  }
  if (DCMI_Init_OV5640(Resolution, Pixel_Format) != BSP_ERROR_NONE)
  {
    ret = BSP_ERROR_PERIPH_FAILURE;
  }
#else
#error "Selected camera sensor is not supported"
#endif

  /* Return BSP status */
  return ret;
}

/**
 * @brief  CAMERA DCMI set crop
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_Set_Crop()
{
  int32_t ret = BSP_ERROR_NONE;

  /* Center-crop the 320x240 frame to 240x240 */
  const uint32_t x0 = (QVGA_RES_WIDTH - QVGA_RES_HEIGHT) / 2;
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

  /* Return BSP status */
  return ret;
}

/**
 * @brief  Start CAMERA DCMI capture
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_StartCapture(uint8_t *camera_capture_buffer)
{
  int32_t ret = BSP_ERROR_NONE;

  /*
   * Start the Camera Capture
   * Using intermediate line buffer in D2-AHB domain to support high pixel clocks.
   */
  if (HAL_DCMIEx_Start_DMA_MDMA(&hcamera_dcmi, CAMERA_MODE_CONTINUOUS,
                                camera_capture_buffer,
                                CAM_LINE_SIZE, CAM_RES_HEIGHT) != HAL_OK)
  {
    ret = BSP_ERROR_COMPONENT_FAILURE;
  }

  /* Return BSP status */
  return ret;
}

/**
 * @brief  CAMERA DCMI set mirrorflip
 * @param  Mirror_Flip boolean value to set/reset mirrorflip
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_Set_MirrorFlip(uint32_t MirrorFlip)
{
  int32_t ret = BSP_ERROR_NONE;

  if ((Camera_Cap.MirrorFlip == 0U) && (MirrorFlip != 0U))
  {
    ret = BSP_ERROR_FEATURE_NOT_SUPPORTED;
  }
  else if (Camera_Drv->MirrorFlipConfig(Camera_CompObj, MirrorFlip) < 0)
  {
    ret = BSP_ERROR_COMPONENT_FAILURE;
  }
  else
  {
    Camera_Ctx.MirrorFlip = MirrorFlip;
  }

  /* Return BSP status */
  return ret;
}

/**
 * @brief  CAMERA DCMI set testbar
 * @param  Testbar boolean value to set/reset testbar
 * @retval BSP status
 */
int32_t BSP_CAMERA_DCMI_Set_TestBar(uint32_t Testbar)
{
  int32_t ret = BSP_ERROR_NONE;

#if CAMERA_SENSOR == CAMERA_SENSOR_OV5640
  if (Testbar)
  {
    if (OV5640_ColorbarModeConfig((OV5640_Object_t *)Camera_CompObj, COLORBAR_MODE_ENABLE) != BSP_ERROR_NONE)
    {
      ret = BSP_ERROR_COMPONENT_FAILURE;
    }
  }
  else
  {
    if (OV5640_ColorbarModeConfig((OV5640_Object_t *)Camera_CompObj, COLORBAR_MODE_DISABLE) != BSP_ERROR_NONE)
    {
      ret = BSP_ERROR_COMPONENT_FAILURE;
    }
  }
#else
#error "Selected camera sensor is not supported"
#endif

  /* Return BSP status */
  return ret;
}

/**
  * @brief  This function handles DCMI interrupt request.
  * @param  Instance Camera instance
  * @retval None
  */
void BSP_CAMERA_DCMI_IRQHandler()
{
  HAL_DCMI_IRQHandler(&hcamera_dcmi);
}

/**
  * @brief  This function handles DCMI DMA interrupt request.
  * @param  Instance Camera instance
  * @retval None
  */
void BSP_CAMERA_DCMI_DMA_IRQHandler()
{
  HAL_DMA_IRQHandler(hcamera_dcmi.DMA_Handle);
}
