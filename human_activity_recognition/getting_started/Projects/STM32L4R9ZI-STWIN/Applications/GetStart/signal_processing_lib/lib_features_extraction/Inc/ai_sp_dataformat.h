/**
 ******************************************************************************
 * @file    ai_sp_dataformat.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
 *
 * @brief   global interface for signal processing data format
 *
 * <DESCRIPTIOM>
 *
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
  
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __AI_SP_DATAFORMAT_H__
#define __AI_SP_DATAFORMAT_H__


#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "arm_math.h"


/* Exported constants --------------------------------------------------------*/
/* Exported defines ----------------------------------------------------------*/

/*! Attributes Flags */
#define _FMT_FLAG_CONST_MASK        (1)
#define _FMT_FLAG_CONST_BITS        (30)
#define _FMT_FLAG_STATIC_MASK       (1)
#define _FMT_FLAG_STATIC_BITS       (29)
#define _FMT_FLAG_SCRATCH_MASK      (1)
#define _FMT_FLAG_SCRATCH_BITS      (28)

/*! 1 bit sign info */
#define _FMT_SIGN_MASK              (0x1)
#define _FMT_SIGN_BITS              (23)

/*! 4 bits reserved for identifying the family format, e.g. float, fixed-point..*/
#define _FMT_TYPE_MASK              (0xF)
#define _FMT_TYPE_BITS              (17)

/*! Padding bits for handling formats not aligned to multiples of 8 bits */
#define _FMT_PBITS_MASK             (0x7)
#define _FMT_PBITS_BITS             (14)

/*! TOTAL number of bits (fractional+integer+sign) (excluded padding ones) */
#define _FMT_BITS_MASK              (0x7F)
#define _FMT_BITS_BITS              (7)

/*! fractional bits field (i.e. for Q formats see @ref AI_FMT_Q) */
#define _FMT_FBITS_MASK             (0x7F)
#define _FMT_FBITS_BITS             (0)


/* Sign information */
#define AI_SP_FMT_UNSIGNED          (0x0)  /* unsigned representation */
#define AI_SP_FMT_SIGNED            (0x1)  /* signed representation */

/* Types */
#define AI_SP_FMT_TYPE_NONE         (0x0)
#define AI_SP_FMT_TYPE_FLOAT        (0x1)
#define AI_SP_FMT_TYPE_Q            (0x2)
#define AI_SP_FMT_TYPE_BOOL         (0x3)


/* Exported macros -----------------------------------------------------------*/
/*
 * The 32bits internal format fields are organized as follows:
 *
 * MSB                                                                       LSB
 *      31     28            24    23      21      17        14       7      0
 * /---------------------------------------------------------------------------/
 * / RES | FLAG |     RES    | SIGN |  RES  |  TYPE |  PBITS  |  BITS  | FBITS /
 * /---------------------------------------------------------------------------/
 * Where:
 * - RES : Reserved - NOT USED FOR NOW
 * - FLAG : 3 Attributes flags
 * - SIGN : 1 bit mark the format as signed type
 * - TYPE : 4 bits mark the format "family" type. Actually 5 families are coded,
 *      @ref AI_SP_FMT_FLOAT (float types)
 *      @ref AI_SP_FMT_Q     (fixed-point types in Qm.n format)
 *      @ref AI_SP_FMT_BOOL  (boolean type)
 * - PBITS 3 bits padding bits used to set the number of padding bits
 *      (per element) to handle special aligned formats/ E.g. a 6 bit format
 *      where each element is stored byte aligned (8 bits) has 2 padding bits.
 *      Usually this is set to 0
 * - BITS 7 bits set the total number of bits of the element, padding bits
 *      excluded. The bits are thus = sign bit + fractional bits + integer bits
 *      The number of integer bits could thus be known using the @ref
 *      AI_SP_FMT_GET_IBITS() macro.
 * - FBITS 7 bits set the number of fractional bits in the format
 */

#define AI_SP_FMT_SET(val, mask, bits)   (uint32_t)(((val)&(mask))<<(bits))
#define AI_SP_FMT_CLR(fmt, mask, bits)   ((uint32_t)(fmt)&(~((mask)<<(bits))))
#define AI_SP_FMT_GET(fmt, mask, bits)   ((uint32_t)((fmt)>>(bits))&(mask))

