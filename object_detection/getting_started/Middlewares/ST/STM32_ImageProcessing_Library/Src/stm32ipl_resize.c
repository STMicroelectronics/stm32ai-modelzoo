/**
 ******************************************************************************
 * @file   stm32ipl_resize.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - scaling and cropping module
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
 * @brief Crops a rectangular region of the source image, starting from the given coordinates, and
 * copies it to the destination image. The size of the cropped region is determined by width and height
 * of the destination image. The two images must have same format. The destination image data
 * buffer must be already allocated by the user. If the region to be cropped falls outside the
 * source image, an error is returned. The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src 	Source image; it must be valid, otherwise an error is returned.
 * @param dst 	Destination image; it must be valid, otherwise an error is returned.
 * @param x		X-coordinate of the top-left corner of the region within the source image.
 * @param y		Y-coordinate of the top-left corner of the region within the source image.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Crop(const image_t *src, image_t *dst, uint32_t x, uint32_t y)
{
	rectangle_t srcRoi;
	int32_t dstW;
	int32_t dstH;

	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_FORMAT(src, dst)

	if ((dst->w < 1) || (dst->h < 1))
		return stm32ipl_err_InvalidParameter;

	dstW = dst->w;
	dstH = dst->h;

	STM32Ipl_RectInit(&srcRoi, x, y, dstW, dstH);

	STM32IPL_CHECK_VALID_ROI(src, &srcRoi)

	switch (src->bpp) {
		case IMAGE_BPP_BINARY:
			for (uint32_t srcY = y, dstY = 0; dstY < dstH; srcY++, dstY++) {
				uint32_t *srcRow = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(src, srcY);
				uint32_t *dstRow = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(dst, dstY);

				for (uint32_t srcX = x, dstX = 0; dstX < dstW; srcX++, dstX++)
					IMAGE_PUT_BINARY_PIXEL_FAST(dstRow, dstX, IMAGE_GET_BINARY_PIXEL_FAST(srcRow, srcX));
			}
			break;

		case IMAGE_BPP_GRAYSCALE:
			for (uint32_t srcY = y, dstY = 0; dstY < dstH; srcY++, dstY++) {
				uint8_t *srcRow = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(src, srcY);
				uint8_t *dstRow = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(dst, dstY);

				for (uint32_t srcX = x, dstX = 0; dstX < dstW; srcX++, dstX++)
					IMAGE_PUT_GRAYSCALE_PIXEL_FAST(dstRow, dstX, IMAGE_GET_GRAYSCALE_PIXEL_FAST(srcRow, srcX));
			}
			break;

		case IMAGE_BPP_RGB565:
			for (uint32_t srcY = y, dstY = 0; dstY < dstH; srcY++, dstY++) {
				uint16_t *srcRow = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(src, srcY);
				uint16_t *dstRow = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(dst, dstY);

				for (uint32_t srcX = x, dstX = 0; dstX < dstW; srcX++, dstX++)
					IMAGE_PUT_RGB565_PIXEL_FAST(dstRow, dstX, IMAGE_GET_RGB565_PIXEL_FAST(srcRow, srcX));
			}
			break;

		case IMAGE_BPP_RGB888:
			for (uint32_t srcY = y, dstY = 0; dstY < dstH; srcY++, dstY++) {
				rgb888_t *srcRow = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(src, srcY);
				rgb888_t *dstRow = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(dst, dstY);

				for (uint32_t srcX = x, dstX = 0; dstX < dstW; srcX++, dstX++)
					IMAGE_PUT_RGB888_PIXEL_FAST(dstRow, dstX, IMAGE_GET_RGB888_PIXEL_FAST(srcRow, srcX));
			}
			break;

		default:
			return stm32ipl_err_UnsupportedFormat;
	}

	return stm32ipl_err_Ok;
}

/**
 * @brief Resizes the source image (whole or a portion of it) to the destination image with Nearest Neighbor method.
 * The two images must have same format. The destination image data buffer must be already allocated
 * by the user and its size must be large enough to contain the resized pixels. When specified, roi defines
 * the region of the source image to be scaled to the destination image resolution. If roi is null, the whole
 * source image is resized to the destination size. The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src 	Source image; it must be valid, otherwise an error is returned.
 * @param dst 	Destination image; it must be valid, otherwise an error is returned;
 * its width and height must be greater than zero.
 * @param roi	Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Resize(const image_t *src, image_t *dst, const rectangle_t *roi)
{
	rectangle_t srcRoi;
	int32_t srcW;
	int32_t srcH;
	int32_t dstW;
	int32_t dstH;
	int32_t wRatio;
	int32_t hRatio;

	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_FORMAT(src, dst)

	if ((dst->w < 1) || (dst->h < 1))
		return stm32ipl_err_InvalidParameter;

	srcW = src->w;
	srcH = src->h;
	dstW = dst->w;
	dstH = dst->h;

	STM32Ipl_RectInit(&srcRoi, 0, 0, srcW, srcH);

	if (roi) {
		if (roi->w < 1 || roi->h < 1)
			return stm32ipl_err_WrongROI;

		if (!STM32Ipl_RectContain(&srcRoi, roi))
			return stm32ipl_err_WrongROI;

		STM32Ipl_RectCopy((rectangle_t*)roi, &srcRoi);
	}

	wRatio = (int32_t) ((roi->w << 16) / dst->w) + 1;
	hRatio = (int32_t) ((roi->h << 16) / dst->h) + 1;

	switch (src->bpp) {
		case IMAGE_BPP_BINARY:
			for (uint32_t y = 0; y < dstH; y++) {
				uint32_t *srcRow = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(src, ((y * hRatio) >> 16) + srcRoi.y);
				uint32_t *dstRow = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(dst, y);

				for (uint32_t x = 0; x < dstW; x++)
					IMAGE_PUT_BINARY_PIXEL_FAST(dstRow, x,
							IMAGE_GET_BINARY_PIXEL_FAST(srcRow, ((x * wRatio) >> 16) + srcRoi.x));
			}
			break;

		case IMAGE_BPP_GRAYSCALE:
			for (uint32_t y = 0; y < dstH; y++) {
				uint8_t *srcRow = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(src, ((y * hRatio) >> 16) + srcRoi.y);
				uint8_t *dstRow = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(dst, y);

				for (uint32_t x = 0; x < dstW; x++)
					IMAGE_PUT_GRAYSCALE_PIXEL_FAST(dstRow, x,
							IMAGE_GET_GRAYSCALE_PIXEL_FAST(srcRow, ((x * wRatio) >> 16) + srcRoi.x));
			}
			break;

		case IMAGE_BPP_RGB565:
			for (uint32_t y = 0; y < dstH; y++) {
				uint16_t *srcRow = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(src, ((y * hRatio) >> 16) + srcRoi.y);
				uint16_t *dstRow = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(dst, y);

				for (uint32_t x = 0; x < dstW; x++)
					IMAGE_PUT_RGB565_PIXEL_FAST(dstRow, x,
							IMAGE_GET_RGB565_PIXEL_FAST(srcRow, ((x * wRatio) >> 16) + srcRoi.x));
			}
			break;

		case IMAGE_BPP_RGB888:
			for (uint32_t y = 0; y < dstH; y++) {
				rgb888_t *srcRow = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(src, ((y * hRatio) >> 16) + srcRoi.y);
				rgb888_t *dstRow = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(dst, y);
				for (uint32_t x = 0; x < dstW; x++)
					IMAGE_PUT_RGB888_PIXEL_FAST(dstRow, x,
							IMAGE_GET_RGB888_PIXEL_FAST(srcRow, ((x * wRatio) >> 16) + srcRoi.x));
			}
			break;

		default:
			return stm32ipl_err_UnsupportedFormat;
	}

	return stm32ipl_err_Ok;
}

/**
 * @brief Resizes (downscale only) the source image to the destination image with Nearest Neighbor method.
 * The two images must have the same format. The destination image data buffer must be already allocated
 * by the user and its size must be large enough to contain the resized pixels.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * Use this function for downscale cases only.
 * @param src 		Source image; it must be valid, otherwise an error is returned;
 * @param dst 		Destination image; its width and height must be greater than zero; it must be valid, otherwise an error is returned;
 * @param reversed 	False to resize in incrementing order, from start to the end of the image;
 * true to resize in decrementing order, from end to start of the image.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Downscale(const image_t *src, image_t *dst, bool reversed)
{
	int32_t dstW;
	int32_t dstH;
	int32_t wRatio;
	int32_t hRatio;

	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_FORMAT(src, dst)

	if ((dst->w < 1) || (dst->h < 1))
		return stm32ipl_err_InvalidParameter;

	dstW = dst->w;
	dstH = dst->h;

	wRatio = (int32_t) ((src->w << 16) / dst->w) + 1;
	hRatio = (int32_t) ((src->h << 16) / dst->h) + 1;

	if (reversed) {
		switch (src->bpp) {
			case IMAGE_BPP_BINARY:
				for (int32_t y = dstH - 1; y >= 0; y--) {
					uint32_t *srcRow = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(src, (y * hRatio) >> 16);
					uint32_t *dstRow = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(dst, y);

					for (int32_t x = dstW - 1; x >= 0; x--)
						IMAGE_PUT_BINARY_PIXEL_FAST(dstRow, x,
								IMAGE_GET_BINARY_PIXEL_FAST(srcRow, (x * wRatio) >> 16));
				}
				break;

			case IMAGE_BPP_GRAYSCALE:
				for (int32_t y = dstH - 1; y >= 0; y--) {
					uint8_t *srcRow = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(src, (y * hRatio) >> 16);
					uint8_t *dstRow = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(dst, y);

					for (int32_t x = dstW - 1; x >= 0; x--)
						IMAGE_PUT_GRAYSCALE_PIXEL_FAST(dstRow, x,
								IMAGE_GET_GRAYSCALE_PIXEL_FAST(srcRow, (x * wRatio)) >> 16);
				}
				break;

			case IMAGE_BPP_RGB565:
				for (int32_t y = dstH - 1; y >= 0; y--) {
					uint16_t *srcRow = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(src, (y * hRatio) >> 16);
					uint16_t *dstRow = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(dst, y);

					for (int x = dstW - 1; x >= 0; x--)
						IMAGE_PUT_RGB565_PIXEL_FAST(dstRow, x,
								IMAGE_GET_RGB565_PIXEL_FAST(srcRow, (x * wRatio) >> 16));
				}

				break;

			case IMAGE_BPP_RGB888:
				for (int32_t y = dstH - 1; y >= 0; y--) {
					rgb888_t *srcRow = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(src, (y * hRatio) >> 16);
					rgb888_t *dstRow = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(dst, y);

					for (int x = dstW - 1; x >= 0; x--)
						IMAGE_PUT_RGB888_PIXEL_FAST(dstRow, x,
								IMAGE_GET_RGB888_PIXEL_FAST(srcRow, (x * wRatio) >> 16));
				}
				break;

			default:
				return stm32ipl_err_UnsupportedFormat;
		}
	} else {
		switch (src->bpp) {
			case IMAGE_BPP_BINARY:
				for (int32_t y = 0; y < dstH; y++) {
					uint32_t *srcRow = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(src, (y * hRatio) >> 16);
					uint32_t *dstRow = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(dst, y);

					for (int32_t x = 0; x < dstW; x++)
						IMAGE_PUT_BINARY_PIXEL_FAST(dstRow, x,
								IMAGE_GET_BINARY_PIXEL_FAST(srcRow, (x * wRatio) >> 16));
				}
				break;

			case IMAGE_BPP_GRAYSCALE:
				for (int32_t y = 0; y < dstH; y++) {
					uint8_t *srcRow = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(src, (y * hRatio) >> 16);
					uint8_t *dstRow = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(dst, y);

					for (int32_t x = 0; x < dstW; x++)
						IMAGE_PUT_GRAYSCALE_PIXEL_FAST(dstRow, x,
								IMAGE_GET_GRAYSCALE_PIXEL_FAST(srcRow, (x * wRatio) >> 16));
				}
				break;

			case IMAGE_BPP_RGB565:
				for (int32_t y = 0; y < dstH; y++) {
					uint16_t *srcRow = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(src, (y * hRatio) >> 16);
					uint16_t *dstRow = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(dst, y);

					for (int32_t x = 0; x < dstW; x++)
						IMAGE_PUT_RGB565_PIXEL_FAST(dstRow, x,
								IMAGE_GET_RGB565_PIXEL_FAST(srcRow, (x * wRatio) >> 16));
				}

				break;

			case IMAGE_BPP_RGB888:
				for (int32_t y = 0; y < dstH; y++) {
					rgb888_t *srcRow = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(src, (y * hRatio) >> 16);
					rgb888_t *dstRow = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(dst, y);

					for (int32_t x = 0; x < dstW; x++)
						IMAGE_PUT_RGB888_PIXEL_FAST(dstRow, x,
								IMAGE_GET_RGB888_PIXEL_FAST(srcRow, (x * wRatio) >> 16));
				}
				break;

			default:
				return stm32ipl_err_UnsupportedFormat;
		}
	}

	return stm32ipl_err_Ok;
}

/**
 * @brief Resizes (downscale only) the source image to the destination image with Nearest Neighbor method.
 * The two images must have the same format. The destination image data buffer must be already allocated
 * by the user and its size must be large enough to contain the resized pixels.
 * The supported format is RGB888 and BGR888. Binary, Grayscale, RGB565 not tested yet
 * Use this function for downscale cases only.
 * @param src 		Source image; it must be valid, otherwise an error is returned;
 * @param dst 		Destination image; its width and height must be greater than zero; it must be valid, otherwise an error is returned;
 * true to resize in decrementing order, from end to start of the image.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Downscale_bilinear(const image_t *src, image_t *dst)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_FORMAT(src, dst)


  uint8_t *dstImage = dst->pixels;
  uint32_t pixelSize;
  int32_t srcStride;
  float widthRatio;
  float heightRatio;

  int32_t maxWidth;
  int32_t maxHeight;

  float srcX, srcY, dX1, dY1, dX2, dY2;
  int32_t dstX1, srcY1, dstX2, srcY2;

  uint8_t *tmp1, *tmp2;
  uint8_t *p1, *p2, *p3, *p4;

  int32_t offset1;
  int32_t offset2;

	switch (src->bpp)
	{
		case IMAGE_BPP_GRAYSCALE:
			pixelSize = 1;
			break;
		case IMAGE_BPP_RGB565:
			pixelSize = 2;
			break;
		case IMAGE_BPP_RGB888:
			pixelSize = 3;
			break;
		default:
			pixelSize = 3;
			break;
	}
  srcStride = pixelSize * src->w;

  widthRatio =  (float) src->w / (float) dst->w;
  heightRatio =  (float) src->h / (float) dst->h;

  /* Get horizontal and vertical limits. */
  maxWidth = src->w - 1;
  maxHeight = src->h - 1;

	for (int32_t y = 0; y < dst->h; y++)
  {
    /* Get Y from source. */
    srcY = (float) y * heightRatio;
    srcY1 = (int32_t) srcY;
    srcY2 = (srcY1 == maxHeight) ? srcY1 : srcY1 + 1;
    dY1 = srcY - (float) srcY1;
    dY2 = 1.0f - dY1;

    /* Calculates the pointers to the two needed lines of the source. */
    tmp1 = src->pixels + srcY1 * srcStride;
    tmp2 = src->pixels + srcY2 * srcStride;

    for (int32_t x = 0; x < dst->w; x++)
    {
      /* Get X from source. */
      srcX = x * widthRatio;
      dstX1 = (int32_t) srcX;
      dstX2 = (dstX1 == maxWidth) ? dstX1 : dstX1 + 1;
      dX1 = srcX - /*(float32)*/dstX1;
      dX2 = 1.0f - dX1;

      /* Calculates the four points (p1,p2, p3, p4) of the source. */
      offset1 = dstX1 * pixelSize;
      offset2 = dstX2 * pixelSize;
      p1 = tmp1 + offset1;
      p2 = tmp1 + offset2;
      p3 = tmp2 + offset1;
      p4 = tmp2 + offset2;
      /* For each channel, interpolate the four points. */
      for (int32_t ch = 0; ch < pixelSize; ch++, dstImage++, p1++, p2++, p3++, p4++)
      {
        *dstImage = (uint8_t)(dY2 * (dX2 * (*p1) + dX1 * (*p2)) + dY1 * (dX2 * (*p3) + dX1 * (*p4)));
      }
    }
  }

	return stm32ipl_err_Ok;
}



#ifdef __cplusplus
}
#endif
