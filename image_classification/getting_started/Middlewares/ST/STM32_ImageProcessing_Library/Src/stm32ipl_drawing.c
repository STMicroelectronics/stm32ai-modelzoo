/**
 ******************************************************************************
 * @file   stm32ipl_drawing.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - drawing function header file
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

#ifdef STM32IPL_ENABLE_HW_SCREEN_DRAWING

#define STM32IPL_LCD_PIXELFORMAT		DMA2D_OUTPUT_ARGB8888

#ifdef USE_STM32H747I_DISCO
#include "stm32h7xx_hal.h"
#include "stm32h7xx_hal_dma2d.h"
#endif /* USE_STM32H747I_DISCO */

#ifdef __cplusplus
extern "C" {
#endif

	ALIGN_32BYTES(static const uint32_t l8Clut[256]) = {
		0x000000, 0x010101, 0x020202, 0x030303, 0x040404, 0x050505, 0x060606, 0x070707,
		0x080808, 0x090909, 0x0a0a0a, 0x0b0b0b, 0x0c0c0c, 0x0d0d0d, 0x0e0e0e, 0x0f0f0f,
		0x101010, 0x111111, 0x121212, 0x131313, 0x141414, 0x151515, 0x161616, 0x171717,
		0x181818, 0x191919, 0x1a1a1a, 0x1b1b1b, 0x1c1c1c, 0x1d1d1d, 0x1e1e1e, 0x1f1f1f,
		0x202020, 0x212121, 0x222222, 0x232323, 0x242424, 0x252525, 0x262626, 0x272727,
		0x282828, 0x292929, 0x2a2a2a, 0x2b2b2b, 0x2c2c2c, 0x2d2d2d, 0x2e2e2e, 0x2f2f2f,
		0x303030, 0x313131, 0x323232, 0x333333, 0x343434, 0x353535, 0x363636, 0x373737,
		0x383838, 0x393939, 0x3a3a3a, 0x3b3b3b, 0x3c3c3c, 0x3d3d3d, 0x3e3e3e, 0x3f3f3f,
		0x404040, 0x414141, 0x424242, 0x434343, 0x444444, 0x454545, 0x464646, 0x474747,
		0x484848, 0x494949, 0x4a4a4a, 0x4b4b4b, 0x4c4c4c, 0x4d4d4d, 0x4e4e4e, 0x4f4f4f,
		0x505050, 0x515151, 0x525252, 0x535353, 0x545454, 0x555555, 0x565656, 0x575757,
		0x585858, 0x595959, 0x5a5a5a, 0x5b5b5b, 0x5c5c5c, 0x5d5d5d, 0x5e5e5e, 0x5f5f5f,
		0x606060, 0x616161, 0x626262, 0x636363, 0x646464, 0x656565, 0x666666, 0x676767,
		0x686868, 0x696969, 0x6a6a6a, 0x6b6b6b, 0x6c6c6c, 0x6d6d6d, 0x6e6e6e, 0x6f6f6f,
		0x707070, 0x717171, 0x727272, 0x737373, 0x747474, 0x757575, 0x767676, 0x777777,
		0x787878, 0x797979, 0x7a7a7a, 0x7b7b7b, 0x7c7c7c, 0x7d7d7d, 0x7e7e7e, 0x7f7f7f,
		0x808080, 0x818181, 0x828282, 0x838383, 0x848484, 0x858585, 0x868686, 0x878787,
		0x888888, 0x898989, 0x8a8a8a, 0x8b8b8b, 0x8c8c8c, 0x8d8d8d, 0x8e8e8e, 0x8f8f8f,
		0x909090, 0x919191, 0x929292, 0x939393, 0x949494, 0x959595, 0x969696, 0x979797,
		0x989898, 0x999999, 0x9a9a9a, 0x9b9b9b, 0x9c9c9c, 0x9d9d9d, 0x9e9e9e, 0x9f9f9f,
		0xa0a0a0, 0xa1a1a1, 0xa2a2a2, 0xa3a3a3, 0xa4a4a4, 0xa5a5a5, 0xa6a6a6, 0xa7a7a7,
		0xa8a8a8, 0xa9a9a9, 0xaaaaaa, 0xababab, 0xacacac, 0xadadad, 0xaeaeae, 0xafafaf,
		0xb0b0b0, 0xb1b1b1, 0xb2b2b2, 0xb3b3b3, 0xb4b4b4, 0xb5b5b5, 0xb6b6b6, 0xb7b7b7,
		0xb8b8b8, 0xb9b9b9, 0xbababa, 0xbbbbbb, 0xbcbcbc, 0xbdbdbd, 0xbebebe, 0xbfbfbf,
		0xc0c0c0, 0xc1c1c1, 0xc2c2c2, 0xc3c3c3, 0xc4c4c4, 0xc5c5c5, 0xc6c6c6, 0xc7c7c7,
		0xc8c8c8, 0xc9c9c9, 0xcacaca, 0xcbcbcb, 0xcccccc, 0xcdcdcd, 0xcecece, 0xcfcfcf,
		0xd0d0d0, 0xd1d1d1, 0xd2d2d2, 0xd3d3d3, 0xd4d4d4, 0xd5d5d5, 0xd6d6d6, 0xd7d7d7,
		0xd8d8d8, 0xd9d9d9, 0xdadada, 0xdbdbdb, 0xdcdcdc, 0xdddddd, 0xdedede, 0xdfdfdf,
		0xe0e0e0, 0xe1e1e1, 0xe2e2e2, 0xe3e3e3, 0xe4e4e4, 0xe5e5e5, 0xe6e6e6, 0xe7e7e7,
		0xe8e8e8, 0xe9e9e9, 0xeaeaea, 0xebebeb, 0xececec, 0xededed, 0xeeeeee, 0xefefef,
		0xf0f0f0, 0xf1f1f1, 0xf2f2f2, 0xf3f3f3, 0xf4f4f4, 0xf5f5f5, 0xf6f6f6, 0xf7f7f7,
		0xf8f8f8, 0xf9f9f9, 0xfafafa, 0xfbfbfb, 0xfcfcfc, 0xfdfdfd, 0xfefefe, 0xffffff
	};

	/*
	 * Returns the DMA2D color format corresponding to the given image format.
	 * format	Image format.
	 * return	DMA2D color format.
	 */
static uint32_t getInputColorMode(uint32_t format)
{
	switch (format) {
		case IMAGE_BPP_BINARY:
			/* Binary format is not directly supported by the hardware,
			 * so the L8 format can be used instead, but a conversion
			 * will be needed within STM32Ipl_DrawScreen(). */
			return DMA2D_INPUT_L8;

		case IMAGE_BPP_GRAYSCALE:
			return DMA2D_INPUT_L8;

		case IMAGE_BPP_RGB565:
			return DMA2D_INPUT_RGB565;

		case IMAGE_BPP_BAYER:
			return 0xFFFFFFFF - 1; /* Not supported. */

		case IMAGE_BPP_RGB888:
			return DMA2D_INPUT_RGB888;

		case IMAGE_BPP_JPEG:
			return 0xFFFFFFFF - 1; /* Not supported. */

		default:
			return 0xFFFFFFFF - 1; /* Not supported. */
	};
}

/**
 * @brief Draws an image on the screen at the (x,y) coordinates using hardware acceleration (DMA2D).
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img	Image; if it is not valid, an error is returned.
 * @param x		Screen x-coordinate of the top-left corner of the image.
 * @param y		Screen y-coordinate of the top-left corner of the image.
 * @return 		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DrawScreen_DMA2D(const image_t *img, uint16_t x, uint16_t y)
{
	static DMA2D_HandleTypeDef hlcd_dma2d;
	uint32_t inputLineOffset = 0;
	uint32_t cssMode = DMA2D_NO_CSS;
	uint32_t saveBytesSwap;
	uint32_t bytesSwap = DMA2D_BYTES_REGULAR;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	saveBytesSwap = hlcd_dma2d.Init.BytesSwap;

	uint32_t destination = STM32IPL_LCD_FB_ADDR + (y * STM32IPL_LCD_WIDTH + x) * STM32IPL_LCD_BPP;
	uint32_t source = (uint32_t)img->data;

	hlcd_dma2d.Init.Mode = DMA2D_M2M_PFC;
	hlcd_dma2d.Init.ColorMode = STM32IPL_LCD_PIXELFORMAT;
	hlcd_dma2d.Init.OutputOffset = STM32IPL_LCD_WIDTH - img->w;
	hlcd_dma2d.Init.AlphaInverted = DMA2D_REGULAR_ALPHA;
	hlcd_dma2d.Init.RedBlueSwap = DMA2D_RB_REGULAR;
	hlcd_dma2d.Init.BytesSwap = bytesSwap;
	hlcd_dma2d.Init.LineOffsetMode = DMA2D_LOM_PIXELS;

	hlcd_dma2d.XferCpltCallback = NULL;
	hlcd_dma2d.XferErrorCallback = NULL;

	hlcd_dma2d.LayerCfg[DMA2D_FOREGROUND_LAYER].AlphaMode = DMA2D_REPLACE_ALPHA;
	hlcd_dma2d.LayerCfg[DMA2D_FOREGROUND_LAYER].InputAlpha = 0xFF;
	hlcd_dma2d.LayerCfg[DMA2D_FOREGROUND_LAYER].InputColorMode = getInputColorMode(img->bpp);
	hlcd_dma2d.LayerCfg[DMA2D_FOREGROUND_LAYER].InputOffset = inputLineOffset;
	hlcd_dma2d.LayerCfg[DMA2D_FOREGROUND_LAYER].AlphaInverted = DMA2D_REGULAR_ALPHA;
	hlcd_dma2d.LayerCfg[DMA2D_FOREGROUND_LAYER].RedBlueSwap = DMA2D_RB_REGULAR;
	hlcd_dma2d.LayerCfg[DMA2D_FOREGROUND_LAYER].ChromaSubSampling = cssMode;

	hlcd_dma2d.Instance = DMA2D;

	/* DMA2D initialization & starting. */
	HAL_DMA2D_DeInit(&hlcd_dma2d);
	if (HAL_DMA2D_Init(&hlcd_dma2d) == HAL_OK) {
		if (HAL_DMA2D_ConfigLayer(&hlcd_dma2d, DMA2D_FOREGROUND_LAYER) == HAL_OK) {
			if (img->bpp == IMAGE_BPP_GRAYSCALE || img->bpp == IMAGE_BPP_BINARY) {
				DMA2D_CLUTCfgTypeDef CLUTCfg;

				/* Load DMA2D foreground CLUT. */
				CLUTCfg.CLUTColorMode = DMA2D_CCM_ARGB8888;
				CLUTCfg.pCLUT = (uint32_t*)l8Clut;
				CLUTCfg.Size = 255;

				HAL_DMA2D_CLUTStartLoad(&hlcd_dma2d, &CLUTCfg, DMA2D_FOREGROUND_LAYER);
				HAL_DMA2D_PollForTransfer(&hlcd_dma2d, 30);
			}

			if (img->bpp == IMAGE_BPP_BINARY) {
				/* Binary format is not supported, so a conversion to L8 is needed. */
				source = (uint32_t)xalloc(img->w * img->h);
				if (source) {
					uint8_t *ptr = (uint8_t*)source;
					for (uint32_t i = 0; i < img->h; i++) {
						uint32_t *row = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR((image_t* )img, i);
						for (uint32_t j = 0; j < img->w; j++) {
							*ptr++ = (IMAGE_GET_BINARY_PIXEL_FAST(row, j) ? 0xFF : 0);
						}
					}
				} else
					return stm32ipl_err_OutOfMemory;
			}

			if (HAL_DMA2D_Start(&hlcd_dma2d, source, destination, img->w, img->h) == HAL_OK) {
				/* Polling for DMA transfer. */
				HAL_DMA2D_PollForTransfer(&hlcd_dma2d, 30);
			}

			if (img->bpp == IMAGE_BPP_BINARY)
				xfree((void*)source);
		}
	}

	/* Restore previous BytesSwap value. */
	hlcd_dma2d.Init.BytesSwap = saveBytesSwap;

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif

#else /* STM32IPL_ENABLE_HW_SCREEN_DRAWING */

#ifdef __cplusplus
extern "C" {
#endif

stm32ipl_err_t STM32Ipl_DrawScreen_DMA2D(const image_t *img, uint16_t x, uint16_t y)
{
	/* Prevent unused argument(s) compilation warning. */
	STM32IPL_UNUSED(img);
	STM32IPL_UNUSED(x);
	STM32IPL_UNUSED(y);

	/* Void implementation. */
	return stm32ipl_err_NotImplemented;
}

#ifdef __cplusplus
}
#endif

#endif /* STM32IPL_ENABLE_HW_SCREEN_DRAWING */

/**
 * @brief Sets the image pixels to zero.
 * The supported formats (for image and mask) are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param invert	If false and mask is not NULL, the image's pixels are set to 0 when the
 * corresponding mask's pixels are 1, otherwise are set to 0 when mask is not 1.
 * @param mask 		Optional image to be used as a pixel level mask for the operation. The mask must have the same resolution
 * as the source image. Only the source pixels that have the corresponding mask pixels set are considered.
 * The pointer to the mask can be null: in this case all the source image pixels are considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Zero(image_t *img, bool invert, const image_t *mask)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (mask) {
		STM32IPL_CHECK_VALID_IMAGE(mask)
		STM32IPL_CHECK_FORMAT(mask, STM32IPL_IF_ALL)
		STM32IPL_CHECK_SAME_SIZE(img, mask)

		imlib_zero(img, (image_t*)mask, invert);
	} else {
		memset(img->data, 0, STM32Ipl_ImageDataSize(img));
	}

	return stm32ipl_err_Ok;
}

/**
 * @brief Fills the image with the given color.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img	Image; if it is not valid, an error is returned.
 * @param roi	Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @param color	Color used to fill the image.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_Fill(image_t *img, const rectangle_t *roi, stm32ipl_color_t color)
{
	uint32_t newColor;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	newColor = STM32Ipl_AdaptColor(img, color);

	if (roi) {
		STM32IPL_CHECK_VALID_ROI(img, roi)

		for (uint32_t y = roi->y, yy = roi->y + roi->h; y < yy; y++) {
			for (uint32_t x = roi->x, xx = roi->x + roi->w; x < xx; x++) {
				imlib_set_pixel(img, x, y, newColor);
			}
		}
	} else {
		for (uint32_t y = 0, yy = img->h; y < yy; y++) {
			for (uint32_t x = 0, xx = img->w; x < xx; x++) {
				imlib_set_pixel(img, x, y, newColor);
			}
		}
	}

	return stm32ipl_err_Ok;
}

/**
 * @brief Draws a colored pixel over an image at location (x, y).
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param x			X-coordinate of the pixel.
 * @param y			Y-coordinate of the pixel.
 * @param color		Color value with 0xRRGGBB format.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DrawPixel(image_t *img, uint16_t x, uint16_t y, stm32ipl_color_t color)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	imlib_set_pixel(img, x, y, STM32Ipl_AdaptColor(img, color));

	return stm32ipl_err_Ok;
}

/**
 * @brief Draws a colored cross over an image at location (x, y).
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param x			X-coordinate of the center of the cross.
 * @param y			Y-coordinate of the center of the cross.
 * @param size		Lenght of the lines making the cross (pixels).
 * @param color		Color value with 0xRRGGBB format.
 * @param thickness	Thickness of the lines (pixels).
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DrawCross(image_t *img, uint16_t x, uint16_t y, uint16_t size, stm32ipl_color_t color,
		uint16_t thickness)
{
	uint32_t newColor;
	uint16_t halfSize = size >> 1;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	newColor = STM32Ipl_AdaptColor(img, color);

	imlib_draw_line(img, x - halfSize, y, x + halfSize, y, newColor, thickness);
	imlib_draw_line(img, x, y - halfSize, x, y + halfSize, newColor, thickness);

	return stm32ipl_err_Ok;
}

/**
 * @brief Draws a colored line over an image from point p0 to point p1.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param p0		Line star point.
 * @param p1		Line end point.
 * @param color		Color value with 0xRRGGBB format.
 * @param thickness	Thickness of the line (pixels).
 * @return 			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DrawLine(image_t *img, const point_t *p0, const point_t *p1, stm32ipl_color_t color, uint16_t thickness)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (!p0 || !p1)
		return stm32ipl_err_InvalidParameter;

	imlib_draw_line(img, p0->x, p0->y, p1->x, p1->y, STM32Ipl_AdaptColor(img, color), thickness);

	return stm32ipl_err_Ok;
}

/**
 * @brief Draws a colored polygon over an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param point		Vector of points.
 * @param nPoints	Number of points (vertexes of the polygon).
 * @param color		Color value with 0xRRGGBB format.
 * @param thickness	Thickness of the line (pixels).
 * @return 			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DrawPolygon(image_t *img, const point_t *point, uint32_t nPoints, stm32ipl_color_t color,
		uint16_t thickness)
{
	uint32_t newColor;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(point)

	newColor = STM32Ipl_AdaptColor(img, color);

	imlib_draw_line(img, point[0].x, point[0].y, point[nPoints - 1].x, point[nPoints - 1].y, newColor, thickness);

	for (uint16_t j = 0; j < nPoints - 1; j++)
		imlib_draw_line(img, point[j].x, point[j].y, point[j + 1].x, point[j + 1].y, newColor, thickness);

	return stm32ipl_err_Ok;
}

/**
 * @brief Draws a colored rectangle over an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param x			X-coordinate of the top-left corner of the rectangle.
 * @param y			Y-coordinate of the top-left corner of the rectangle.
 * @param width		Width of rectangle (pixels).
 * @param height	Height of rectangle (pixels).
 * @param color		Color value with 0xRRGGBB format.
 * @param thickness	Thickness of the lines (pixels).
 * @param fill		When true, the rectangle is filled, otherwise it is not.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DrawRectangle(image_t *img, uint16_t x, uint16_t y, uint16_t width, uint16_t height,
		stm32ipl_color_t color, uint16_t thickness, bool fill)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (width < 2 || height < 2)
		return stm32ipl_err_InvalidParameter;

	imlib_draw_rectangle(img, x, y, width, height, STM32Ipl_AdaptColor(img, color), thickness, fill);

	return stm32ipl_err_Ok;
}

/**
 * @brief Draws a colored circle over an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param cx		X-coordinate of the circle's center.
 * @param cy		Y-coordinate of the circle's center.
 * @param radius	Radius of the circle (pixels).
 * @param color		Color value with 0xRRGGBB format.
 * @param thickness	Thickness of the line (pixels).
 * @param fill		When true, the circle is filled, otherwise it is not.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DrawCircle(image_t *img, uint16_t cx, uint16_t cy, uint16_t radius, stm32ipl_color_t color,
		uint16_t thickness, bool fill)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	imlib_draw_circle(img, cx, cy, radius, STM32Ipl_AdaptColor(img, color), thickness, fill);

	return stm32ipl_err_Ok;
}

/**
 * @brief Draws a colored ellipse over an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param ellipse	Ellipse; if it is not valid, an error is returned.
 * @param color		Color value with 0xRRGGBB format.
 * @param thickness	Thickness of the line (pixels).
 * @param fill		When true, the ellipse is filled, otherwise it is not.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_DrawEllipse(image_t *img, const ellipse_t *ellipse, stm32ipl_color_t color, uint16_t thickness,
		bool fill)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_CHECK_VALID_PTR_ARG(ellipse)

	imlib_draw_ellipse(img, ellipse->center.x, ellipse->center.y, ellipse->radiusX, ellipse->radiusY, ellipse->rotation,
			STM32Ipl_AdaptColor(img, color), thickness, fill);

	return stm32ipl_err_Ok;
}
