/**
 ******************************************************************************
 * @file   stm32ipl_filtering.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - filtering module
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
 * @brief Applies a standard mean blurring filter using a box filter to an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param kSize		Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param threshold True enables adaptive thresholding of the image, which sets pixels to one or zero
 * based on a pixel’s brightness in relation to the brightness of the kernel of pixels around them.
 * @param offset	Negative value sets more pixels to 1 as you make it more negative, while a
 * positive value only sets the sharpest contrast changes to 1.
 * @param invert	True inverts the binary image resulting output.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_MeanFilter(image_t *img, uint8_t kSize, bool threshold, int32_t offset, bool invert,
		const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_mean_filter(img, kSize, threshold, offset, invert, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Applies a standard mean blurring filter using a box filter to an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		 Image; if it is not valid, an error is returned.
 * @param kSize		 Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param percentile [0, 1] value; it controls the percentile of the value used in the kernel. By default each
 * pixel is replaced with the 50th percentile (center) of its neighbors. You can set this to 0 for a
 * min filter, 0.25 for a lower quartile filter, 0.75 for an upper quartile filter, and 1.0 for a max filter.
 * @param threshold  True enables adaptive thresholding of the image, which sets pixels to one or zero
 * based on a pixel’s brightness in relation to the brightness of the kernel of pixels around them.
 * @param offset	 Negative value sets more pixels to 1 as you make it more negative, while a
 * positive value only sets the sharpest contrast changes to 1.
 * @param invert	 True inverts the binary image resulting output.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			 stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_MedianFilter(image_t *img, uint8_t kSize, float percentile, bool threshold, int32_t offset,
		bool invert, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	if ((percentile < 0.0f) || (percentile > 1.0f))
		return stm32ipl_err_InvalidParameter;

	imlib_median_filter(img, kSize, percentile, threshold, offset, invert, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Runs the mode filter on the image by replacing each pixel with the mode of their neighbours.
 * This method works great on grayscale images. However, on RGB images it creates a lot of artifacts
 * on edges because of the non-linear nature of the operation.
 * The supported formats are Binary, Grayscale, RGB565B, RGB888.
 * @param img 		Image; if it is not valid, an error is returned.
 * @param kSize 	Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), etc.
 * @param threshold True enables adaptive thresholding of the image, which sets pixels to one or zero
 * based on a pixel’s brightness in relation to the brightness of the kernel of pixels around them.
 * @param offset	Negative value sets more pixels to 1 as you make it more negative, while a
 * positive value only sets the sharpest contrast changes to 1.
 * @param invert 	True sets the binary image resulting output.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_ModeFilter(image_t *img, uint8_t kSize, bool threshold, int32_t offset, bool invert,
		const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_mode_filter(img, kSize, threshold, offset, invert, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Runs the midpoint filter on the image. This filter finds the midpoint
 * ((max-min)/2) of each pixel neighborhood in the image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img 		Image; if it is not valid, an error is returned.
 * @param kSize 	Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), etc.
 * @param bias 		[0, 1] value; it controls the min/max mixing; 0 for min filtering only, 1.0 for max filtering only.
 * @param threshold True enables adaptive thresholding of the image which sets pixels to one or zero
 * based on a pixel’s brightness in relation to the brightness of the kernel of pixels around them.
 * @param offset  	If threshold is true and offset set to a negative value, sets more pixels to 1
 * as you make it more negative, while a positive value only sets the sharpest contrast changes to 1.
 * @param invert 	If threshold is true and invert is true the binary image resulting output is inverted.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_MidpointFilter(image_t *img, uint8_t kSize, float bias, bool threshold, int32_t offset,
bool invert, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	if ((bias < 0.0f) || (bias > 1.0f))
		return stm32ipl_err_InvalidParameter;

	imlib_midpoint_filter(img, kSize, bias, threshold, offset, invert, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Convolves an image by a bilateral filter. The bilateral filter smooth the image
 * while keeping edges in the image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img 			Image; if it is not valid, an error is returned.
 * @param kSize			Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), etc.
 * @param colorSigma 	Controls how closely colors are matched using the bilateral filter.
 * Increase this to increase color blurring.
 * @param spaceSigma 	Controls how closely pixels space-wise are blurred with each other.
 * Increase this to increase pixel blurring.
 * @param threshold 	True enables adaptive thresholding of the image, which sets pixels
 * to one or zero based on a pixel’s brightness in relation to the brightness of the kernel
 * of pixels around them.
 * @param offset  		If threshold is true and offset set to a negative value, sets more
 * pixels to 1 as you make it more negative, while a positive value only sets the sharpest
 * contrast changes to 1.
 * @param invert 		If threshold is true and invert is true the binary image resulting
 * output is inverted.
 * @param mask 			Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_BilateralFilter(image_t *img, uint8_t kSize, float colorSigma, float spaceSigma, bool threshold,
		int32_t offset, bool invert, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	imlib_bilateral_filter((image_t*)img, kSize, colorSigma, spaceSigma, threshold, offset, invert, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Convolves the image by krn kernel.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param kSize		Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param krn		Kernel data.
 * @param mul		Number to multiply the convolution pixel results by. If 0, the value that will prevent
 * scaling in the convolution output. Basically allows you to do a global contrast adjustment. Pixels
 * that go outside of the image mins and maxes for color channels will be clipped.
 * @param add		Value to add to each convolution pixel result. Basically allows you to do a global
 * brightness adjustment. Pixels that go outside of the image mins and maxes for color channels will be clipped.
 * @param threshold If true, the adaptive thresholding of the image is enabled and sets pixels to one or zero
 * based on a pixel’s brightness in relation to the brightness of the kernel of pixels around them.
 * @param offset	Negative offset value sets more pixels to 1 as you make it more negative, while a positive
 * value only sets the sharpest contrast changes to 1.
 * @param invert	True inverts the binary image resulting output.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Morph(image_t *img, uint8_t kSize, const int32_t *krn, float mul, int32_t add, bool threshold,
		int32_t offset, bool invert, const image_t *mask)
{
	int n;
	int m;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	n = kSize * 2 + 1;
	m = 0;

	for (int i = 0; i < n * n; i++) {
		m += krn[i];
	}

	if (m == 0) {
		m = 1;
	}
	if (mul == 0)
		mul = 1.0f / m;

	imlib_morph(img, kSize, (int*)krn, mul, add, threshold, offset, invert, (image_t*)mask);

	return stm32ipl_err_Ok;
}

/**
 * @brief Convolves the image by a smoothing gaussian kernel.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param kSize		Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param threshold	True enables adaptive thresholding of the image, which sets pixels to one or zero
 * based on a pixel’s brightness in relation to the brightness of the kernel of pixels around them.
 * @param unsharp	True improves image sharpness on edges.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Gaussian(image_t *img, uint8_t kSize, bool threshold, bool unsharp, const image_t *mask)
{
	int k_2;
	int n;
	int *pascal;
	int *krn;
	int m;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	k_2 = kSize * 2;
	n = k_2 + 1;

	pascal = xalloc0(n * sizeof(int));
	if (!pascal)
		return stm32ipl_err_OutOfMemory;

	pascal[0] = 1;

	for (int i = 0; i < k_2; i++) {
		/* Compute a row of pascal's triangle. */
		pascal[i + 1] = (pascal[i] * (k_2 - i)) / (i + 1);
	}

	krn = xalloc0(n * n * sizeof(int));
	if (!krn) {
		xfree(pascal);
		return stm32ipl_err_OutOfMemory;
	}

	m = 0;

	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			int temp = pascal[i] * pascal[j];
			krn[(i * n) + j] = temp;
			m += temp;
		}
	}

	xfree(pascal);

	if (unsharp) {
		krn[((n / 2) * n) + (n / 2)] -= m * 2;
		m = -m;
	}

	imlib_morph(img, kSize, krn, 1.0f / m, 0, threshold, 0, false, (image_t*)mask);

	xfree(krn);

	return stm32ipl_err_Ok;
}

