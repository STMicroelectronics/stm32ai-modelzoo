/**
 ******************************************************************************
 * @file   stm32ipl_masking.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - masking module
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
 * @brief Masks an image with zeros, except a rectangular region.
 * The supported formats are (Binary, Grayscale, RGB565, RGB888).
 * @param img 		Image; if it is not valid, an error is returned.
 * @param x 		X-coordinate of the top-left corner of the rectangle.
 * @param y 		Y-coordinate of the top-left corner of the rectangle.
 * @param width		Width of the rectangle
 * @param height	Height of the rectangle
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_ImageMaskRectangle(image_t *img, uint16_t x, uint16_t y, uint16_t width, uint16_t height)
{
	image_t mask;
	stm32ipl_err_t res;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	res = STM32Ipl_AllocData(&mask, img->w, img->h, IMAGE_BPP_BINARY);
	if (res != stm32ipl_err_Ok)
		return res;

	STM32Ipl_Fill(&mask, 0, STM32IPL_COLOR_BLACK);

	imlib_draw_rectangle(&mask, x, y, width, height, -1, 0, true);
	imlib_zero(img, &mask, true);

	STM32Ipl_ReleaseData(&mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Masks an image with zeros, except a circular region.
 * The supported formats are (Binary, Grayscale, RGB565, RGB888).
 * @param img 		Image; if it is not valid, an error is returned.
 * @param cx 		X-coordinate of the center of the circle.
 * @param cy 		Y-coordinate of the center of the circle.
 * @param radius	Radius of the circle.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_ImageMaskCircle(image_t *img, uint16_t cx, uint16_t cy, uint16_t radius)
{
	image_t mask;
	stm32ipl_err_t res;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	res = STM32Ipl_AllocData(&mask, img->w, img->h, IMAGE_BPP_BINARY);
	if (res != stm32ipl_err_Ok)
		return res;

	STM32Ipl_Fill(&mask, 0, STM32IPL_COLOR_BLACK);

	imlib_draw_circle(&mask, cx, cy, radius, -1, 0, true);
	imlib_zero(img, &mask, true);

	STM32Ipl_ReleaseData(&mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Masks an image with zeros, except an elliptical region.
 * The supported formats are (Binary, Grayscale, RGB565, RGB888).
 * @param img 		Image; if it is not valid, an error is returned.
 * @param ellipse 	Ellipse defining the mask; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_ImageMaskEllipse(image_t *img, const ellipse_t *ellipse)
{
	image_t mask;
	stm32ipl_err_t res;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(ellipse)

	if (ellipse->rotation > 360)
		return stm32ipl_err_InvalidParameter;

	res = STM32Ipl_AllocData(&mask, img->w, img->h, IMAGE_BPP_BINARY);
	if (res != stm32ipl_err_Ok)
		return res;

	STM32Ipl_Fill(&mask, 0, STM32IPL_COLOR_BLACK);

	imlib_draw_ellipse(&mask, ellipse->center.x, ellipse->center.y, ellipse->radiusX, ellipse->radiusY,
			ellipse->rotation, -1, 0, true);

	imlib_zero(img, &mask, true);

	STM32Ipl_ReleaseData(&mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Gets if a pixel/point into an image is masked or not.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img 	Image; if it is not valid, an error is returned.
 * @param x 	X-coordinate of the point.
 * @param y 	Y-coordinate of the point.
 * @return 		true if the pixel is masked. See note for more details.
 * @note For Binary, true if value is 1; false if value is 0.
 * For Grayscale, true if the value is > (COLOR_GRAYSCALE_MAX - COLOR_GRAYSCALE_MIN) / 2) + COLOR_GRAYSCALE_MIN.
 * For RGB565/RGB888, true if the Y value is > (COLOR_Y_MAX - COLOR_Y_MIN) / 2) + COLOR_Y_MIN).
 */
bool STM32Ipl_GetMaskPixel(const image_t *img, uint16_t x, uint16_t y)
{
	if (!img || !img->data)
		return false;

	return image_get_mask_pixel((image_t*)img, x, y);
}

#ifdef __cplusplus
}
#endif
