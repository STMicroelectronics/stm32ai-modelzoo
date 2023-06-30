/**
 ******************************************************************************
 * @file   stm32ipl.h
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library functions header file
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

#ifndef __STM32IPL_H_
#define __STM32IPL_H_

#include "stm32ipl_conf.h"
#include "stm32ipl_imlib.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifndef M_PI
#define M_PI    3.14159265f
#endif

#ifndef M_PI_2
#define M_PI_2  1.57079632f
#endif

#define STM32IPL_UNUSED(x)           ((void)(x))
#define STM32IPL_MAX(a, b)           ((a) > (b) ? (a) : (b))
#define STM32IPL_MIN(a, b)           ((a) < (b) ? (a) : (b))
#define STM32IPL_DEG2RAD(x)          (((x) * M_PI) / 180)
#define STM32IPL_RAD2DEG(x)          (((x) * 180) / M_PI)

#define STM32IPL_COLOR_BLUE          0x0000FFUL
#define STM32IPL_COLOR_GREEN         0x00FF00UL
#define STM32IPL_COLOR_RED           0xFF0000UL
#define STM32IPL_COLOR_CYAN          0x00FFFFUL
#define STM32IPL_COLOR_MAGENTA       0xFF00FFUL
#define STM32IPL_COLOR_YELLOW        0xFFFF00UL
#define STM32IPL_COLOR_LIGHTBLUE     0x8080FFUL
#define STM32IPL_COLOR_LIGHTGREEN    0x80FF80UL
#define STM32IPL_COLOR_LIGHTRED      0xFF8080UL
#define STM32IPL_COLOR_LIGHTCYAN     0x80FFFFUL
#define STM32IPL_COLOR_LIGHTMAGENTA  0xFF80FFUL
#define STM32IPL_COLOR_LIGHTYELLOW   0xFFFF80UL
#define STM32IPL_COLOR_DARKBLUE      0x000080UL
#define STM32IPL_COLOR_DARKGREEN     0x008000UL
#define STM32IPL_COLOR_DARKRED       0x800000UL
#define STM32IPL_COLOR_DARKCYAN      0x008080UL
#define STM32IPL_COLOR_DARKMAGENTA   0x800080UL
#define STM32IPL_COLOR_DARKYELLOW    0x808000UL
#define STM32IPL_COLOR_WHITE         0xFFFFFFUL
#define STM32IPL_COLOR_LIGHTGRAY     0xD3D3D3UL
#define STM32IPL_COLOR_GRAY          0x808080UL
#define STM32IPL_COLOR_DARKGRAY      0x404040UL
#define STM32IPL_COLOR_BLACK         0x000000UL
#define STM32IPL_COLOR_BROWN         0xA52A2AUL
#define STM32IPL_COLOR_ORANGE        0xFFA500UL

#define STM32IPL_IF_ALL              (stm32ipl_if_binary | stm32ipl_if_grayscale | stm32ipl_if_rgb565 | stm32ipl_if_rgb888)
#define STM32IPL_IF_RGB_ONLY         (stm32ipl_if_rgb565 | stm32ipl_if_rgb888)
#define STM32IPL_IF_NOT_RGB          (stm32ipl_if_binary | stm32ipl_if_grayscale)
#define STM32IPL_IF_NOT_RGB88        (stm32ipl_if_binary | stm32ipl_if_grayscale | stm32ipl_if_rgb565)
#define STM32IPL_IF_GRAY_ONLY        (stm32ipl_if_grayscale)

#define STM32IPL_CHECK_VALID_IMAGE(img) \
	if (!img || !img->data) \
		return stm32ipl_err_InvalidParameter; \

#define STM32IPL_CHECK_FORMAT(img, formats) \
if (!STM32Ipl_ImageFormatSupported((img), (formats))) \
	return stm32ipl_err_UnsupportedFormat; \

#define STM32IPL_CHECK_SAME_SIZE(src, dst) \
	if ((src->w != dst->w) || (src->h != dst->h)) \
		return stm32ipl_err_InvalidParameter; \

#define STM32IPL_CHECK_SAME_FORMAT(src, dst) \
	if (src->bpp != dst->bpp) \
		return stm32ipl_err_InvalidParameter; \

#define STM32IPL_CHECK_SAME_HEADER(src, dst) \
	if ((src->w != dst->w) || (src->h != dst->h) || (src->bpp != dst->bpp)) \
		return stm32ipl_err_InvalidParameter; \

#define STM32IPL_CHECK_VALID_PTR_ARG(ptr) \
	if (!ptr) return stm32ipl_err_InvalidParameter; \

#define STM32IPL_CHECK_VALID_ROI(img, roi) \
{ \
	rectangle_t _fullRoi; \
	STM32Ipl_RectInit(&_fullRoi, 0, 0, img->w, img->h); \
	if (!STM32Ipl_RectContain(&_fullRoi, roi)) \
		return stm32ipl_err_WrongROI; \
}

#define STM32IPL_GET_REAL_ROI(img, roi, realRoi) \
	if (roi) { \
		STM32IPL_CHECK_VALID_ROI(img, roi) \
		*realRoi = *roi; \
	} else \
		STM32Ipl_RectInit(realRoi, 0, 0, img->w, img->h); \

/**
 * @brief STM32IPL color type. It has 0xRRGGBB format.
 * STM32IPL_COLOR_xxx colors follow such format.
 */
