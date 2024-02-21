/**
 ******************************************************************************
 * @file   stm32ipl_stats.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - statistics module
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
 * @brief Initializes an image histogram to zero values.
 * @param hist	Histogram; if it is not valid, an error is returned.
 * @return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_HistInit(histogram_t *hist)
{
	STM32IPL_CHECK_VALID_PTR_ARG(hist)

	memset(hist, 0, sizeof(histogram_t));

	return stm32ipl_err_Ok;
}

/**
 * @brief Allocates the memory buffers needed to contain the LAB histogram data.
 * The size of such buffers depends on the size of given LAB channels.
 * Assuming the input histogram data pointers are null to avoid memory leakage.
 * It is up to the caller to release the histogram memory buffers with STM32Ipl_HistReleaseData().
 * @param hist		Histogram; if it is not valid, an error is returned.
 * @param lCount	Number of bins relative to the L channel.
 * @param aCount	Number of bins relative to the A channel.
 * @param bCount	Number of bins relative to the B channel.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_HistAllocData(histogram_t *hist, uint32_t lCount, uint32_t aCount, uint32_t bCount)
{
	STM32IPL_CHECK_VALID_PTR_ARG(hist)

	memset(hist, 0, sizeof(histogram_t));

	if (lCount) {
		hist->LBins = xalloc(lCount * sizeof(float));
		if (!hist->LBins)
			return stm32ipl_err_OutOfMemory;
	}

	if (aCount) {
		hist->ABins = xalloc(aCount * sizeof(float));
		if (!hist->ABins) {
			xfree(hist->LBins);
			return stm32ipl_err_OutOfMemory;
		}
	}

	if (bCount) {
		hist->BBins = xalloc(bCount * sizeof(float));
		if (!hist->BBins) {
			xfree(hist->LBins);
			xfree(hist->ABins);
			return stm32ipl_err_OutOfMemory;
		}
	}

	hist->LBinCount = lCount;
	hist->ABinCount = aCount;
	hist->BBinCount = bCount;

	return stm32ipl_err_Ok;
}

/**
 * @brief Releases the data memory buffers of an histogram and resets its structure.
 * @param hist	Histogram.
 * @return		void.
 */
void STM32Ipl_HistReleaseData(histogram_t *hist)
{
	if (!hist)
		return;

	xfree(hist->LBins);
	xfree(hist->ABins);
	xfree(hist->BBins);

	memset(hist, 0, sizeof(histogram_t));
}

