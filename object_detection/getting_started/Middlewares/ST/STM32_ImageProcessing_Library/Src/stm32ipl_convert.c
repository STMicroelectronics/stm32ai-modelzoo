/**
 ******************************************************************************
 * @file   stm32ipl_convert.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - image convert module
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

extern const float xyz_table[256];

#ifdef __cplusplus
extern "C" {
#endif

/**
 * brief Copies the source image pixels to the destination image buffer.
 * The two buffers must have the same size.
 * Assuming the two given data pointers point to valid buffers.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * param src	 Source image data.
 * param dst     Destination image data.
 * param size	 Size (bytes) of the image buffer.
 * param reverse Forces the reversed processing (from the last to the first pixel).
 * return		 void.
 */
static void STM32Ipl_SimpleCopy(const uint8_t *src, uint8_t *dst, uint32_t size, bool reverse)
{
	if (reverse) {
		src += size;
		dst += size;
		for (uint32_t i = 0; i < size; i++)
			*dst-- = *src--;
	} else {
		for (uint32_t i = 0; i < size; i++)
			*dst++ = *src++;
	}
}

/**
 * brief Converts the source image pixels from Binary to Grayscale and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst   	 Destination image data buffer.
 * param width	 Width of the two images.
 * param height	 Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_BinaryToY8(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t *srcData = (uint32_t*)src;
	uint32_t srcRowLen = (width + UINT32_T_MASK) >> UINT32_T_SHIFT;

	if (reverse) {
		srcData += srcRowLen * (height - 1);
		dst += (width * height) - 1;
		for (uint32_t y = 0; y < height; y++) {
			for (int32_t x = width - 1; x >= 0; x--)
				*dst-- = COLOR_BINARY_TO_GRAYSCALE(IMAGE_GET_BINARY_PIXEL_FAST(srcData, x));

			srcData -= srcRowLen;
		}

	} else {
		for (uint32_t y = 0; y < height; y++) {
			for (uint32_t x = 0; x < width; x++)
				*dst++ = COLOR_BINARY_TO_GRAYSCALE(IMAGE_GET_BINARY_PIXEL_FAST(srcData, x));

			srcData += srcRowLen;
		}
	}
}

/**
 * brief Converts the source image pixels from Binary to RGB565 and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_BinaryToRGB565(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t *srcData = (uint32_t*)src;
	uint32_t srcRowLen = (width + UINT32_T_MASK) >> UINT32_T_SHIFT;
	uint16_t *dstData = (uint16_t*)dst;

	if (reverse) {
		srcData += srcRowLen * (height - 1);
		dstData += (width * height) - 1;
		for (uint32_t y = 0; y < height; y++) {
			for (int32_t x = width - 1; x >= 0; x--)
				*dstData-- = COLOR_BINARY_TO_RGB565(IMAGE_GET_BINARY_PIXEL_FAST(srcData, x));

			srcData -= srcRowLen;
		}
	} else {
		for (uint32_t y = 0; y < height; y++) {
			for (uint32_t x = 0; x < width; x++)
				*dstData++ = COLOR_BINARY_TO_RGB565(IMAGE_GET_BINARY_PIXEL_FAST(srcData, x));

			srcData += srcRowLen;
		}
	}
}

/**
 * brief Converts the source image pixels from Binary to RGB888 and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_BinaryToRGB888(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t *srcData = (uint32_t*)src;
	uint32_t srcRowLen = (width + UINT32_T_MASK) >> UINT32_T_SHIFT;

	if (reverse) {
		srcData += srcRowLen * (height - 1);
		dst += (width * height * 3) - 1;
		for (uint32_t y = 0; y < height; y++) {
			for (int32_t x = width - 1; x >= 0; x--) {
				uint8_t v = 0xFF * IMAGE_GET_BINARY_PIXEL_FAST(srcData, x);
				*dst-- = v;
				*dst-- = v;
				*dst-- = v;
			}
			srcData -= srcRowLen;
		}

	} else {
		for (uint32_t y = 0; y < height; y++) {
			for (uint32_t x = 0; x < width; x++) {
				uint8_t v = 0xFF * IMAGE_GET_BINARY_PIXEL_FAST(srcData, x);
				*dst++ = v;
				*dst++ = v;
				*dst++ = v;
			}

			srcData += srcRowLen;
		}
	}
}

/**
 * brief Converts the source image pixels from Grayscale to RGB565 and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_Y8ToBinary(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t *dstData = (uint32_t*)dst;
	uint32_t dstRowLen = (width + UINT32_T_MASK) >> UINT32_T_SHIFT;

	if (reverse) {
		src += (width * height) - 1;
		dstData += dstRowLen * (height - 1);

		for (uint32_t y = 0; y < height; y++) {
			for (int32_t x = width - 1; x >= 0; x--) {
				IMAGE_PUT_BINARY_PIXEL_FAST(dstData, x, COLOR_GRAYSCALE_TO_BINARY(*src));
				src--;
			}

			dstData -= dstRowLen;
		}

	} else {
		for (uint32_t y = 0; y < height; y++) {
			for (uint32_t x = 0; x < width; x++) {
				IMAGE_PUT_BINARY_PIXEL_FAST(dstData, x, COLOR_GRAYSCALE_TO_BINARY(*src));
				src++;
			}

			dstData += dstRowLen;
		}
	}
}

/**
 * brief Converts the source image pixels from Grayscale to RGB565 and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_Y8ToRGB565(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint16_t *dstData = (uint16_t*)dst;
	uint32_t size = width * height;

	if (reverse) {
		src += (width * height) - 1;
		dstData += (width * height) - 1;
		for (uint32_t i = 0; i < size; i++) {
			*dstData-- = COLOR_GRAYSCALE_TO_RGB565(*src);
			src--;
		}
	} else {
		for (uint32_t i = 0; i < size; i++) {
			*dstData++ = COLOR_GRAYSCALE_TO_RGB565(*src);
			src++;
		}
	}
}

/**
 * brief Converts the source image pixels from Grayscale to RGB888 and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_Y8ToRGB888(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t size = width * height;

	if (reverse) {
		src += (width * height) - 1;
		dst += (width * height * 3) - 1;
		for (uint32_t i = 0; i < size; i++) {
			uint8_t v = *src--;
			*dst-- = v;
			*dst-- = v;
			*dst-- = v;
		}
	} else {
		for (uint32_t i = 0; i < size; i++) {
			uint8_t v = *src++;
			*dst++ = v;
			*dst++ = v;
			*dst++ = v;
		}
	}
}

/**
 * brief Converts the source image pixels from RGB565 to Binary and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_RGB565ToBinary(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint16_t *srcData = (uint16_t*)src;
	uint32_t *dstData = (uint32_t*)dst;
	uint32_t dstRowLen = (width + UINT32_T_MASK) >> UINT32_T_SHIFT;

	if (reverse) {
		srcData += width * (height - 1);
		dstData += dstRowLen * (height - 1);
		for (uint32_t y = 0; y < height; y++) {
			for (int32_t x = width - 1; x >= 0; x--)
				IMAGE_PUT_BINARY_PIXEL_FAST(dstData, x, COLOR_RGB565_TO_BINARY(srcData[x]));

			srcData -= width;
			dstData -= dstRowLen;
		}
	} else {
		for (uint32_t y = 0; y < height; y++) {
			for (uint32_t x = 0; x < width; x++)
				IMAGE_PUT_BINARY_PIXEL_FAST(dstData, x, COLOR_RGB565_TO_BINARY(srcData[x]));

			srcData += width;
			dstData += dstRowLen;
		}
	}
}

/**
 * brief Converts the source image pixels from RGB565 to Grayscale and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_RGB565ToY8(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t size = width * height;
	uint16_t *srcData = (uint16_t*)src;

	if (reverse) {
		srcData += (width * height) - 1;
		dst += (width * height) - 1;
		for (uint32_t i = 0; i < size; i++) {
			*dst-- = COLOR_RGB565_TO_GRAYSCALE(*srcData);
			srcData--;
		}
	} else {
		for (uint32_t i = 0; i < size; i++) {
			*dst++ = COLOR_RGB565_TO_GRAYSCALE(*srcData);
			srcData++;
		}
	}
}

/**
 * brief Converts the source image pixels from RGB565 to RGB888 and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_RGB565ToRGB888(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t size = width * height;
	uint16_t *srcData = (uint16_t*)src;

	if (reverse) {
		srcData += (width * height) - 1;
		dst += (width * height * 3) - 1;
		for (uint32_t i = 0; i < size; i++) {
			uint16_t v = *srcData--;
			*dst-- = COLOR_RGB565_TO_R8(v);
			*dst-- = COLOR_RGB565_TO_G8(v);
			*dst-- = COLOR_RGB565_TO_B8(v);
		}
	} else {
		for (uint32_t i = 0; i < size; i++) {
			uint16_t v = *srcData++;
			*dst++ = COLOR_RGB565_TO_B8(v);
			*dst++ = COLOR_RGB565_TO_G8(v);
			*dst++ = COLOR_RGB565_TO_R8(v);
		}
	}
}

/**
 * brief Converts the source image pixels from RGB888 to Binary and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_RGB888ToBinary(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t *dstData = (uint32_t*)dst;
	uint32_t dstRowLen = (width + UINT32_T_MASK) >> UINT32_T_SHIFT;

	if (reverse) {
		rgb888_t *rgb888 = (rgb888_t*)(src + (width * height * 3) - 3);
		dstData += dstRowLen * (height - 1);
		for (uint32_t y = 0; y < height; y++) {
			for (int32_t x = width - 1; x >= 0; x--) {
				IMAGE_PUT_BINARY_PIXEL_FAST(dstData, x, COLOR_RGB888_TO_BINARY(*rgb888));
				rgb888--;
			}

			dstData -= dstRowLen;
		}
	} else {
		rgb888_t *rgb888 = (rgb888_t*)src;
		for (uint32_t y = 0; y < height; y++) {
			for (uint32_t x = 0; x < width; x++) {
				IMAGE_PUT_BINARY_PIXEL_FAST(dstData, x, COLOR_RGB888_TO_BINARY(*rgb888));
				rgb888++;
			}

			dstData += dstRowLen;
		}
	}
}

/**
 * brief Converts the source image pixels from RGB888 to Grayscale and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height  Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_RGB888ToY8(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t size = width * height;

	if (reverse) {
		src += (width * height * 3) - 1;
		dst += (width * height) - 1;
		for (uint32_t i = 0; i < size; i++) {
			uint8_t r = *src--;
			uint8_t g = *src--;
			uint8_t b = *src--;
			*dst-- = COLOR_RGB888_TO_Y(r, g, b);
		}
	} else {
		for (uint32_t i = 0; i < size; i++) {
			uint8_t b = *src++;
			uint8_t g = *src++;
			uint8_t r = *src++;
			*dst++ = COLOR_RGB888_TO_Y(r, g, b);
		}
	}
}

/**
 * brief Converts the source image pixels from RGB888 to RGB565 and stores the converted data to the destination buffer.
 * Assuming the two given data pointers point to valid buffers.
 * param src	 Source image data buffer.
 * param dst     Destination image data buffer.
 * param width	 Width of the two images.
 * param height	 Height of the two images.
 * param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * return		 void.
 */
