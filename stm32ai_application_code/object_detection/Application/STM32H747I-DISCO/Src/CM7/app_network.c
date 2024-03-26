/**
 ******************************************************************************
 * @file    app_network.c
 * @author  MCD Application Team
 * @brief   FP VISION AI configuration
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
#include "app_network.h"
#include "app_utility.h"
#include "layers.h"
#include <stdio.h>
#include <string.h>
#include "app_postprocess.h"

/* Private typedef -----------------------------------------------------------*/
/* Private defines -----------------------------------------------------------*/
/* Private macros ------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Global variables ----------------------------------------------------------*/

/* Private function prototypes -----------------------------------------------*/
static void ImageResize(image_t *, image_t *);
static void PixelFormatConversion(AppConfig_TypeDef *, image_t *, image_t *);
static void Pixel_RB_Swap(void *, void *, uint32_t );
static void PixelValueConversion(AppConfig_TypeDef *, void *);
static void Output_Dequantize(AppConfig_TypeDef* );


/* Functions Definition ------------------------------------------------------*/
/**
 * @brief Run preprocessing stages on captured frame
 * @param App_Config_Ptr pointer to application context
 */
/**
 * @brief Run preprocessing stages on captured frame
 * @param App_Config_Ptr pointer to application context
 */
void Network_Preprocess(AppConfig_TypeDef *App_Config_Ptr)
{ 
  image_t src_img;
  image_t dst_img;
  
  App_Config_Ptr->Tfps_start =Utility_GetTimeStamp();

  src_img.data=App_Config_Ptr->camera_capture_buffer;
#if ASPECT_RATIO_MODE == ASPECT_RATIO_PADDING
  src_img.w=CAM_RES_WITH_BORDERS;
  src_img.h=CAM_RES_WITH_BORDERS;
#else
  src_img.w=CAM_RES_WIDTH;
  src_img.h=CAM_RES_HEIGHT;
#endif
  src_img.bpp=IMAGE_BPP_RGB565;
  dst_img.data=App_Config_Ptr->rescaled_image_buffer;
  dst_img.w=AI_NETWORK_WIDTH;
  dst_img.h=AI_NETWORK_HEIGHT;
  dst_img.bpp=IMAGE_BPP_RGB565;
  
  /**********************/
  /****Image resizing****/
  /**********************/
  ImageResize(&src_img, &dst_img);
  
  if(App_Config_Ptr->PixelFormatConv == HW_PFC)
    /******************************************************************************************/
    /****Coherency purpose: clean the source buffer area in L1 D-Cache before DMA2D reading****/
    /******************************************************************************************/
    Utility_DCache_Coherency_Maintenance((void *)(App_Config_Ptr->rescaled_image_buffer), RESCALED_FRAME_BUFFER_SIZE, CLEAN);
  

  src_img.data=App_Config_Ptr->rescaled_image_buffer;
  src_img.w=AI_NETWORK_WIDTH;
  src_img.h=AI_NETWORK_HEIGHT;
  src_img.bpp=IMAGE_BPP_RGB565;
  dst_img.data=App_Config_Ptr->nn_input_buffer;
  dst_img.w=AI_NETWORK_WIDTH;
  dst_img.h=AI_NETWORK_HEIGHT;

#if PP_COLOR_MODE == RGB_FORMAT
  dst_img.bpp = IMAGE_BPP_RGB888;
#elif PP_COLOR_MODE == BGR_FORMAT
  dst_img.bpp = IMAGE_BPP_RGB888;
#elif PP_COLOR_MODE == GRAYSCALE_FORMAT
  dst_img.bpp = IMAGE_BPP_GRAYSCALE;
#else
 #error Color format no supported
#endif
  
  /*************************************/
  /****Image Pixel Format Conversion****/
  /*************************************/
  PixelFormatConversion(App_Config_Ptr, &src_img, &dst_img);
  
  if(App_Config_Ptr->PixelFormatConv == HW_PFC)
  {
    /**************************************************************************************/
    /****Coherency purpose: invalidate the source area in L1 D-Cache before CPU reading****/
    /**************************************************************************************/
    Utility_DCache_Coherency_Maintenance((void *)(App_Config_Ptr->activation_buffer[AI_NETWORK_INPUTS_IN_ACTIVATIONS_INDEX]),
										AI_NETWORK_INPUTS_IN_ACTIVATIONS_SIZE + 32 - (AI_NETWORK_INPUTS_IN_ACTIVATIONS_SIZE%32),
									   INVALIDATE);
  }
  
  /***********************************************************/
  /*********Pixel value convertion and normalisation**********/
  /***********************************************************/
  PixelValueConversion(App_Config_Ptr, (void*)(App_Config_Ptr->nn_input_buffer));
}


/**
 * @brief Run neural network inference on preprocessed captured frame
 * @param App_Config_Ptr pointer to application context
 */
