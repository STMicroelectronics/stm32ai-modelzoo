/**
 * @file   stm32ipl_imlib.h
 */
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

#ifndef __STM32IPL_IMLIB_EXT_H__
#define __STM32IPL_IMLIB_EXT_H__

#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <limits.h>
#include <float.h>
#include <math.h>
#include <arm_math.h>
#include "array.h"
#include "fmath.h"
#include "collections.h"
#include "imlib_config.h"

///@cond
#define IM_LOG2_2(x)    (((x) &                0x2ULL) ? ( 2                        ) :             1) // NO ({ ... }) !
#define IM_LOG2_4(x)    (((x) &                0xCULL) ? ( 2 +  IM_LOG2_2((x) >>  2)) :  IM_LOG2_2(x)) // NO ({ ... }) !
#define IM_LOG2_8(x)    (((x) &               0xF0ULL) ? ( 4 +  IM_LOG2_4((x) >>  4)) :  IM_LOG2_4(x)) // NO ({ ... }) !
#define IM_LOG2_16(x)   (((x) &             0xFF00ULL) ? ( 8 +  IM_LOG2_8((x) >>  8)) :  IM_LOG2_8(x)) // NO ({ ... }) !
#define IM_LOG2_32(x)   (((x) &         0xFFFF0000ULL) ? (16 + IM_LOG2_16((x) >> 16)) : IM_LOG2_16(x)) // NO ({ ... }) !
#define IM_LOG2(x)      (((x) & 0xFFFFFFFF00000000ULL) ? (32 + IM_LOG2_32((x) >> 32)) : IM_LOG2_32(x)) // NO ({ ... }) !

#define INT8_T_BITS     (sizeof(int8_t) * 8)
#define INT8_T_MASK     (INT8_T_BITS - 1)
#define INT8_T_SHIFT    IM_LOG2(INT8_T_MASK)

#define INT16_T_BITS    (sizeof(int16_t) * 8)
#define INT16_T_MASK    (INT16_T_BITS - 1)
#define INT16_T_SHIFT   IM_LOG2(INT16_T_MASK)

#define INT32_T_BITS    (sizeof(int32_t) * 8)
#define INT32_T_MASK    (INT32_T_BITS - 1)
#define INT32_T_SHIFT   IM_LOG2(INT32_T_MASK)

#define INT64_T_BITS    (sizeof(int64_t) * 8)
#define INT64_T_MASK    (INT64_T_BITS - 1)
#define INT64_T_SHIFT   IM_LOG2(INT64_T_MASK)

#define UINT8_T_BITS    (sizeof(uint8_t) * 8)
#define UINT8_T_MASK    (UINT8_T_BITS - 1)
#define UINT8_T_SHIFT   IM_LOG2(UINT8_T_MASK)

#define UINT16_T_BITS   (sizeof(uint16_t) * 8)
#define UINT16_T_MASK   (UINT16_T_BITS - 1)
#define UINT16_T_SHIFT  IM_LOG2(UINT16_T_MASK)

#define UINT32_T_BITS   (sizeof(uint32_t) * 8)
#define UINT32_T_MASK   (UINT32_T_BITS - 1)
#define UINT32_T_SHIFT  IM_LOG2(UINT32_T_MASK)

#define UINT64_T_BITS   (sizeof(uint64_t) * 8)
#define UINT64_T_MASK   (UINT64_T_BITS - 1)
#define UINT64_T_SHIFT  IM_LOG2(UINT64_T_MASK)
///@endcond

// STM32IPL
/**
 * @brief Structure used to access single channels of RGB888 images.
 */
typedef struct _rgb888_t
{
	uint8_t b; /**< Blue channel. */
	uint8_t g; /**< Green channel. */
	uint8_t r; /**< Red channel. */
} rgb888_t;

/////////////////
// Point Stuff //
/////////////////
/**
 * @brief Defines a 2D point in terms of x and y coordinates.
 */
typedef struct point
{
	int16_t x; /**< Horizontal coordinate of the point. */
	int16_t y; /**< Vertical coordinate of the point. */
} point_t;

////////////////
// Line Stuff //
////////////////
/**
 * @brief Defines a line in terms of horizontal and vertical coordinates of its extreme points.
 */
typedef struct line
{
	int16_t x1; /**< X-coordinate of the first point. */
	int16_t y1; /**< Y-cordinate of the first point. */
	int16_t x2; /**< X-coordinate of the second point. */
	int16_t y2; /**< Y-coordinate of the second point. */
} line_t;

/////////////////////
// Rectangle Stuff //
/////////////////////
/**
 * @brief Defines a rectangle
 */
typedef struct rectangle
{
	int16_t x; /**< X-coordinate of the top-left corner of the rectangle. */
	int16_t y; /**< Y-coordinate of the top-left corner of the rectangle. */
	int16_t w; /**< Width of the rectangle. */
	int16_t h; /**< Height of the rectangle. */
} rectangle_t;

/////////////////
// Color Stuff //
/////////////////
/**
 * @brief Represents color ranges expressed in the L*A*B* color space.
 *
 * A range is defined with minimum and maximum values for each channel.
 * The L* values can vary between 0 and 1 when these thresholds must be used to filter Binary images.
 * The L* values can vary between 0 and 255 when these thresholds must be used to filter Grayscale images.
 * The L* values can vary between 0 and 100 when these thresholds must be used to filter RGB images.
 * The A* values can vary between -128 and 127 (used only when these thresholds must be used to filter RGB images).
 * The B* values can vary between -128 and 127 (used only when these thresholds must be used to filter RGB images).
 */