/**
 * @brief Convolves the image by a edge detecting laplacian kernel.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param kSize		Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param sharpen	If true, this method will instead sharpen the image. Increase the kernel size
 * then to increase the image sharpness.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Laplacian(image_t *img, uint8_t kSize, bool sharpen, const image_t *mask)
{
	int k_2;
	int n;
	int *pascal;
	int *krn;
	int m;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	k_2 = kSize * 2;
	n = k_2 + 1;

	pascal = xalloc0(n * sizeof(int));
	if (!pascal)
		return stm32ipl_err_OutOfMemory;

	pascal[0] = 1;

	for (int i = 0; i < k_2; i++) {
		/* Compute a row of pascal's triangle. */
		pascal[i + 1] = (pascal[i] * (k_2 - i)) / (i + 1);
	}

	krn = xalloc0(n * n * sizeof(int));
	if (!krn) {
		xfree(pascal);
		return stm32ipl_err_OutOfMemory;
	}

	m = 0;

	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			int temp = pascal[i] * pascal[j];
			krn[(i * n) + j] = -temp;
			m += temp;
		}
	}

	xfree(pascal);

	krn[((n / 2) * n) + (n / 2)] += m;
	m = krn[((n / 2) * n) + (n / 2)];

	if (sharpen) {
		krn[((n / 2) * n) + (n / 2)] += m;
	}

	imlib_morph(img, kSize, krn, 1.0f / m, 0, false, 0, false, (image_t*)mask);

	xfree(krn);

	return stm32ipl_err_Ok;
}

