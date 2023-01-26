/**
 ******************************************************************************
 * @file   stm32ipl_warping.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - warping module
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.
 *
 * Portions of this file are part of the OpenMV project.
 *
 * Copyright (c) 2013-2019 Ibrahim Abdelkader <iabdalkader@openmv.io>
 * Copyright (c) 2013-2019 Kwabena W. Agyeman <kwagyeman@openmv.io>
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#include "stm32ipl.h"
#include "stm32ipl_imlib_int.h"
#include "matd.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Calculates the affine transformation matrix from three pairs of corresponding
 * source and destination points.
 * @param src 		Vector of three source points (coordinates of triangle vertices);
 * it must be valid, otherwise an error is returned.
 * @param dst		Vector of three destination points (coordinates of triangle vertices);
 * ; it must be valid, otherwise an error is returned.
 * @param affine	Vector of six numbers representing the 2×3 affine transformation matrix;
 * it must be valid, otherwise an error is returned. The first 3 elements correspond to the
 * the first line of the matrix, while the last 3 elements correspond to the second line.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_GetAffineTransform(const point_t *src, const point_t *dst, float *affine)
{
	float a[6 * 6];
	float b[6];
	matd_t *A;
	matd_t *B;
	matd_t *M;

	if (!src || !dst || !affine)
		return stm32ipl_err_InvalidParameter;

	A = matd_create(6, 6);
	B = matd_create(6, 1);

	for (uint8_t i = 0; i < 3; i++) {
		uint8_t j;
		uint8_t k;
		j = i * 12;
		k = j + 6;
		a[j] = a[k + 3] = src[i].x;
		a[j + 1] = a[k + 4] = src[i].y;
		a[j + 2] = a[k + 5] = 1;
		a[j + 3] = a[j + 4] = a[j + 5] = 0;
		a[k] = a[k + 1] = a[k + 2] = 0;
		b[i * 2] = dst[i].x;
		b[i * 2 + 1] = dst[i].y;
	}

	for (int i = 0; i < 6; i++)
		for (int j = 0; j < 6; j++) {
			MATD_EL(A, i, j)= a[i * 6 + j];
		}

	for (int i = 0; i < 6; i++)
		for (int j = 0; j < 1; j++) {
			MATD_EL(B, i, j)= b[i];
		}

	M = matd_solve(A, B);

	for (int i = 0; i < 6; i++) {
		affine[i] = MATD_EL(M, i, 0);
	}

	matd_destroy(M);
	matd_destroy(B);
	matd_destroy(A);

	return stm32ipl_err_Ok;
}

/**
 * @brief Applies an affine transformation matrix to an image. The content of the provided image
 * is overwritten with the result of the transformation.
 * The supported formats are (Binary, Grayscale, RGB565, RGB888).
 * @param img		Image; it must be valid, otherwise an error is returned.
 * @param affine	Vector of six numbers representing the 2×3 affine transformation matrix;
 * it must be valid, otherwise an error is returned. The first 3 elements correspond to the
 * the first line of the matrix, while the last 3 elements correspond to the second line.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_WarpAffine(image_t *img, const float *affine)
{
	stm32ipl_err_t res;
	uint32_t h;
	uint32_t w;
	float p[9];
	image_t aux;
	matd_t *T3;
	matd_t *T4;

	STM32IPL_CHECK_VALID_IMAGE(img)
	STM32IPL_CHECK_FORMAT(img, STM32IPL_IF_ALL)

	if (!affine)
		return stm32ipl_err_InvalidParameter;

	h = img->h;
	w = img->w;

	/* Create a temporary copy of the image to pull pixels from. */
	STM32Ipl_Init(&aux, 0, 0, (image_bpp_t)0, 0);
	res = STM32Ipl_Clone(img, &aux);
	if (res)
		return res;

	/* Clear the image. */
	memset(img->data, 0, STM32Ipl_ImageDataSize(img));

	for (uint8_t i = 0; i < 6; i++) {
		p[i] = affine[i];
	}

	p[6] = 0;
	p[7] = 0;
	p[8] = 1;

	T3 = matd_create_data(3, 3, p);
	T4 = matd_inverse(T3);

	if (T4) {
		float T4_00 = MATD_EL(T4, 0, 0), T4_01 = MATD_EL(T4, 0, 1), T4_02 = MATD_EL(T4, 0, 2);
		float T4_10 = MATD_EL(T4, 1, 0), T4_11 = MATD_EL(T4, 1, 1), T4_12 = MATD_EL(T4, 1, 2);
		float T4_20 = MATD_EL(T4, 2, 0), T4_21 = MATD_EL(T4, 2, 1), T4_22 = MATD_EL(T4, 2, 2);

		if ((fast_fabsf(T4_20) < MATD_EPS) && (fast_fabsf(T4_21) < MATD_EPS)) { /* Warp affine. */
			T4_00 /= T4_22;
			T4_01 /= T4_22;
			T4_02 /= T4_22;
			T4_10 /= T4_22;
			T4_11 /= T4_22;
			T4_12 /= T4_22;

			switch (img->bpp) {
				case IMAGE_BPP_BINARY: {
					uint32_t *tmp = (uint32_t*)(aux.data);

					for (uint32_t y = 0, yy = h; y < yy; y++) {
						uint32_t *row_ptr = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, y);
						for (uint32_t x = 0, xx = w; x < xx; x++) {
							int32_t sourceX = fast_roundf(T4_00 * x + T4_01 * y + T4_02);
							int32_t sourceY = fast_roundf(T4_10 * x + T4_11 * y + T4_12);

							if ((0 <= sourceX) && (sourceX < w) && (0 <= sourceY) && (sourceY < h)) {
								uint32_t *ptr = tmp + (((w + UINT32_T_MASK) >> UINT32_T_SHIFT) * sourceY);
								uint32_t pixel = IMAGE_GET_BINARY_PIXEL_FAST(ptr, sourceX);
								IMAGE_PUT_BINARY_PIXEL_FAST(row_ptr, x, pixel);
							}
						}
					}
					break;
				}
				case IMAGE_BPP_GRAYSCALE: {
					uint8_t *tmp = (uint8_t*)(aux.data);

					for (uint32_t y = 0, yy = h; y < yy; y++) {
						uint8_t *row_ptr = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, y);
						for (uint32_t x = 0, xx = w; x < xx; x++) {
							int32_t sourceX = fast_roundf(T4_00 * x + T4_01 * y + T4_02);
							int32_t sourceY = fast_roundf(T4_10 * x + T4_11 * y + T4_12);

							if ((0 <= sourceX) && (sourceX < w) && (0 <= sourceY) && (sourceY < h)) {
								uint8_t *ptr = tmp + (w * sourceY);
								uint8_t pixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(ptr, sourceX);
								IMAGE_PUT_GRAYSCALE_PIXEL_FAST(row_ptr, x, pixel);
							}
						}
					}
					break;
				}
				case IMAGE_BPP_RGB565: {
					uint16_t *tmp = (uint16_t*)(aux.data);

					for (uint32_t y = 0, yy = h; y < yy; y++) {
						uint16_t *row_ptr = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, y);
						for (uint32_t x = 0, xx = w; x < xx; x++) {
							int32_t sourceX = fast_roundf(T4_00 * x + T4_01 * y + T4_02);
							int32_t sourceY = fast_roundf(T4_10 * x + T4_11 * y + T4_12);

							if ((0 <= sourceX) && (sourceX < w) && (0 <= sourceY) && (sourceY < h)) {
								uint16_t *ptr = tmp + (w * sourceY);
								uint16_t pixel = IMAGE_GET_RGB565_PIXEL_FAST(ptr, sourceX);
								IMAGE_PUT_RGB565_PIXEL_FAST(row_ptr, x, pixel);
							}
						}
					}
					break;
				}

				case IMAGE_BPP_RGB888: {
					rgb888_t *tmp = (rgb888_t*)(aux.data);

					for (uint32_t y = 0, yy = h; y < yy; y++) {
						rgb888_t *row_ptr = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, y);
						for (uint32_t x = 0, xx = w; x < xx; x++) {
							int32_t sourceX = fast_roundf(T4_00 * x + T4_01 * y + T4_02);
							int32_t sourceY = fast_roundf(T4_10 * x + T4_11 * y + T4_12);

							if ((0 <= sourceX) && (sourceX < w) && (0 <= sourceY) && (sourceY < h)) {
								rgb888_t *ptr = tmp + (w * sourceY);
								rgb888_t pixel = IMAGE_GET_RGB888_PIXEL_FAST(ptr, sourceX);
								IMAGE_PUT_RGB888_PIXEL_FAST(row_ptr, x, pixel);
							}
						}
					}
					break;
				}

				default: {
					break;
				}
			}
		} else { /* Warp perspective. */
			switch (img->bpp) {
				case IMAGE_BPP_BINARY: {
					uint32_t *tmp = (uint32_t*)(aux.data);

					for (uint32_t y = 0, yy = h; y < yy; y++) {
						uint32_t *row_ptr = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, y);
						for (uint32_t x = 0, xx = w; x < xx; x++) {
							float xxx = T4_00 * x + T4_01 * y + T4_02;
							float yyy = T4_10 * x + T4_11 * y + T4_12;
							float zzz = T4_20 * x + T4_21 * y + T4_22;
							int32_t sourceX = fast_roundf(xxx / zzz);
							int32_t sourceY = fast_roundf(yyy / zzz);

							if ((0 <= sourceX) && (sourceX < w) && (0 <= sourceY) && (sourceY < h)) {
								uint32_t *ptr = tmp + (((w + UINT32_T_MASK) >> UINT32_T_SHIFT) * sourceY);
								uint32_t pixel = IMAGE_GET_BINARY_PIXEL_FAST(ptr, sourceX);
								IMAGE_PUT_BINARY_PIXEL_FAST(row_ptr, x, pixel);
							}
						}
					}
					break;
				}
				case IMAGE_BPP_GRAYSCALE: {
					uint8_t *tmp = (uint8_t*)(aux.data);

					for (uint32_t y = 0, yy = h; y < yy; y++) {
						uint8_t *row_ptr = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, y);
						for (uint32_t x = 0, xx = w; x < xx; x++) {
							float xxx = T4_00 * x + T4_01 * y + T4_02;
							float yyy = T4_10 * x + T4_11 * y + T4_12;
							float zzz = T4_20 * x + T4_21 * y + T4_22;
							int32_t sourceX = fast_roundf(xxx / zzz);
							int32_t sourceY = fast_roundf(yyy / zzz);

							if ((0 <= sourceX) && (sourceX < w) && (0 <= sourceY) && (sourceY < h)) {
								uint8_t *ptr = tmp + (w * sourceY);
								uint8_t pixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(ptr, sourceX);
								IMAGE_PUT_GRAYSCALE_PIXEL_FAST(row_ptr, x, pixel);
							}
						}
					}
					break;
				}
				case IMAGE_BPP_RGB565: {
					uint16_t *tmp = (uint16_t*)(aux.data);

					for (uint32_t y = 0, yy = h; y < yy; y++) {
						uint16_t *row_ptr = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, y);
						for (uint32_t x = 0, xx = w; x < xx; x++) {
							float xxx = T4_00 * x + T4_01 * y + T4_02;
							float yyy = T4_10 * x + T4_11 * y + T4_12;
							float zzz = T4_20 * x + T4_21 * y + T4_22;
							int32_t sourceX = fast_roundf(xxx / zzz);
							int32_t sourceY = fast_roundf(yyy / zzz);

							if ((0 <= sourceX) && (sourceX < w) && (0 <= sourceY) && (sourceY < h)) {
								uint16_t *ptr = tmp + (w * sourceY);
								uint16_t pixel = IMAGE_GET_RGB565_PIXEL_FAST(ptr, sourceX);
								IMAGE_PUT_RGB565_PIXEL_FAST(row_ptr, x, pixel);
							}
						}
					}
					break;
				}

				case IMAGE_BPP_RGB888: {
					rgb888_t *tmp = (rgb888_t*)(aux.data);

					for (uint32_t y = 0, yy = h; y < yy; y++) {
						rgb888_t *row_ptr = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, y);
						for (uint32_t x = 0, xx = w; x < xx; x++) {
							float xxx = T4_00 * x + T4_01 * y + T4_02;
							float yyy = T4_10 * x + T4_11 * y + T4_12;
							float zzz = T4_20 * x + T4_21 * y + T4_22;
							int32_t sourceX = fast_roundf(xxx / zzz);
							int32_t sourceY = fast_roundf(yyy / zzz);

							if ((0 <= sourceX) && (sourceX < w) && (0 <= sourceY) && (sourceY < h)) {
								rgb888_t *ptr = tmp + (w * sourceY);
								rgb888_t pixel = IMAGE_GET_RGB888_PIXEL_FAST(ptr, sourceX);
								IMAGE_PUT_RGB888_PIXEL_FAST(row_ptr, x, pixel);
							}
						}
					}
					break;
				}

				default: {
					break;
				}
			}
		}
	}

	matd_destroy(T4);
	matd_destroy(T3);

	STM32Ipl_ReleaseData(&aux);

	return stm32ipl_err_Ok;
}