typedef struct color_thresholds_list_lnk_data
{
	uint8_t LMin; /**< Minimum L* (lightness) value. */
	uint8_t LMax; /**< Maximum L* (lightness) value. */
	int8_t AMin;  /**< Minimum A* (green-red opponent) color value. */
	int8_t AMax;  /**< Maximum A* (green-red opponent) color value. */
	int8_t BMin;  /**< Minimum B* (blue-yellow opponent) color value. */
	int8_t BMax;  /**< Maximum B* (blue-yellow opponent) color value. */
} color_thresholds_list_lnk_data_t;

/////////////////
// Color Stuff //
/////////////////
#define COLOR_THRESHOLD_BINARY(pixel, threshold, invert) \
({ \
    (((threshold)->LMin <= pixel) && (pixel <= (threshold)->LMax)) ^ invert; \
})

#define COLOR_THRESHOLD_GRAYSCALE(pixel, threshold, invert) \
({ \
    (((threshold)->LMin <= pixel) && (pixel <= (threshold)->LMax)) ^ invert; \
})

#define COLOR_THRESHOLD_RGB565(pixel, threshold, invert) \
({ \
    uint8_t _l = COLOR_RGB565_TO_L(pixel); \
    int8_t _a = COLOR_RGB565_TO_A(pixel); \
    int8_t _b = COLOR_RGB565_TO_B(pixel); \
    (((threshold)->LMin <= _l) && (_l <= (threshold)->LMax) && \
    ((threshold)->AMin <= _a) && (_a <= (threshold)->AMax) && \
    ((threshold)->BMin <= _b) && (_b <= (threshold)->BMax)) ^ invert; \
})

#define COLOR_THRESHOLD_RGB888(pixel, threshold, invert) \
({ \
    uint8_t _l = COLOR_RGB888_TO_L(pixel); \
    int8_t _a = COLOR_RGB888_TO_A(pixel); \
    int8_t _b = COLOR_RGB888_TO_B(pixel); \
    (((threshold)->LMin <= _l) && (_l <= (threshold)->LMax) && \
    ((threshold)->AMin <= _a) && (_a <= (threshold)->AMax) && \
    ((threshold)->BMin <= _b) && (_b <= (threshold)->BMax)) ^ invert; \
})

#define COLOR_BOUND_BINARY(pixel0, pixel1, threshold) \
({ \
    (abs(pixel0 - pixel1) <= (threshold)); \
})

#define COLOR_BOUND_GRAYSCALE(pixel0, pixel1, threshold) \
({ \
    (abs(pixel0 - pixel1) <= (threshold)); \
})

#define COLOR_BOUND_RGB565(pixel0, pixel1, threshold) \
({ \
    (abs(COLOR_RGB565_TO_R5(pixel0) - COLOR_RGB565_TO_R5(pixel1)) <= COLOR_RGB565_TO_R5(threshold)) && \
    (abs(COLOR_RGB565_TO_G6(pixel0) - COLOR_RGB565_TO_G6(pixel1)) <= COLOR_RGB565_TO_G6(threshold)) && \
    (abs(COLOR_RGB565_TO_B5(pixel0) - COLOR_RGB565_TO_B5(pixel1)) <= COLOR_RGB565_TO_B5(threshold)); \
})

///@cond
#define COLOR_BINARY_MIN 0
#define COLOR_BINARY_MAX 1
#define COLOR_GRAYSCALE_BINARY_MIN 0x00
#define COLOR_GRAYSCALE_BINARY_MAX 0xFF
#define COLOR_RGB565_BINARY_MIN 0x0000
#define COLOR_RGB565_BINARY_MAX 0xFFFF

#define COLOR_GRAYSCALE_MIN 0
#define COLOR_GRAYSCALE_MAX 255

#define COLOR_R5_MIN 0
#define COLOR_R5_MAX 31
#define COLOR_G6_MIN 0
#define COLOR_G6_MAX 63
#define COLOR_B5_MIN 0
#define COLOR_B5_MAX 31

#define COLOR_R8_MIN 0
#define COLOR_R8_MAX 255
#define COLOR_G8_MIN 0
#define COLOR_G8_MAX 255
#define COLOR_B8_MIN 0
#define COLOR_B8_MAX 255

#define COLOR_L_MIN 0
#define COLOR_L_MAX 100
#define COLOR_A_MIN -128
#define COLOR_A_MAX 127
#define COLOR_B_MIN -128
#define COLOR_B_MAX 127

#define COLOR_Y_MIN 0
#define COLOR_Y_MAX 255
#define COLOR_U_MIN -128
#define COLOR_U_MAX 127
#define COLOR_V_MIN -128
#define COLOR_V_MAX 127
///@endcond

// RGB565 Stuff //
#define COLOR_RGB565_TO_R5(pixel) (((pixel) >> 11) & 0x1F)

#define COLOR_RGB565_TO_R8(pixel) \
({ \
	uint16_t __pixel = (pixel); \
	__pixel = (__pixel >> 8) & 0xF8; \
	__pixel | (__pixel >> 5); \
})

