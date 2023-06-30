/**
 ******************************************************************************
 * @file   stm32ipl_equalization.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - equalization module
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

#include "stm32ipl.h"
#include "stm32ipl_imlib_int.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Quickly changes the image gamma, contrast, and brightness
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param gamma			With values greater than 1.0, it makes the image darker in a non-linear manner,
 * while with values less than 1.0 it makes the image brighter. The gamma value is applied to the image by scaling
 * all pixel color channels to be between [0:1) and then doing a remapping of pow(pixel, 1/gamma) on all
 * pixels before scaling back.
 * @param contrast		With values greater than 1.0, it makes the image brighter in a linear manner,
 * while with values less than 1.0 it makes the image darker. The contrast value is applied to the image by scaling
 * all pixel color channels to be between [0:1) and then doing a remapping of pixel contrast on all
 * pixels before scaling back.
 * @param brightness	With values greater than 0.0, it makes the image brighter in a constant manner,
 * while with values less than 0.0, it makes the image darker. The brightness value is applied to the image by scaling
 * all pixel color channels to be between [0:1) and then doing a remapping of pixel + brightness on all
 * pixels before scaling back
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GammaCorr(image_t *img, float gamma, float contrast, float brightness)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	imlib_gamma_corr(img, gamma, contrast, brightness);

	return stm32ipl_err_Ok;
}

/**
 * @brief Performs (in-place) a histogram equalization of an image (normalizes contrast and brightness of the image).
 * The supported formats (for image and mask) are Binary, Grayscale, RGB565, RGB888.
 * @param img	Image; if it is not valid, an error is returned.
 * @param mask 	Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return 		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_HistEq(image_t *img, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_histeq(img, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Performs (in-place) a contrast limited adaptive histogram equalization of an image
 * (it normalizes the contrast and brightness of the image).
 * The supported formats (for image and mask) are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param clipLimit 	Provides a way to limit the contrast of the adaptive histogram equalization.
 * Use a small value, i.e. 10, to produce good equalized images
 * @param mask 			Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return				stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_HistEqClahe(image_t *img, float clipLimit, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_clahe_histeq(img, clipLimit, (image_t*)mask);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
