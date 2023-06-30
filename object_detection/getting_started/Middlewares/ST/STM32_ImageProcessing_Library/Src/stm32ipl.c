/**
 ******************************************************************************
 * @file   stm32ipl.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - main image processing module
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
 * @brief Initializes the memory manager used by this library.
 * @param memAddr	Address of the memory buffer allocated to STM32IPL for its internal purposes.
 * @param memSize	Size of the memory buffer (bytes).
 * @return			void.
 */
void STM32Ipl_InitLib(void *memAddr, uint32_t memSize)
{
	umm_init(memAddr, memSize);
	fb_init();
}

/**
 * @brief De-initializes the memory manager of this library.
 * @return	void.
 */
void STM32Ipl_DeInitLib(void)
{
	umm_uninit();
}

/**
 * @brief Initializes an image structure with the given arguments.
 * @param img		Image: it must point to a valid structure.
 * @param width		Image width.
 * @param height	Image height.
 * @param format    Image format.
 * @param data		Pointer to the pixel data assigned to image.
 * @return			void.
 */
void STM32Ipl_Init(image_t *img, uint32_t width, uint32_t height, image_bpp_t format, void *data)
{
	if (img) {
		img->w = width;
		img->h = height;
		img->bpp = format;
		img->data = data;
	}
}

/**
 * @brief Allocates a data memory buffer to contain the image pixels and consequently
 * initializes the given image structure. The size of such buffer depends on given
 * width, height and format. Assuming the input image data pointer is null to avoid
 * memory leakage. The caller is responsible of releasing the data memory buffer with STM32Ipl_ReleaseData().
 * @param img		Image; if it is not valid, an error is returned.
 * @param width		Image width.
 * @param height	Image height.
 * @param format	Image format.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_AllocData(image_t *img, uint32_t width, uint32_t height, image_bpp_t format)
{
	uint8_t *data;

	if (!img)
		return stm32ipl_err_InvalidParameter;

	data = xalloc(STM32Ipl_DataSize(width, height, format));
	if (!data) {
		STM32Ipl_Init(img, 0, 0, (image_bpp_t)0, 0);
		return stm32ipl_err_OutOfMemory;
	}

	img->w = width;
	img->h = height;
	img->bpp = format;
	img->data = data;

	return stm32ipl_err_Ok;
}

/**
 * @brief Allocates a data memory buffer to the destination image taking the source image as reference in terms of its resolution and format.
 * No data pixel is copied from the source image. Assuming the destination image data pointer is null to avoid memory leakage.
 * The caller is responsible of releasing the data memory buffer with STM32Ipl_ReleaseData().
 * @param src	Source image; if it is not valid, an error is returned. Its size and format are taken as reference for the allocation of the destination image data buffer.
 * @param dst	Destination image: it must point to a valid structure, otherwise an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_AllocDataRef(const image_t *src, image_t *dst)
{
	uint8_t *data;

	STM32IPL_CHECK_VALID_IMAGE(src)

	if (!dst)
		return stm32ipl_err_InvalidParameter;

	data = xalloc(STM32Ipl_DataSize(src->w, src->h, (image_bpp_t)src->bpp));
	if (!data) {
		STM32Ipl_Init(dst, 0, 0, (image_bpp_t)0, 0);
		return stm32ipl_err_OutOfMemory;
	}

	dst->w = src->w;
	dst->h = src->h;
	dst->bpp = src->bpp;
	dst->data = data;

	return stm32ipl_err_Ok;
}

/**
 * @brief Releases the data memory buffer of the image and resets the image structure.
 * @param img	Image.
 * @return		void.
 */
void STM32Ipl_ReleaseData(image_t *img)
{
	if (img) {
		xfree(img->data);
		STM32Ipl_Init(img, 0, 0, (image_bpp_t)0, 0);
	}
}

/**
 * @brief Returns the size of the data memory needed to store an image with the given properties.
 * The supported formats are Binary, Grayscale, RGB565, RGB888, Bayer.
 * @param width		Image width.
 * @param height	Image height.
 * @param format	Image format.
 * @return			Size of the image data buffer (bytes), 0 in case of wrong/unsupported arguments.
 */
uint32_t STM32Ipl_DataSize(uint32_t width, uint32_t height, image_bpp_t format)
{
	switch ((uint32_t)format) {
		case IMAGE_BPP_BINARY:
			return ((width + UINT32_T_MASK) >> UINT32_T_SHIFT) * height * sizeof(uint32_t);

		case IMAGE_BPP_GRAYSCALE:
			return width * height * sizeof(uint8_t);

		case IMAGE_BPP_RGB565:
			return width * height * sizeof(uint16_t);

		case IMAGE_BPP_BAYER:
			return width * height * sizeof(uint8_t);

		case IMAGE_BPP_RGB888:
			return width * height * 3;
	}

	return 0;
}

/**
 * @brief Returns the size (bytes) of the data buffer of an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888, Bayer.
 * @param img	Image.
 * @return		Size of the image data buffer (bytes), 0 in case of wrong/unsupported argument.
 */