#define COLOR_RGB565_TO_G6(pixel) (((pixel) >> 5) & 0x3F)

#define COLOR_RGB565_TO_G8(pixel) \
({ \
	uint16_t __pixel = (pixel); \
	__pixel = (__pixel >> 3) & 0xFC; \
	__pixel | (__pixel >> 6); \
})

#define COLOR_RGB565_TO_B5(pixel) ((pixel) & 0x1F)

#define COLOR_RGB565_TO_B8(pixel) \
({ \
	uint16_t __pixel = (pixel); \
	__pixel = (__pixel << 3) & 0xF8; \
	__pixel | (__pixel >> 5); \
})

#define COLOR_R5_G6_B5_TO_RGB565(r5, g6, b5) (((r5) << 11) | ((g6) << 5) | (b5))

#define COLOR_R8_G8_B8_TO_RGB565(r8, g8, b8) ((((r8) & 0xF8) << 8) | (((g8) & 0xFC) << 3) | ((b8) >> 3))

#define COLOR_RGB888_TO_Y(r8, g8, b8) ((((r8) * 38) + ((g8) * 75) + ((b8) * 15)) >> 7) // 0.299R + 0.587G + 0.114B

#define COLOR_RGB565_TO_Y(rgb565) \
({ \
	int r = COLOR_RGB565_TO_R8((rgb565)); \
	int g = COLOR_RGB565_TO_G8((rgb565)); \
	int b = COLOR_RGB565_TO_B8((rgb565)); \
	COLOR_RGB888_TO_Y(r, g, b); \
})

#define COLOR_Y_TO_RGB888(pixel) ((pixel) * 0x010101)

#define COLOR_Y_TO_RGB565(pixel) \
({ \
	int __rb_pixel = ((pixel) >> 3) & 0x1F; \
	(__rb_pixel * 0x0801) + (((pixel) << 3) & 0x7E0); \
})

#define COLOR_RGB888_TO_U(r8, g8, b8) ((((r8) * -21) - ((g8) * 43) + ((b8) * 64)) >> 7) // -0.168736R - 0.331264G + 0.5B

#define COLOR_RGB565_TO_U(rgb565) \
({ \
	int r = COLOR_RGB565_TO_R8((rgb565)); \
	int g = COLOR_RGB565_TO_G8((rgb565)); \
	int b = COLOR_RGB565_TO_B8((rgb565)); \
	COLOR_RGB888_TO_U(r, g, b); \
})

#define COLOR_RGB888_TO_V(r8, g8, b8) ((((r8) * 64) - ((g8) * 54) - ((b8) * 10)) >> 7) // 0.5R - 0.418688G - 0.081312B

#define COLOR_RGB565_TO_V(rgb565) \
({ \
	int r = COLOR_RGB565_TO_R8((rgb565)); \
	int g = COLOR_RGB565_TO_G8((rgb565)); \
	int b = COLOR_RGB565_TO_B8((rgb565)); \
	COLOR_RGB888_TO_V(r, g, b); \
})

extern const int8_t lab_table[196608 / 2];

#ifdef IMLIB_ENABLE_LAB_LUT
#define COLOR_RGB565_TO_L(pixel) lab_table[((pixel>>1) * 3) + 0]
#define COLOR_RGB565_TO_A(pixel) lab_table[((pixel>>1) * 3) + 1]
#define COLOR_RGB565_TO_B(pixel) lab_table[((pixel>>1) * 3) + 2]
#else
#define COLOR_RGB565_TO_L(pixel) imlib_rgb565_to_l(pixel)
#define COLOR_RGB565_TO_A(pixel) imlib_rgb565_to_a(pixel)
#define COLOR_RGB565_TO_B(pixel) imlib_rgb565_to_b(pixel)
#endif

// FIXME: lut based version is missing here.
#define COLOR_RGB888_TO_L(pixel) imlib_rgb888_to_l(pixel) // STM32IPL
#define COLOR_RGB888_TO_A(pixel) imlib_rgb888_to_a(pixel) // STM32IPL
#define COLOR_RGB888_TO_B(pixel) imlib_rgb888_to_b(pixel) // STM32IPL

#define COLOR_LAB_TO_RGB565(l, a, b) imlib_lab_to_rgb(l, a, b)
#define COLOR_YUV_TO_RGB565(y, u, v) imlib_yuv_to_rgb((y) + 128, u, v)

#define COLOR_YUV_TO_RGB888(y, u, v) imlib_yuv_to_rgb888((y) + 128, u, v) // STM32IPL
#define COLOR_LAB_TO_RGB888(l, a, b) imlib_lab_to_rgb888(l, a, b) // STM32IPL

