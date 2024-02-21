/**
 ******************************************************************************
 * @file   stm32ipl_image_io_jpg_sw.h
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - JPEG SW codec header file
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#ifndef __STM32IPL_IMAGE_IO_JPG_SW_H_
#define __STM32IPL_IMAGE_IO_JPG_SW_H_

///@cond

#include "stm32ipl.h"

#ifdef STM32IPL_ENABLE_IMAGE_IO
#ifdef STM32IPL_ENABLE_JPEG
#ifndef STM32IPL_ENABLE_HW_JPEG_CODEC

#include "ff.h"

#ifdef __cplusplus
extern "C" {
#endif

stm32ipl_err_t readJPEGSW(image_t *img, FIL *fp);
stm32ipl_err_t saveJPEGSW(const image_t *img, const char *filename);

#ifdef __cplusplus
}
#endif

#endif /* STM32IPL_ENABLE_HW_JPEG_CODEC */
#endif /* STM32IPL_ENABLE_JPEG */
#endif /* STM32IPL_ENABLE_IMAGE_IO */

///@endcond

#endif /* __STM32IPL_IMAGE_IO_JPG_SW_H_ */