/**
 * @brief Convolves the image by a edge detecting Sobel kernel.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param kSize		Kernel size; use 1 (3x3 kernel), 2 (5x5 kernel), ..., n (((n*2)+1)x((n*2)+1) kernel).
 * @param sharpen	If true, this method will instead sharpen the image. Increase the kernel size
 * then to increase the image sharpness.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Sobel(image_t *img, uint8_t kSize, bool sharpen, const image_t *mask)
{
	int k_2;
	int n;
	int *pascal;
	int *krn;
	int m;
	float mul;
	image_t sobel_x;
	image_t sobel_y;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	k_2 = kSize * 2;
	n = k_2 + 1;

	pascal = xalloc(n * sizeof(int));
	if (!pascal) {
		return stm32ipl_err_OutOfMemory;
	}
	pascal[0] = 1;

	for (int i = 0; i < k_2; i++) {
		/* Compute a row of pascal's triangle. */
		pascal[i + 1] = (pascal[i] * (k_2 - i)) / (i + 1);
	}

	krn = xalloc(n * n * sizeof(int));
	if (!krn) {
		xfree(pascal);
		return stm32ipl_err_OutOfMemory;
	}

	m = 0;

	for (int i = 0; i < n; i++) {
		if (i < (n - 1) / 2) {
			for (int j = 0; j < n; j++) {
				int temp = pascal[i] * pascal[j];
				krn[(i * n) + j] = -temp;
				m += temp;
			}
		} else
			if (i > (n - 1) / 2) {
				for (int j = 0; j < n; j++) {
					int temp = pascal[i] * pascal[j];
					krn[(i * n) + j] = temp;
					m += temp;
				}

			} else
				if (i == (n - 1) / 2) {
					for (int j = 0; j < n; j++) {
						krn[(i * n) + j] = 0;
					}
				}
	}

	if (sharpen) {
		krn[((n / 2) * n) + (n / 2)] += m / 2;
	}

	mul = 1.0f / m;

	sobel_x.data = xalloc(STM32Ipl_ImageDataSize(img));
	if (!sobel_x.data) {
		xfree(pascal);
		xfree(krn);
		return stm32ipl_err_OutOfMemory;
	}

	STM32Ipl_Init(&sobel_x, img->w, img->h, (image_bpp_t)img->bpp, (void*)sobel_x.data);

	sobel_y.data = xalloc(STM32Ipl_ImageDataSize(img));
	if (!sobel_y.data) {
		xfree(pascal);
		xfree(krn);
		xfree(sobel_x.data);
		return stm32ipl_err_OutOfMemory;
	}

	STM32Ipl_Init(&sobel_y, img->w, img->h, (image_bpp_t)img->bpp, (void*)sobel_y.data);

	memcpy(sobel_x.data, img->data, STM32Ipl_ImageDataSize(img));
	memcpy(sobel_y.data, img->data, STM32Ipl_ImageDataSize(img));

	imlib_morph(&sobel_x, kSize, krn, mul, 0, false, 0, false, (image_t*)mask);

	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			int temp = pascal[i] * pascal[j];
			if (j < (n - 1) / 2)
				krn[(i * n) + j] = -temp;
			else
				if (j > (n - 1) / 2)
					krn[(i * n) + j] = temp;
				else
					krn[(i * n) + j] = 0;
		}
	}

	if (sharpen) {
		krn[((n / 2) * n) + (n / 2)] += m % 2 ? m / 2 : (m / 2) + 1;
	}

	imlib_morph(&sobel_y, kSize, krn, mul, 0, false, 0, false, (image_t*)mask);

	STM32Ipl_Add(&sobel_x, &sobel_y, 1, NULL);

	xfree(img->data);
	STM32Ipl_Init(img, img->w, img->h, (image_bpp_t)sobel_x.bpp, (void*)sobel_x.data);

	xfree(sobel_y.data);
	xfree(pascal);
	xfree(krn);

	return stm32ipl_err_Ok;
}

