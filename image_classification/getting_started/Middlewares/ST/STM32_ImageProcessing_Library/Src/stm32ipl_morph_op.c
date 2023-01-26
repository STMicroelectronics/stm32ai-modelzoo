/**
 ******************************************************************************
 * @file   stm32ipl_morph_op.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - morphological operators module
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
 * @brief Adds pixels to the edges of segmented areas.
 * Convolving a kernel pixels across the previously segmented image and setting the center pixel of the kernel
 * if the sum of the neighbour pixels set is greater than threshold.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param kSize			Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param threshold 	Minimum value of the sum of neighbour pixel in the kernel.
 * @param mask		 	Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that have the
 * corresponding mask pixels set are considered. The pointer to the mask can be null: in this case all
 * the source image pixels are considered.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Dilate(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_dilate(img, kSize, threshold, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Removes pixels from the edges of segmented areas.
 * Convolving a kernel pixels across the image and zeroing the center pixel of the kernel
 * if the sum of the neighbour pixels set is not greater than threshold.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param kSize			Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param threshold 	Minimum value of the sum of neighbour pixel in the kernel.
 * @param mask		 	Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that have the
 * corresponding mask pixels set are considered. The pointer to the mask can be null: in this case all
 * the source image pixels are considered.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Erode(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_erode(img, kSize, threshold, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Performs erosion and dilation on an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param kSize	is 		Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param threshold 	Threshold parameter used by dilate and erode.
 * @param mask		 	Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that have the
 * corresponding mask pixels set are considered. The pointer to the mask can be null: in this case all
 * the source image pixels are considered.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Open(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_open(img, kSize, threshold, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Performs dilation and erosion on an image in order.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param kSize			Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param threshold 	Threshold parameter used by dilate and erode.
 * @param mask		 	Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that have the
 * corresponding mask pixels set are considered. The pointer to the mask can be null: in this case all
 * the source image pixels are considered.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Close(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_close(img, kSize, threshold, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Performs the difference of an image and the opened image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param kSize			Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param threshold 	Threshold parameter used by dilate and erode.
 * @param mask		 	Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that have the
 * corresponding mask pixels set are considered. The pointer to the mask can be null: in this case all
 * the source image pixels are considered.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_TopHat(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_top_hat(img, kSize, threshold, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Performs the difference of an image and the closed image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param kSize			Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param threshold 	Threshold parameter used by dilate and erode.
 * @param mask		 	Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that have the
 * corresponding mask pixels set are considered. The pointer to the mask can be null: in this case all
 * the source image pixels are considered.
 * @return	stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_BlackHat(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_black_hat(img, kSize, threshold, (image_t*)mask);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