#define COLOR_BAYER_TO_RGB565(img, x, y, r, g, b)            \
({                                                           \                             \
    if ((y % 2) == 0) {                                    \
        if ((x % 2) == 0) {                                \
            r = (IM_GET_RAW_PIXEL(img, x-1, y-1)  +      \
                 IM_GET_RAW_PIXEL(img, x+1, y-1)  +      \
                 IM_GET_RAW_PIXEL(img, x-1, y+1)  +      \
                 IM_GET_RAW_PIXEL(img, x+1, y+1)) >> 2;  \
                                                             \
            g = (IM_GET_RAW_PIXEL(img, x,   y-1)  +      \
                 IM_GET_RAW_PIXEL(img, x,   y+1)  +      \
                 IM_GET_RAW_PIXEL(img, x-1, y)    +      \
                 IM_GET_RAW_PIXEL(img, x+1, y))   >> 2;  \
                                                             \
            b = IM_GET_RAW_PIXEL(img,  x, y);            \
        } else {                                             \
            r = (IM_GET_RAW_PIXEL(img, x, y-1)  +        \
                 IM_GET_RAW_PIXEL(img, x, y+1)) >> 1;    \
                                                             \
            b = (IM_GET_RAW_PIXEL(img, x-1, y)  +        \
                 IM_GET_RAW_PIXEL(img, x+1, y)) >> 1;    \
                                                             \
            g =  IM_GET_RAW_PIXEL(img, x, y);            \
        }                                                    \
    } else {                                                 \
        if ((x % 2) == 0) {                                \
            r = (IM_GET_RAW_PIXEL(img, x-1, y)  +        \
                 IM_GET_RAW_PIXEL(img, x+1, y)) >> 1;    \
                                                             \
            g =  IM_GET_RAW_PIXEL(img, x, y);            \
                                                             \
            b = (IM_GET_RAW_PIXEL(img, x, y-1)  +        \
                 IM_GET_RAW_PIXEL(img, x, y+1)) >> 1;    \
        } else {                                             \
            r = IM_GET_RAW_PIXEL(img,  x, y);            \
                                                             \
            g = (IM_GET_RAW_PIXEL(img, x, y-1)    +      \
                 IM_GET_RAW_PIXEL(img, x, y+1)    +      \
                 IM_GET_RAW_PIXEL(img, x-1, y)    +      \
                 IM_GET_RAW_PIXEL(img, x+1, y))   >> 2;  \
                                                             \
            b = (IM_GET_RAW_PIXEL(img, x-1, y-1)  +      \
                 IM_GET_RAW_PIXEL(img, x+1, y-1)  +      \
                 IM_GET_RAW_PIXEL(img, x-1, y+1)  +      \
                 IM_GET_RAW_PIXEL(img, x+1, y+1)) >> 2;  \
        }                                                    \
    }                                                        \
    r  = r >> 3;                                             \
    g  = g >> 2;                                             \
    b  = b >> 3;                                             \
})

#define COLOR_BINARY_TO_GRAYSCALE(pixel) ((pixel) * COLOR_GRAYSCALE_MAX)
#define COLOR_BINARY_TO_RGB565(pixel) COLOR_YUV_TO_RGB565(((pixel) ? 127 : -128), 0, 0)
#define COLOR_BINARY_TO_RGB888(pixel) COLOR_YUV_TO_RGB888(((pixel) ? 127 : -128), 0, 0) // STM32IPL
#define COLOR_RGB565_TO_BINARY(pixel) (COLOR_RGB565_TO_Y(pixel) > (((COLOR_Y_MAX - COLOR_Y_MIN) / 2) + COLOR_Y_MIN))
#define COLOR_RGB565_TO_GRAYSCALE(pixel) COLOR_RGB565_TO_Y(pixel)
#define COLOR_GRAYSCALE_TO_BINARY(pixel) ((pixel) > (((COLOR_GRAYSCALE_MAX - COLOR_GRAYSCALE_MIN) / 2) + COLOR_GRAYSCALE_MIN))
#define COLOR_GRAYSCALE_TO_RGB565(pixel) COLOR_YUV_TO_RGB565(((pixel) - 128), 0, 0)
#define COLOR_RGB888_TO_GRAYSCALE(pixel) COLOR_RGB888_TO_Y((pixel).r, (pixel).g, (pixel).b) // STM32IPL
#define COLOR_RGB888_TO_BINARY(pixel) (COLOR_RGB888_TO_GRAYSCALE(pixel) > (((COLOR_Y_MAX - COLOR_Y_MIN) / 2) + COLOR_Y_MIN)) // STM32IPL

/////////////////
// Image Stuff //
/////////////////
/**
 * @brief Enumerator representing the image's data formats.
 */
typedef enum image_bpp
{
	IMAGE_BPP_BINARY,       /* BPP = 0 */			/**< Binary image. Each pixel can assume 0-1 values. Image lines are padded with zeros and aligned to 32 bits. */
	IMAGE_BPP_GRAYSCALE,    /* BPP = 1 */			/**< Grayscale image. Each pixel can assume values in the range [0, 255]. */
	IMAGE_BPP_RGB565,       /* BPP = 2 */			/**< Color image. Each pixel is represented with 16 bits; R and B channels are described with 5 bits, G with 6 bits. */
	IMAGE_BPP_BAYER,        /* BPP = 3 */			/**< Not used by STM32IPL. */
	IMAGE_BPP_RGB888,       /* BPP = 4 STM32IPL */	/**< Color image. Each pixel is represented with 24 bits, 8 bits for each EGB channel. */
	IMAGE_BPP_BGR888,       /* BPP = 4 STM32IPL */	/**< Color image. Each pixel is represented with 24 bits, 8 bits for each EGB channel. */
	IMAGE_BPP_JPEG          /* BPP > 4 */			/**< Not used by STM32IPL. */
} image_bpp_t;

