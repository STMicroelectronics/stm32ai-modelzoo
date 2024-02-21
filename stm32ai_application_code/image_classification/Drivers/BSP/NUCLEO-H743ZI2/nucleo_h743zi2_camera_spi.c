 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_camera_spi.c
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
#include "nucleo_h743zi2_camera_spi.h"
#include "ArducamCamera.h"
#include "stm32h7xx_hal.h"

/* Private variables ---------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;
static ArducamCamera cam_i;
SPI_HandleTypeDef hspi1;
static uint8_t *camera_capture_buffer;


/* Public functions Definition -----------------------------------------------*/
/**
 * @brief  Arducam camera init with the Arducam library
 * @param  None
 * @retval None
 */
void SPI_Cam_Init_Begin(uint8_t *p_camera_capture_buffer)
{
  camera_capture_buffer = p_camera_capture_buffer;
  // PA15  ------> SPI1_NSS
  cam_i = createArducamCamera(15);
  if (begin(&cam_i) != 0)
  {
	  Error_Handler();
  }
}

/**
 * @brief  Arducam camera take picture with the Arducam library
 * @param  None
 * @retval None
 */
void SPI_Cam_Take_Picture()
{
    if (takePicture(&cam_i, CAM_IMAGE_MODE_QVGA, CAM_IMAGE_PIX_FMT_RGB565) != CAM_ERR_SUCCESS)
    {
    	Error_Handler();
    }
}

/**
 * @brief  Fetch the data from the SPI camera and put it into App_Config.camera_capture_buffer
 * @param  None
 * @retval None
 */
void SPI_Cam_Fetch_Data()
{
#if ASPECT_RATIO_MODE == ASPECT_RATIO_CROP
  int size = 80;
  int rx_len;
  int buffer_pos = 0;
  int row_buffer_pos;
  int col_buffer_pos;
  int left_border = RGB_565_BPP*(QVGA_RES_WIDTH-CAM_RES_WIDTH)/2; //80
  int right_border = (RGB_565_BPP*QVGA_RES_WIDTH)-(RGB_565_BPP*(QVGA_RES_WIDTH-CAM_RES_WIDTH)/2)-1; //559
  for (int row_qvga = QVGA_RES_HEIGHT-1; row_qvga > 0; row_qvga--) {
	  for (int col_qvga = 0; col_qvga < QVGA_RES_WIDTH*RGB_565_BPP; col_qvga+=size) {
		  if (col_qvga < left_border || col_qvga > right_border){
			  rx_len = readBuff(&cam_i, NULL, size); //Flush 80 bytes
			  if (rx_len != size){Error_Handler();}
		  }
		  else {
			  row_buffer_pos = row_qvga * RGB_565_BPP * CAM_RES_WIDTH;
			  col_buffer_pos = col_qvga - size;
			  buffer_pos = row_buffer_pos + col_buffer_pos;
			  rx_len = readBuff(&cam_i, &camera_capture_buffer[buffer_pos], size);
			  if (rx_len != size){Error_Handler();}
		  }
	  }
  }
#else
  int rx_len;
  int size = 160;
  int buffer_pos;

  for (int row_qvga = QVGA_RES_HEIGHT-1; row_qvga > 0; row_qvga--) {
    for (int col_qvga = 0; col_qvga < QVGA_RES_WIDTH*RGB_565_BPP; col_qvga+=size) {
    	buffer_pos = row_qvga * RGB_565_BPP * CAM_RES_WIDTH + col_qvga;
    	rx_len = readBuff(&cam_i, &camera_capture_buffer[buffer_pos], size);
    	if (rx_len != size){Error_Handler();}
    }
  }
#endif
}

/**
 * @brief  Swap some bytes to correct the buffer
 * @param  None
 * @retval None
 */
void SPI_Cam_Swap_Bytes()
{
  int i;

  for (i = 0; i < CAM_FRAME_BUFFER_SIZE; i+= 2) {
    uint8_t tmp = camera_capture_buffer[i];

    camera_capture_buffer[i] = camera_capture_buffer[i + 1];
    camera_capture_buffer[i + 1] = tmp;
  }
  /*Notifies the backgound task about new frame available for processing*/
  App_Config.new_frame_ready = 1;
}

void delayInit()
{

}

void delayMs(uint16_t nms)
{
  HAL_Delay(nms);
}

/**
  * @brief SPI1 Initialization Function
  * @param None
  * @retval None
  */
void spiBegin()
{
  /* SPI1 parameter configuration*/
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_MASTER;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi1.Init.NSS = SPI_NSS_SOFT;
  hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_8;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi1.Init.CRCPolynomial = 0x0;
  hspi1.Init.NSSPMode = SPI_NSS_PULSE_ENABLE;
  hspi1.Init.NSSPolarity = SPI_NSS_POLARITY_LOW;
  hspi1.Init.FifoThreshold = SPI_FIFO_THRESHOLD_01DATA;
  hspi1.Init.TxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
  hspi1.Init.RxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
  hspi1.Init.MasterSSIdleness = SPI_MASTER_SS_IDLENESS_00CYCLE;
  hspi1.Init.MasterInterDataIdleness = SPI_MASTER_INTERDATA_IDLENESS_00CYCLE;
  hspi1.Init.MasterReceiverAutoSusp = SPI_MASTER_RX_AUTOSUSP_DISABLE;
  hspi1.Init.MasterKeepIOState = SPI_MASTER_KEEP_IO_STATE_ENABLE;
  hspi1.Init.IOSwap = SPI_IO_SWAP_DISABLE;
  if (HAL_SPI_Init(&hspi1) != HAL_OK)
  {
    Error_Handler();
  }
}

uint8_t spiReadWriteByte(uint8_t TxData)
{
  HAL_StatusTypeDef ret;
  uint8_t RxData;

  ret = HAL_SPI_TransmitReceive(&hspi1, &TxData, &RxData, 1, HAL_MAX_DELAY);
  assert(ret == HAL_OK);

  return RxData;
}

void spiCsLow(int pin)
{
  __HAL_SPI_ENABLE(&hspi1);
  HAL_GPIO_WritePin(SPI_CAMERA_CS_GPIO_Port, SPI_CAMERA_CS_Pin, GPIO_PIN_RESET);
}

void spiCsHigh(int pin)
{
  HAL_GPIO_WritePin(SPI_CAMERA_CS_GPIO_Port, SPI_CAMERA_CS_Pin, GPIO_PIN_SET);
  __HAL_SPI_DISABLE(&hspi1);
}

void spiCsOutputMode(int pin)
{
  ;
}