/**
 * @brief Calculates the LAB histogram of an image. Histograms of Grayscale and Binary images have one channel
 * with some number of bins. Histograms of RGB565 and RGB888 have three channels with some number of bins each.
 * All bins are normalized so that all bins in a channel sum to 1. Assuming the input histogram data pointers are
 * null to avoid memory leakage. This function allocates the histogram memory buffers; it is up to the caller to
 * release the histogram memory buffers with STM32Ipl_HistReleaseData().
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img	Image; if it is not valid, an error is returned.
 * @param out	Resulting LAB histogram; if it is not valid, an error is returned.
 * @param roi	Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetHistogram(const image_t *img, histogram_t *out, const rectangle_t *roi)
{
	rectangle_t realRoi;
	list_t thresholds;
	bool invert = false;
	image_t *other = NULL;
	uint32_t lCount = 0;
	uint32_t aCount = 0;
	uint32_t bCount = 0;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(out)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	STM32Ipl_HistInit(out);

	list_init(&thresholds, sizeof(color_thresholds_list_lnk_data_t));

	switch (img->bpp) {
		case IMAGE_BPP_BINARY: {
			lCount = COLOR_BINARY_MAX - COLOR_BINARY_MIN + 1;
			break;
		}

		case IMAGE_BPP_GRAYSCALE: {
			lCount = COLOR_GRAYSCALE_MAX - COLOR_GRAYSCALE_MIN + 1;
			break;
		}

		case IMAGE_BPP_RGB565:
		case IMAGE_BPP_RGB888: {
			lCount = COLOR_L_MAX - COLOR_L_MIN + 1;
			aCount = COLOR_A_MAX - COLOR_A_MIN + 1;
			bCount = COLOR_B_MAX - COLOR_B_MIN + 1;
			break;
		}

		default: {
			return stm32ipl_err_InvalidParameter;
		}
	}

	STM32Ipl_HistAllocData(out, lCount, aCount, bCount);

	imlib_get_histogram(out, (image_t*)img, &realRoi, &thresholds, invert, other);

	list_free(&thresholds);

	return stm32ipl_err_Ok;
}

/**
 * @brief Gets the LAB percentile from a LAB histogram.
 * @param hist			LAB histogram; if it is not valid, an error is returned.
 * @param format		Format of the image the provided histogram was obtained from.
 * supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param out			Resulting percentile.
 * @param percentile	Value used to get the result. When set to 0.1, this method will tell you
 * (going from left-to-right in the histogram) what bin, when summed into an accumulator, caused the
 * accumulator to cross 0.1. This is useful to determine min (with 0.1) and max (with 0.9) of a color
 * distribution without outlier effects ruining your results for adaptive color tracking.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetPercentile(const histogram_t *hist, image_bpp_t format, percentile_t *out, float percentile)
{
	image_t img;

	if (!hist || !out)
		return stm32ipl_err_InvalidParameter;

	img.bpp = format;

	STM32IPL_CHECK_FORMAT(&img, STM32IPL_IF_ALL)

	if ((format == IMAGE_BPP_BINARY || format == IMAGE_BPP_GRAYSCALE) && !hist->LBins)
		return stm32ipl_err_InvalidParameter;
	else
		if ((format == IMAGE_BPP_RGB565 || format == IMAGE_BPP_RGB888) && !hist->LBins && !hist->ABins && !hist->BBins)
			return stm32ipl_err_InvalidParameter;

	imlib_get_percentile(out, format, (histogram_t*)hist, percentile);

	return stm32ipl_err_Ok;
}

/**
 * @brief Uses Otsu method to compute the optimal threshold values that split each channel of the histogram into two halves.
 * Supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param hist		LAB histogram; if it is not valid, an error is returned.
 * @param format	Format of the image the provided histogram was obtained from.
 * @param out		Resulting LAB thresholds.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetThreshold(const histogram_t *hist, image_bpp_t format, threshold_t *out)
{
	image_t img;

	if (!hist || !out)
		return stm32ipl_err_InvalidParameter;

	img.bpp = format;

	STM32IPL_CHECK_FORMAT(&img, STM32IPL_IF_ALL)

	imlib_get_threshold(out, format, (histogram_t*)hist);

	return stm32ipl_err_Ok;
}

/**
 * @brief Determines a similarity score between two images (or between an image and a color value)
 * with a Structural Similarity (SSIM) algorithm that compares 8x8 pixel blocks. Such score is
 * described in terms of the following statistics calculated among the image blocks: average,
 * standard deviation, minimum and maximum.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		First image; if it is not valid, an error is returned.
 * @param other		Second image (optional); when used, it must have same format and size as
 * the first image, otherwise an error is returned.
 * @param color 	This value has 0xRRGGBB format and is used only when the second image is NULL.
 * @param avg		Average similarity among the image blocks.
 * @param std		Standard deviation among the image blocks.
 * @param min		Minimum value among the image blocks.
 * @param max		Maximum value among the image blocks.
 * @return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetSimilarity(const image_t *img, const image_t *other, stm32ipl_color_t color, float *avg,
		float *std, float *min, float *max)
{
	uint32_t newColor = 0;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(avg)
	STM32IPL_CHECK_VALID_PTR_ARG(std)
	STM32IPL_CHECK_VALID_PTR_ARG(min)
	STM32IPL_CHECK_VALID_PTR_ARG(max)

	/* Alternatively use the other image or the color value to be added to the source image. */
	if (other) {
		STM32IPL_CHECK_VALID_IMAGE(other)
		STM32IPL_CHECK_SAME_HEADER(img, other)
	} else {
		newColor = STM32Ipl_AdaptColor(img, newColor);
	}

	imlib_get_similarity((image_t*)img, NULL, (image_t*)other, newColor, avg, std, min, max);

	return stm32ipl_err_Ok;
}