void Network_Inference(AppConfig_TypeDef *App_Config_Ptr)
{
  App_Config_Ptr->Tinf_start =Utility_GetTimeStamp();
  
  /***********************************/
  /*********Run NN inference**********/
  /***********************************/
  ai_run((void*)App_Config_Ptr->nn_input_buffer, (void**)App_Config_Ptr->nn_output_buffer);
  
  App_Config_Ptr->Tinf_stop =Utility_GetTimeStamp();
}

/**
 * @brief Run post-processing operation
 * @param App_Config_Ptr pointer to application context
 */
void Network_Postprocess(AppConfig_TypeDef *App_Config_Ptr)
{
  /*** At that point, it is recommended to wait until current camera acquisition is completed  
  *** before proceeding in order to avoid bottleneck at FMC slave (btw LTDC/DMA2D and DMA).
  ***/
  while(App_Config_Ptr->new_frame_ready == 0);
  
  /**NN ouput dequantization if required**/
  Output_Dequantize(App_Config_Ptr);

  //*******************************  Process   ********************************
  //post processing the output of the inference
  if (App_Config_Ptr->error == AI_OBJDETECT_POSTPROCESS_ERROR_NO)
  {
    App_Config_Ptr->error = app_postprocess_run( App_Config_Ptr->nn_output_buffer,
                                                (void*)&App_Config_Ptr->output,
                                                (void*)&App_Config_Ptr->input_static_param);
  }
  else
  {
    while(1);
  }

  if (App_Config_Ptr->error != AI_OBJDETECT_POSTPROCESS_ERROR_NO)
  {
    while(1);
  }

  App_Config_Ptr->Tfps_stop =Utility_GetTimeStamp();
}

/**
 * @brief De-initializes the generated C model for a neural network
 */
void Network_Deinit(void) 
{ 
  ai_deinit(); 
}

/**
  * @brief  Initializes the generated C model for a neural network
  * @param  App_Config_Ptr pointer to application context
  * @retval None
  */
void Network_Init(AppConfig_TypeDef *App_Config_Ptr)
{
  void *input_data_ptr;
  void *output_data_ptr[AI_NETWORK_OUT_NUM];
  
  ai_init((void*)(App_Config_Ptr->activation_buffer), &input_data_ptr, output_data_ptr);
  
  if(input_data_ptr!= NULL)
    App_Config_Ptr->nn_input_buffer=input_data_ptr;
  else
    while(1);
  
  for (uint8_t i = 0; i < AI_NETWORK_OUT_NUM; i++)
  {
    if(output_data_ptr[i]!= NULL)
    {
      App_Config_Ptr->nn_output_buffer[i] = output_data_ptr[i];
    }
    else
    {
      while (1);     
    }
  } 
}

/**
* @brief  Performs the dequantization of a quantized NN output
* @param  App_Config_Ptr pointer to application context
* @retval None
*/
static void Output_Dequantize(AppConfig_TypeDef *App_Config_Ptr)
{
  /**Check format of the output and convert to float if required**/
  if(ai_get_output_format() == AI_BUFFER_FMT_TYPE_Q)
  {
    float scale;
    int32_t zero_point;
    ai_i8 *nn_output_i8;
    ai_u8 *nn_output_u8;
    float *nn_output_f32;
    
    /*Check what type of quantization scheme is used for the output*/
    switch(ai_get_output_quantization_scheme())
    {
    case AI_FXP_Q:
      
      scale=ai_get_output_fxp_scale();
      
      /* Dequantize NN output - in-place 8-bit to float conversion */
      nn_output_i8 = (ai_i8 *) App_Config_Ptr->nn_output_buffer[0];
      nn_output_f32 = (float *) App_Config_Ptr->nn_output_buffer[0];
      for(int32_t i = AI_NET_OUTPUT_SIZE - 1; i >= 0; i--)
      {
        float q_value = (float) *(nn_output_i8 + i);
        *(nn_output_f32 + i) = scale * q_value;
      }
      break;
      
    case AI_UINT_Q:
      
      scale = ai_get_output_scale();
      zero_point = ai_get_output_zero_point();
      
      /* Dequantize NN output - in-place 8-bit to float conversion */
      nn_output_u8 = (ai_u8 *) App_Config_Ptr->nn_output_buffer[0];
      nn_output_f32 = (float *) App_Config_Ptr->nn_output_buffer[0];
      for(int32_t i = AI_NET_OUTPUT_SIZE - 1; i >= 0; i--)
      {
        int32_t q_value = (int32_t) *(nn_output_u8 + i);
        *(nn_output_f32 + i) = scale * (q_value - zero_point);
      }
      break;
      
    case AI_SINT_Q:
      
      scale = ai_get_output_scale();
      zero_point = ai_get_output_zero_point();
      
      /* Dequantize NN output - in-place 8-bit to float conversion */
      nn_output_i8 = (ai_i8 *) App_Config_Ptr->nn_output_buffer[0];
      nn_output_f32 = (float *) App_Config_Ptr->nn_output_buffer[0];
      for(int32_t i = AI_NET_OUTPUT_SIZE - 1; i >= 0; i--)
      {
        int32_t q_value = (int32_t) *(nn_output_i8 + i);
        *(nn_output_f32 + i) = scale * (q_value - zero_point);
      }
      break;
      
    default:
      break;
    }  
  }
}

