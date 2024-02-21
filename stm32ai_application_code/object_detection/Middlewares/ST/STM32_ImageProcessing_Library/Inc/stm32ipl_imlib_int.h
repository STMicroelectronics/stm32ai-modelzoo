/*
 * This file is part of the OpenMV project.
 *
 * Copyright (c) 2013-2019 Ibrahim Abdelkader <iabdalkader@openmv.io>
 * Copyright (c) 2013-2019 Kwabena W. Agyeman <kwagyeman@openmv.io>
 *
 * This work is licensed under the MIT license, see the file LICENSE for details.
 *
 * Image processing library.
 */

#ifndef __STM32IPL_IMLIB_INT_H__
#define __STM32IPL_IMLIB_INT_H__

#include "stm32ipl_mem_alloc.h"	// STM32IPL

///@cond

#ifndef M_PI				// STM32IPL
#define M_PI    3.14159265f // STM32IPL
#endif 						// STM32IPL

#define IM_MAX(a,b)     ({ (a) > (b) ? (a) : (b); })
#define IM_MIN(a,b)     ({ (a) < (b) ? (a) : (b); })
#define IM_DIV(a,b)     ({ (b) ? ((a) / (b)) : 0; })
#define IM_MOD(a,b)     ({ (b) ? ((a) % (b)) : 0; })

#define IM_DEG2RAD(x)   (((x)*M_PI)/180)
#define IM_RAD2DEG(x)   (((x)*180)/M_PI)

/////////////////
// Point Stuff //
/////////////////
void point_init(point_t *ptr, int x, int y);
void point_copy(point_t *dst, point_t *src);
bool point_equal_fast(point_t *ptr0, point_t *ptr1);
int point_quadrance(point_t *ptr0, point_t *ptr1);
void point_rotate(int x, int y, float r, int center_x, int center_y, int16_t *new_x, int16_t *new_y);
void point_min_area_rectangle(point_t *corners, point_t *new_corners, int corners_len);

////////////////
// Line Stuff //
////////////////
bool lb_clip_line(line_t *l, int x, int y, int w, int h);

/////////////////////
// Rectangle Stuff //
/////////////////////
void rectangle_init(rectangle_t *ptr, int x, int y, int w, int h);
void rectangle_copy(rectangle_t *dst, rectangle_t *src);
bool rectangle_equal_fast(rectangle_t *ptr0, rectangle_t *ptr1);
bool rectangle_overlap(rectangle_t *ptr0, rectangle_t *ptr1);
void rectangle_intersected(rectangle_t *dst, rectangle_t *src);
void rectangle_united(rectangle_t *dst, rectangle_t *src);

typedef enum
{
	COLOR_PALETTE_RAINBOW, COLOR_PALETTE_IRONBOW
} color_palette_t;

// Color palette LUTs
extern const uint16_t rainbow_table[256];
extern const uint16_t ironbow_table[256];

void image_init(image_t *ptr, int w, int h, int bpp, void *data);
void image_copy(image_t *dst, image_t *src);
size_t image_size(image_t *ptr);
bool image_get_mask_pixel(image_t *ptr, int x, int y);

// Old Image Macros - Will be refactor and removed. But, only after making sure through testing new macros work.

// Image kernels
extern const int8_t kernel_gauss_3[9];
extern const int8_t kernel_gauss_5[25];
extern const int kernel_laplacian_3[9];
extern const int kernel_high_pass_3[9];

typedef struct simple_color
{
	uint8_t G; // Gray
	union
	{
		int8_t L; // LAB L
		uint8_t red; // RGB888 Red
	};
	union
	{
		int8_t A; // LAB A
		uint8_t green; // RGB888 Green
	};
	union
	{
		int8_t B; // LAB B
		uint8_t blue; // RGB888 Blue
	};
} simple_color_t;

typedef void (*line_op_t)(image_t*, int, void*, void*, bool);

typedef enum edge_detector_type
{
	EDGE_CANNY,
	EDGE_SIMPLE,
} edge_detector_t;

void imlib_image_operation(image_t *img, const char *path, image_t *other, int scalar, line_op_t op, void *data);

#define FIND_BLOBS_ANGLE_RESOLUTION (360 / FIND_BLOBS_CORNERS_RESOLUTION)

/* Point functions */
point_t* point_alloc(int16_t x, int16_t y);
bool point_equal(point_t *p1, point_t *p2);
float point_distance(point_t *p1, point_t *p2);