/* Flag attributes */
#define AI_SP_FMT_SET_CONST(val)     AI_SP_FMT_SET(val, _FMT_FLAG_CONST_MASK, _FMT_FLAG_CONST_BITS)
#define AI_SP_FMT_CLR_CONST(fmt)     AI_SP_FMT_CLR(fmt, _FMT_FLAG_CONST_MASK, _FMT_FLAG_CONST_BITS)
#define AI_SP_FMT_GET_CONST(fmt)     AI_SP_FMT_GET(fmt, _FMT_FLAG_CONST_MASK, _FMT_FLAG_CONST_BITS)
#define AI_SP_FMT_SET_STATIC(val)    AI_SP_FMT_SET(val, _FMT_FLAG_STATIC_MASK, _FMT_FLAG_STATIC_BITS)
#define AI_SP_FMT_CLR_STATIC(fmt)    AI_SP_FMT_CLR(fmt, _FMT_FLAG_STATIC_MASK, _FMT_FLAG_STATIC_BITS)
#define AI_SP_FMT_GET_STATIC(fmt)    AI_SP_FMT_GET(fmt, _FMT_FLAG_STATIC_MASK, _FMT_FLAG_STATIC_BITS)
#define AI_SP_FMT_SET_SCRATCH(val)   AI_SP_FMT_SET(val, _FMT_FLAG_SCRATCH_MASK, _FMT_FLAG_SCRATCH_BITS)
#define AI_SP_FMT_CLR_SCRATCH(fmt)   AI_SP_FMT_CLR(fmt, _FMT_FLAG_SCRATCH_MASK, _FMT_FLAG_SCRATCH_BITS)
#define AI_SP_FMT_GET_SCRATCH(fmt)   AI_SP_FMT_GET(fmt, _FMT_FLAG_SCRATCH_MASK, _FMT_FLAG_SCRATCH_BITS)

/* Sign information */
#define AI_SP_FMT_SET_SIGN(val)      AI_SP_FMT_SET(val, _FMT_SIGN_MASK, _FMT_SIGN_BITS)
#define AI_SP_FMT_CLR_SIGN(fmt)      AI_SP_FMT_CLR(fmt, _FMT_SIGN_MASK, _FMT_SIGN_BITS)
#define AI_SP_FMT_GET_SIGN(fmt)      AI_SP_FMT_GET(fmt, _FMT_SIGN_MASK, _FMT_SIGN_BITS)

/* Type information */
#define AI_SP_FMT_SET_TYPE(val)      AI_SP_FMT_SET(val, _FMT_TYPE_MASK, _FMT_TYPE_BITS)
#define AI_SP_FMT_CLR_TYPE(fmt)      AI_SP_FMT_CLR(fmt, _FMT_TYPE_MASK, _FMT_TYPE_BITS)
#define AI_SP_FMT_GET_TYPE(fmt)      AI_SP_FMT_GET(fmt, _FMT_TYPE_MASK, _FMT_TYPE_BITS)

/* Padding bits information */
#define AI_SP_FMT_SET_PBITS(val)     AI_SP_FMT_SET(val, _FMT_PBITS_MASK, _FMT_PBITS_BITS)
#define AI_SP_FMT_CLR_PBITS(fmt)     AI_SP_FMT_CLR(fmt, _FMT_PBITS_MASK, _FMT_PBITS_BITS)
#define AI_SP_FMT_GET_PBITS(fmt)     AI_SP_FMT_GET(fmt, _FMT_PBITS_MASK, _FMT_PBITS_BITS)

/* Total number of bits information */
#define AI_SP_FMT_SET_BITS(val)       AI_SP_FMT_SET(val, _FMT_BITS_MASK, _FMT_BITS_BITS)
#define AI_SP_FMT_CLR_BITS(fmt)       AI_SP_FMT_CLR(fmt, _FMT_BITS_MASK, _FMT_BITS_BITS)
#define AI_SP_FMT_GET_BITS(fmt)       AI_SP_FMT_GET(fmt, _FMT_BITS_MASK, _FMT_BITS_BITS)

/* Number of fractional bits information */
#define AI_SP_FMT_SET_FBITS(val)       AI_SP_FMT_SET(val, _FMT_FBITS_MASK, _FMT_FBITS_BITS)
#define AI_SP_FMT_CLR_FBITS(fmt)       AI_SP_FMT_CLR(fmt, _FMT_FBITS_MASK, _FMT_FBITS_BITS)
#define AI_SP_FMT_GET_FBITS(fmt)       AI_SP_FMT_GET(fmt, _FMT_FBITS_MASK, _FMT_FBITS_BITS)

