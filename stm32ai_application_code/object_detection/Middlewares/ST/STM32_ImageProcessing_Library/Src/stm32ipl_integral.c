/**
 ******************************************************************************
 * @file   stm32ipl_integral.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - integral image module
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
 * @brief Allocates a data memory buffer to contain the integral image data and consequently
 * initializes the given integral image structure. The size of such buffer depends on given
 * width, height. Assuming the input integral image data pointer is null to avoid
 * memory leakage. The caller is responsible of releasing the data memory buffer with STM32Ipl_IIReleaseData().
 * @param iimg		Integral image; if it is not valid, an error is returned.
 * @param width		Integral image width.
 * @param height	Integral image height.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_IIAllocData(i_image_t *iimg, uint32_t width, uint32_t height)
{
	uint32_t *data;

	STM32IPL_CHECK_VALID_IMAGE(iimg)

	data = xalloc(width * height * sizeof(uint32_t));
	if (!data) {
		iimg->w = 0;
		iimg->h = 0;
		iimg->data = 0;
		return stm32ipl_err_OutOfMemory;
	}

	iimg->w    = width;
	iimg->h    = height;
	iimg->data = data;

	return stm32ipl_err_Ok;
}

/**
 * @brief Releases the data memory buffer of the integral image and resets the integral image structure.
 * @param iimg		Integral image; if it is not valid, an error is returned.
 * @return			void.
 */
void STM32Ipl_IIReleaseData(i_image_t *iimg)
{
	if (iimg)
		xfree(iimg->data);
}

/**
 * @brief Calculates the integral image of an image and stores the results into the destination data buffer.
 * The destination image data buffer must be already allocated by the user.
 * Source and destination images must have same size.
 * The supported format is Grayscale.
 * @param src		Source image; if it is not valid, an error is returned.
 * @param dst		Destination integral image; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_II(const image_t *src, i_image_t *dst)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_SAME_SIZE(src, dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_GRAY_ONLY)

	imlib_integral_image((image_t*)src, dst);

	return stm32ipl_err_Ok;
}

/**
 * @brief Calculates the scaled integral image of an image and stores the results into the destination data buffer.
 * The destination image data buffer must be already allocated by the user. The size of the destination image must
 * be equal or smaller than the size of the source image.
 * The supported format is Grayscale.
 * @param src		Source image; if it is not valid, an error is returned.
 * @param dst		Destination integral image; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_IIScaled(const image_t *src, i_image_t *dst)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_GRAY_ONLY)

	if ((src->w < dst->w) || (src->h < dst->h))
		return stm32ipl_err_InvalidParameter;

	imlib_integral_image_scaled((image_t*)src, dst);

	return stm32ipl_err_Ok;
}

/**
 * @brief Calculates the squared integral image of an image and stores the results
 * into the destination data buffer.
 * Source and destination images must have same size.
 * The supported format is Grayscale.
 * @param src		Source image; if it is not valid, an error is returned.
 * @param dst		Destination integral image; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_IISq(const image_t *src, i_image_t *dst)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_SAME_SIZE(src, dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_GRAY_ONLY)

	imlib_integral_image_sq((image_t*)src, dst);

	return stm32ipl_err_Ok;
}

/**
 * @brief Calculates the sum of the pixels value of a particular ROI of an integral.
 * The supported format is Grayscale.
 * @param iimg		Integral image; if it is not valid, an error is returned.
 * @param x			X-coordinate of the ROI.
 * @param y			Y-coordinate of the ROI.
 * @param width		Width of the ROI.
 * @param height	Height of the ROI.
 * @return			Sum of the pixels value within the ROI.
 */
uint32_t STM32Ipl_IILookup(const i_image_t *iimg, uint32_t x, uint32_t y, uint32_t width, uint32_t height)
{
	rectangle_t roi;
	rectangle_t fullRoi;

	if (!iimg || !iimg->data)
		return 0;

	STM32Ipl_RectInit(&roi, x, y, width, height);
	STM32Ipl_RectInit(&fullRoi, 0, 0, iimg->w, iimg->h);

	if (!STM32Ipl_RectContain(&fullRoi, &roi))
		return 0;

	return imlib_integral_lookup((i_image_t*)iimg, x, y, width, height);
}

#ifdef __cplusplus
}
#endif
