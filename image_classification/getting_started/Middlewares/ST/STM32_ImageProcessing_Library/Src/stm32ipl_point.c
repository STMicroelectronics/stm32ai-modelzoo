/**
 ******************************************************************************
 * @file   stm32ipl_point.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - point module
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
 * @brief Initializes a point.
 * @param p		Pointer to the point; if it is not valid, an error is returned.
 * @param x	 	X-coordinate of the point.
 * @param y		Y-coordinate of the point.
 * @return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_PointInit(point_t *p, int16_t x, int16_t y)
{
	STM32IPL_CHECK_VALID_PTR_ARG(p)

	p->x = x;
	p->y = y;

	return stm32ipl_err_Ok;
}

/**
 * @brief Allocates and initializes a point.
 * @param x 	X-coordinate of the point.
 * @param y		Y-coordinate of the point.
 * @return		The allocated point structure.
 */
point_t* STM32Ipl_PointAlloc(int16_t x, int16_t y)
{
	return point_alloc(x, y);
}

/**
 * @brief Copies the source point to the destination point.
 * @param src	Source point; if it is not valid, an error is returned.
 * @param dst	Destination point; if it is not valid, an error is returned.
 * @return		stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_PointCopy(const point_t *src, point_t *dst)
{
	if (!src || !dst)
		return stm32ipl_err_InvalidParameter;

	memcpy(dst, src, sizeof(point_t));

	return stm32ipl_err_Ok;
}

/**
 * @brief Checks if two points are equal.
 * @param p0	First point; if it is not valid, false is returned.
 * @param p1	Second point; if it is not valid, false is returned.
 * @return		True if the two points are equal, false otherwise.
 */
bool STM32Ipl_PointEqual(const point_t *p0, const point_t *p1)
{
	if (!p0 || !p1)
		return false;

	if (p0 == p1)
		return true;

	return point_equal((point_t*)p0, (point_t*)p1);
}

/**
 * @brief Checks if two points are equal by comparing their memory blocks.
 * @param p0	First point; if it is not valid, false is returned.
 * @param p1	Second point; if it is not valid, false is returned.
 * @return		True if the two points are equal, false otherwise.
 */
bool STM32Ipl_PointEqualFast(const point_t *p0, const point_t *p1)
{
	if (!p0 || !p1)
		return false;

	if (p0 == p1)
		return true;

	return point_equal_fast((point_t*)p0, (point_t*)p1);
}

/**
 * @brief Gets the Euclidean distance between two points:
 * \f$(x0, y0)\f$ and \f$(x1, y1)\f$ is \f$\sqrt{(x1 - x0) ^ 2 + (y1 - y0) ^ 2}\f$.
 * @param p0		First point; if it is not valid, false is returned.
 * @param p1		Second point; if it is not valid, false is returned.
 * @param distance 	Returned Eucledian distance (pixels); if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_PointDistance(const point_t *p0, const point_t *p1, float *distance)
{
	if (!p0 || !p1 || !distance)
		return stm32ipl_err_InvalidParameter;

	*distance = point_distance((point_t*)p0, (point_t*)p1);

	return stm32ipl_err_Ok;
}

/**
 * @brief Gets the squared Euclidean distance between two points:
 * \f$(x0, y0)\f$ and \f$(x1, y1)\f$ is \f$(x1 - x0) ^ 2 + (y1 - y0) ^ 2\f$.
 * @param p0		First point; if it is not valid, false is returned.
 * @param p1		Second point; if it is not valid, false is returned.
 * @param quadrance	Returned squared Eucledian distance (pixels); if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_PointQuadrance(const point_t *p0, const point_t *p1, uint32_t *quadrance)
{
	if (!p0 || !p1 || !quadrance)
		return stm32ipl_err_InvalidParameter;

	*quadrance = point_quadrance((point_t*)p0, (point_t*)p1);

	return stm32ipl_err_Ok;
}

/**
 * @brief Rotates a point (x, y) by given degrees around a center of rotation (centerX, centerY).
 * @param x 		X-coordinate of the point.
 * @param y 		Y-coordinate of the point.
 * @param degree 	Amount of rotation (degrees).
 * @param centerX	X-coordinate of the center of rotation.
 * @param centerY	Y-coordinate of the center of rotation.
 * @param outX		X-coordinate of the rotated point; if it is not valid, an error is returned.
 * @param outY		Y-coordinate of the rotated point; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_PointRotate(int16_t x, int16_t y, uint16_t degree, int16_t centerX, int16_t centerY,
		int16_t *outX, int16_t *outY)
{
	if (!outX || !outY)
		return stm32ipl_err_InvalidParameter;

	point_rotate(x, y, STM32IPL_DEG2RAD(degree), centerX, centerY, outX, outY);

	return stm32ipl_err_Ok;
}

/**
 * @brief Gets the minimum area rectangle enclosing a polygon represented by the given points;
 * the result is a rectangle, expressed as a four points vector (its corners), that can be rotated.
 * @param points 		Points of the polygon; they must be ordered; if it is not valid, an error is returned.
 * @param nPoints		Number of points composing the polygon
 * @param out			Returned four points vector containing the corners of the (eventually rotated)
 * bounding rectangle; if it is not valid, an error is returned.
 * @return				stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_PointMinAreaRectangle(const point_t *points, uint16_t nPoints, point_t *out)
{
	if (!points || !out)
		return stm32ipl_err_InvalidParameter;

	point_min_area_rectangle((point_t*)points, out, nPoints);

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