/* Rectangle functions */
rectangle_t* rectangle_alloc(int16_t x, int16_t y, int16_t w, int16_t h);
bool rectangle_equal(rectangle_t *r1, rectangle_t *r2);
bool rectangle_intersects(rectangle_t *r1, rectangle_t *r2);
bool rectangle_subimg(image_t *img, rectangle_t *r, rectangle_t *r_out);
array_t* rectangle_merge(array_t *rectangles);
void rectangle_expand(rectangle_t *r, int x, int y);

/* Separable 2D convolution */
void imlib_sepconv3(image_t *img, const int8_t *krn, const float m, const int b);

/* Image Statistics */
int imlib_image_mean(image_t *src, int *r_mean, int *g_mean, int *b_mean);
int imlib_image_std(image_t *src); // grayscale only

/* Template Matching */
void imlib_midpoint_pool(image_t *img_i, image_t *img_o, int x_div, int y_div, const int bias);
void imlib_mean_pool(image_t *img_i, image_t *img_o, int x_div, int y_div);
float imlib_template_match_ds(image_t *image, image_t *template, rectangle_t *r);
float imlib_template_match_ex(image_t *image, image_t *template, rectangle_t *roi, int step, rectangle_t *r);

/* Integral image functions */
void imlib_integral_image_alloc(struct integral_image *sum, int w, int h);
void imlib_integral_image_free(struct integral_image *sum);
void imlib_integral_image(struct image *src, struct integral_image *sum);
void imlib_integral_image_sq(struct image *src, struct integral_image *sum);
void imlib_integral_image_scaled(struct image *src, struct integral_image *sum);
uint32_t imlib_integral_lookup(struct integral_image *src, int x, int y, int w, int h);

// Integral moving window
void imlib_integral_mw_alloc(mw_image_t *sum, int w, int h);
void imlib_integral_mw_free(mw_image_t *sum);
void imlib_integral_mw_scale(rectangle_t *roi, mw_image_t *sum, int w, int h);
void imlib_integral_mw(image_t *src, mw_image_t *sum);
void imlib_integral_mw_sq(image_t *src, mw_image_t *sum);
void imlib_integral_mw_shift(image_t *src, mw_image_t *sum, int n);
void imlib_integral_mw_shift_sq(image_t *src, mw_image_t *sum, int n);
void imlib_integral_mw_ss(image_t *src, mw_image_t *sum, mw_image_t *ssq, rectangle_t *roi);
void imlib_integral_mw_shift_ss(image_t *src, mw_image_t *sum, mw_image_t *ssq, rectangle_t *roi, int n);
long imlib_integral_mw_lookup(mw_image_t *sum, int x, int y, int w, int h);

/* Haar/VJ */
int imlib_load_cascade(struct cascade *cascade, const char *path);
array_t* imlib_detect_objects(struct image *image, struct cascade *cascade, struct rectangle *roi);

// Edge detection
void imlib_edge_simple(image_t *src, rectangle_t *roi, int low_thresh, int high_thresh);
void imlib_edge_canny(image_t *src, rectangle_t *roi, int low_thresh, int high_thresh);

// Helper Functions
void imlib_zero(image_t *img, image_t *mask, bool invert);

// Drawing Functions
void imlib_set_pixel(image_t *img, int x, int y, int p);
void imlib_draw_line(image_t *img, int x0, int y0, int x1, int y1, int c, int thickness);
void imlib_draw_rectangle(image_t *img, int rx, int ry, int rw, int rh, int c, int thickness, bool fill);
void imlib_draw_circle(image_t *img, int cx, int cy, int r, int c, int thickness, bool fill);
void imlib_draw_ellipse(image_t *img, int cx, int cy, int rx, int ry, int rotation, int c, int thickness, bool fill);

