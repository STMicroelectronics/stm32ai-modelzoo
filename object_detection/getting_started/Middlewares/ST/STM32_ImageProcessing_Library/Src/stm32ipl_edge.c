/**
 ******************************************************************************
 * @file   stm32ipl_edge.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - edge detection module
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
 * @brief Simple edge detector. The supported format is Grayscale.
 * @param img		Image; if it is not valid, an error is returned.
 * @param roi		Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param minTh 	Minimum threshold for hysteresis (values in the range [0, 255]).
 * @param maxTh 	Maximum threshold for hysteresis (values in the range [0, 255]).
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_EdgeSimple(image_t *img, const rectangle_t *roi, int32_t minTh, int32_t maxTh)
{
	rectangle_t realRoi;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_GRAY_ONLY)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	imlib_edge_simple(img, &realRoi, minTh, maxTh);

	return stm32ipl_err_Ok;
}

/**
 * @brief Canny edge detector. The supported format is Grayscale.
 * @param img		Image; if it is not valid, an error is returned.
 * @param roi		Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param minTh 	Minimum threshold for hysteresis (values in the range [0, 255]).
 * @param maxTh 	Maximum threshold for hysteresis (values in the range [0, 255]).
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_EdgeCanny(image_t *img, const rectangle_t *roi, int32_t minTh, int32_t maxTh)
{
	rectangle_t realRoi;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_GRAY_ONLY)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	imlib_edge_canny(img, &realRoi, minTh, maxTh);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
