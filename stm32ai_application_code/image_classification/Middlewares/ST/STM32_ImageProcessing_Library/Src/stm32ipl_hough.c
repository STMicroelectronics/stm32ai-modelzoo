/**
 ******************************************************************************
 * @file   stm32ipl_hough.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - Hough transforms module
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
 * @brief Finds all infinite lines in the image using the Hough transform. Returns a list of lines ().
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param out			List of find_lines_list_lnk_data_t objects representing the lines found.
 * @param roi			Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param xStride 		Number of x pixels to skip when doing the Hough transform. Only increase this if lines you are searching for are large and bulky.
 * @param yStride 		Number of y pixels to skip when doing the Hough transform. Only increase this if lines you are searching for are large and bulky.
 * @param threshold 	Controls what lines are detected from the Hough transform. Only lines with a magnitude greater than or equal to threshold are returned.
 * The right value of threshold for your application is image dependent. Note that the magnitude of a line is the sum of all Sobel filter magnitudes of pixels that make up that line.
 * @param thetaMargin	Controls the merging of detected lines.
 * @param rhoMargin		Controls the merging of detected lines.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 * @note Lines which are thetaMargin degrees apart and rhoMargin apart are merged.
 */
stm32ipl_err_t STM32Ipl_FindLines(const image_t *img, list_t *out, const rectangle_t *roi, uint8_t xStride,
		uint8_t yStride, uint32_t threshold, uint8_t thetaMargin, uint8_t rhoMargin)
{
	rectangle_t realRoi;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(out)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	if ((xStride == 0) || (yStride == 0))
		return stm32ipl_err_InvalidParameter;

	imlib_find_lines(out, (image_t*)img, &realRoi, xStride, yStride, threshold, thetaMargin, rhoMargin);

	return stm32ipl_err_Ok;
}

/**
 * @brief Finds circles in an image using the Hough transform.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param roi			Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param out			List of find_circles_list_lnk_data_t objects representing the circles found.
 * @param xStride 		Number of x pixels to skip when doing the Hough transform. Only increase this if circles you are searching for are large and bulky.
 * @param yStride 		Number of y pixels to skip when doing the Hough transform. Only increase this if circles you are searching for are large and bulky.
 * @param threshold		Only circles with a magnitude greater than or equal to threshold are returned.
 * @param xMargin		Circles which are xMargin, yMargin and rMargin pixels apart are merged.
 * @param yMargin		Circles which are xMargin, yMargin and rMargin pixels apart are merged.
 * @param rMargin		Circles which are xMargin, yMargin and rMargin pixels apart are merged.
 * @param rMin			Controls the minimum circle radius detected. Increase this to speed up the execution.
 * @param rMax			Controls the maximum circle radius detected. Decrease this to speed up the execution.
 * @param rStep			Controls how to step the radius detection by.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_FindCircles(const image_t *img, list_t *out, const rectangle_t *roi, uint32_t xStride,
		uint32_t yStride, uint32_t threshold, uint32_t xMargin, uint32_t yMargin, uint32_t rMargin, uint32_t rMin,
		uint32_t rMax, uint32_t rStep)
{
	rectangle_t realRoi;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(out)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	if (xStride == 0 || yStride == 0)
		return stm32ipl_err_InvalidParameter;

	rMin = STM32IPL_MAX(rMin, 2);
	rMax = STM32IPL_MIN(rMax, STM32IPL_MIN((realRoi.w / 2), (realRoi.h / 2)));

	imlib_find_circles(out, (image_t*)img, &realRoi, xStride, yStride, threshold, xMargin, yMargin, rMargin, rMin, rMax,
			rStep);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
