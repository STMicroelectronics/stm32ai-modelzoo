/*
 * This file is part of the OpenMV project.
 *
 * Copyright (c) 2013-2019 Ibrahim Abdelkader <iabdalkader@openmv.io>
 * Copyright (c) 2013-2019 Kwabena W. Agyeman <kwagyeman@openmv.io>
 *
 * This work is licensed under the MIT license, see the file LICENSE for details.
 *
 * Fast approximate math functions.
 */
#ifndef __FMATH_H__
#define __FMATH_H__
#include <stdlib.h>
#include <stdint.h>
#include <float.h>
#include "common.h" /* STM32IPL added */

/* STM32IPL removed as the definitions of such functions has been added below.
float fast_sqrtf(float x);
int fast_floorf(float x);
int fast_ceilf(float x);
int fast_roundf(float x);
*/
float fast_atanf(float x);
float fast_atan2f(float y, float x);
float fast_expf(float x);
float fast_cbrtf(float d);
/* STM32IPL removed as the definitions of such functions has been added below.
float fast_fabsf(float d);
*/
float fast_log(float x);
float fast_log2(float x);
float fast_powf(float a, float b);
void fast_get_min_max(float *data, size_t data_len, float *p_min, float *p_max);
extern const float cos_table[360];
extern const float sin_table[360];


/* STM32IPL following functions have been added to allow their "visibility" as they are inline. */
float OMV_ATTR_ALWAYS_INLINE fast_sqrtf(float x)
{
#if defined ( __CC_ARM )
    __asm volatile
    {
        vsqrt.f32  x, x;
    };
#else
    asm volatile (
            "vsqrt.f32  %[r], %[x]\n"
            : [r] "=t" (x)
            : [x] "t"  (x));
#endif
    return x;
}

int OMV_ATTR_ALWAYS_INLINE fast_floorf(float x)
{
    int i;
#if defined ( __CC_ARM )
    __asm volatile
    {
        vcvt.S32.f32  x, x;
        vmov.f32  i, x;
    };
#else
    asm volatile (
            "vcvt.S32.f32  %[r], %[x]\n"
            : [r] "=t" (i)
            : [x] "t"  (x));
#endif
    return i;
}

int OMV_ATTR_ALWAYS_INLINE fast_ceilf(float x)
{
    int i;
    x += 0.9999f;
#if defined ( __CC_ARM )
    __asm volatile
    {
          vcvt.S32.f32  x, x;
          vmov.f32  i, x;
    };
#else
    asm volatile (
            "vcvt.S32.f32  %[r], %[x]\n"
            : [r] "=t" (i)
            : [x] "t"  (x));
#endif
    return i;
}

int OMV_ATTR_ALWAYS_INLINE fast_roundf(float x)
{
    int i;
#if defined ( __CC_ARM )
    __asm volatile
    {
        vcvtr.s32.f32  x, x;
        vmov.f32  i, x;
    };
#else
    asm volatile (
            "vcvtr.s32.f32  %[r], %[x]\n"
            : [r] "=t" (i)
            : [x] "t"  (x));
#endif
    return i;
}

float OMV_ATTR_ALWAYS_INLINE fast_fabsf(float x)
{
#if defined ( __CC_ARM )
    __asm volatile
    {
        vabs.f32  x, x;
    };
#else
    asm volatile (
            "vabs.f32  %[r], %[x]\n"
            : [r] "=t" (x)
            : [x] "t"  (x));
#endif
    return x;
}


#endif // __FMATH_H__