typedef uint32_t stm32ipl_color_t;	/**< STM32IPL color type. It has 0xRRGGBB format. */

/**
 * @brief STM32IPL error types.
 */
typedef enum _stm32ipl_err_t
{
	stm32ipl_err_Ok                 =   0,	/**< No error. */
	stm32ipl_err_Generic            =  -1,	/**< Generic error. */
	stm32ipl_err_InvalidParameter   =  -2,	/**< Function parameter is not valid. */
	stm32ipl_err_OutOfMemory        =  -3,	/**< No memory is available. */
	stm32ipl_err_BadPointer         =  -4,	/**< Invalid pointer. */
	stm32ipl_err_UnsupportedFormat  =  -5,	/**< Format is not supported. */
	stm32ipl_err_OpeningFile        =  -6,	/**< Error opening file. */
	stm32ipl_err_ClosingFile        =  -7,	/**< Error closing file. */
	stm32ipl_err_ReadingFile        =  -8,	/**< Error reading file. */
	stm32ipl_err_WritingFile        =  -9,	/**< Error writing file. */
	stm32ipl_err_SeekingFile        = -10,	/**< Error seeking file. */
	stm32ipl_err_NotImplemented     = -11,	/**< Function is not implemented. */
	stm32ipl_err_OpNotCompleted     = -12,	/**< Operation was not completed. */
	stm32ipl_err_WrongSize          = -13,	/**< Size is wrong. */
	stm32ipl_err_EmptyImage         = -14,	/**< Image is empty. */
	stm32ipl_err_EmptyMatrix        = -15,	/**< Matrix is empty. */
	stm32ipl_err_WrongMatrixDim     = -16,	/**< Matrix has wrong dimension. */
	stm32ipl_err_ZeroMatrixDim      = -17,	/**< Matrix has zero dimension. */
	stm32ipl_err_ReadingDatabase    = -18,	/**< Error reading the database. */
	stm32ipl_err_WritingDatabase    = -19,	/**< Error writing the database. */
	stm32ipl_err_UnsupportedMethod  = -20,	/**< Method is not supported. */
	stm32ipl_err_NotAllowed         = -21,	/**< Operation is not allowed. */
	stm32ipl_err_NotInPlaceFunction = -22,	/**< Function does not work in place. */
	stm32ipl_err_OpeningSource      = -23,	/**< Error opening source. */
	stm32ipl_err_WrongROI           = -24,	/**< ROI is wrong. */
} stm32ipl_err_t;

/**
 * The image formats supported by this library.
 */
typedef enum _stm32ipl_if_t
{
	stm32ipl_if_binary = 1,
	stm32ipl_if_grayscale = 2,
	stm32ipl_if_rgb565 = 4,
	stm32ipl_if_rgb888 = 8,
} stm32ipl_if_t;

/**
 * @brief Represents an ellipse on a plane.
 * Each ellipse is specified by the center point (mass center),
 * length of each semi-axis (semi-major and semi-minor axis)
 * and the rotation angle expressed in degrees.
 */
