 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_camera_usb.c
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
#include <assert.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "nucleo_h743zi2_camera_usb.h"
#include "usb_cam.h"
#include "main.h"
#include "printf.h"
#include "stm32h7xx_hal.h"
#include "stm32h7xx_hal_def.h"

/* Private macros ------------------------------------------------------------*/
#define container_of(ptr, type, member) ({ \
  void *__mptr = (ptr); \
  __mptr - offsetof(type,member); \
})

#define CAPTURE_PERIOD          (0x51615)
#define SOI_SIZE                (2)
#define MCU_SIZE                (8)

#define JPG_SOI  0xD8
#define JPG_EOI  0xD9
#define JPG_RST0 0xD0
#define JPG_RST1 0xD1
#define JPG_RST2 0xD2
#define JPG_RST3 0xD3
#define JPG_RST4 0xD4
#define JPG_RST5 0xD5
#define JPG_RST6 0xD6
#define JPG_RST7 0xD7
#define JPG_TEM  0x01
#define JPG_DHT  0xC4
#define JPG_SOS  0xDA

/* Private variables ---------------------------------------------------------*/
HCD_HandleTypeDef         hhcd_USB_OTG_FS;
USB_CAM_DeviceInfo_t      dev_info;
USB_CAM_CaptureInfo_t     info;
JPEG_HandleTypeDef        hjpeg;
static USB_CAM_Hdl_t      app_Hdl;
static uint8_t            jpeg_buffer[JPEG_BUFFER_SIZE];
__attribute__((section(".jpeg_temp_buffer")))
__attribute__ ((aligned (32)))
static uint8_t            jpeg_temp_buffer[QVGA_RES_WIDTH * MCU_SIZE * RGB_565_BPP];
#if ASPECT_RATIO_MODE == ASPECT_RATIO_CROP
__attribute__((section(".jpeg_temp_buffer_crop")))
__attribute__ ((aligned (32)))
static uint8_t            jpeg_temp_buffer_crop[QVGA_RES_WIDTH * MCU_SIZE * RGB_565_BPP];
#endif
static uint8_t            *image_buffer;
static volatile uint8_t   *new_frame_ready;

static const uint8_t soi_huffman_table[] = {
  0xff, 0xd8, /* SOI */
  0xff, 0xc4, 0x00, 0x1f, 0x00, 0x00, 0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, /* H0 */
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a,
  0x0b,
  0xff, 0xc4, 0x00, 0xb5, 0x10, 0x00, 0x02, 0x01, 0x03, 0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, /* H1 */
  0x04, 0x00, 0x00, 0x01, 0x7d, 0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41,
  0x06, 0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xa1, 0x08, 0x23, 0x42, 0xb1,
  0xc1, 0x15, 0x52, 0xd1, 0xf0, 0x24, 0x33, 0x62, 0x72, 0x82, 0x09, 0x0a, 0x16, 0x17, 0x18, 0x19,
  0x1a, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44,
  0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x63, 0x64,
  0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x83, 0x84,
  0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2,
  0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9,
  0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7,
  0xd8, 0xd9, 0xda, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf1, 0xf2, 0xf3,
  0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa,
  0xff, 0xc4, 0x00, 0x1f, 0x01, 0x00, 0x03, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, /* H2 */
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a,
  0x0b,
  0xff, 0xc4, 0x00, 0xb5, 0x11, 0x00, 0x02, 0x01, 0x02, 0x04, 0x04, 0x03, 0x04, 0x07, 0x05, 0x04, /* H3 */
  0x04, 0x00, 0x01, 0x02, 0x77, 0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21, 0x31, 0x06, 0x12,
  0x41, 0x51, 0x07, 0x61, 0x71, 0x13, 0x22, 0x32, 0x81, 0x08, 0x14, 0x42, 0x91, 0xa1, 0xb1, 0xc1,
  0x09, 0x23, 0x33, 0x52, 0xf0, 0x15, 0x62, 0x72, 0xd1, 0x0a, 0x16, 0x24, 0x34, 0xe1, 0x25, 0xf1,
  0x17, 0x18, 0x19, 0x1a, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43,
  0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x63,
  0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x82,
  0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99,
  0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7,
  0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5,
  0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf2, 0xf3,
  0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa,
};

