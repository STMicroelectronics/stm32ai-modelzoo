/**
 ******************************************************************************
 * @file   stm32ipl_rotation.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - rotation module
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
 * @brief Corrects (in-place) perspective issues in an image by doing a 3D rotation.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img			Image; if it is not valid, an error is returned.
 * @param rotationX		Number of rotation degrees around the X axis (i.e. this spins the image up and down).
 * @param rotationY		Number of rotation degrees around the Y axis (i.e. this spins the image left and right).
 * @param rotationZ		Number of rotation degrees around the Z axis (i.e. this spins the image in place).
 * @param translationX	Number of units to move the image to the left or right after rotation.
 * 						Because this translation is applied in 3D space the units are not pixels.
 * @param translationY	Number of units to move the image to the up or down after rotation.
 * 						Because this translation is applied in 3D space the units are not pixels.
 * @param zoom			Zoom ratio (1.0f by default).
 * @param fov			FOV must be > 0 and < 180. Used internally when doing 2D->3D projection before rotating the image in 3D space.
 * 						As this value approaches 0, the image is placed at infinity away from the viewport. As this value approaches 180,
 * 						the image is placed within the viewport. Used to change the 2D->3D mapping effect.
 * 						Typical value is 60.
 * @param corners		Pointer to an array of 8 float values, corresponding to four (x,y) tuples representing four corners used to
 * 						create a 4-point correspondence homography that will map the first corner to (0, 0), the second corner to
 * 						(image_width-1, 0), the third corner to (image_width-1, image_height-1), and the fourth corner to (0, image_height-1).
 * 						The 3D rotation is then applied after the image is re-mapped. *
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Rotation(image_t *img, float rotationX, float rotationY, float rotationZ, float translationX,
		float translationY, float zoom, float fov, const float *corners)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if ((fov <= 0) || (fov >= 180) || (zoom <= 0))
		return stm32ipl_err_InvalidParameter;

	imlib_rotation_corr(img, rotationX, rotationY, rotationZ, translationX, translationY, zoom, fov, (float*)corners);

	return stm32ipl_err_Ok;
}

/**
 * @brief Transforms the source image into the destination image by using the given transformation parameters.
 * The two images must have same format and size. The destination image must be valid and its data memory
 * already allocated by the caller. The supported formats (for source, destination and mask images) are
 * Binary, Grayscale, RGB565, RGB888.
 * @param src		Source image; if it is not valid, an error is returned.
 * @param dst		Destination image; if it is not valid, an error is returned.
 * @param mirror	True to horizontally mirror the replacing image.
 * @param flip		True to vertically flip the replacing image
 * @param transpose	True to flip the image along the diagonal (this changes the image image width/height if the image is non-square).
 * @param mask 	Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Replace(const image_t *src, image_t *dst, bool mirror, bool flip, bool transpose,
		const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_FORMAT(src, dst)
	STM32IPL_CHECK_SAME_SIZE(src, dst)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(src, mask)
	}

	imlib_replace((image_t*)src, NULL, dst, 0, mirror, flip, transpose, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Vertically flips the source image into the destination image.
 * The two images must have same format and resolution.
 * The destination image must be valid and its data memory already allocated by the caller.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst	Destination image; if it is not valid, an error is returned.
 * @return stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Flip(const image_t *src, image_t *dst)
{
	return STM32Ipl_Replace((image_t*)src, dst, false, true, false, NULL);
}

/**
 * @brief Horizontally mirrors the source image into the destination image.
 * The two images must have same format and resolution.
 * The destination image must be valid and its data memory already allocated by the caller.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst	Destination image; if it is not valid, an error is returned.
 * @return stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Mirror(const image_t *src, image_t *dst)
{
	return STM32Ipl_Replace((image_t*)src, dst, true, false, false, NULL);
}

/**
 * @brief Flips and mirrors the source image into the destination image (same as a 180 degrees rotation).
 * The two images must have same format and resolution.
 * The destination image must be valid and its data memory already allocated by the caller.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst	Destination image; if it is not valid, an error is returned.
 * @return stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_FlipMirror(const image_t *src, image_t *dst)
{
	return STM32Ipl_Replace((image_t*)src, dst, true, true, false, NULL);
}

/**
 * @brief Rotates (clockwise) the source image by 90 degrees into the destination image.
 * The two images must have same format and resolution.
 * The destination image must be valid and its data memory already allocated by the caller.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst	Destination image; if it is not valid, an error is returned.
 * @return stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Rotation90(const image_t *src, image_t *dst)
{
	return STM32Ipl_Replace((image_t*)src, dst, false, true, true, NULL);
}

/**
 * @brief Rotates (clockwise) the source image by 180 degrees into the destination image.
 * The two images must have same format and resolution.
 * The destination image must be valid and its data memory already allocated by the caller.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst	Destination image; if it is not valid, an error is returned.
 * @return stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Rotation180(const image_t *src, image_t *dst)
{
	return STM32Ipl_Replace((image_t*)src, dst, true, true, false, NULL);
}

/**
 * @brief Rotates (clockwise) the source image by 270 degrees into the destination image.
 * The two images must have same format and resolution.
 * The destination image must be valid and its data memory already allocated by the caller.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst	Destination image; if it is not valid, an error is returned.
 * @return stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Rotation270(const image_t *src, image_t *dst)
{
	return STM32Ipl_Replace((image_t*)src, dst, true, false, true, NULL);
}

/**
 * @brief Performs lens correction to un-fisheye the image due to the lens distortion.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param strength	Defines how much to un-fisheye the image. Try 1.8f and then increase or decrease from there until the image looks good.
 * @param zoom		Amount to zoom in on the image by. The value must be > 0.
 * @param xCorr		Pixel offset from center; it can be negative or positive.
 * @param yCorr		Pixel offset from center; it can be negative or positive.
 * @return 			stm32ipl_err_Ok on success, error otherwise.
 * @note 			Image's width and height must be even numbers.
 */
stm32ipl_err_t STM32Ipl_LensCorr(image_t *img, float strength, float zoom, float xCorr, float yCorr)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if ((strength <= 0) || (zoom <= 0) || ((img->w % 2) != 0) || ((img->h % 2) != 0))
		return stm32ipl_err_InvalidParameter;

	imlib_lens_corr(img, strength, zoom, xCorr, yCorr);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