/*! Macro used to compute the integer bits for a format */
#define AI_SP_FMT_GET_IBITS(fmt_) \
  ((int16_t)AI_SP_FMT_GET_BITS(fmt_) - AI_SP_FMT_GET_FBITS(fmt_) - AI_SP_FMT_GET_SIGN(fmt_))

/*! Macro used to compute the total number of bits (bits size) in case of padding */
#define AI_SP_FMT_GET_BITS_SIZE(fmt_) \
  (AI_SP_FMT_GET_BITS(fmt_) + AI_SP_FMT_GET_PBITS(fmt_))

/*! Some generic format macros */
#define AI_SP_FMT_INIT(constbits_, staticbits_, scratchbits_, chbits_, \
  signbits_, transbits_, typebits_, pbits_, bits_, fbits_) \
        (AI_SP_FMT_SET_CONST(constbits_) | \
         AI_SP_FMT_SET_STATIC(staticbits_) | \
         AI_SP_FMT_SET_SCRATCH(scratchbits_) | \
         AI_SP_FMT_SET_SIGN(signbits_) | \
         AI_SP_FMT_SET_TYPE(typebits_) | \
         AI_SP_FMT_SET_PBITS(pbits_) | \
         AI_SP_FMT_SET_BITS(bits_) | \
         AI_SP_FMT_SET_FBITS(fbits_))

#define AI_SP_FMT_FLOAT32_RESET() \
        ((uint32_t)0 | \
         AI_SP_FMT_SET_CONST(0) | \
         AI_SP_FMT_SET_STATIC(0) | \
         AI_SP_FMT_SET_SCRATCH(0) | \
         AI_SP_FMT_SET_SIGN(AI_SP_FMT_SIGNED) | \
         AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_FLOAT) | \
         AI_SP_FMT_SET_PBITS(0) | \
         AI_SP_FMT_SET_BITS(32) | \
         AI_SP_FMT_SET_FBITS(0))

#define AI_SP_FMT_INT32_RESET() \
        ((uint32_t)0 | \
         AI_SP_FMT_SET_CONST(0) | \
         AI_SP_FMT_SET_STATIC(0) | \
         AI_SP_FMT_SET_SCRATCH(0) | \
         AI_SP_FMT_SET_SIGN(AI_SP_FMT_SIGNED) | \
         AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_Q) | \
         AI_SP_FMT_SET_PBITS(0) | \
         AI_SP_FMT_SET_BITS(32) | \
         AI_SP_FMT_SET_FBITS(0))

#define AI_SP_FMT_INT16_RESET() \
        ((uint32_t)0 | \
         AI_SP_FMT_SET_CONST(0) | \
         AI_SP_FMT_SET_STATIC(0) | \
         AI_SP_FMT_SET_SCRATCH(0) | \
         AI_SP_FMT_SET_SIGN(AI_SP_FMT_SIGNED) | \
         AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_Q) | \
         AI_SP_FMT_SET_PBITS(0) | \
         AI_SP_FMT_SET_BITS(16) | \
         AI_SP_FMT_SET_FBITS(0))

#define AI_SP_FMT_UINT32_RESET() \
        ((uint32_t)0 | \
         AI_SP_FMT_SET_CONST(0) | \
         AI_SP_FMT_SET_STATIC(0) | \
         AI_SP_FMT_SET_SCRATCH(0) | \
         AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_Q) | \
         AI_SP_FMT_SET_PBITS(0) | \
         AI_SP_FMT_SET_BITS(32) | \
         AI_SP_FMT_SET_FBITS(0))

#define AI_SP_FMT_UINT16_RESET() \
        ((uint32_t)0 | \
         AI_SP_FMT_SET_CONST(0) | \
         AI_SP_FMT_SET_STATIC(0) | \
         AI_SP_FMT_SET_SCRATCH(0) | \
         AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_Q) | \
         AI_SP_FMT_SET_PBITS(0) | \
         AI_SP_FMT_SET_BITS(16) | \
         AI_SP_FMT_SET_FBITS(0))


/* Exported types ------------------------------------------------------------*/
//typedef struct AI_SP_StreamData {
//    void        *pData;
//    uint32_t    data_fmt;
//    uint16_t    data_width;   /* Number of elements (columns) in the data array */
//    uint16_t    data_height;  /* Number of channels (lines) in the data array - should be 1 for 1-D arrays*/
//} AI_SP_StreamData_t;




#ifdef __cplusplus
}
#endif

#endif      /* __AI_SP_DATAFORMAT_H__  */