static struct cvt_JpegDecodeCtx {
  JPEG_HandleTypeDef hjpeg;
  DMA2D_HandleTypeDef hdma2d;
#if ASPECT_RATIO_MODE == ASPECT_RATIO_CROP
  DMA_HandleTypeDef hdma_memtomem_dma1_stream1;
#endif
  uint8_t *p_dst;
  uint8_t *p_src;
  int src_len;
  int width;
  int height;
  int dst_stride;
  int row_nb;
  int total;
} JPG_DecodeCtx;

/* Private functions prototypes ----------------------------------------------*/
static uint8_t *jpg_move_to_next_marker(uint8_t *data, uint8_t *end);
static uint8_t *jpg_jump_marker(uint8_t *data, uint8_t *end);
static uint8_t *jpg_get_marker(uint8_t *data, uint8_t *end, uint8_t *marker);
static int jpg_is_huffman_present(uint8_t *data, int len);

static void MX_USB_OTG_FS_HCD_Init(void);
void HAL_HCD_MspInit(HCD_HandleTypeDef* hhcd);
static void JpegInit();
static void JpegToRgb(uint8_t *p_dst, uint8_t *p_src, int src_len);

/* Private functions definitions ---------------------------------------------*/
static uint8_t *jpg_move_to_next_marker(uint8_t *data, uint8_t *end)
{
	while (data < end) {
		if (*data == 0xFF)
			data++;
		else if (*(data - 1) == 0xFF)
			return data;
		else
			assert(0);
	}

	return NULL;
}

static uint8_t *jpg_jump_marker(uint8_t *data, uint8_t *end)
{
	int len;

	if (data + 2 > end)
		return NULL;

	len = *data++;
	len = (len << 8) + *data++;

	data += len - 2;

	return data < end ? data : NULL;
}

static uint8_t *jpg_get_marker(uint8_t *data, uint8_t *end, uint8_t *marker)
{
	data = jpg_move_to_next_marker(data, end);
	if (!data)
		return NULL;

	*marker = *data++;
	switch (*marker) {
	case JPG_SOI:
	case JPG_EOI:
	case JPG_RST0...JPG_RST7:
	case JPG_TEM:
		/* standalone marker */
		data = data < end ? data : NULL;
		break;
	case JPG_SOS:
		/* jpg data begins */
		data = NULL;
		break;
	default:
		/* others marker with len */
		data = jpg_jump_marker(data, end);
		break;
	}

	return data;
}

static int jpg_is_huffman_present(uint8_t *data, int len)
{
	uint8_t *end = data + len;
	uint8_t marker;

	do {
		data = jpg_get_marker(data, end, &marker);
		if (marker == JPG_DHT)
			return 1;
	} while (data);

	return 0;
}


void HAL_JPEG_GetDataCallback(JPEG_HandleTypeDef *hjpeg, uint32_t NbDecodedData)
{
  struct cvt_JpegDecodeCtx *ctx = container_of(hjpeg, struct cvt_JpegDecodeCtx, hjpeg);

  HAL_JPEG_ConfigInputBuffer(hjpeg, ctx->p_src + SOI_SIZE, ctx->src_len - SOI_SIZE);
}

