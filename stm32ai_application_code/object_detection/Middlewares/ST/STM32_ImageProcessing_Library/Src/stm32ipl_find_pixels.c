/**
 ******************************************************************************
 * @file   stm32ipl_find_pixels.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - find pixels module
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
 * @brief Gets the value of a pixel in an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img	Image; if it is not valid, an error is returned.
 * @param x 	X-coordinate of the pixel.
 * @param y 	Y-coordinate of the pixrl.
 * @param p 	Value of the pixel.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetPixel(const image_t *img, uint16_t x, uint16_t y, stm32ipl_color_t *p)
{
	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if ((x >= img->w) && (y >= img->h))
		return stm32ipl_err_InvalidParameter;

	switch (img->bpp) {
		case IMAGE_BPP_BINARY: {
			*p = (stm32ipl_color_t)IMAGE_GET_BINARY_PIXEL(img, x, y);
			break;
		}

		case IMAGE_BPP_GRAYSCALE: {
			*p = (stm32ipl_color_t)IMAGE_GET_GRAYSCALE_PIXEL(img, x, y);
			break;
		}

		case IMAGE_BPP_RGB565: {
			*p = (stm32ipl_color_t)IMAGE_GET_RGB565_PIXEL(img, x, y);
			break;
		}

		case IMAGE_BPP_RGB888: {
			rgb888_t pixel888;
			pixel888 = IMAGE_GET_RGB888_PIXEL(img, x, y);
			*p = (stm32ipl_color_t)((pixel888.r << 16) | (pixel888.g << 8) | (pixel888.b));
			break;
		}

		default: {
			return stm32ipl_err_InvalidParameter;
		}
	}

	return stm32ipl_err_Ok;
}

/**
 * @brief Finds minimum and maximum point locations in an image. For RGB images, the Y value is considered.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param outMin	List of point_t elements that represents the coordinates of the minimum values;
 * if it is not valid, an error is returned.
 * @param outMax	List of point_t elements that represents the coordinates of maximum values;
 * if it is not valid, an error is returned.
 * @param roi		Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_FindMinMaxLoc(const image_t *img, list_t *outMin, list_t *outMax, const rectangle_t *roi)
{
	rectangle_t realRoi;
	point_t p;
	uint32_t max;
	uint32_t min;
	uint32_t i;
	uint32_t j;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	if (!outMin || !outMax)
		return stm32ipl_err_InvalidParameter;

	max = 0;
	min = 0xFFFFFFFF;
	i = 0;
	j = 0;

	p.x = realRoi.x;
	p.y = realRoi.y;

	list_push_front(outMin, &p);
	list_push_front(outMax, &p);

	switch (img->bpp) {
		case IMAGE_BPP_BINARY: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				uint32_t *row_ptr = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					uint32_t value = IMAGE_GET_BINARY_PIXEL_FAST(row_ptr, x);
					if (value < min) {
						min = value;
						list_clear(outMin);
						i = 0;
						p.x = x;
						p.y = y;
						list_insert(outMin, &p, i);

						if (outMin->size == i) {
							list_clear(outMin);
							list_clear(outMax);
							return stm32ipl_err_OutOfMemory;
						}

						i++;
					} else
						if (value == min) {
							p.x = x;
							p.y = y;
							list_insert(outMin, &p, i);

							if (outMin->size == i) {
								list_clear(outMin);
								list_clear(outMax);
								return stm32ipl_err_OutOfMemory;
							}

							i++;
						}

					if (value > max) {
						max = value;
						list_clear(outMax);
						j = 0;
						p.x = x;
						p.y = y;
						list_insert(outMax, &p, j);

						if (outMax->size == j) {
							list_clear(outMax);
							list_clear(outMin);
							return stm32ipl_err_OutOfMemory;
						}

						j++;

					} else
						if (value == max) {
							p.x = x;
							p.y = y;
							list_insert(outMax, &p, j);

							if (outMax->size == j) {
								list_clear(outMax);
								list_clear(outMin);
								return stm32ipl_err_OutOfMemory;
							}

							j++;

						}
				}
			}
			break;
		}

		case IMAGE_BPP_GRAYSCALE: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				uint8_t *row_ptr = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					uint8_t value = IMAGE_GET_GRAYSCALE_PIXEL_FAST(row_ptr, x);

					if (value < min) {
						min = value;
						list_clear(outMin);
						i = 0;
						p.x = x;
						p.y = y;
						list_insert(outMin, &p, i);

						if (outMin->size == i) {
							list_clear(outMin);
							list_clear(outMax);
							return stm32ipl_err_OutOfMemory;
						}

						i++;
					} else
						if (value == min) {
							p.x = x;
							p.y = y;
							list_insert(outMin, &p, i);

							if (outMin->size == i) {
								list_clear(outMin);
								list_clear(outMax);
								return stm32ipl_err_OutOfMemory;
							}

							i++;
						}

					if (value > max) {
						max = value;
						list_clear(outMax);
						j = 0;
						p.x = x;
						p.y = y;
						list_insert(outMax, &p, j);

						if (outMax->size == j) {
							list_clear(outMax);
							list_clear(outMin);
							return stm32ipl_err_OutOfMemory;
						}

						j++;
					} else
						if (value == max) {
							p.x = x;
							p.y = y;
							list_insert(outMax, &p, j);

							if (outMax->size == j) {
								list_clear(outMax);
								list_clear(outMin);
								return stm32ipl_err_OutOfMemory;
							}

							j++;
						}
				}
			}
			break;
		}

		case IMAGE_BPP_RGB565: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				uint16_t *row_ptr = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					uint8_t value = COLOR_RGB565_TO_GRAYSCALE(IMAGE_GET_RGB565_PIXEL_FAST(row_ptr, x));
					if (value < min) {
						min = value;
						list_clear(outMin);
						i = 0;
						p.x = x;
						p.y = y;
						list_insert(outMin, &p, i);

						if (outMin->size == i) {
							list_clear(outMin);
							list_clear(outMax);
							return stm32ipl_err_OutOfMemory;
						}

						i++;
					} else
						if (value == min) {
							p.x = x;
							p.y = y;
							list_insert(outMin, &p, i);

							if (outMin->size == i) {
								list_clear(outMin);
								list_clear(outMax);
								return stm32ipl_err_OutOfMemory;
							}

							i++;
						}

					if (value > max) {
						max = value;
						list_clear(outMax);
						j = 0;
						p.x = x;
						p.y = y;
						list_insert(outMax, &p, j);

						if (outMax->size == j) {
							list_clear(outMax);
							list_clear(outMin);
							return stm32ipl_err_OutOfMemory;
						}

						j++;
					} else
						if (value == max) {
							p.x = x;
							p.y = y;
							list_insert(outMax, &p, j);

							if (outMax->size == j) {
								list_clear(outMax);
								list_clear(outMin);
								return stm32ipl_err_OutOfMemory;
							}

							j++;
						}
				}
			}
			break;
		}

		case IMAGE_BPP_RGB888: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				rgb888_t *row_ptr = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					uint8_t value = COLOR_RGB888_TO_GRAYSCALE(IMAGE_GET_RGB888_PIXEL_FAST(row_ptr, x));
					if (value < min) {
						min = value;
						list_clear(outMin);
						i = 0;
						p.x = x;
						p.y = y;
						list_insert(outMin, &p, i);

						if (outMin->size == i) {
							list_clear(outMin);
							list_clear(outMax);
							return stm32ipl_err_OutOfMemory;
						}

						i++;
					} else {
						if (value == min) {
							p.x = x;
							p.y = y;
							list_insert(outMin, &p, i);

							if (outMin->size == i) {
								list_clear(outMin);
								list_clear(outMax);
								return stm32ipl_err_OutOfMemory;
							}

							i++;
						}

						if (value > max) {
							max = value;
							list_clear(outMax);
							j = 0;
							p.x = x;
							p.y = y;
							list_insert(outMax, &p, j);

							if (outMax->size == j) {
								list_clear(outMax);
								list_clear(outMin);
								return stm32ipl_err_OutOfMemory;
							}

							j++;

						} else
							if (value == max) {

								p.x = x;
								p.y = y;
								list_insert(outMax, &p, j);

								if (outMax->size == j) {
									list_clear(outMax);
									list_clear(outMin);
									return stm32ipl_err_OutOfMemory;
								}

								j++;

							}
					}
				}
			}
			break;
		}

		default:
			return stm32ipl_err_InvalidParameter;
	}

	return stm32ipl_err_Ok;
}

/**
 * @brief Finds the locations of non zero pixels in an image.
 * The supported formats are Binary, Grayscale, RGB565, RGB888.
 * @param img		Image; if it is not valid, an error is returned.
 * @param out		List of point_t elements that represents the coordinates of the non zero pixels;
 * if it is not valid, an error is returned.
 * @param roi		Optional region of interest of the source image where the functions operates;
 * when defined, it must be contained in the source image and have positive dimensions, otherwise
 * an error is returned; when not defined, the whole image is considered.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_FindNonZeroLoc(const image_t *img, list_t *out, const rectangle_t *roi)
{
	rectangle_t realRoi;
	point_t p;
	uint32_t i;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)
	STM32IPL_GET_REAL_ROI(img, roi, &realRoi)

	if (!out)
		return stm32ipl_err_InvalidParameter;

	i = 0;

	switch (img->bpp) {
		case IMAGE_BPP_BINARY: {
			for (int y = realRoi.y, yy = realRoi.y + realRoi.h; y < yy; y++) {
				uint32_t *row_ptr = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, y);
				for (int x = realRoi.x, xx = realRoi.x + realRoi.w; x < xx; x++) {
					if (IMAGE_GET_BINARY_PIXEL_FAST(row_ptr, x) > 0) {
						p.x = x;
						p.y = y;
						list_insert(out, &p, i);

						if (out->size == i) {
							list_clear(out);
							return stm32ipl_err_OutOfMemory;
						}

						i++;
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
						p.x = x;
						p.y = y;

						list_insert(out, &p, i);

						if (out->size == i) {
							list_clear(out);
							return stm32ipl_err_OutOfMemory;
						}

						i++;
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
						p.x = x;
						p.y = y;
						list_insert(out, &p, i);

						if (out->size == i) {
							list_clear(out);
							return stm32ipl_err_OutOfMemory;
						}

						i++;
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

						p.x = x;
						p.y = y;
						list_insert(out, &p, i);

						if (out->size == i) {
							list_clear(out);
							return stm32ipl_err_OutOfMemory;
						}

						i++;
					}
				}
			}
			break;
		}
		default:
			return stm32ipl_err_InvalidParameter;
	}

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