// Binary Functions
void imlib_binary(image_t *out, image_t *img, list_t *thresholds, bool invert, bool zero, image_t *mask);
void imlib_invert(image_t *img);
void imlib_b_and(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_b_nand(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_b_or(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_b_nor(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_b_xor(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_b_xnor(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_erode(image_t *img, int ksize, int threshold, image_t *mask);
void imlib_dilate(image_t *img, int ksize, int threshold, image_t *mask);
void imlib_open(image_t *img, int ksize, int threshold, image_t *mask);
void imlib_close(image_t *img, int ksize, int threshold, image_t *mask);
void imlib_top_hat(image_t *img, int ksize, int threshold, image_t *mask);
void imlib_black_hat(image_t *img, int ksize, int threshold, image_t *mask);

// Math Functions
void imlib_gamma_corr(image_t *img, float gamma, float scale, float offset);
void imlib_replace(image_t *img, const char *path, image_t *other, int scalar, bool hmirror, bool vflip, bool transpose,
		image_t *mask);
void imlib_add(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_sub(image_t *img, const char *path, image_t *other, int scalar, bool reverse, image_t *mask);
void imlib_mul(image_t *img, const char *path, image_t *other, int scalar, bool invert, image_t *mask);
void imlib_div(image_t *img, const char *path, image_t *other, int scalar, bool invert, bool mod, image_t *mask);
void imlib_min(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_max(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);
void imlib_difference(image_t *img, const char *path, image_t *other, int scalar, image_t *mask);

// Filtering Functions
void imlib_histeq(image_t *img, image_t *mask);
void imlib_clahe_histeq(image_t *img, float clip_limit, image_t *mask);
void imlib_mean_filter(image_t *img, const int ksize, bool threshold, int offset, bool invert, image_t *mask);
void imlib_median_filter(image_t *img, const int ksize, float percentile, bool threshold, int offset, bool invert,
		image_t *mask);
void imlib_mode_filter(image_t *img, const int ksize, bool threshold, int offset, bool invert, image_t *mask);
void imlib_midpoint_filter(image_t *img, const int ksize, float bias, bool threshold, int offset, bool invert,
		image_t *mask);
void imlib_morph(image_t *img, const int ksize, const int *krn, const float m, const int b, bool threshold, int offset,
		bool invert, image_t *mask);
void imlib_bilateral_filter(image_t *img, const int ksize, float color_sigma, float space_sigma, bool threshold,
		int offset, bool invert, image_t *mask);

// Lens/Rotation Correction
void imlib_lens_corr(image_t *img, float strength, float zoom, float x_corr, float y_corr);
void imlib_rotation_corr(image_t *img, float x_rotation, float y_rotation, float z_rotation, float x_translation,
		float y_translation, float zoom, float fov, float *corners);
// Statistics
void imlib_get_similarity(image_t *img, const char *path, image_t *other, int scalar, float *avg, float *std,
		float *min, float *max);
void imlib_get_histogram(histogram_t *out, image_t *ptr, rectangle_t *roi, list_t *thresholds, bool invert,
		image_t *other);
void imlib_get_percentile(percentile_t *out, image_bpp_t bpp, histogram_t *ptr, float percentile);
void imlib_get_threshold(threshold_t *out, image_bpp_t bpp, histogram_t *ptr);
void imlib_get_statistics(statistics_t *out, image_bpp_t bpp, histogram_t *ptr);
bool imlib_get_regression(find_lines_list_lnk_data_t *out, image_t *ptr, rectangle_t *roi, unsigned int x_stride,
		unsigned int y_stride, list_t *thresholds, bool invert, unsigned int area_threshold,
		unsigned int pixels_threshold, bool robust);
// Color Tracking
void imlib_find_blobs(list_t *out, image_t *ptr, rectangle_t *roi, unsigned int x_stride, unsigned int y_stride,
		list_t *thresholds, bool invert, unsigned int area_threshold, unsigned int pixels_threshold,
		bool merge, int margin,
		bool (*threshold_cb)(void*, find_blobs_list_lnk_data_t*), void *threshold_cb_arg,
		bool (*merge_cb)(void*, find_blobs_list_lnk_data_t*, find_blobs_list_lnk_data_t*), void *merge_cb_arg,
		unsigned int x_hist_bins_max, unsigned int y_hist_bins_max, uint32_t max_blobs); // STM32IPL: max_blobs parameter added.

// Shape Detection
void imlib_find_lines(list_t *out, image_t *ptr, rectangle_t *roi, unsigned int x_stride, unsigned int y_stride,
		uint32_t threshold, unsigned int theta_margin, unsigned int rho_margin);
void imlib_find_circles(list_t *out, image_t *ptr, rectangle_t *roi, unsigned int x_stride, unsigned int y_stride,
		uint32_t threshold, unsigned int x_margin, unsigned int y_margin, unsigned int r_margin, unsigned int r_min,
		unsigned int r_max, unsigned int r_step);

// Statistics
bool stm32ipl_get_regression_points(const point_t *points, uint16_t nPoints, find_lines_list_lnk_data_t *out,
		bool robust); // STM32IPL

// STM32IPL: added prototypes.
void merge_alot(list_t *out, int threshold, int theta_threshold);
size_t trace_line(image_t *ptr, line_t *l, int *theta_buffer, uint32_t *mag_buffer, point_t *point_buffer);
/// @endcond

#endif //__STM32IPL_IMLIB_INT_H__