void HAL_JPEG_DataReadyCallback(JPEG_HandleTypeDef *hjpeg, uint8_t *pDataOut, uint32_t OutDataLength)
{
  struct cvt_JpegDecodeCtx *ctx = container_of(hjpeg, struct cvt_JpegDecodeCtx, hjpeg);
  DMA2D_HandleTypeDef *p_hdma2d = &ctx->hdma2d;
  int ret;

  SCB_CleanDCache_by_Addr((uint32_t *)pDataOut, OutDataLength);
#if ASPECT_RATIO_MODE == ASPECT_RATIO_CROP
  ret = HAL_DMA2D_Start(p_hdma2d, (uint32_t) pDataOut, (uint32_t) jpeg_temp_buffer_crop, QVGA_RES_WIDTH, MCU_SIZE);
  assert(ret == HAL_OK);
  ret = HAL_DMA2D_PollForTransfer(p_hdma2d, 1000);
  assert(ret == HAL_OK);

  for (int i = 0; i < MCU_SIZE; i++)
  {
    HAL_DMA_Start(&JPG_DecodeCtx.hdma_memtomem_dma1_stream1, 
    (uint32_t) (jpeg_temp_buffer_crop + (QVGA_RES_WIDTH - QVGA_RES_HEIGHT) + i * QVGA_RES_WIDTH * RGB_565_BPP), 
    (uint32_t) (ctx->p_dst + i * ctx->dst_stride), 
    ctx->dst_stride);
    assert(ret == HAL_OK);
    HAL_DMA_PollForTransfer(&JPG_DecodeCtx.hdma_memtomem_dma1_stream1, HAL_DMA_FULL_TRANSFER, 1000);
    assert(ret == HAL_OK);
  }
#else
  ret = HAL_DMA2D_Start(p_hdma2d, (uint32_t) pDataOut, (uint32_t) ctx->p_dst, ctx->width, MCU_SIZE);
  assert(ret == HAL_OK);
  ret = HAL_DMA2D_PollForTransfer(p_hdma2d, 1000);
  assert(ret == HAL_OK);
#endif
  ctx->p_dst += ctx->dst_stride * MCU_SIZE;
  ctx->row_nb++;
  ctx->total += OutDataLength;
}

void HAL_JPEG_DecodeCpltCallback(JPEG_HandleTypeDef *hjpeg)
{
  ;
}

void HAL_JPEG_ErrorCallback(JPEG_HandleTypeDef *hjpeg)
{
  Error_Handler();
}

void HAL_JPEG_MspInit(JPEG_HandleTypeDef* hjpeg)
{
  if (hjpeg->Instance==JPEG)
  {
    __HAL_RCC_JPEG_CLK_ENABLE();
  }
}

void HAL_JPEG_MspDeInit(JPEG_HandleTypeDef* hjpeg)
{
  if (hjpeg->Instance==JPEG)
  {
    __HAL_RCC_JPEG_CLK_DISABLE();
  }
}

void HAL_DMA2D_MspInit(DMA2D_HandleTypeDef* hdma2d)
{
  if(hdma2d->Instance==DMA2D)
  {
    __HAL_RCC_DMA2D_CLK_ENABLE();
  }
}

void HAL_DMA2D_MspDeInit(DMA2D_HandleTypeDef* hdma2d)
{
  if(hdma2d->Instance==DMA2D)
  {
    __HAL_RCC_DMA2D_CLK_DISABLE();
  }
}

/* OverCurrent occurs while powering webcam */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  if(GPIO_Pin == USB_OTG_FS_OVCR_Pin)
  {
    Error_Handler();
  }
}