/**
 * @brief Represents the image in terms of its width, height, format, pointer to the pixels data.
 */
typedef struct image
{
	int w;		/**< Width of the image (pixels). */
	int h;		/**< Height of the image (pixels). */
	int bpp;	/**< Format of the image (actually contains image_bpp_t values). */
	union
	{
		uint8_t *pixels;	/**< Pointer to the pixels data. */
		uint8_t *data;		/**< Pointer to the pixels data. */
	};
} image_t;

///@cond
#define IMAGE_BINARY_LINE_LEN(image) (((image)->w + UINT32_T_MASK) >> UINT32_T_SHIFT)
#define IMAGE_BINARY_LINE_LEN_BYTES(image) (IMAGE_BINARY_LINE_LEN(image) * sizeof(uint32_t))

#define IMAGE_GRAYSCALE_LINE_LEN(image) ((image)->w)
#define IMAGE_GRAYSCALE_LINE_LEN_BYTES(image) (IMAGE_GRAYSCALE_LINE_LEN(image) * sizeof(uint8_t))

#define IMAGE_RGB565_LINE_LEN(image) ((image)->w)
#define IMAGE_RGB565_LINE_LEN_BYTES(image) (IMAGE_RGB565_LINE_LEN(image) * sizeof(uint16_t))

// STM32IPL
#define IMAGE_RGB888_LINE_LEN(image) ((image)->w)
#define IMAGE_RGB888_LINE_LEN_BYTES(image) (IMAGE_RGB888_LINE_LEN(image) * sizeof(rgb888_t))

#define IMAGE_GET_BINARY_PIXEL(image, x, y) \
({ \
    (((uint32_t *)(image)->data)[((((image)->w + UINT32_T_MASK) >> UINT32_T_SHIFT) * (y)) + ((x) >> UINT32_T_SHIFT)] >> ((x) & UINT32_T_MASK)) & 1; \
})

#define IMAGE_PUT_BINARY_PIXEL(image, x, y, v) \
({ \
    size_t _i = ((((image)->w + UINT32_T_MASK) >> UINT32_T_SHIFT) * (y)) + ((x) >> UINT32_T_SHIFT); \
    size_t _j = (x) & UINT32_T_MASK; \
    ((uint32_t *)(image)->data)[_i] = (((uint32_t *)(image)->data)[_i] & (~(1 << _j))) | (((v) & 1) << _j); \
})

#define IMAGE_CLEAR_BINARY_PIXEL(image, x, y) \
({ \
    ((uint32_t *)(image)->data)[((((image)->w + UINT32_T_MASK) >> UINT32_T_SHIFT) * (y)) + ((x) >> UINT32_T_SHIFT)] &= ~(1 << ((x) & UINT32_T_MASK)); \
})

#define IMAGE_SET_BINARY_PIXEL(image, x, y) \
({ \
    ((uint32_t *)(image)->data)[((((image)->w + UINT32_T_MASK) >> UINT32_T_SHIFT) * (y)) + ((x) >> UINT32_T_SHIFT)] |= 1 << ((x) & UINT32_T_MASK); \
})

#define IMAGE_GET_GRAYSCALE_PIXEL(image, x, y) \
({ \
    ((uint8_t *)(image)->data)[((image)->w * (y)) + (x)]; \
})

#define IMAGE_PUT_GRAYSCALE_PIXEL(image, x, y, v) \
({ \
    ((uint8_t *)(image)->data)[((image)->w * (y)) + (x)] = (v); \
})

#define IMAGE_GET_RGB565_PIXEL(image, x, y) \
({ \
    ((uint16_t *)(image)->data)[((image)->w * (y)) + (x)]; \
})

#define IMAGE_PUT_RGB565_PIXEL(image, x, y, v) \
({ \
    ((uint16_t *)(image)->data)[((image)->w * (y)) + (x)] = (v); \
})

// STM32IPL
#define IMAGE_PUT_RGB888_PIXEL(image, x, y, v) \
({ \
    ((rgb888_t *)(image)->data)[((image)->w * (y)) + (x)] = (v); \
})

// STM32IPL
#define IMAGE_GET_RGB888_PIXEL(image, x, y) \
({ \
	((rgb888_t *)(image)->data)[((image)->w * (y)) + (x)]; \
})

// Fast Stuff //
#define IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(image, y) \
({ \
   ((uint32_t*)((image)->data)) + ((((image)->w + UINT32_T_MASK) >> UINT32_T_SHIFT) * (y)); \
})

#define IMAGE_GET_BINARY_PIXEL_FAST(row_ptr, x) \
({ \
    (row_ptr[(x) >> UINT32_T_SHIFT] >> ((x) & UINT32_T_MASK)) & 1; \
})

#define IMAGE_PUT_BINARY_PIXEL_FAST(row_ptr, x, v) \
({ \
    size_t _i = (x) >> UINT32_T_SHIFT; \
    size_t _j = (x) & UINT32_T_MASK; \
    row_ptr[_i] = (row_ptr[_i] & (~(1 << _j))) | (((v) & 1) << _j); \
})

