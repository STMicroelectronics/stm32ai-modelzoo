/**
 ******************************************************************************
 * @file   stm32ipl_geometry.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - geometry module
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
 * @brief Clips a line in a rectangle area (Liang-Barsky line clipping).
 * @param l 		Line; if it is not valid, an error is returned.
 * @param x 		X-coordinate of the top-left corner of the rectangle.
 * @param y 		Y-coordinate of the top-left corner of the rectangle.
 * @param width		Width of the rectangle.
 * @param height	Height of the rectangle.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
bool STM32Ipl_ClipLine(line_t *l, int16_t x, int16_t y, int16_t width, int16_t height)
{
	if (!l)
		return false;

	return lb_clip_line(l, x, y, width, height);
}

/**
 * @brief Gets the length of a line.
 * @param l			Line; if it is not valid, an error is returned.
 * @param length 	Line length; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_LineLength(const line_t *l, float *length)
{
	int32_t xDiff;
	int32_t yDiff;

	if (!l || !length)
		return stm32ipl_err_InvalidParameter;

	xDiff = l->x2 - l->x1;
	yDiff = l->y2 - l->y1;

	*length = fast_sqrtf((xDiff * xDiff) + (yDiff * yDiff));

	return stm32ipl_err_Ok;
}

/**
 * @brief Gets the length of a polyline.
 * @param points	Vector of points describing the polyline; if it is not valid, an error is returned.
 * @param count		Length of the vector (number of points).
 * @param closed	When true, the polyline is considered closed.
 * @param out		Lenght of the polyline; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_PolylineLength(const point_t *points, uint16_t count, bool closed, float *out)
{
	uint16_t last;
	float prevX;
	float prevY;

	if (!points || count <= 1) {
		*out = 0.0f;
		return stm32ipl_err_InvalidParameter;
	}

	last = closed ? (count - 1) : 0;

	prevX = points[last].x;
	prevY = points[last].y;

	for (uint16_t i = 0; i < count; i++) {
		float px = (float)points[i].x;
		float py = (float)points[i].y;
		float dx = px - prevX;
		float dy = py - prevY;

		*out += fast_sqrtf(dx * dx + dy * dy);

		prevX = px;
		prevY = py;
	}

	return stm32ipl_err_Ok;
}

/**
 *
 * @brief Gets the circle that encloses four points representing the four corners of a rectangle.
 * @param points	Vector of four points representing the four corners of a rectangle;
 * if it is not valid, an error is returned.
 * @param center		Center of the circle; if it is not valid, an error is returned.
 * @param radius		Radius of the circle; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_EnclosingCircle(const point_t *points, point_t *center, uint16_t *radius)
{
	int16_t x0, y0, x1, y1, x2, y2, x3, y3;
	float d0, d1, d2, d3;
	float cx, cy;

	if (!points || !center || !radius)
		return stm32ipl_err_InvalidParameter;

	x0 = points[0].x;
	y0 = points[0].y;

	x1 = points[1].x;
	y1 = points[1].y;

	x2 = points[2].x;
	y2 = points[2].y;

	x3 = points[3].x;
	y3 = points[3].y;

	cx = (x0 + x1 + x2 + x3) / 4;
	cy = (y0 + y1 + y2 + y3) / 4;

	d0 = fast_sqrtf(((x0 - cx) * (x0 - cx)) + ((y0 - cy) * (y0 - cy)));
	d1 = fast_sqrtf(((x1 - cx) * (x1 - cx)) + ((y1 - cy) * (y1 - cy)));
	d2 = fast_sqrtf(((x2 - cx) * (x2 - cx)) + ((y2 - cy) * (y2 - cy)));
	d3 = fast_sqrtf(((x3 - cx) * (x3 - cx)) + ((y3 - cy) * (y3 - cy)));

	center->x = (int16_t)cx;
	center->y = (int16_t)cy;

	*radius = fast_roundf(STM32IPL_MAX(d0, STM32IPL_MAX(d1, STM32IPL_MAX(d2, d3))));

	return stm32ipl_err_Ok;

}

/**
 * @brief Gets the ellipse that encloses a rectangle described by its four corners.
 * @param points	Vector of four points representing the four corners of a rectangle;
 * if it is not valid, an error is returned.
 * @param out		Ellipse; if it is not valid, an error is returned.
 * @return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_EnclosingEllipse(const point_t *points, ellipse_t *out)
{
	int16_t x0, y0, x1, y1, x2, y2, x3, y3;
	float m0x, m0y, m1x, m1y, m2x, m2y, m3x, m3y;
	float cx, cy;
	float d0, d1, d2, d3;
	float l0, l1;

	if (!points || !out)
		return stm32ipl_err_InvalidParameter;

	x0 = points[0].x;
	y0 = points[0].y;
	x1 = points[1].x;
	y1 = points[1].y;
	x2 = points[2].x;
	y2 = points[2].y;
	x3 = points[3].x;
	y3 = points[3].y;

	m0x = (x0 + x1) / 2;
	m0y = (y0 + y1) / 2;
	m1x = (x1 + x2) / 2;
	m1y = (y1 + y2) / 2;
	m2x = (x2 + x3) / 2;
	m2y = (y2 + y3) / 2;
	m3x = (x3 + x0) / 2;
	m3y = (y3 + y0) / 2;

	cx = (x0 + x1 + x2 + x3) / 4;
	cy = (y0 + y1 + y2 + y3) / 4;

	d0 = fast_sqrtf(((m0x - cx) * (m0x - cx)) + ((m0y - cy) * (m0y - cy)));
	d1 = fast_sqrtf(((m1x - cx) * (m1x - cx)) + ((m1y - cy) * (m1y - cy)));
	d2 = fast_sqrtf(((m2x - cx) * (m2x - cx)) + ((m2y - cy) * (m2y - cy)));
	d3 = fast_sqrtf(((m3x - cx) * (m3x - cx)) + ((m3y - cy) * (m3y - cy)));

	l0 = fast_sqrtf(((m0x - m2x) * (m0x - m2x)) + ((m0y - m2y) * (m0y - m2y)));
	l1 = fast_sqrtf(((m1x - m3x) * (m1x - m3x)) + ((m1y - m3y) * (m1y - m3y)));

	if (l0 >= l1) {
		out->rotation = (int16_t)STM32IPL_RAD2DEG(fast_atan2f(m0y - m2y, m0x - m2x));
	} else {
		out->rotation = (int16_t)STM32IPL_RAD2DEG(fast_atan2f(m1y - m3y, m1x - m3x) + M_PI_2);
	}

	out->center.x = (int16_t)cx;
	out->center.y = (int16_t)cy;
	out->radiusX = (int16_t)STM32IPL_MIN(d0, d2);
	out->radiusY = (int16_t)STM32IPL_MIN(d1, d3);

	return stm32ipl_err_Ok;
}

/**
 * @brief Gets the ellipse enclosing a polygon represented by the given points
 * @param points	Points of the polygon; they must be ordered; if it is not valid, an error is returned.
 * @param nPoints	Number of points composing the polygon.
 * @param out		Ellipse; if it is not valid, an error is returned.
 * @return			stm32ipl_err_Ok on success, error otherwise
 */
stm32ipl_err_t STM32Ipl_FitEllipse(const point_t *points, uint16_t nPoints, ellipse_t *out)
{
	point_t minCorners[4];
	ellipse_t ellipse;

	if (!points || !out)
		return stm32ipl_err_InvalidParameter;

	STM32Ipl_PointMinAreaRectangle(points, nPoints, minCorners);

	STM32Ipl_EnclosingEllipse(minCorners, &ellipse);

	*out = ellipse;

	return stm32ipl_err_Ok;
}

#ifdef __cplusplus
}
#endif