/**
 * @brief Applies an affine transformation matrix to a vector of points.
 * The content of the provided point vector is overwritten with the result of the transformation.
 * @param points	Vector of points; it must be valid, otherwise an error is returned.
 * @param nPoints	The number of vector's elements.
 * @param affine	Vector of six numbers representing the 2×3 affine transformation matrix;
 * it must be valid, otherwise an error is returned. The first 3 elements correspond to the
 * the first line of the matrix, while the last 3 elements correspond to the second line.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_WarpAffinePoints(point_t *points, uint32_t nPoints, const float *affine)
{
	float p[9];
	matd_t *T4;

	if (!points || !affine)
		return stm32ipl_err_InvalidParameter;

	for (uint8_t i = 0; i < 6; i++) {
		p[i] = affine[i];
	}
	p[6] = 0;
	p[7] = 0;
	p[8] = 1;

	T4 = matd_create_data(3, 3, p);

	if (T4) {
		float T4_00 = MATD_EL(T4, 0, 0), T4_01 = MATD_EL(T4, 0, 1), T4_02 = MATD_EL(T4, 0, 2);
		float T4_10 = MATD_EL(T4, 1, 0), T4_11 = MATD_EL(T4, 1, 1), T4_12 = MATD_EL(T4, 1, 2);
		float T4_20 = MATD_EL(T4, 2, 0), T4_21 = MATD_EL(T4, 2, 1), T4_22 = MATD_EL(T4, 2, 2);

		if ((fast_fabsf(T4_20) < MATD_EPS) && (fast_fabsf(T4_21) < MATD_EPS)) { /* Warp affine. */
			T4_00 /= T4_22;
			T4_01 /= T4_22;
			T4_02 /= T4_22;
			T4_10 /= T4_22;
			T4_11 /= T4_22;
			T4_12 /= T4_22;

			for (uint32_t idx = 0; idx < nPoints; idx++) {
				point_t *point = &(points[idx]);
				int32_t sourceX = fast_roundf(T4_00 * point->x + T4_01 * point->y + T4_02);
				int32_t sourceY = fast_roundf(T4_10 * point->x + T4_11 * point->y + T4_12);
				point->x = (int16_t)sourceX;
				point->y = (int16_t)sourceY;
			}
		} else { /* Warp perspective. */
			for (uint32_t idx = 0; idx < nPoints; idx++) {
				point_t *point = &(points[idx]);
				float xxx = T4_00 * point->x + T4_01 * point->y + T4_02;
				float yyy = T4_10 * point->x + T4_11 * point->y + T4_12;
				float zzz = T4_20 * point->x + T4_21 * point->y + T4_22;
				int32_t sourceX = fast_roundf(xxx / zzz);
				int32_t sourceY = fast_roundf(yyy / zzz);

				point->x = (int16_t)sourceX;
				point->y = (int16_t)sourceY;
			}
		}
	}

	matd_destroy(T4);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