#define IMAGE_CLEAR_BINARY_PIXEL_FAST(row_ptr, x) \
({ \
    row_ptr[(x) >> UINT32_T_SHIFT] &= ~(1 << ((x) & UINT32_T_MASK)); \
})

#define IMAGE_SET_BINARY_PIXEL_FAST(row_ptr, x) \
({ \
    row_ptr[(x) >> UINT32_T_SHIFT] |= 1 << ((x) & UINT32_T_MASK); \
})

#define IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(image, y) \
({ \
    ((uint8_t *)(image)->data) + ((image)->w * (y)); \
})

#define IMAGE_GET_GRAYSCALE_PIXEL_FAST(row_ptr, x) \
({ \
    row_ptr[(x)]; \
})

#define IMAGE_PUT_GRAYSCALE_PIXEL_FAST(row_ptr, x, v) \
({ \
    row_ptr[(x)] = (v); \
})

#define IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(image, y) \
({ \
    ((uint16_t *)(image)->data) + ((image)->w * (y)); \
})

#define IMAGE_GET_RGB565_PIXEL_FAST(row_ptr, x) \
({ \
    row_ptr[(x)]; \
})

#define IMAGE_PUT_RGB565_PIXEL_FAST(row_ptr, x, v) \
({ \
    row_ptr[(x)] = (v); \
})

// STM32IPL
#define IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(image, y) \
({ \
    ((rgb888_t*)((image)->data)) + ((image)->w * (y)); \
})

// STM32IPL
#define IMAGE_GET_RGB888_PIXEL_FAST(row_ptr, x) \
({ \
    (row_ptr)[(x)]; \
})

// STM32IPL
#define IMAGE_PUT_RGB888_PIXEL_FAST(row_ptr, x, v) \
({ \
    (row_ptr)[(x)] = (v); \
})

// Old Image Macros - Will be refactor and removed. But, only after making sure through testing new macros work.

#define IM_RGB5652L(p) \
    ({lab_table[(((p) >> 1) * 3) + 0];})

#define IM_RGB5652A(p) \
    ({lab_table[(((p) >> 1) * 3) + 1];})

#define IM_RGB5652B(p) \
    ({lab_table[(((p) >> 1) * 3) + 2];})

// Grayscale maxes
#define IM_MAX_GS (255)

// RGB565 maxes
#define IM_MAX_R5 (31)
#define IM_MAX_G6 (63)
#define IM_MAX_B5 (31)

// Grayscale histogram
#define IM_G_HIST_SIZE (256)
#define IM_G_HIST_OFFSET (0)

// LAB histogram
#define IM_L_HIST_SIZE (256)
#define IM_L_HIST_OFFSET (0)
#define IM_A_HIST_SIZE (256)
#define IM_A_HIST_OFFSET (256)
#define IM_B_HIST_SIZE (256)
#define IM_B_HIST_OFFSET (512)

#define IM_IS_BINARY(img) \
    ({img->bpp == IMAGE_BPP_BINARY;})

#define IM_IS_GS(img) \
    ({img->bpp == IMAGE_BPP_GRAYSCALE;})

#define IM_IS_RGB565(img) \
    ({img->bpp == IMAGE_BPP_RGB565;})

#define IM_IS_BAYER(img) \
    ({img->bpp == IMAGE_BPP_BAYER;})

#define IM_IS_JPEG(img) \
    ({img->bpp >= IMAGE_BPP_JPEG;})

#define IM_IS_MUTABLE(img) \
    ({(img->bpp == IMAGE_BPP_GRAYSCALE || img->bpp == IMAGE_BPP_RGB565);})

#define IM_X_INSIDE(img, x) \
    ({(0 <= (x)) && ((x) < img->w);})

#define IM_Y_INSIDE(img, y) \
    ({(0 <= (y)) && ((y) < img->h);})

#define IM_GET_GS_PIXEL(img, x, y) \
    ({((uint8_t*)img->pixels)[((y) * img->w) + (x)];})

#define IM_GET_RAW_PIXEL(img, x, y) \
    ({((uint8_t*)img->pixels)[((y) * img->w) + (x)];})

#define IM_GET_RAW_PIXEL_CHECK_BOUNDS_X(img, x, y) \
    ({((uint8_t*)img->pixels)[((y) * img->w) + (((x) < 0) ? 0 : ((x) >= img->w) ? (img->w - 1) : (x))];})

#define IM_GET_RAW_PIXEL_CHECK_BOUNDS_Y(img, x, y) \
    ({((uint8_t*)img->pixels)[((((y) < 0) ? 0 : ((y) >= img->h) ? (img->h - 1) : (y)) * img->w) + (x)];})

#define IM_GET_RAW_PIXEL_CHECK_BOUNDS_XY(img, x, y)	\
	({((uint8_t*)img->pixels)[(((y) < 0) ? 0 : (((y) >= img->h) ? (img->h - 1) : ((y) * img->w))) + \
							  (((x) < 0) ? 0 : (((x) >= img->w) ? (img->w - 1) : (x)))];})

#define IM_GET_RGB565_PIXEL(img, x, y) \
    ({((uint16_t*)img->pixels)[((y) * img->w) + (x)];})

#define IM_GET_RGB888_PIXEL(img, x, y) \
    ({((rgb888_t*)img->pixels)[((y) * img->w) + (x)];})

