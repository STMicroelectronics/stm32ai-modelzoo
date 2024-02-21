#ifndef AI_LITE_MATH_HELPERS_H
#define AI_LITE_MATH_HELPERS_H
#include <math.h>

#include "ai_platform.h"
#include "ai_platform_interface.h"
#include "ai_datatypes_defines.h"

#define AI_FLOAT_TOLERANCE      (6.19209290e-5F)  /* Used for small calculation
                                                     noise issues */
#define AI_FLOAT_EPSILON        (1.19209290e-7F)
#define AI_I8_EPSILON           (0.00787401F)     /* 1/(2^7 - 1)  */
#define AI_I16_EPSILON          (3.051851e-5F)    /* 1/(2^15 - 1) */

#define AI_FLT_MAX              (3.40282346638528859812e+38f)

#define AI_MIN(x,y)             ( ((x)<(y)) ? (x) : (y) )
#define AI_MAX(x,y)             ( ((x)>(y)) ? (x) : (y) )
#define AI_SIGN(x)              (((x)>0) ? 1 : -1)
#define AI_CLAMP(x, min, max)   AI_MIN(AI_MAX(x,min), max)
#define AI_ABS(x)               fabsf(x)
#define AI_ABS_DIFF(x, y)       ( ((x)>(y)) ? ((x)-(y)) : ((y)-(x)) )
#define AI_NEG(x)               ( -1 * (x) )
#define AI_NOT(x)               ( ((x)==true) ? false : true)
#define AI_RECIPROCAL(x)        ( 1.0f / (x) )
#define AI_CEIL(x)              ceilf(x)
#define AI_FLOOR(x)             floorf(x)
#define AI_FLOOR_DIV(x, y)      AI_FLOOR((x)/(y))  /* floor division: x // y */
#define AI_FLOOR_MOD(x, y)      fmodf(x, y)
#define AI_ROUND(x)             roundf(x)
#define AI_POW(x,y)             powf(x, y)

#define AI_SQUARED_DIFF(x, y)   (((x)-(y)) * ((x)-(y)))

#define AI_FLOAT_NEGATIVE_HALF        (-0.5f + AI_FLOAT_EPSILON)
#define AI_FLOAT_POSITIVE_HALF        (0.5f)


#define AI_MATH_ACOS(x)         acosf(x)
#define AI_MATH_ACOSH(x)        acoshf(x)
#define AI_MATH_ASIN(x)         asinf(x)
#define AI_MATH_ASINH(x)        asinhf(x)
#define AI_MATH_ATAN(x)         atanf(x)
#define AI_MATH_ATANH(x)        atanhf(x)
#define AI_MATH_COS(x)          cosf(x)
#define AI_MATH_COSH(x)         coshf(x)
#define AI_MATH_ERF(x)          erff(x)
#define AI_MATH_EXP(x)          expf(x)
#define AI_MATH_LOG(x)          logf(x)
#define AI_MATH_POW(x, e)       powf((x), (e))
#define AI_MATH_RSQRT(x)        (1.0f / AI_MATH_SQRT(x))
#define AI_MATH_SIN(x)          sinf(x)
#define AI_MATH_SINH(x)         sinhf(x)
#define AI_MATH_SQRT(x)         ai_math_sqrt(x)
#define AI_MATH_TAN(x)          tanf(x)
#define AI_MATH_TANH(x)         tanhf(x)
#define AI_MATH_SQUARE(x)       AI_MATH_POW(x, 2.0f)