/**
 * @brief Gets some statistics of an image: mean, median, mode, standard deviation, min, max, lower quartile,
 * and upper quartile, calculated for each color channel of the histogram of the image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img	Image; if it is not valid, an error is returned.
 * @param out	Statistics for each histogram channel (that is, L for Binary or Grayscale images, LAB for RGB images);
 * if it is not valid, an error is returned.
 * @param roi	Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetStatistics(const image_t *img, statistics_t *out, const rectangle_t *roi)
{
	histogram_t hist;
	stm32ipl_err_t error;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(out)

	error = STM32Ipl_GetHistogram(img, &hist, roi);
	if (error != stm32ipl_err_Ok)
		return error;

	imlib_get_statistics(out, (image_bpp_t)img->bpp, &hist);

	STM32Ipl_HistReleaseData(&hist);

	return stm32ipl_err_Ok;
}

/**
 * @brief Computes a linear regression on all the thresholded pixels in the image.
 * The linear regression is computed using least-squares normally which is fast, but cannot handle any outlier.
 * If robust is true then the Theil–Sen linear regression is used instead, which computes the median of all slopes
 * between all thresholded pixels in the image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img				Image; if it is not valid, an error is returned.
 * @param out				Information about the found line; if it is not valid, an error is returned.
 * @param roi				Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param xStride			Number of x pixels to skip over when evaluating the image.
 * @param yStride			Number of y pixels to skip over when evaluating the image.
 * @param thresholds		List of color_thresholds_list_lnk_data_t.
 * @param invert			Inverts the thresholding operation such that instead of matching pixels inside of some known
 * color bounds pixels are matched that are outside of the known color bounds.
 * @param areaThreshold		If the regression’s bounding box area is less than areaThreshold, then out values are set to zero.
 * @param pixelsThreshold	If the regression’s pixel count is less than pixelsThreshold, then then out values are set to zero.
 * @param robust			When true, the Theil–Sen linear regression is used instead which computes the median of all slopes
 * between all thresholded pixels in the image.
 * @return					stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetRegressionImage(const image_t *img, find_lines_list_lnk_data_t *out, const rectangle_t *roi,
		uint8_t xStride, uint8_t yStride, const list_t *thresholds, bool invert, uint32_t areaThreshold,
		uint32_t pixelsThreshold, bool robust)
{
	rectangle_t realRoi;
	bool res;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(out)
	STM32IPL_CHECK_VALID_PTR_ARG(thresholds)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	if (list_size((list_t*)thresholds) == 0)
		return stm32ipl_err_InvalidParameter;

	res = imlib_get_regression(out, (image_t*)img, &realRoi, xStride, yStride, (list_t*)thresholds, invert,
			areaThreshold, pixelsThreshold, robust);
	if (res)
		return stm32ipl_err_Ok;

	return stm32ipl_err_OpNotCompleted;
}

/**
 * @brief Gets the mean of image data values.
 * The supported formats are Grayscale, RGB565, RGB888.
 * @param img	 	Image; if it is not valid, an error is returned.
 * @param outR 		R mean value or Grayscale mean value; if it is not valid, an error is returned.
 * @param outG 		G mean value or Grayscale mean value; if it is not valid, an error is returned.
 * @param outB 		B mean value or Grayscale mean value; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetMean(const image_t *img, int32_t *outR, int32_t *outG, int32_t *outB)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, (stm32ipl_if_grayscale | stm32ipl_if_rgb565 | stm32ipl_if_rgb888))

	if (!outR || !outG || !outB)
		return stm32ipl_err_InvalidParameter;

	imlib_image_mean((image_t*)img, (int*)outR, (int*)outG, (int*)outB);

	return stm32ipl_err_Ok;
}

/**
 * @brief Gets the standard deviation value of an image.
 * The supported format is Grayscale.
 * @param src		Image; if it is not valid, an error is returned.
 * @param out		Resulting standard deviation; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetStdDev(const image_t *src, int32_t *out)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_GRAY_ONLY)
	STM32IPL_CHECK_VALID_PTR_ARG(out)

	*out = imlib_image_std((image_t*)src);

	return stm32ipl_err_Ok;
}

/**
 * @brief Counts the number of non zero pixels in an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param out		Number of non zero pixel; if it is not valid, an error is returned.
 * @param roi		Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_CountNonZero(const image_t *img, uint32_t *out, const rectangle_t *roi)
{
	rectangle_t realRoi;
	uint32_t nonZero;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	if (!out)
		return stm32ipl_err_InvalidParameter;

	nonZero = 0;

	switch (img->bpp) {
		case IMAGE_BPP_BINARY: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				uint32_t *row_ptr = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					if (IMAGE_GET_BINARY_PIXEL_FAST(row_ptr, x) > 0) {
						nonZero++;
					}
				}
			}
			break;
		}

		case IMAGE_BPP_GRAYSCALE: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				uint8_t *row_ptr = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					if (IMAGE_GET_GRAYSCALE_PIXEL_FAST(row_ptr, x) > 0) {
						nonZero++;
					}
				}
			}
			break;
		}

		case IMAGE_BPP_RGB565: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				uint16_t *row_ptr = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					if (COLOR_RGB565_TO_GRAYSCALE(IMAGE_GET_RGB565_PIXEL_FAST(row_ptr, x)) > 0) {
						nonZero++;
					}
				}
			}
			break;
		}

		case IMAGE_BPP_RGB888: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				rgb888_t *row_ptr = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					if (COLOR_RGB888_TO_GRAYSCALE(IMAGE_GET_RGB888_PIXEL_FAST(row_ptr, x)) > 0) {
						nonZero++;
					}
				}
			}
			break;
		}

		default:
			return stm32ipl_err_InvalidParameter;
	}

	*out = nonZero;

	return stm32ipl_err_Ok;

}

/**
 * @brief Computes a linear regression using points.
 * The linear regression is computed using least-squares normally which is fast but cannot handle any outliers.
 * If robust is True then the Theil-Sen linear regression is used instead which computes the median of all slopes between all thresholded pixels in the image
 * @param out		output and contains find_lines_list_lnk_data with the line points, magnitude.
 * @param points	points used in the regression
 * @param nPoints	number of first points used to find line with the regression
 * @param robust	is True then the Theil-Sen linear regression is used instead which computes the median of all slopes between all thresholded pixels in the image.
 * @return	stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_GetRegressionPoints(const point_t *points, uint16_t nPoints, find_lines_list_lnk_data_t *out,
		bool robust)
{
	bool res;

	if (!out || !points)
		return stm32ipl_err_InvalidParameter;

	res = stm32ipl_get_regression_points(points, nPoints, out, robust);

	return res ? stm32ipl_err_Ok : stm32ipl_err_OpNotCompleted;
}

#ifdef __cplusplus
}
#endif