#define IM_SET_GS_PIXEL(img, x, y, p) \
    ({((uint8_t*)img->pixels)[((y) * img->w) + (x)] = (p);})

#define IM_SET_RGB565_PIXEL(img, x, y, p) \
    ({((uint16_t*)img->pixels)[((y) * img->w) + (x)] = (p);})

#define IM_SET_RGB888_PIXEL(img, x, y, p) \
    ({((rgb888_t*)img->pixels)[((y) * img->w) + (x)] = (p);})

#define IM_EQUAL(img0, img1) \
    ({(img0->w==img1->w)&&(img0->h==img1->h)&&(img0->bpp==img1->bpp);})

#define IM_TO_GS_PIXEL(img, x, y)    \
    ( img->bpp == IMAGE_BPP_GRAYSCALE ? img->pixels[((y)*img->w)+(x)] : \
    img->bpp == IMAGE_BPP_RGB565 ? COLOR_RGB565_TO_Y(((uint16_t*)img->pixels)[((y)*img->w)+(x)]) : \
    COLOR_RGB888_TO_Y( ((uint8_t*)img->pixels)[(3 * ((y) * img->w + x)) + 2], ((uint8_t*)img->pixels)[ (3 * ((y) * img->w + x)) + 1], ((uint8_t*)img->pixels)[ (3 * ((y) * img->w + x))]))
///@endcond

/**
 * @brief Structure describing an integral image.
 */
typedef struct integral_image
{
	int w;			/**< Width.*/
	int h;			/**< Height*/
	uint32_t *data;	/**< Data.*/
} i_image_t;

/**
 * @brief Structure describing an integral image using a moving window.
 */
typedef struct
{
	int w;				/**< Width.*/
	int h;				/**< Height*/
	int y_offs;			/**< Vertical offset. */
	int x_ratio;		/**< Horizontal ratio. */
	int y_ratio;		/**< Vertical ratio. */
	uint32_t **data;	/**< Data.*/
	uint32_t **swap;	/**< Swap buffer.*/
} mw_image_t;

/**
 * @brief Structure describing a window size.
 */
typedef struct size
{
	int w;	/**< Width.*/
	int h;	/**< Height*/
} wsize_t;

/**
 * @brief Structure describing a Haar cascade.
 */
typedef struct cascade
{
	int std;						/**< Image standard deviation.*/
	int step;						/**< Image scanning factor.*/
	float threshold;				/**< Detection threshold.*/
	float scale_factor;				/**< Image scaling factor.*/
	int n_stages;					/**< Number of stages in the cascade.*/
	int n_features;					/**< Number of features in the cascade.*/
	int n_rectangles;				/**< Number of rectangles in the cascade.*/
	wsize_t window;					/**< Detection window size.*/
	image_t *img;					/**< Grayscale image.*/
	mw_image_t *sum;				/**< Integral image.*/
	mw_image_t *ssq;				/**< Squared integral image.*/
	uint8_t *stages_array;			/**< Number of features per stage.*/
	int16_t *stages_thresh_array;	/**< Stages thresholds.*/
	int16_t *tree_thresh_array;		/**< Features threshold (1 per feature).*/
	int16_t *alpha1_array;			/**< Alpha1 array (1 per feature).*/
	int16_t *alpha2_array;			/**< Alpha2 array (1 per feature).*/
	int8_t *num_rectangles_array;	/**< Number of rectangles per features (1 per feature).*/
	int8_t *weights_array;			/**< Rectangles weights (1 per rectangle).*/
	int8_t *rectangles_array;		/**< Rectangles array.*/
} cascade_t;

/**
 * @brief Kind of possible template matching algorithms.
 */
typedef enum template_match
{
	SEARCH_EX, /**< Exhaustive search. */
	SEARCH_DS, /**< Diamond search. */
} template_match_t;

/**
 * @brief LAB histogram.
 */
typedef struct histogram
{
	int LBinCount;	/**< Number of L bins. */
	float *LBins;	/**< Pointer to the L bins. */
	int ABinCount;	/**< Number of A bins. */
	float *ABins;	/**< Pointer to the A bins. */
	int BBinCount;	/**< Number of B bins. */
	float *BBins;	/**< Pointer to the B bins. */
} histogram_t;

/**
 * @brief LAB color percentile.
 */
typedef struct percentile
{
	uint8_t LValue;	/**< Lightness (or Grayscale) percentile. */
	int8_t AValue;	/**< A percentile. */
	int8_t BValue;	/**< B percentile. */
} percentile_t;

/**
 * @brief LAB threshold.
 */
typedef struct threshold
{
	uint8_t LValue;	/**< Lightness (or Grayscale) value. */
	int8_t AValue;	/**< A value. */
	int8_t BValue;	/**< B value. */
} threshold_t;

/**
 * @brief LAB statistics calculated on an image.
 *
 * Represents mean, median, mode, standard deviation, min, max,
 * LQ (Grayscale Lower Quartile), UQ (Grayscale Upper Quartile) for each LAB channel.
 */