#define AI_MATH_ACOS(x)         acosf(x)
#define AI_MATH_ACOSH(x)        acoshf(x)
#define AI_MATH_ASIN(x)         asinf(x)
#define AI_MATH_ASINH(x)        asinhf(x)
#define AI_MATH_ATAN(x)         atanf(x)
#define AI_MATH_ATANH(x)        atanhf(x)
#define AI_MATH_COS(x)          cosf(x)
#define AI_MATH_COSH(x)         coshf(x)
#define AI_MATH_ERF(x)          erff(x)
#define AI_MATH_EXP(x)          expf(x)
#define AI_MATH_LOG(x)          logf(x)
#define AI_MATH_POW(x, e)       powf((x), (e))
#define AI_MATH_RSQRT(x)        (1.0f / AI_MATH_SQRT(x))
#define AI_MATH_SIN(x)          sinf(x)
#define AI_MATH_SINH(x)         sinhf(x)
#define AI_MATH_SQRT(x)         ai_math_sqrt(x)
#define AI_MATH_TAN(x)          tanf(x)
#define AI_MATH_TANH(x)         tanhf(x)
#define AI_MATH_SQUARE(x)       AI_MATH_POW(x, 2.0f)
#define AI_MATH_RELU_TEST(x, thr, min, max) \
  (((x)<=(thr)) ? (min) : (max))

#define AI_MATH_CLIP_LINEAR_REMAP(x, alpha, beta) \
  (AI_MAX(0, AI_MIN(1, ((x) * (alpha) + (beta)))))

#define AI_MATH_RELU_GENERIC(x, thr, alpha, max) \
  AI_MATH_RELU_TEST(x, max, AI_MATH_RELU_GENERIC_NO_MAX(x, thr, alpha), max)

#define AI_MATH_RELU_GENERIC_NO_MAX(x, thr, alpha) \
  AI_MATH_RELU_TEST(x, thr, ((alpha)*((x)-(thr))), x)

#define AI_MATH_RELU_THRESHOLDED(x, thr) \
  AI_MATH_RELU_TEST(x, thr, 0, (x))

#define AI_MATH_LEAKY_RELU(x, neg_slope, pos_slope) \
  AI_MATH_RELU_TEST(x, 0, (x)*(neg_slope), (x)*(pos_slope))
//          ( ((x)>0) ? (x)*(pos_slope) : (x)*(neg_slope) )

#define AI_MATH_PRELU(x, slope) \
  AI_MATH_RELU_TEST(x, 0, (x)*(slope), (x))
// AI_MATH_LEAKY_RELU(x, slope, 1)

#define AI_MATH_RELU(x) \
  AI_MATH_RELU_TEST(x, 0, 0, x)
//  AI_MAX(x, 0)

#define AI_MATH_ELU(x, alpha) \
  (AI_MAX(0.0f, (x)) + AI_MIN(0.0f, (alpha) * (AI_MATH_EXP(x)-1.0f)))

#define AI_MATH_SELU(x, alpha, scale) \
  ((scale)*AI_MATH_ELU(x, alpha))

#define AI_MATH_SCALED_TANH(x, alpha, beta) \
  ((alpha)*AI_MATH_TANH((beta)*(x)))

#define AI_MATH_SIGMOID(x) \
  (1.0f / (1.0f + AI_MATH_EXP(-(x))))

#define AI_MATH_LOGISTIC(x)\
    (x < 0) ? (1.0f -(1.0f / (1.0f + AI_MATH_EXP(-AI_ABS(x))))) :\
    (1.0f / (1.0f + AI_MATH_EXP(-AI_ABS(x))))

#define AI_MATH_HARD_SIGMOID(x, alpha, beta) \
    AI_MATH_CLIP_LINEAR_REMAP(x, alpha, beta)

/* Formula with higher accuracy */
#define AI_MATH_SWISH(x) \
  ((x) * AI_MATH_SIGMOID(x))

#define AI_MATH_HARD_SWISH(x) \
  ((x) * AI_MATH_CLIP_LINEAR_REMAP(x, 1.0f/6, 0.5f))

#define AI_MATH_SOFT_PLUS(x) \
  AI_MATH_LOG(1.0f + AI_MATH_EXP(x))

#define AI_MATH_SOFT_SIGN(x) \
  ((x) / (1.0f + AI_ABS(x)))


AI_API_DECLARE_BEGIN

/*!
 * @brief platform optimized square root on a float value
 * @ingroup math_helpers
 * @param x input value
 * @return square root of the value
 */
AI_INTERFACE_ENTRY ai_float ai_math_sqrt(const ai_float x);


AI_API_DECLARE_END

#endif /* AI_LITE_MATH_HELPERS_H */
