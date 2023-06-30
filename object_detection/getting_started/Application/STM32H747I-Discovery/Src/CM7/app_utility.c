/**
 ******************************************************************************
 * @file    app_utility.c
 * @author  MCD Application Team
 * @brief   FP VISION utilities
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
#include "app_utility.h"

/* Private typedef -----------------------------------------------------------*/
/* Private defines -----------------------------------------------------------*/
/* Private macros ------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Global variables ----------------------------------------------------------*/
extern DMA2D_HandleTypeDef hlcd_dma2d;

/* Private function prototypes -----------------------------------------------*/
static uint32_t GetBytesPerPixel(uint32_t );

/* Functions Definition ------------------------------------------------------*/
/**
 * @brief Helper function to get the bytes per pixels according to the DMA2D color mode
 *
 * @param dma2d_color DMA2D color mode
 * @return uint32_t bytes per pixels for the input mode, either 4,3,2 or 0 if unknown input mode
 */
static uint32_t GetBytesPerPixel(uint32_t dma2d_color)
{
  switch (dma2d_color)
  {
    case DMA2D_OUTPUT_ARGB8888:
      return 4;
    case DMA2D_OUTPUT_RGB888:
      return 3;
    case DMA2D_OUTPUT_RGB565:
    case DMA2D_OUTPUT_ARGB1555:
    case DMA2D_OUTPUT_ARGB4444:
      return 2;
    default:
      return 0;
  }
}

/**
* @brief  Get timestamp
* @param  Utils_Context_Ptr  Pointer to Utilities context
* @retval Time stamp
*/
uint32_t Utility_GetTimeStamp(void)
{
  return HAL_GetTick();
}

/**
 * @brief Performs a DMA transfer from an arbitrary address to an arbitrary address
 *
 * @param pSrc address of the source
 * @param pDst address of the destination
 * @param x x position in the destination
 * @param y y position in the destination
 * @param xsize width of the source
 * @param ysize height of the source
 * @param rowStride width of the destination
 * @param input_color_format input color format (e.g DMA2D_INPUT_RGB888)
 * @param output_color_format output color format (e.g DMA2D_OUTPUT_ARGB888)
 * @param pfc boolean flag for pixel format conversion (set to 1 if input and output format are different, else 0)
 * @param red_blue_swap boolean flag for red-blue channel swap, 0 if no swap, else 1
*/
void Utility_Dma2d_Memcpy(uint32_t *pSrc, uint32_t *pDst, uint16_t x, uint16_t y, uint16_t xsize, uint16_t ysize,
                        uint32_t rowStride, uint32_t input_color_format, uint32_t output_color_format, int pfc,
                        int red_blue_swap)
{
  uint32_t bytepp = GetBytesPerPixel(output_color_format);

  uint32_t destination = (uint32_t)pDst + (y * rowStride + x) * bytepp;
  uint32_t source = (uint32_t)pSrc;

  HAL_DMA2D_DeInit(&hlcd_dma2d);

  /*##-1- Configure the DMA2D Mode, Color Mode and output offset #############*/
  hlcd_dma2d.Init.Mode = pfc ? DMA2D_M2M_PFC : DMA2D_M2M;
  hlcd_dma2d.Init.ColorMode = output_color_format;

  /* Output offset in pixels == nb of pixels to be added at end of line to come to the  */
  /* first pixel of the next line : on the output side of the DMA2D computation         */
  hlcd_dma2d.Init.OutputOffset = rowStride - xsize;

  /*##-2- DMA2D Callbacks Configuration ######################################*/
  hlcd_dma2d.XferCpltCallback = NULL;

  /*##-3- Foreground Configuration ###########################################*/
  hlcd_dma2d.LayerCfg[1].AlphaMode = DMA2D_REPLACE_ALPHA;
  hlcd_dma2d.LayerCfg[1].InputAlpha = 0xFF;
  hlcd_dma2d.LayerCfg[1].InputColorMode = input_color_format;
  hlcd_dma2d.LayerCfg[1].InputOffset = 0;
  hlcd_dma2d.LayerCfg[1].RedBlueSwap = red_blue_swap ? DMA2D_RB_SWAP : DMA2D_RB_REGULAR;

  /* DMA2D Initialization */
  if (HAL_DMA2D_Init(&hlcd_dma2d) == HAL_OK)
  {
    if (HAL_DMA2D_ConfigLayer(&hlcd_dma2d, 1) == HAL_OK)
    {
      if (HAL_DMA2D_Start(&hlcd_dma2d, source, destination, xsize, ysize) == HAL_OK)
      {
        /* Polling For DMA transfer */
        HAL_DMA2D_PollForTransfer(&hlcd_dma2d, 30);
      }
    }
  }
}




/**
 * @brief Performs Data Cache maintenance for coherency purpose
 * @param mem_addr Pointer to memory block address (aligned to 32-byte boundary)
 * @param mem_size Size of memory block (in number of bytes)
 * @param Maintenance_operation type of maintenance: CLEAN or INVALIDATE
 * @retval None
 */
void Utility_DCache_Coherency_Maintenance(uint32_t *mem_addr, int32_t mem_size, DCache_Coherency_TypeDef Maintenance_operation)
{
  /*Check alignement on 32-bytes for the memory adress and check that the memory size is multiple of 32-bytes*/
  if(((uint32_t)mem_addr%32 != 0) || (mem_size%32 != 0))
    while(1);
  
  if(Maintenance_operation == INVALIDATE)
  {
    SCB_InvalidateDCache_by_Addr((void*)mem_addr, mem_size);
  }
  else if(Maintenance_operation == CLEAN)
  {
    SCB_CleanDCache_by_Addr((void *)mem_addr, mem_size);
  }
}

/**
 * @brief Bubble sorting algorithm on probabilities
 * @param prob pointer to probabilities buffer
 * @param classes pointer to classes buffer
 * @param size numer of values
 */
void Utility_Bubblesort(float *prob, int *classes, int size)
{
  float p;
  int c;

  for (int i = 0; i < size; i++)
  {
    for (int ii = 0; ii < size - i - 1; ii++)
    {
      if (prob[ii] < prob[ii + 1])
      {
        p = prob[ii];
        prob[ii] = prob[ii + 1];
        prob[ii + 1] = p;
        c = classes[ii];
        classes[ii] = classes[ii + 1];
        classes[ii + 1] = c;
      }
    }
  }
}