/**
 * @brief Performs image (or selected Region Of Interest) resizing
 * @param src Pointer to source image
 * @param dst Pointer to destination image
 */
static void ImageResize(image_t *src, image_t *dst)
{
  if (STM32Ipl_Downscale(src, dst, 0) != stm32ipl_err_Ok)
  {
    while (1);
  }
}

/**
 * @brief Performs a pixel format conversion either by HW or SW
 * @param App_Config_Ptr Pointer to application context
 * @param src Pointer to source image
 * @param dst Pointer to destination image
 */
static void PixelFormatConversion(AppConfig_TypeDef *App_Config_Ptr, image_t *src, image_t *dst)
{
  image_t *src_img = src;
  image_t *dst_img = dst;
  uint32_t rb_swap = App_Config_Ptr->red_blue_swap;
  
  switch (App_Config_Ptr->PixelFormatConv)
  {
  case HW_PFC: /* Use DMA2D to perform pixel format convertion from RGB565 to RGB888 */
    
    if((src_img->bpp == IMAGE_BPP_RGB565) && (dst_img->bpp == IMAGE_BPP_RGB888))
    {
      /* DMA2D transfer with PFC */
      Utility_Dma2d_Memcpy((uint32_t *)(src_img->data),
                         (uint32_t *)(dst_img->data),
                         0,
                         0,
                         src_img->w,
                         src_img->h,
                         dst_img->w,
                         DMA2D_INPUT_RGB565,
                         DMA2D_OUTPUT_RGB888,
                         1,
                         rb_swap);
    }
    else if((src_img->bpp == IMAGE_BPP_RGB888) && (dst_img->bpp == IMAGE_BPP_BGR888))
    {
      /* DMA2D transfer with PFC */
      Utility_Dma2d_Memcpy((uint32_t *)(src_img->data),
                         (uint32_t *)(dst_img->data),
                         0,
                         0,
                         src_img->w,
                         src_img->h,
                         dst_img->w,
                         DMA2D_INPUT_RGB888,
                         DMA2D_OUTPUT_RGB888,
                         1,
                         rb_swap);
    }
    else
    {
      while (1);
    }
    
    break;
    
  case SW_PFC: /* Use SW routine to perform pixel format convertion from RGB565 to grayscale */
   
    if (rb_swap != 0)
    {
      uint32_t nb_pixels = dst_img->w * dst_img->h;
      Pixel_RB_Swap(src_img->data, dst_img->data, nb_pixels);
    }
    
    if (STM32Ipl_ConvertRev(src_img, dst_img, 0) != stm32ipl_err_Ok)
    {
      while (1);
    }
    break;
    
    
  default:
    while(1);
    break;
  }
}

/**
 * @brief  Performs pixel R & B swapping
 * @param  pSrc            Pointer to source buffer
 * @param  pDst            Pointer to destination buffer
 * @param  pixels          Number of pixels
 */
static void Pixel_RB_Swap(void *pSrc, void *pDst, uint32_t pixels)
{
  struct rgb_Src
  {
    uint8_t r, g, b;
  };
  
  struct rgb_Dst
  {
    uint8_t r, g, b;
  };
  
  uint8_t tmp_r;
  
  struct rgb_Src *pivot = (struct rgb_Src *) pSrc;
  struct rgb_Dst *dest = (struct rgb_Dst *) pDst;
  
  for (int i = pixels-1; i >= 0; i--)
  {
    tmp_r=pivot[i].r;
    
    dest[i].r = pivot[i].b;
    dest[i].b = tmp_r;
    dest[i].g = pivot[i].g;
  }
}

/**
* @brief  Performs pixel conversion in format expected by NN input
* @param  App_Config_Ptr Pointer to the application context
* @param  pSrc           Pointer to source buffer
* @retval None
*/
void PixelValueConversion(AppConfig_TypeDef *App_Config_Ptr, void *pSrc)
{
  /**Check data format expected by the model input and perform the right conversion**/
  if(App_Config_Ptr->nn_input_type == UINT8_FORMAT)
  {
	  /*Nothing to do*/
  }
  else if(App_Config_Ptr->nn_input_type == INT8_FORMAT)
  {
	/*Conversion format from uint8 to int8*/
	const uint32_t nb_pixels = AI_NETWORK_WIDTH * AI_NETWORK_HEIGHT * AI_NETWORK_CHANNEL;
	uint8_t *source = (uint8_t *)pSrc;
	uint8_t unsigned_input_value;
	int8_t *destination = (int8_t *) App_Config_Ptr->nn_input_buffer;
	int8_t signed_input_value;


	for (int32_t i = 0; i < nb_pixels; i++)
	{
		unsigned_input_value= (uint8_t)source[i];
		signed_input_value= ((int16_t)unsigned_input_value)-128;
		destination[i]= signed_input_value;
	}
  }
  else
  {
	  while(1);
  }
}
