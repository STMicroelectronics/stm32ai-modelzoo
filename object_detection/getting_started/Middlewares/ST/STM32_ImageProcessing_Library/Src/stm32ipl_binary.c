/**
 ******************************************************************************
 * @file   stm32ipl_binary.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - binarization module
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
 * @brief Binarizes the source image by comparing the source pixels with the given thresholds and stores the
 * resulting black/white pixels to the destination image. Source and destination images must have same resolution.
 * The destination image must be valid and its data memory already allocated by the caller. The format of the
 * destination image must be binary, otherwise it must have the same format of the source image.
 * The supported formats (for source, destination and mask images) are Binary, Grayscale, RGB565, RGB888.
 * @param src			Source image; if it is not valid, an error is returned.
 * @param dst			Destination image; if it is not valid, an error is returned.
 * @param thresholds		List of color_thresholds_list_lnk_data_t objects.
 * @param invert			Inverts the thresholding operation such that, instead of matching pixels inside of the
 * given color bounds, pixels are matched outside of the given color bounds.
 * @param zero			When true, the destination image thresholded pixels are set to 0 and pixels not in the
 * threshold list are left untouched.
 * @param mask 			Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Binary(const image_t *src, image_t *dst, const list_t *thresholds, bool invert, bool zero,
		const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_SIZE(src, dst)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(src, mask)
	}

	imlib_binary(dst, (image_t*)src, (list_t*)thresholds, invert, zero, (image_t*)mask);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
