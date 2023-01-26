/**
 ******************************************************************************
 * @file   stm32ipl_rect.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - rectangle module
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
 * @brief Initializes a rectangle.
 * @param r			Pointer to the rectangle; if it is not valid, an error is returned.
 * @param x 		X-coordinate of the top-left corner.
 * @param y			Y-coordinate of the top-left corner.
 * @param width		Width of the rectangle.
 * @param height	Height of the rectangle.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_RectInit(rectangle_t *r, int16_t x, int16_t y, int16_t width, int16_t height)
{
	STM32IPL_CHECK_VALID_PTR_ARG(r)

	r->x = x;
	r->y = y;
	r->w = width;
	r->h = height;

	return stm32ipl_err_Ok;
}

/**
 * @brief Allocates and initializes a rectangle.
 * @param x 		X-coordinate of the top-left corner.
 * @param y			Y-coordinate of the top-left corner.
 * @param width		Width.
 * @param height	Height.
 * @return			The allocated rectangle.
 */
rectangle_t* STM32Ipl_RectAlloc(int16_t x, int16_t y, int16_t width, int16_t height)
{
	return rectangle_alloc(x, y, width, height);
}

/**
 * @brief Copies the source rectangle to the destination rectangle.
 * @param src	Source rectangle; if it is not valid, an error is returned.
 * @param dst	Destination rectangle; if it is not valid, an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_RectCopy(const rectangle_t *src, rectangle_t *dst)
{
	if (!src || !dst)
		return stm32ipl_err_InvalidParameter;

	memcpy(dst, src, sizeof(rectangle_t));

	return stm32ipl_err_Ok;
}

/**
 * @brief Checks if two rectangles are equal.
 * @param r0	First rectangle; if it is not valid, false is returned.
 * @param r1	Second rectangle; if it is not valid, false is returned.
 * @return		True if the two rectangles are equal, false otherwise.
 */
bool STM32Ipl_RectEqual(const rectangle_t *r0, const rectangle_t *r1)
{
	if (!r0 || !r1)
		return false;

	if (r0 == r1)
		return true;

	return rectangle_equal((rectangle_t*)r0, (rectangle_t*)r1);
}

/**
 * @brief Checks if two rectangles are equal by comparing their memory blocks.
 * @param r0	First rectangle; if it is not valid, false is returned.
 * @param r1	Second rectangle; if it is not valid, false is returned.
 * @return		True if the two rectangles are equal, false otherwise.
 */
bool STM32Ipl_RectEqualFast(const rectangle_t *r0, const rectangle_t *r1)
{
	if (!r0 || !r1)
		return false;

	if (r0 == r1)
		return true;

	return rectangle_equal_fast((rectangle_t*)r0, (rectangle_t*)r1);
}

/**
 * @brief Determines if rectangle r1 is inside rectangle r0.
 * @param r0	First rectangle; if it is not valid, false is returned.
 * @param r1	Second rectangle; if it is not valid, false is returned.
 * @return		True if the second rectangle is contained in the first one, false otherwise.
 */
bool STM32Ipl_RectContain(const rectangle_t *r0, const rectangle_t *r1)
{
	if (r0 && r1)
		return ((r0->x <= r1->x) && ((r1->x + r1->w) <= (r0->x + r0->w)) && (r0->y <= r1->y)
				&& ((r1->y + r1->h) <= (r0->y + r0->h)));

	return false;
}

/**
 * @brief Determines if two rectangles overlap.
 * @param r0	First rectangle; if it is not valid, false is returned.
 * @param r1	Second rectangle; if it is not valid, false is returned.
 * @return		True if the two rectangles overlap, false otherwise.
 */
bool STM32Ipl_RectOverlap(const rectangle_t *r0, const rectangle_t *r1)
{
	if (r0 && r1)
		return rectangle_overlap((rectangle_t*)r0, (rectangle_t*)r1);

	return false;
}

/**
 * @brief Finds the intersection of two rectangles and saves it into the
 * destination rectangle.
 * @param src	Source rectangle; if it is not valid, an error is returned.
 * @param dst	Destination rectangle; if it is not valid, an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_RectIntersected(const rectangle_t *src, rectangle_t *dst)
{
	if (!src || !dst)
		return stm32ipl_err_InvalidParameter;

	rectangle_intersected(dst, (rectangle_t*)src);

	return stm32ipl_err_Ok;
}

/**
 * @brief Finds the union of two rectangles and saves it into the destination rectangle.
 * @param src	Source rectangle; if it is not valid, an error is returned.
 * @param dst	Destination rectangle; if it is not valid, an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_RectUnited(const rectangle_t *src, rectangle_t *dst)
{
	if (!src || !dst)
		return stm32ipl_err_InvalidParameter;

	rectangle_united(dst, (rectangle_t*)src);

	return stm32ipl_err_Ok;
}

/**
 * @brief Expands a rectangle to include a point.
 * @param r		Rectangle; if it is not valid, an error is returned.
 * @param x 	X-coordinate of the point.
 * @param y 	Y-coordinate of the point.
 * @return		stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_RectExpand(rectangle_t *r, uint16_t x, uint16_t y)
{
	rectangle_t rect;

	STM32IPL_CHECK_VALID_PTR_ARG(r)

	rectangle_copy(&rect, r);
	rectangle_expand(r, x, y);

	if (r->w != rect.w)
		r->w = r->w - r->x;
	if (r->h != rect.h)
		r->h = r->h - r->x;

	if (r->x < rect.x)
		r->w = (rect.w + rect.x) - r->x;
	if (r->y < rect.y)
		r->h = (rect.h + rect.y) - r->y;

	return stm32ipl_err_Ok;
}

/**
 * @brief Determines the ROI obtained by intersecting the image with rectangle src;
 * if the intersection is not empty, the obtained ROI is saved in dst and
 * true is returned; if the intersection is empty, false is returned.
 * @param img	Image; if it is not valid, an error is returned.
 * @param src	Source ROI; if it is not valid, an error is returned.
 * @param dst	Destination ROI (valid only when this function returns true); if it is not valid, an error is returned.
 * @return		True if the intersection is not empty, false otherwise.
 */
bool STM32Ipl_RectSubImage(const image_t *img, const rectangle_t *src, rectangle_t *dst)
{
	if (!img || !img->data || !src || !dst)
		return false;

	return rectangle_subimg((image_t*)img, (rectangle_t*)src, dst);
}

/**
 * @brief Copies the rectangle values to a four points vector in a clockwise manner.
 * The vector must be allocated by the caller.
 * @param r			Rectangle; if it is not valid, an error is returned.
 * @param points	Four points vector; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_RectToPoints(const rectangle_t *r, point_t *points)
{
	STM32IPL_CHECK_VALID_PTR_ARG(r)
	STM32IPL_CHECK_VALID_PTR_ARG(points)

	points[0].x = r->x;
	points[0].y = r->y;

	points[1].x = r->x + r->w;
	points[1].y = r->y;

	points[2].x = points[1].x;
	points[2].y = r->y + r->h;

	points[3].x = r->x;
	points[3].y = points[2].y;

	return stm32ipl_err_Ok;
}

/**
 * @brief Merges an array of rectangles, and returns the results in the array itself.
 * If two rectangles overlap, they are merged to obtain an average rectangle.
 * @param rects	Pointer to pointer to an array of rectangle_t; if it is not valid, an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_RectMerge(array_t **rects)
{
	if (!rects || !(*rects))
		return stm32ipl_err_InvalidParameter;

	*rects = rectangle_merge(*rects);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
