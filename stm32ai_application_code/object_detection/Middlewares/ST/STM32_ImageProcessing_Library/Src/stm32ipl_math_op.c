/**
 ******************************************************************************
 * @file   stm32ipl_math_op.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - mathematical operators module
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

#define CHECK_AND_ADAPT(imgA, imgB, color, mask) \
	uint32_t newColor = 0; \
\
	STM32IPL_CHECK_VALID_IMAGE(imgA) \
	STM32IPL_CHECK_FORMAT(imgA, STM32IPL_IF_ALL) \
\
	if (mask) { \
		STM32IPL_CHECK_VALID_IMAGE(mask) \
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL) \
		STM32IPL_CHECK_SAME_SIZE(imgA, mask) \
	} \
 \
	if (imgB) { \
		STM32IPL_CHECK_VALID_IMAGE(imgB) \
		STM32IPL_CHECK_SAME_HEADER(imgA, imgB) \
	} else { \
		newColor = STM32Ipl_AdaptColor(imgA, color); \
	} \


/**
 * @brief Inverts the image; in-place function, no memory is allocated.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img	Image to be inverted; if it is not valid, an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Invert(image_t *img)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	imlib_invert(img);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise AND of an image with another one (or a color value): imgA = imgA AND imgB, or imgA = imgA AND color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned.
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_And(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_b_and(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise NAND of an image with another one (or a color value): imgA = imgA NAND imgB, or imgA = imgA NAND color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned.
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Nand(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_b_nand(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise OR of an image with another one (or a color value): imgA = imgA OR imgB, or imgA = imgA OR color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Or(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_b_or(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise NOR of an image with another one (or a color value): imgA = imgA NOR imgB, or imgA = imgA NOR color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Nor(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_b_nor(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise XOR of an image with another one (or a color value): imgA = imgA XOR imgB, or imgA = imgA XOR color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Xor(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_b_xor(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise XNOR of an image with another one (or a color value): imgA = imgA XNOR imgB, or imgA = imgA XNOR color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Xnor(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_b_xnor(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise addiction of an image with another one (or a color value): imgA = imgA + imgB, or imgA = imgA + color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Add(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_add(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise subtraction of an image (or a color value) from another one: imgA = imgA - imgB, or imgA = imgA - color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param invert 	When true, the operands are swapped, that is imgA = imgB - imgA, or imgA = color - imgA.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Sub(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, bool invert,
		const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_sub(imgA, NULL, (image_t*)imgB, newColor, invert, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise multiplication of an image (or a color value) with another one: imgA = imgA * imgB, or imgA = imgA * color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param invert	When true, the multiplication operation changes from (a * b) to (1 / ((1 / a) * (1 / b))); this lightens the image
 * instead of darkening it (e.g. multiply versus burn operations).
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Mul(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, bool invert,
		const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_mul(imgA, NULL, (image_t*)imgB, newColor, invert, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise division of an image with another one (or a color value): imgA = imgA / imgB, or imgA = imgA / color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param invert	When true, the operands are swapped, that is imgA = imgB / imgA, or imgA = color / imgA.
 * @param mod		When true, change the division operation to the modulus operation.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Div(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, bool invert, bool mod,
		const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_div(imgA, NULL, (image_t*)imgB, newColor, invert, mod, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Executes a pixel-wise absolute difference between an image and another one (or a color value): imgA = |imgA - imgB|, or imgA = |imgA - color|.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Diff(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_difference(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Calculates the pixel-wise minimum between an image and another one (or a color value): imgA = min(imgA, imgB), or imgA = min(imgA, color).
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Min(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_min(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Calculates the pixel-wise maximum between an image and another one (or a color value): imgA = max(imgA, imgB), or imgA = max(imgA, color).
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param imgA		First image; it is overwritten with the result of the operation. If it is not valid, an error is returned.
 * @param imgB		Second image (optional); when used, it must have same format and size as the first image, otherwise an error is returned..
 * @param color 	This value has 0xRRGGBB format and is used instead of imgB only when imgB is NULL.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_Max(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask)
{
	CHECK_AND_ADAPT(imgA, imgB, color, mask)

	imlib_max(imgA, NULL, (image_t*)imgB, newColor, (image_t*)mask);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