typedef struct _ellipse_t
{
	point_t center;   /**< Coordinates of the center of the ellipse. */
	int16_t radiusX;  /**< Length of the horizontal semi-axis. */
	int16_t radiusY;  /**< Length of the vertical semi-axis. */
	int16_t rotation; /**< Rotation angle (degrees). */
} ellipse_t;

/** @defgroup initLibrary Library initialization
 * Functions necessary to initialize and de-initialize the library
 *  @{
 */
void STM32Ipl_InitLib(void *memAddr, uint32_t memSize);
void STM32Ipl_DeInitLib(void);
/** @} */

/**
 * @defgroup imageInitSupport Image initialization and support
 *
 *  @{
 */
void STM32Ipl_Init(image_t *img, uint32_t width, uint32_t height, image_bpp_t format, void *data);
stm32ipl_err_t STM32Ipl_AllocData(image_t *img, uint32_t width, uint32_t height, image_bpp_t format);
stm32ipl_err_t STM32Ipl_AllocDataRef(const image_t *src, image_t *dst);
void STM32Ipl_ReleaseData(image_t *img);
uint32_t STM32Ipl_DataSize(uint32_t width, uint32_t height, image_bpp_t format);
uint32_t STM32Ipl_ImageDataSize(const image_t *img);
bool STM32Ipl_ImageFormatSupported(const image_t *img, uint32_t formats);
stm32ipl_err_t STM32Ipl_Copy(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_CopyData(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_Clone(const image_t *src, image_t *dst);
uint32_t STM32Ipl_AdaptColor(const image_t *img, stm32ipl_color_t color);
/** @} */

/**
 * @defgroup memAlloc Memory allocation functions
 *
 *  @{
 */
void* STM32Ipl_Alloc(uint32_t size);
void* STM32Ipl_Alloc0(uint32_t size);
void STM32Ipl_Free(void *mem);
void* STM32Ipl_Realloc(void *mem, uint32_t size);
/** @} */

/**
 * @defgroup binarization Binarization
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_Binary(const image_t *src, image_t *dst, const list_t *thresholds, bool invert, bool zero,
		const image_t *mask);
/** @} */

/**
 * @defgroup blobs Color blobs detection
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_FindBlobs(const image_t *img, list_t *out, const rectangle_t *roi, const list_t *thresholds,
		uint8_t x_stride, uint8_t y_stride, uint16_t area_threshold, uint16_t pixels_threshold, bool merge,
		uint8_t margin, bool invert, uint32_t maxBlobs);
/** @} */

/**
 * @defgroup convert Color conversion
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_Convert(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_ConvertRev(const image_t *src, image_t *dst, bool reverse);
int8_t STM32Ipl_RGB565ToL(uint16_t pixel);
int8_t STM32Ipl_RGB565ToA(uint16_t pixel);
int8_t STM32Ipl_RGB565ToB(uint16_t pixel);
int8_t STM32Ipl_RGB888ToL(rgb888_t pixel);
int8_t STM32Ipl_RGB888ToA(rgb888_t pixel);
int8_t STM32Ipl_RGB888ToB(rgb888_t pixel);
rgb888_t STM32Ipl_LABToRGB888(uint8_t l, int8_t a, int8_t b);
uint16_t STM32Ipl_LABToRGB565(uint8_t l, int8_t a, int8_t b);
uint16_t STM32Ipl_YUVToRGB565(uint8_t y, int8_t u, int8_t v);
rgb888_t STM32Ipl_YUVToRGB888(uint8_t y, int8_t u, int8_t v);

/** @} */

/**
 * @defgroup drawing Drawing
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_Zero(image_t *img, bool invert, const image_t *mask);
stm32ipl_err_t STM32Ipl_Fill(image_t *img, const rectangle_t *roi, uint32_t value);
stm32ipl_err_t STM32Ipl_DrawScreen_DMA2D(const image_t *image, uint16_t x, uint16_t y);
stm32ipl_err_t STM32Ipl_DrawPixel(image_t *img, uint16_t x, uint16_t y, stm32ipl_color_t color);
stm32ipl_err_t STM32Ipl_DrawCross(image_t *img, uint16_t x, uint16_t y, uint16_t size, stm32ipl_color_t color,
		uint16_t thickness);
stm32ipl_err_t STM32Ipl_DrawLine(image_t *img, const point_t *p0, const point_t *p1, stm32ipl_color_t color, uint16_t thickness);
stm32ipl_err_t STM32Ipl_DrawPolygon(image_t *img, const point_t *point, uint32_t nPoints, stm32ipl_color_t color,
		uint16_t thickness);
stm32ipl_err_t STM32Ipl_DrawRectangle(image_t *img, uint16_t x, uint16_t y, uint16_t width, uint16_t height,
		stm32ipl_color_t color, uint16_t thickness, bool fill);
stm32ipl_err_t STM32Ipl_DrawCircle(image_t *img, uint16_t cx, uint16_t cy, uint16_t radius, stm32ipl_color_t color,
		uint16_t thickness, bool fill);
stm32ipl_err_t STM32Ipl_DrawEllipse(image_t *img, const ellipse_t *ellipse, stm32ipl_color_t color, uint16_t thickness,
		bool fill);
/** @} */

/**
 * @defgroup edge Edge detection
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_EdgeSimple(image_t *img, const rectangle_t *roi, int32_t minTh, int32_t maxTh);
stm32ipl_err_t STM32Ipl_EdgeCanny(image_t *img, const rectangle_t *roi, int32_t minTh, int32_t maxTh);
/** @} */

/**
 * @defgroup equalization Equalization
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_GammaCorr(image_t *img, float gamma_val, float contrast, float brightness);
stm32ipl_err_t STM32Ipl_HistEq(image_t *img, const image_t *mask);
stm32ipl_err_t STM32Ipl_HistEqClahe(image_t *img, float clipLimit, const image_t *mask);
/** @} */

/**
 * @defgroup filtering Filtering
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_MeanFilter(image_t *img, uint8_t kSize, bool threshold, int32_t offset, bool invert,
		const image_t *mask);
stm32ipl_err_t STM32Ipl_MedianFilter(image_t *img, uint8_t kSize, float percentile, bool threshold, int32_t offset,
bool invert, const image_t *mask);
stm32ipl_err_t STM32Ipl_ModeFilter(image_t *img, uint8_t kSize, bool threshold, int32_t offset, bool invert,
		const image_t *mask);
stm32ipl_err_t STM32Ipl_MidpointFilter(image_t *img, uint8_t kSize, float bias, bool threshold, int32_t offset,
bool invert, const image_t *mask);
stm32ipl_err_t STM32Ipl_BilateralFilter(image_t *img, uint8_t kSize, float colorSigma, float spaceSigma, bool threshold,
		int32_t offset, bool invert, const image_t *mask);
stm32ipl_err_t STM32Ipl_Morph(image_t *img, uint8_t kSize, const int32_t *krn, float mul, int32_t add, bool threshold,
		int32_t offset, bool invert, const image_t *mask);
stm32ipl_err_t STM32Ipl_Gaussian(image_t *img, uint8_t kSize, bool threshold, bool unsharp, const image_t *mask);
stm32ipl_err_t STM32Ipl_Laplacian(image_t *img, uint8_t kSize, bool sharpen, const image_t *mask);
stm32ipl_err_t STM32Ipl_Sobel(image_t *img, uint8_t kSize, bool sharpen, const image_t *mask);
stm32ipl_err_t STM32Ipl_Scharr(image_t *img, uint8_t kSize, bool sharpen, const image_t *mask);
stm32ipl_err_t STM32Ipl_MidpointPool(const image_t *src, image_t *dst, uint16_t xDiv, uint16_t yDiv, uint16_t bias);
stm32ipl_err_t STM32Ipl_MeanPool(const image_t *src, image_t *dst, uint16_t xDiv, uint16_t yDiv);
/** @} */

/**
 * @defgroup findPixel Find Pixels
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_GetPixel(const image_t *img, uint16_t x, uint16_t y, stm32ipl_color_t *p);
stm32ipl_err_t STM32Ipl_FindMinMaxLoc(const image_t *img, list_t *outMin, list_t *outMax, const rectangle_t *roi);
stm32ipl_err_t STM32Ipl_FindNonZeroLoc(const image_t *img, list_t *out, const rectangle_t *roi);
/** @} */

/**
 * @defgroup geometry Geometry
 *
 *  @{
 */
bool STM32Ipl_ClipLine(line_t *l, int16_t x, int16_t y, int16_t width, int16_t h);
stm32ipl_err_t STM32Ipl_LineLength(const line_t *l, float *length);
stm32ipl_err_t STM32Ipl_PolylineLength(const point_t *points, uint16_t count, bool is_closed, float *perimeter);
stm32ipl_err_t STM32Ipl_EnclosingCircle(const point_t *points, point_t *center, uint16_t *radius);
stm32ipl_err_t STM32Ipl_EnclosingEllipse(const point_t *points, ellipse_t *out);
stm32ipl_err_t STM32Ipl_FitEllipse(const point_t *points, uint16_t nPoints, ellipse_t *out);
/** @} */

/**
 * @defgroup hough Hough
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_FindLines(const image_t *img, list_t *out, const rectangle_t *roi, uint8_t xStride,
		uint8_t yStride, uint32_t threshold, uint8_t thetaMargin, uint8_t rhoMargin);
stm32ipl_err_t STM32Ipl_FindCircles(const image_t *img, list_t *out, const rectangle_t *roi, uint32_t xStride,
		uint32_t yStride, uint32_t threshold, uint32_t xMargin, uint32_t yMargin, uint32_t rMargin, uint32_t rMin,
		uint32_t rMax, uint32_t rStep);
/** @} */

/**
 * @defgroup imageIO Image I/O
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_ReadImage(image_t *img, const char *filename);
stm32ipl_err_t STM32Ipl_WriteImage(const image_t *img, const char *filename);
/** @} */

/**
 * @defgroup integralImage Integral image
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_IIAllocData(i_image_t *iimg, uint32_t width, uint32_t height);
void STM32Ipl_IIReleaseData(i_image_t *iimg);
stm32ipl_err_t STM32Ipl_II(const image_t *src, i_image_t *dst);
stm32ipl_err_t STM32Ipl_IIScaled(const image_t *src, i_image_t *dst);
stm32ipl_err_t STM32Ipl_IISq(const image_t *src, i_image_t *dst);
uint32_t STM32Ipl_IILookup(const i_image_t *iimg, uint32_t x, uint32_t y, uint32_t width, uint32_t height);
/** @} */

/**
 * @defgroup masking Masking
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_ImageMaskRectangle(image_t *img, uint16_t x, uint16_t y, uint16_t width, uint16_t height);
stm32ipl_err_t STM32Ipl_ImageMaskCircle(image_t *img, uint16_t cx, uint16_t cy, uint16_t radius);
stm32ipl_err_t STM32Ipl_ImageMaskEllipse(image_t *img, const ellipse_t *ellipse);
bool STM32Ipl_GetMaskPixel(const image_t *img, uint16_t x, uint16_t y);
/** @} */

/**
 * @defgroup mathOp Mathematical operators
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_Invert(image_t *img);
stm32ipl_err_t STM32Ipl_And(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask);
stm32ipl_err_t STM32Ipl_Nand(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask);
stm32ipl_err_t STM32Ipl_Or(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask);
stm32ipl_err_t STM32Ipl_Nor(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask);
stm32ipl_err_t STM32Ipl_Xor(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask);
stm32ipl_err_t STM32Ipl_Xnor(image_t *imgA, const image_t *imgB, stm32ipl_color_t color, const image_t *mask);
stm32ipl_err_t STM32Ipl_Add(image_t *img, const image_t *other, stm32ipl_color_t scalar, const image_t *mask);
stm32ipl_err_t STM32Ipl_Sub(image_t *img, const image_t *other, stm32ipl_color_t scalar, bool invert,
		const image_t *mask);
stm32ipl_err_t STM32Ipl_Mul(image_t *img, const image_t *other, stm32ipl_color_t scalar, bool invert,
		const image_t *mask);
stm32ipl_err_t STM32Ipl_Div(image_t *img, const image_t *other, stm32ipl_color_t scalar, bool invert, bool mod,
		const image_t *mask);
stm32ipl_err_t STM32Ipl_Diff(image_t *img, const image_t *other, stm32ipl_color_t scalar, const image_t *mask);
stm32ipl_err_t STM32Ipl_Min(image_t *img, const image_t *other, stm32ipl_color_t scalar, const image_t *mask);
stm32ipl_err_t STM32Ipl_Max(image_t *img, const image_t *other, stm32ipl_color_t scalar, const image_t *mask);
/** @} */

/**
 * @defgroup morph Morphological operators
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_Dilate(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask);
stm32ipl_err_t STM32Ipl_Erode(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask);
stm32ipl_err_t STM32Ipl_Open(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask);
stm32ipl_err_t STM32Ipl_Close(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask);
stm32ipl_err_t STM32Ipl_TopHat(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask);
stm32ipl_err_t STM32Ipl_BlackHat(image_t *img, uint8_t kSize, uint8_t threshold, const image_t *mask);
/** @} */

/**
 * @defgroup objDet Object detection
 *
 *  @{
 */
#ifdef STM32IPL_ENABLE_OBJECT_DETECTION
#ifdef STM32IPL_ENABLE_FRONTAL_FACE_CASCADE
stm32ipl_err_t STM32Ipl_LoadFaceCascade(cascade_t *cascade);
#endif /* STM32IPL_ENABLE_FRONTAL_FACE_CASCADE */
#ifdef STM32IPL_ENABLE_EYE_CASCADE
stm32ipl_err_t STM32Ipl_LoadEyeCascade(cascade_t *cascade);
#endif /* STM32IPL_ENABLE_EYE_CASCADE */
stm32ipl_err_t STM32Ipl_DetectObject(const image_t *img, array_t **out, const rectangle_t *roi, cascade_t *cascade,
		float scaleFactor, float threshold);
#endif /* STM32IPL_ENABLE_OBJECT_DETECTION */
/** @} */

/**
 * @defgroup point Point
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_PointInit(point_t *p, int16_t x, int16_t y);
point_t* STM32Ipl_PointAlloc(int16_t x, int16_t y);
stm32ipl_err_t STM32Ipl_PointCopy(const point_t *src, point_t *dst);
bool STM32Ipl_PointEqual(const point_t *p0, const point_t *p1);
bool STM32Ipl_PointEqualFast(const point_t *p0, const point_t *p1);
stm32ipl_err_t STM32Ipl_PointDistance(const point_t *p0, const point_t *p1, float *distance);
stm32ipl_err_t STM32Ipl_PointQuadrance(const point_t *p0, const point_t *p1, uint32_t *quadrance);
stm32ipl_err_t STM32Ipl_PointRotate(int16_t x, int16_t y, uint16_t degree, int16_t centerX, int16_t centerY,
		int16_t *outX, int16_t *outY);
stm32ipl_err_t STM32Ipl_PointMinAreaRectangle(const point_t *points, uint16_t nPoints, point_t *out);
/** @} */

/**
 * @defgroup rectangle Rectangle
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_RectInit(rectangle_t *r, int16_t x, int16_t y, int16_t width, int16_t height);
rectangle_t* STM32Ipl_RectAlloc(int16_t x, int16_t y, int16_t width, int16_t height);
stm32ipl_err_t STM32Ipl_RectCopy(const rectangle_t *src, rectangle_t *dst);
bool STM32Ipl_RectEqual(const rectangle_t *r0, const rectangle_t *r1);
bool STM32Ipl_RectEqualFast(const rectangle_t *r0, const rectangle_t *r1);
bool STM32Ipl_RectContain(const rectangle_t *r0, const rectangle_t *r1);
bool STM32Ipl_RectOverlap(const rectangle_t *r0, const rectangle_t *r1);
stm32ipl_err_t STM32Ipl_RectIntersected(const rectangle_t *src, rectangle_t *dst);
stm32ipl_err_t STM32Ipl_RectUnited(const rectangle_t *src, rectangle_t *dst);
stm32ipl_err_t STM32Ipl_RectExpand(rectangle_t *r, uint16_t x, uint16_t y);
bool STM32Ipl_RectSubImage(const image_t *img, const rectangle_t *src, rectangle_t *dst);
stm32ipl_err_t STM32Ipl_RectToPoints(const rectangle_t *r, point_t *points);
stm32ipl_err_t STM32Ipl_RectMerge(array_t **rects);
/** @} */

/**
 * @defgroup resizeCrop Resize and cropping
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_Crop(const image_t *src, image_t *dst, uint32_t x, uint32_t y);
stm32ipl_err_t STM32Ipl_Resize(const image_t *src, image_t *dst, const rectangle_t *roi);
stm32ipl_err_t STM32Ipl_Downscale(const image_t *src, image_t *dst, bool reversed);
stm32ipl_err_t STM32Ipl_Downscale_bilinear(const image_t *src, image_t *dst);
/** @} */

/**
 * @defgroup rotationTransform Rotation and transformation
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_Rotation(image_t *img, float rotationX, float rotationY, float rotationZ, float translationX,
		float translationY, float zoom, float fov, const float *corners);
stm32ipl_err_t STM32Ipl_Replace(const image_t *src, image_t *dst, bool mirror, bool flip, bool transpose,
		const image_t *mask);
stm32ipl_err_t STM32Ipl_Flip(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_Mirror(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_FlipMirror(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_Rotation90(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_Rotation180(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_Rotation270(const image_t *src, image_t *dst);
stm32ipl_err_t STM32Ipl_LensCorr(image_t *img, float strength, float zoom, float xCorr, float yCorr);
/** @} */

/**
 * @defgroup stats Statistics
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_HistInit(histogram_t *hist);
stm32ipl_err_t STM32Ipl_HistAllocData(histogram_t *hist, uint32_t lCount, uint32_t aCount, uint32_t bCount);
void STM32Ipl_HistReleaseData(histogram_t *hist);
stm32ipl_err_t STM32Ipl_GetSimilarity(const image_t *img, const image_t *other, stm32ipl_color_t scalar, float *avg,
		float *std, float *min, float *max);
stm32ipl_err_t STM32Ipl_GetPercentile(const histogram_t *ptr, image_bpp_t bpp, percentile_t *out, float percentile);
stm32ipl_err_t STM32Ipl_GetThreshold(const histogram_t *ptr, image_bpp_t bpp, threshold_t *out);
stm32ipl_err_t STM32Ipl_GetHistogram(const image_t *img, histogram_t *out, const rectangle_t *roi);
stm32ipl_err_t STM32Ipl_GetStatistics(const image_t *img, statistics_t *out, const rectangle_t *roi);
stm32ipl_err_t STM32Ipl_GetRegressionImage(const image_t *img, find_lines_list_lnk_data_t *out, const rectangle_t *roi,
		uint8_t xStride, uint8_t yStride, const list_t *thresholds, bool invert, uint32_t areaThreshold,
		uint32_t pixelsThreshold, bool robust);
stm32ipl_err_t STM32Ipl_GetRegressionPoints(const point_t *points, uint16_t nPoints, find_lines_list_lnk_data_t *out,
bool robust);
stm32ipl_err_t STM32Ipl_GetMean(const image_t *img, int32_t *outR, int32_t *outG, int32_t *outB);
stm32ipl_err_t STM32Ipl_GetStdDev(const image_t *src, int32_t *out);
stm32ipl_err_t STM32Ipl_CountNonZero(const image_t *img, uint32_t *out, const rectangle_t *roi);
/** @} */

/**
 * @defgroup templateMatching Template matching
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_FindTemplate(const image_t *img, const image_t *template, const rectangle_t *roi,
		float threshold, uint32_t step, template_match_t searchType, rectangle_t *templateRect, float *correlation);
/** @} */

/**
 * @defgroup warping Warping
 *
 *  @{
 */
stm32ipl_err_t STM32Ipl_GetAffineTransform(const point_t *src, const point_t *dst, float *affine);
stm32ipl_err_t STM32Ipl_WarpAffine(image_t *img, const float *affine);
stm32ipl_err_t STM32Ipl_WarpAffinePoints(point_t *points, uint32_t nPoints, const float *affine);
/** @} */

#ifdef __cplusplus
}
#endif

#endif  // __STM32IPL_H_