static void STM32Ipl_RGB888ToRGB565(const uint8_t *src, uint8_t *dst, uint32_t width, uint32_t height, bool reverse)
{
	uint32_t size = width * height;
	uint16_t *dstData = (uint16_t*)dst;

	if (reverse) {
		src += (width * height * 3) - 1;
		dstData += (width * height) - 1;
		for (uint32_t i = 0; i < size; i++) {
			uint8_t r = *src--;
			uint8_t g = *src--;
			uint8_t b = *src--;
			*dstData-- = COLOR_R8_G8_B8_TO_RGB565(r, g, b);
		}
	} else {
		for (uint32_t i = 0; i < size; i++) {
			uint8_t b = *src++;
			uint8_t g = *src++;
			uint8_t r = *src++;
			*dstData++ = COLOR_R8_G8_B8_TO_RGB565(r, g, b);
		}
	}
}

/**
 * @brief Converts the source image data to the format of the destination image and stores the
 * converted data to the destination buffer. The two images must have the same resolution.
 * The destination image data buffer must be already allocated and must have the right size to
 * contain the converted image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src	  Source image.
 * @param dst	  Destination image.
 * @param reverse If true, the processing is executed in reverse mode (from the last to the first pixel),
 * otherwise it is executed normally (from the first to the last pixel).
 * @return		  stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_ConvertRev(const image_t *src, image_t *dst, bool reverse)
{
	STM32IPL_CHECK_VALID_IMAGE(src)
	STM32IPL_CHECK_VALID_IMAGE(dst)
	STM32IPL_CHECK_FORMAT(src, STM32IPL_IF_ALL)
	STM32IPL_CHECK_FORMAT(dst, STM32IPL_IF_ALL)
	STM32IPL_CHECK_SAME_SIZE(src, dst)

	if (src->data == dst->data)
		return stm32ipl_err_InvalidParameter;

	switch (src->bpp) {
		case IMAGE_BPP_BINARY:
			switch (dst->bpp) {
				case IMAGE_BPP_BINARY:
					STM32Ipl_SimpleCopy(src->data, dst->data, STM32Ipl_ImageDataSize(dst), reverse);
					break;

				case IMAGE_BPP_GRAYSCALE:
					STM32Ipl_BinaryToY8(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_RGB565:
					STM32Ipl_BinaryToRGB565(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_RGB888:
					STM32Ipl_BinaryToRGB888(src->data, dst->data, src->w, src->h, reverse);
					break;

				default:
					return stm32ipl_err_UnsupportedFormat;
			}
			break;

		case IMAGE_BPP_GRAYSCALE:
			switch (dst->bpp) {
				case IMAGE_BPP_BINARY:
					STM32Ipl_Y8ToBinary(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_GRAYSCALE:
					STM32Ipl_SimpleCopy(src->data, dst->data, STM32Ipl_ImageDataSize(dst), reverse);
					break;

				case IMAGE_BPP_RGB565:
					STM32Ipl_Y8ToRGB565(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_RGB888:
					STM32Ipl_Y8ToRGB888(src->data, dst->data, src->w, src->h, reverse);
					break;

				default:
					return stm32ipl_err_UnsupportedFormat;
			}
			break;

		case IMAGE_BPP_RGB565: {
			switch (dst->bpp) {
				case IMAGE_BPP_BINARY:
					STM32Ipl_RGB565ToBinary(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_GRAYSCALE:
					STM32Ipl_RGB565ToY8(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_RGB565:
					STM32Ipl_SimpleCopy(src->data, dst->data, STM32Ipl_ImageDataSize(dst), reverse);
					break;

				case IMAGE_BPP_RGB888:
					STM32Ipl_RGB565ToRGB888(src->data, dst->data, src->w, src->h, reverse);
					break;

				default:
					return stm32ipl_err_UnsupportedFormat;
			}
			break;
		}

		case IMAGE_BPP_RGB888: {
			switch (dst->bpp) {
				case IMAGE_BPP_BINARY:
					STM32Ipl_RGB888ToBinary(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_GRAYSCALE:
					STM32Ipl_RGB888ToY8(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_RGB565:
					STM32Ipl_RGB888ToRGB565(src->data, dst->data, src->w, src->h, reverse);
					break;

				case IMAGE_BPP_RGB888:
					STM32Ipl_SimpleCopy(src->data, dst->data, STM32Ipl_ImageDataSize(dst), reverse);
					break;

				default:
					return stm32ipl_err_UnsupportedFormat;
			}
			break;
		}

		default:
			return stm32ipl_err_UnsupportedFormat;
	}

	return stm32ipl_err_Ok;
}

/**
 * @brief Converts the source image data to the format of the destination image and stores the
 * converted data to the destination buffer. The two images must have the same resolution.
 * The destination image data buffer must be already allocated and must have the right size to
 * contain the converted image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param src	  Source image; if it is not valid, an error is returned.
 * @param dst	  Destination image; if it is not valid, an error is returned.
 * @return		  stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Convert(const image_t *src, image_t *dst)
{
	return STM32Ipl_ConvertRev(src, dst, false);
}

/**
 * @brief Converts a RGB565 pixel value to an L value of L*A*B* color space.
 * @param pixel	  RGB565 pixel value.
 * @return		  The converted value.
 */