uint32_t STM32Ipl_ImageDataSize(const image_t *img)
{
	return img ? STM32Ipl_DataSize(img->w, img->h, (image_bpp_t)img->bpp) : 0;
}

/**
 * @brief Checks if the image's format is among the provided formats.
 * @param img		Image.
 * @param formats	Supported formats.
 * @return			True if the image's format is among the provided formats, false otherwise.
 */
bool STM32Ipl_ImageFormatSupported(const image_t *img, uint32_t formats)
{
	stm32ipl_if_t format;

	switch (img->bpp) {
		case IMAGE_BPP_BINARY:
			format = stm32ipl_if_binary;
			break;

		case IMAGE_BPP_GRAYSCALE:
			format = stm32ipl_if_grayscale;
			break;

		case IMAGE_BPP_RGB565:
			format = stm32ipl_if_rgb565;
			break;

		case IMAGE_BPP_RGB888:
			format = stm32ipl_if_rgb888;
			break;

		default:
			return false;
	}

	return (format & formats);
}

/**
 * @brief Copies the source image into the destination one. Only the image structure is copied,
 * so beware the source image's data buffer will be shared with the destination image, as no new memory
 * buffer is allocated.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst   Destination image; if it is not valid, an error is returned. Assuming its data pointer
 * is null to avoid memory leakage.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Copy(const image_t *src, image_t *dst)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	if (!dst)
		return stm32ipl_err_InvalidParameter;

	memcpy(dst, src, sizeof(image_t));

	return stm32ipl_err_Ok;
}

/**
 * @brief Copies the source image's data buffer into the destination image's data buffer.
 * Only the pixel data is actually copied. Source and destination images must have same size and format.
 * The destination image data pointer must refer to a valid memory buffer as no new memory is allocated.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst   Destination image; if it is not valid, an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_CopyData(const image_t *src, image_t *dst)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_SAME_SIZE(src, dst)
	STM32IPL_CHECK_SAME_FORMAT(src, dst)

	memcpy(dst->data, src->data, STM32Ipl_ImageDataSize(dst));

	return stm32ipl_err_Ok;
}

/**
 * @brief Clones the source image into the destination one. If the destination image data pointer
 * is null, a new memory buffer is allocated, filled with the source pixel data and assigned to
 * the destination image. If the destination image data pointer points to a valid allocated buffer,
 * such buffer must have the right size to contain the source image. In case of success, the two
 * images will have same size, format and content.
 * @param src	Source image; if it is not valid, an error is returned.
 * @param dst   Destination image; if it is not valid, an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Clone(const image_t *src, image_t *dst)
{
	uint8_t *data;
	size_t size;

	STM32IPL_CHECK_VALID_IMAGE(src)
	if (!dst)
		return stm32ipl_err_InvalidParameter;

	size = STM32Ipl_ImageDataSize(src);

	if (dst->data) {
		STM32IPL_CHECK_SAME_SIZE(src, dst)
		STM32IPL_CHECK_SAME_FORMAT(src, dst)
	} else {
		data = xalloc(size);
		if (!data) {
			STM32Ipl_Init(dst, 0, 0, (image_bpp_t)0, 0);
			return stm32ipl_err_OutOfMemory;
		}

		dst->w = src->w;
		dst->h = src->h;
		dst->bpp = src->bpp;
		dst->data = data;
	}

	memcpy(dst->data, src->data, size);

	return stm32ipl_err_Ok;
}

/**
 * @brief Adapts a color (represented in the 0xRRGGBB format) to the format of an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image: if it is not valid, 0 is returned. color is adapted to the image's format.
 * @param color		Color value with 0xRRGGBB format.
 * @return			the color adapted to the image's format.
 */
uint32_t STM32Ipl_AdaptColor(const image_t *img, stm32ipl_color_t color)
{
	stm32ipl_color_t adaptedColor = 0;
	rgb888_t pixel;

	if (!img)
		return 0;

	pixel.r = (color >> 16) & 0xFF;
	pixel.g = (color >> 8) & 0xFF;
	pixel.b = color & 0xFF;

	switch (img->bpp) {
		case IMAGE_BPP_BINARY: {
			adaptedColor = COLOR_RGB888_TO_BINARY(pixel);
			break;
		}
		case IMAGE_BPP_GRAYSCALE: {
			adaptedColor = COLOR_RGB888_TO_GRAYSCALE(pixel);
			break;
		}
		case IMAGE_BPP_RGB565: {
			adaptedColor = COLOR_R8_G8_B8_TO_RGB565(pixel.r, pixel.g, pixel.b);
			break;
		}
		case IMAGE_BPP_RGB888: {
			adaptedColor = ((pixel.r << 16) | (pixel.g << 8) | (pixel.b));
			break;
		}
		default: {
			break;
		}
	}

	return adaptedColor;
}

#ifdef __cplusplus
}
#endif