typedef struct statistics
{
	uint8_t LMean;		/**< Mean value of L channel. */
	uint8_t LMedian;	/**< Median value of L channel. */
	uint8_t LMode;		/**< Mode value of L channel. */
	uint8_t LSTDev;		/**< Standard deviation value of L channel. */
	uint8_t LMin;		/**< Min value of L channel. */
	uint8_t LMax;		/**< Max value of L channel. */
	uint8_t LLQ;		/**< Grayscale Lower Quartile value of L channel. */
	uint8_t LUQ;		/**< Grayscale Upper Quartile value of L channel. */

	int8_t AMean;		/**< Mean value of A channel. */
	int8_t AMedian;		/**< Median value of A channel. */
	int8_t AMode;		/**< Mode value of A channel. */
	int8_t ASTDev;		/**< Standard deviation value of A channel. */
	int8_t AMin;		/**< Min value of A channel. */
	int8_t AMax;		/**< Max value of A channel. */
	int8_t ALQ;			/**< Grayscale Lower Quartile value of A channel. */
	int8_t AUQ;			/**< Grayscale Upper Quartile value of A channel. */

	int8_t BMean;		/**< Mean value of B channel. */
	int8_t BMedian;		/**< Median value of B channel. */
	int8_t BMode;		/**< Mode value of B channel. */
	int8_t BSTDev;		/**< Standard deviation value of B channel. */
	int8_t BMin;		/**< Min value of B channel. */
	int8_t BMax;		/**< Max value of B channel. */
	int8_t BLQ;			/**< Grayscale Lower Quartile value of B channel. */
	int8_t BUQ;			/**< Grayscale Upper Quartile value of B channel. */
} statistics_t;

/**
 * @def FIND_BLOBS_CORNERS_RESOLUTION
 * @brief Defines the maximum points corners around a blob.
 *
 * Must be multiple of 4
 */
#define FIND_BLOBS_CORNERS_RESOLUTION 20  //multiple of 4

/**
 * @brief Blob representation.
 */
typedef struct find_blobs_list_lnk_data
{
	point_t corners[FIND_BLOBS_CORNERS_RESOLUTION];	/**< Representation using points. */
	rectangle_t rect;								/**< Representation using rectangle. */
	uint32_t pixels;								/**< Number of pixels composing the blob. */
	uint32_t perimeter;								/**< Size of blob's perimeter. */
	uint32_t code;									/**< Identification code of blob*/
	uint32_t count;									/**< Number of merged blobs. */
	float centroid_x;								/**< X center of the blob. */
	float centroid_y;								/**< Y center of the blob. */
	float rotation;									/**< Rotation of the blob (radians). */
	float roundness;								/**< Value (in the range [0, 1]) representing how round the object is; a circle has roundness = 1. */
	uint16_t x_hist_bins_count;						/**< Number of bins on the x-axis of histogram. */
	uint16_t y_hist_bins_count;						/**< Number of bins on the y-axis of histogram. */
	uint16_t *x_hist_bins;							/**< Histogram of the x-axis of all columns in a blob. Bin values are scaled between 0 and 1. */
	uint16_t *y_hist_bins;							/**< Histogram of the y-axis of all columns in a blob. Bin values are scaled between 0 and 1. */
	float centroid_x_acc;							/**< Not used by STM32IPL. */
	float centroid_y_acc;							/**< Not used by STM32IPL. */
	float rotation_acc_x;							/**< Not used by STM32IPL. */
	float rotation_acc_y;							/**< Not used by STM32IPL. */
	float roundness_acc;							/**< Not used by STM32IPL. */
} find_blobs_list_lnk_data_t;

/**
 * @brief Full line representation.
 *
 * Representation of the line in Cartesian and Polar coordinates with its magnitude.
 */
typedef struct find_lines_list_lnk_data
{
	line_t line;		/**< Line expressed in Cartesian coordinates. */
	uint32_t magnitude;	/**< Sum of all Sobel filter magnitudes of pixels that make up that line. */
	int16_t theta;		/**< Theta value of the line in Polar coordinates. */
	int16_t rho;		/**< Rho value of the line in Polar coordinates. */
} find_lines_list_lnk_data_t;

/**
 * @brief Circle representation.
 */
typedef struct find_circles_list_lnk_data
{
	point_t p;			/**< Center of the circle (X,Y coordinates). */
	uint16_t r;			/**< Radius of the circle (pixels). */
	uint16_t magnitude;	/**< Sum of all Sobel filter magnitudes of pixels that make up that circle. */
} find_circles_list_lnk_data_t;

///@cond
/* Color space functions. */
int8_t imlib_rgb565_to_l(uint16_t pixel);
int8_t imlib_rgb565_to_a(uint16_t pixel);
int8_t imlib_rgb565_to_b(uint16_t pixel);
int8_t imlib_rgb888_to_l(rgb888_t pixel); // STM32IPL
int8_t imlib_rgb888_to_a(rgb888_t pixel); // STM32IPL
int8_t imlib_rgb888_to_b(rgb888_t pixel); // STM32IPL
rgb888_t imlib_lab_to_rgb888(uint8_t l, int8_t a, int8_t b); // STM32IPL
uint16_t imlib_lab_to_rgb(uint8_t l, int8_t a, int8_t b);
uint16_t imlib_yuv_to_rgb(uint8_t y, int8_t u, int8_t v);
rgb888_t imlib_yuv_to_rgb888(uint8_t y, int8_t u, int8_t v); // STM32IPL
///@endcond

#endif //__STM32IPL_IMLIB_EXT_H__