/**
 * @brief Convolves the image by a edge detecting Scharr kernel.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param kSize		Kernel size; currently only kSize = 1 is allowed, corresponding to a 3x3 kernel.
 * @param sharpen	If true, this method will instead sharpen the image. Increase the kernel size
 * then to increase the image sharpness.
 * @param mask 		Optional image to be used as a pixel level mask for the operation.
 * The mask must have the same resolution as the source image. Only the source pixels that
 * have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Scharr(image_t *img, uint8_t kSize, bool sharpen, const image_t *mask)
{
	int k_2;
	int n;
	int *krn;
	int m;
	float mul;
	image_t scharr_x;
	image_t scharr_y;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)
	}

	k_2 = kSize * 2;

	if (k_2 != 2)
		return stm32ipl_err_NotImplemented;

	n = k_2 + 1;

	krn = xalloc(n * n * sizeof(int));
	if (krn == NULL) {
		return stm32ipl_err_OutOfMemory;
	}

	krn[0] = -3;
	krn[1] = -10;
	krn[2] = -3;
	krn[3] = 0;
	krn[4] = 0;
	krn[5] = 0;
	krn[6] = 3;
	krn[7] = 10;
	krn[8] = 3;

	m = 32;

	if (sharpen) {
		krn[((n / 2) * n) + (n / 2)] += m % 2 ? m / 2 : (m / 2) + 1;
	}

	mul = 1.0f / m;

	scharr_x.data = xalloc(STM32Ipl_ImageDataSize(img));
	if (!scharr_x.data) {
		xfree(krn);
		return stm32ipl_err_OutOfMemory;
	}
	STM32Ipl_Init(&scharr_x, img->w, img->h, (image_bpp_t)img->bpp, (void*)scharr_x.data);

	scharr_y.data = xalloc(STM32Ipl_ImageDataSize(img));
	if (!scharr_y.data) {
		xfree(krn);
		xfree(scharr_x.data);
		return stm32ipl_err_OutOfMemory;
	}
	STM32Ipl_Init(&scharr_y, img->w, img->h, (image_bpp_t)img->bpp, (void*)scharr_y.data);

	memcpy(scharr_x.data, img->data, STM32Ipl_ImageDataSize(img));
	memcpy(scharr_y.data, img->data, STM32Ipl_ImageDataSize(img));

	if (sharpen) {
		krn[((n / 2) * n) + (n / 2)] += m / 2;
	}

	imlib_morph(&scharr_x, kSize, krn, mul, 0, false, 0, false, (image_t*)mask);

	krn[0] = -3;
	krn[1] = 0;
	krn[2] = 3;
	krn[3] = -10;
	krn[4] = 0;
	krn[5] = 10;
	krn[6] = -3;
	krn[7] = 0;
	krn[8] = 3;

	imlib_morph(&scharr_y, kSize, krn, mul, 0, false, 0, false, (image_t*)mask);

	STM32Ipl_Add(&scharr_x, &scharr_y, 1, NULL);

	xfree(img->data);
	STM32Ipl_Init(img, img->w, img->h, (image_bpp_t)scharr_x.bpp, (void*)scharr_x.data);

	xfree(scharr_y.data);
	xfree(krn);

	return stm32ipl_err_Ok;
}

/**
 * @brief Finds the midpoints of xDiv * yDiv kernels in the source image and stores them in
 * the destination image. The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src		Source image; if it is not valid, an error is returned.
 * @param dst		Destination image; it must have the same format as the source image;
 * its width and height must be a fraction of source image (dstW = srcW / xDiv) and (dstH = srcH / yDiv),
 *  otherwise an error is returned; if it is not valid, an error is returned.
 * @param xDiv 		Width of the kernel.
 * @param yDiv		Height of the kernel.
 * @param bias		A bias of 0 returns the min of each area while a bias of 256 returns the max of each area.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_MidpointPool(const image_t *src, image_t *dst, uint16_t xDiv, uint16_t yDiv, uint16_t bias)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_FORMAT(src, dst)

	if ((src == dst))
		return stm32ipl_err_InvalidParameter;

	if (((src->w / xDiv) != dst->w) || ((src->h / yDiv) != dst->h))
		return stm32ipl_err_InvalidParameter;

	if (bias > 256)
		return stm32ipl_err_InvalidParameter;

	imlib_midpoint_pool((image_t*)src, dst, xDiv, yDiv, bias);

	return stm32ipl_err_Ok;
}

/**
 * @brief Finds the mean of xDiv * yDiv kernels in the source image and stores them in
 * the destination image. The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src		Source image; if it is not valid, an error is returned.
 * @param dst		Destination image; if it is not valid, an error is returned;
 * it must have the same format as the source image; its width and height must be a
 * fraction of source image (dstW = srcW / xDiv) and (dstH = srcH / yDiv),
 * otherwise an error is returned.
 * @param xDiv 		Width of the kernel.
 * @param yDiv		Height of the kernel.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_MeanPool(const image_t *src, image_t *dst, uint16_t xDiv, uint16_t yDiv)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_FORMAT(src, dst)

	if ((src == dst))
		return stm32ipl_err_InvalidParameter;

	if (((src->w / xDiv) != dst->w) || ((src->h / yDiv) != dst->h))
		return stm32ipl_err_InvalidParameter;

	imlib_mean_pool((image_t*)src, dst, xDiv, yDiv);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