#if ASPECT_RATIO_MODE == ASPECT_RATIO_CROP
static void cvt_DmaInit(void)
{
  /* DMA controller clock enable */
  __HAL_RCC_DMA1_CLK_ENABLE();

  /* Configure DMA request hdma_memtomem_dma1_stream1 on DMA1_Stream1 */
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Instance = DMA1_Stream1;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.Request = DMA_REQUEST_MEM2MEM;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.Direction = DMA_MEMORY_TO_MEMORY;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.PeriphInc = DMA_PINC_ENABLE;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.MemInc = DMA_MINC_ENABLE;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.Mode = DMA_NORMAL;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.Priority = DMA_PRIORITY_LOW;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.FIFOMode = DMA_FIFOMODE_ENABLE;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.FIFOThreshold = DMA_FIFO_THRESHOLD_FULL;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.MemBurst = DMA_MBURST_SINGLE;
  JPG_DecodeCtx.hdma_memtomem_dma1_stream1.Init.PeriphBurst = DMA_PBURST_SINGLE;
  if (HAL_DMA_Init(&JPG_DecodeCtx.hdma_memtomem_dma1_stream1) != HAL_OK)
  {
    Error_Handler();
  }

  /* DMA interrupt init */
  /* DMA1_Stream0_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Stream0_IRQn);
}
#endif

static void cvt_Dma2dInit()
{
  DMA2D_HandleTypeDef *p_hdma2d = &JPG_DecodeCtx.hdma2d;
  int ret;

  p_hdma2d->Instance = DMA2D;
  p_hdma2d->Init.Mode = DMA2D_M2M_PFC;
  p_hdma2d->Init.ColorMode = DMA2D_OUTPUT_RGB565;
  p_hdma2d->Init.OutputOffset = 0;

  p_hdma2d->LayerCfg[1].AlphaMode = DMA2D_NO_MODIF_ALPHA;
  p_hdma2d->LayerCfg[1].InputAlpha = 0;
  p_hdma2d->LayerCfg[1].InputColorMode = DMA2D_INPUT_YCBCR;
  p_hdma2d->LayerCfg[1].InputOffset = 0;
  p_hdma2d->LayerCfg[1].RedBlueSwap = DMA2D_RB_REGULAR;
  p_hdma2d->LayerCfg[1].ChromaSubSampling = DMA2D_CSS_422;

  ret = HAL_DMA2D_Init(p_hdma2d);
  assert(ret == HAL_OK);

  ret = HAL_DMA2D_ConfigLayer(p_hdma2d, DMA2D_FOREGROUND_LAYER);
  assert(ret == HAL_OK);
}

static void JpegInit(void)
{
  JPEG_HandleTypeDef *p_hjpeg = &JPG_DecodeCtx.hjpeg;
  int ret;

  p_hjpeg->Instance = JPEG;
  ret = HAL_JPEG_Init(p_hjpeg);
  assert(ret == HAL_OK);
}

static void JpegToRgb(uint8_t *p_dst, uint8_t *p_src, int src_len)
{
  int ret;

  JPG_DecodeCtx.p_dst = p_dst;
  JPG_DecodeCtx.p_src = p_src;
  JPG_DecodeCtx.src_len = src_len;
  JPG_DecodeCtx.width = CAM_RES_WIDTH;
  JPG_DecodeCtx.height = CAM_RES_HEIGHT;
  JPG_DecodeCtx.dst_stride = CAM_LINE_SIZE;
  JPG_DecodeCtx.row_nb = 0;
  JPG_DecodeCtx.total = 0;

  cvt_Dma2dInit();
#if ASPECT_RATIO_MODE == ASPECT_RATIO_CROP
  cvt_DmaInit();
#endif

  if (jpg_is_huffman_present(JPG_DecodeCtx.p_src, JPG_DecodeCtx.src_len))
    ret = HAL_JPEG_Decode(&JPG_DecodeCtx.hjpeg, JPG_DecodeCtx.p_src, JPG_DecodeCtx.src_len, jpeg_temp_buffer,
                          QVGA_RES_WIDTH * MCU_SIZE * RGB_565_BPP, 1000);
  else
    ret = HAL_JPEG_Decode(&JPG_DecodeCtx.hjpeg, (uint8_t *) soi_huffman_table, sizeof(soi_huffman_table), jpeg_temp_buffer,
                          QVGA_RES_WIDTH * MCU_SIZE * RGB_565_BPP, 1000);
  assert(ret == HAL_OK);

  HAL_DMA2D_DeInit(&JPG_DecodeCtx.hdma2d);
}

/**
  * @brief USB_OTG_FS Initialization Function
  * @param None
  * @retval None
  */
static void MX_USB_OTG_FS_HCD_Init(void)
{
  hhcd_USB_OTG_FS.Instance = USB_OTG_FS;
  hhcd_USB_OTG_FS.Init.Host_channels = 16;
  hhcd_USB_OTG_FS.Init.speed = HCD_SPEED_FULL;
  hhcd_USB_OTG_FS.Init.dma_enable = DISABLE;
  hhcd_USB_OTG_FS.Init.phy_itface = HCD_PHY_EMBEDDED;
  hhcd_USB_OTG_FS.Init.Sof_enable = ENABLE;
  if (HAL_HCD_Init(&hhcd_USB_OTG_FS) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
* @brief HCD MSP Initialization
* This function configures the hardware resources used in this example
* @param hhcd: HCD handle pointer
* @retval None
*/
void HAL_HCD_MspInit(HCD_HandleTypeDef* hhcd)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInitStruct = {0};
  if(hhcd->Instance==USB_OTG_FS)
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
    __HAL_RCC_GPIOD_CLK_ENABLE();
    __HAL_RCC_GPIOG_CLK_ENABLE();
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

    /* Peripheral clock enable */
    __HAL_RCC_USB_OTG_FS_CLK_ENABLE();
    /* USB_OTG_FS interrupt Init */
    HAL_NVIC_SetPriority(OTG_FS_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(OTG_FS_IRQn);
    
    /*Configure GPIO pin : USB_OTG_FS_PWR_EN_Pin */
    HAL_GPIO_WritePin(USB_OTG_FS_PWR_EN_GPIO_Port, USB_OTG_FS_PWR_EN_Pin, GPIO_PIN_RESET);
    
    GPIO_InitStruct.Pin       = USB_OTG_FS_PWR_EN_Pin;
    GPIO_InitStruct.Mode      = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull      = GPIO_NOPULL;
    GPIO_InitStruct.Speed     = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(USB_OTG_FS_PWR_EN_GPIO_Port, &GPIO_InitStruct);

    /*Configure GPIO pin : USB_OTG_FS_OVCR_Pin */
    GPIO_InitStruct.Pin       = USB_OTG_FS_OVCR_Pin;
    GPIO_InitStruct.Mode      = GPIO_MODE_IT_RISING_FALLING;
    GPIO_InitStruct.Pull      = GPIO_NOPULL;
    HAL_GPIO_Init(USB_OTG_FS_OVCR_GPIO_Port, &GPIO_InitStruct);

    /* EXTI interrupt init*/
    HAL_NVIC_SetPriority(EXTI9_5_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);
  }
}

/* Public functions ----------------------------------------------------------*/
/**
  * @brief  Initializes the camera in default mode.
  * @param  camera_buffer_ptr Camera buffer to store the image
  * @param  new_frame_ready_p Pointer to set new frame ready value
  * @retval BSP status
  */
int BSP_CAMERA_USB_Init(uint8_t *camera_buffer_ptr, volatile uint8_t *new_frame_ready_p)
{
  USB_CAM_Conf_t conf_usb = {0};
  int ret;

  new_frame_ready = new_frame_ready_p;
  image_buffer = camera_buffer_ptr;

  MX_USB_OTG_FS_HCD_Init();
  
  JpegInit();
  
  /* Allow printf function to display USB communication information using serial port */
  MX_USART3_UART_Init();

  conf_usb.p_hhcd = &hhcd_USB_OTG_FS;
  conf_usb.width = QVGA_RES_WIDTH;
  conf_usb.height = QVGA_RES_HEIGHT;
  conf_usb.period = CAPTURE_PERIOD;
  conf_usb.payload_type = USB_CAM_PAYLOAD_JPEG;
  app_Hdl = USB_CAM_Init(&conf_usb);
  assert(app_Hdl);
  
  ret = USB_CAM_SetupDevice(app_Hdl, &dev_info);
  if (ret)
  {
    Error_Handler();
  }

  return ret;
}

/**
  * @brief  Start new frame capture.
  * @retval BSP status
  */
int BSP_CAMERA_USB_StartCapture()
{
  int ret;
  
  ret = USB_CAM_PushBuffer(app_Hdl, jpeg_buffer, JPEG_BUFFER_SIZE);
  assert(ret == 0);

  return ret;
}

/**
  * @brief  Wait for camera frame.
  * @retval BSP status
  */
int BSP_CAMERA_USB_WaitForFrame()
{
  int ret;

  do {
    ret = USB_CAM_PopBuffer(app_Hdl, &info);
  } while (ret);

  if (info.len == JPEG_BUFFER_SIZE)
    /* JPEG buffer saturated */
    Error_Handler();
  
  JpegToRgb(image_buffer, info.buffer, info.len);

  *new_frame_ready = 1;

  return ret;
}
