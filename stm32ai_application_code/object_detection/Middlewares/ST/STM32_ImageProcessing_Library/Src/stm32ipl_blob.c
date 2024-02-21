/**
 ******************************************************************************
 * @file   stm32ipl_blob.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - blob detection module
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
 * @brief Finds all blobs (connected pixel regions that pass a color threshold test) in an image
 * and returns a list of find_blobs_list_lnk_data_t objects which describe each blob found.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img				Image; if it is not valid, an error is returned.
 * @param out				List of find_blobs_list_lnk_data_t objects representing the blobs found.
 * @param roi				Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param thresholds		List of color_thresholds_list_lnk_data_t objects. It is possible to pass up to
 * 32 threshold objects in one call.
 * @param xStride			Number of x pixels to skip when searching for a blob. Once a blob is found,
 * the line fill algorithm will be pixel accurate. Increase xStride to speed up finding blobs if blobs
 * are known to be large.
 * @param yStride			Number of y pixels to skip when searching for a blob. Once a blob is found,
 * the line fill algorithm will be pixel accurate. Increase yStride to speed up finding blobs if blobs
 * are known to be large.
 * @param areaThreshold		Filter out the blobs with bounding box area lesser than areaThreshold.
 * @param pixelsThreshold	Filter out the blobs with the pixel are lesser than pixelsThreshold.
 * @param merge				When true, all not filtered out blobs with bounding rectangles intersecting each other are merged.
 * @param margin			Value used to increase or decrease the size of the bounding rectangles for blobs during the intersection test.
 * For example, with a margin of one, blobs with bounding rectangles that are one pixel away from each other will be merged.
 * @param invert			Inverts the thresholding operation such that, instead of matching pixels inside of some known color bounds pixels,
 * are matched those that are outside of the known color bounds.
 * @param maxBlobs			Maximum number of blob objects that can be found; it must be a positive number (minimum value is 1).
 * This value determines the amount of memory allocated to store the list of returned blobs, so it must be chosen with care. In case
 *  as is too high in respect to the available memory, it is possible that this function fails due to the
 * @return					stm32ipl_err_Ok on success.
 */
stm32ipl_err_t STM32Ipl_FindBlobs(const image_t *img, list_t *out, const rectangle_t *roi, const list_t *thresholds,
		uint8_t xStride, uint8_t yStride, uint16_t areaThreshold, uint16_t pixelsThreshold, bool merge, uint8_t margin,
		bool invert, uint32_t maxBlobs)
{
	rectangle_t realRoi;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	if (!thresholds || !out || (list_size((list_t*)thresholds) == 0))
		return stm32ipl_err_InvalidParameter;

	if (xStride == 0 || yStride == 0)
		return stm32ipl_err_InvalidParameter;

	imlib_find_blobs(out, (image_t*)img, &realRoi, xStride, yStride, (list_t*)thresholds, invert, areaThreshold,
			pixelsThreshold, merge, margin,
			NULL, NULL, NULL, NULL, 0, 0, maxBlobs);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