int8_t STM32Ipl_RGB565ToL(uint16_t pixel)
{
	return imlib_rgb565_to_l(pixel);
}

/**
 * @brief Converts a RGB565 pixel value to an A value of L*A*B* color space.
 * @param pixel	  RGB565 pixel value.
 * @return		  The converted value.
 */
int8_t STM32Ipl_RGB565ToA(uint16_t pixel)
{
	return imlib_rgb565_to_a(pixel);
}

/**
 * @brief Converts a RGB565 pixel value to an B value of L*A*B* color space.
 * @param pixel	  RGB565 pixel value.
 * @return		  The converted value.
 */
int8_t STM32Ipl_RGB565ToB(uint16_t pixel)
{
	return imlib_rgb565_to_b(pixel);
}

/**
 * @brief Converts a RGB888 pixel value to an L value of L*A*B* color space.
 * @param pixel	  RGB888 pixel value.
 * @return		  The converted value.
 */
int8_t STM32Ipl_RGB888ToL(rgb888_t pixel)
{
	return imlib_rgb888_to_l(pixel);
}

/**
 * @brief Converts a RGB888 pixel value to an A value of L*A*B* color space.
 * @param pixel	  RGB888 pixel value.
 * @return		  The converted value.
 */
int8_t STM32Ipl_RGB888ToA(rgb888_t pixel)
{
	return imlib_rgb888_to_a(pixel);
}

