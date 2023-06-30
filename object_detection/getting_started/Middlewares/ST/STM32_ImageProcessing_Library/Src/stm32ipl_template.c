/**
 ******************************************************************************
 * @file   stm32ipl_template.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - template matching module
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
 * @brief Finds the rectangular region in an image that best correlates with a template images, using
 * the Normalized Cross Correlation.
 * The supported format is Grayscale.
 * @param img			Image; if it is not valid, an error is returned.
 * @param template		Template image to be found within img; if it is not valid, an error is returned.
 * @param roi			Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param threshold		Floating point number in the range [0, 1]; a higher value prevents false
 * positives while lowering the detection rate; a lower value does the opposite.
 * @param step			Number of pixels to skip past while looking for the template. Skipping pixels
 * considerably speeds the execution up. This only affects the algorithm in SEARCH_EX mode.
 * @param searchType	The type of search; it can be either SEARCH_DS or SEARCH_EX: SEARCH_DS searches
 * for the template using a faster algorithm than SEARCH_EX, but it may not find the template if it is
 * near the edges of the image; SEARCH_EX does an exhaustive search for the image, but it can be much
 * slower than SEARCH_DS.
 * @param templateRect	Returns the region corresponding to the template found. If no template has found,
 * its values are set to zero.
 * @param correlation	Returns the correlation value between the input template and the template found.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_FindTemplate(const image_t *img, const image_t *template, const rectangle_t *roi,
		float threshold, uint32_t step, template_match_t searchType, rectangle_t *templateRect, float *correlation)
{
	rectangle_t realRoi;
	float corr;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_GRAY_ONLY)
	STM32IPL_CHECK_VALID_IMAGE(template)
	STM32IPL_CHECK_FORMAT(template, STM32IPL_IF_GRAY_ONLY)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)
	STM32IPL_CHECK_VALID_PTR_ARG(templateRect)
	STM32IPL_CHECK_VALID_PTR_ARG(correlation)

	/* Make sure that ROI is bigger than or equal to the template size. */
	if ((realRoi.w < template->w || realRoi.h < template->h))
		return stm32ipl_err_InvalidParameter;

	if (searchType == SEARCH_DS)
		corr = imlib_template_match_ds((image_t*)img, (image_t*)template, templateRect);
	else
		corr = imlib_template_match_ex((image_t*)img, (image_t*)template, &realRoi, step, templateRect);

	if (corr < threshold) {
		templateRect->x = 0;
		templateRect->y = 0;
		templateRect->w = 0;
		templateRect->h = 0;
	}

	*correlation = corr;

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