/**
 * @brief Converts a RGB888 pixel value to an B value of L*A*B* color space.
 * @param pixel	  RGB888 pixel value.
 * @return		  The converted value.
 */
int8_t STM32Ipl_RGB888ToB(rgb888_t pixel)
{
	return imlib_rgb888_to_b(pixel);
}

/**
 * @brief Converts a L*A*B* pixel value to an RGB888 value.
 * @param l	  L component of the pixel value.
 * @param a	  A component of the pixel value.
 * @param b	  B component of the pixel value.
 * @return	  The converted value.
 */
rgb888_t STM32Ipl_LABToRGB888(uint8_t l, int8_t a, int8_t b)
{
	return imlib_lab_to_rgb888(l, a, b);
}

/**
 * @brief Converts a L*A*B* pixel value to an RGB565 value.
 * @param l	  L component of the pixel value.
 * @param a	  A component of the pixel value.
 * @param b	  B component of the pixel value.
 * @return	  The converted value.
 */
uint16_t STM32Ipl_LABToRGB565(uint8_t l, int8_t a, int8_t b)
{
	return imlib_lab_to_rgb(l, a, b);
}

/**
 * @brief Converts a YCbCr pixel value to an RGB565 value.
 * @param y	  Y component of the pixel value.
 * @param u	  Cb component of the pixel value.
 * @param v	  Cr component of the pixel value.
 * @return	  The converted value.
 */
uint16_t STM32Ipl_YUVToRGB565(uint8_t y, int8_t u, int8_t v)
{
	return imlib_yuv_to_rgb(y, u, v);
}

/**
 * @brief Converts a YCbCr pixel value to an RGB888 value.
 * @param y	  Y component of the pixel value.
 * @param u	  Cb component of the pixel value.
 * @param v	  Cr component of the pixel value.
 * @return	  The converted value.
 */
rgb888_t STM32Ipl_YUVToRGB888(uint8_t y, int8_t u, int8_t v)
{
	return imlib_yuv_to_rgb888(y, u, v);
}

#ifdef __cplusplus
}
#endif
