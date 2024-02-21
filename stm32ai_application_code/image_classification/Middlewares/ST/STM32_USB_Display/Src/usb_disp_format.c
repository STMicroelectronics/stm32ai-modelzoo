/**
 ******************************************************************************
 * @file    usb_disp_format.c
 * @author  GPM Application Team
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#include "usb_disp_format.h"

#include "cmsis_compiler.h"
#include <stdint.h>
#include <string.h>

#ifndef MIN
#define MIN(a, b)  (((a) < (b)) ? (a) : (b))
#endif /* MIN */

#define CLAMP(v, v_min, v_max) do { \
  v = v < v_min ? v_min : v; \
  v = v > v_max ? v_max : v; \
} while (0)

static int32_t USB_DISP_RED_Y_LUT[256];
static int32_t USB_DISP_RED_CB_LUT[256];
static int32_t USB_DISP_BLUE_CB_RED_CR_LUT[256];
static int32_t USB_DISP_GREEN_Y_LUT[256];
static int32_t USB_DISP_GREEN_CR_LUT[256];
static int32_t USB_DISP_GREEN_CB_LUT[256];
static int32_t USB_DISP_BLUE_Y_LUT[256];
static int32_t USB_DISP_BLUE_CR_LUT[256];

#define RGB_2_Y(r, g, b, y) do { \
  y = USB_DISP_RED_Y_LUT[r] + USB_DISP_GREEN_Y_LUT[g] + USB_DISP_BLUE_Y_LUT[b]; \
  CLAMP(y, 0, 255); \
} while(0)

#define RGB_2_CR(r, g, b, cr) do { \
  cr = USB_DISP_BLUE_CB_RED_CR_LUT[r] + USB_DISP_GREEN_CR_LUT[g] + USB_DISP_BLUE_CR_LUT[b] + 128; \
  CLAMP(cr, 0, 255); \
} while(0)

#define RGB_2_CB(r, g, b, cb) do { \
  cb = USB_DISP_RED_CB_LUT[r] + USB_DISP_GREEN_CB_LUT[g] + USB_DISP_BLUE_CB_RED_CR_LUT[b] + 128; \
  CLAMP(cb, 0, 255); \
} while(0)

__STATIC_FORCEINLINE void USB_DISP_DualPelRgbToYuv(uint8_t *r, uint8_t *g, uint8_t *b, int32_t *y, int32_t *cb, int32_t *cr)
{
  uint8_t red, green, blue;

  RGB_2_Y(r[0], g[0], b[0], y[0]);
  RGB_2_Y(r[1], g[1], b[1], y[1]);

  red = (r[0] + r[1] + 1) / 2;
  green = (g[0] + g[1] + 1) / 2;
  blue = (b[0] + b[1] + 1) / 2;

  RGB_2_CR(red, green, blue, cr[0]);
  RGB_2_CB(red, green, blue, cb[0]);
}

static void USB_DISP_CvtGreyToMcu422(uint8_t *p_dst, uint8_t *p_src, int pitch, int x_limit, int y_limit)
{
  uint8_t *p_dst_l[2];
  int32_t luma;
  int x, y;

  p_dst_l[0] = p_dst;
  p_dst_l[1] = p_dst + 64;
  for (y = 0; y < y_limit; y++)
  {
    for (x = 0; x < x_limit; x += 2)
    {
      uint32_t p;

      p = p_src[x];
      RGB_2_Y(p, p, p, luma);
      p_dst_l[x / 8][(x % 8) + 0] = luma;
      p = p_src[x + 1];
      RGB_2_Y(p, p, p, luma);
      p_dst_l[x / 8][(x % 8) + 1] = luma;
    }
    p_dst_l[0] += 8;
    p_dst_l[1] += 8;
    p_src += pitch;
  }

  memset(p_dst + 128, 0x80, 64);
  memset(p_dst + 192, 0x80, 64);
}

static void USB_DISP_CvtArgbToMcu422(uint8_t *p_dst, uint8_t *p_src, int pitch, int x_limit, int y_limit)
{
  uint32_t *p_src_argb = (uint32_t *)p_src;
  uint8_t *p_dst_l[2];
  uint8_t *p_dst_cb;
  uint8_t *p_dst_cr;
  int32_t luma[2];
  int32_t cb, cr;
  uint8_t b[2];
  uint8_t g[2];
  uint8_t r[2];
  int x, y;

  p_dst_l[0] = p_dst;
  p_dst_l[1] = p_dst + 64;
  p_dst_cb = p_dst + 128;
  p_dst_cr = p_dst + 192;
  for (y = 0; y < y_limit; y++)
  {
    for (x = 0; x < x_limit; x += 2)
    {
      uint32_t p;

      p = p_src_argb[x];
      b[0] = (p >> 0) & 0xff;
      g[0] = (p >> 8) & 0xff;
      r[0] = (p >> 16) & 0xff;
      p = p_src_argb[x + 1];
      b[1] = (p >> 0) & 0xff;
      g[1] = (p >> 8) & 0xff;
      r[1] = (p >> 16) & 0xff;

      USB_DISP_DualPelRgbToYuv(r, g, b, luma, &cb, &cr);
      p_dst_l[x / 8][(x % 8) + 0] = luma[0];
      p_dst_l[x / 8][(x % 8) + 1] = luma[1];
      p_dst_cb[x / 2] = cb;
      p_dst_cr[x / 2] = cr;
    }
    p_dst_l[0] += 8;
    p_dst_l[1] += 8;
    p_dst_cb += 8;
    p_dst_cr += 8;
    p_src_argb += pitch / 4;
  }
}

static void USB_DISP_CvtYuv422ToMcu422(uint8_t *p_dst, uint8_t *p_src, int pitch, int x_limit, int y_limit)
{
  uint32_t *p_src_yuyv = (uint32_t *)p_src;
  uint8_t *p_dst_l[2];
  uint8_t *p_dst_cb;
  uint8_t *p_dst_cr;
  int x, y;

  p_dst_l[0] = p_dst;
  p_dst_l[1] = p_dst + 64;
  p_dst_cb = p_dst + 128;
  p_dst_cr = p_dst + 192;
  for (y = 0; y < y_limit; y++)
  {
    for (x = 0; x < x_limit; x += 2)
    {
      uint32_t yuyv = p_src_yuyv[x / 2];

      p_dst_l[x / 8][(x % 8) + 0] = (yuyv >> 0) & 0xff;
      p_dst_l[x / 8][(x % 8) + 1] = (yuyv >> 16) & 0xff;
      p_dst_cb[x / 2] = (yuyv >> 8) & 0xff;
      p_dst_cr[x / 2] = (yuyv >> 24) & 0xff;
    }
    p_dst_l[0] += 8;
    p_dst_l[1] += 8;
    p_dst_cb += 8;
    p_dst_cr += 8;
    p_src_yuyv += pitch / 4;
  }
}

static void USB_DISP_CvtRgb565ToMcu422(uint8_t *p_dst, uint8_t *p_src, int pitch, int x_limit, int y_limit)
{
  uint32_t *p_src_dual_rgb565 = (uint32_t *)p_src;
  uint8_t *p_dst_l[2];
  uint8_t *p_dst_cb;
  uint8_t *p_dst_cr;
  int32_t luma[2];
  int32_t cb, cr;
  uint8_t b[2];
  uint8_t g[2];
  uint8_t r[2];
  int x, y;

  p_dst_l[0] = p_dst;
  p_dst_l[1] = p_dst + 64;
  p_dst_cb = p_dst + 128;
  p_dst_cr = p_dst + 192;
  for (y = 0; y < y_limit; y++)
  {
    for (x = 0; x < x_limit; x += 2)
    {
      uint32_t p = p_src_dual_rgb565[x / 2];

      b[0] = (p >> 0) & 0x1f;
      b[0] = (b[0] << 3) | (b[0] >> 2);
      g[0] = (p >> 5) & 0x3f;
      g[0] = (g[0] << 2) | (g[0] >> 4);
      r[0] = (p >> 11) & 0x1f;
      r[0] = (r[0] << 3) | (r[0] >> 2);
      b[1] = (p >> 16) & 0x1f;
      b[1] = (b[1] << 3) | (b[1] >> 2);
      g[1] = (p >> 21) & 0x3f;
      g[1] = (g[1] << 2) | (g[1] >> 4);
      r[1] = (p >> 27) & 0x1f;
      r[1] = (r[1] << 3) | (r[1] >> 2);

      USB_DISP_DualPelRgbToYuv(r, g, b, luma, &cb, &cr);
      p_dst_l[x / 8][(x % 8) + 0] = luma[0];
      p_dst_l[x / 8][(x % 8) + 1] = luma[1];
      p_dst_cb[x / 2] = cb;
      p_dst_cr[x / 2] = cr;
    }
    p_dst_l[0] += 8;
    p_dst_l[1] += 8;
    p_dst_cb += 8;
    p_dst_cr += 8;
    p_src_dual_rgb565 += pitch / 4;
  }
}

static void USB_DISP_FormatToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height, int byte_per_pel,
                                        void (*cvt)(uint8_t *, uint8_t *, int , int , int ))
{
  int src_pitch = width * byte_per_pel;
  int mcu_width = (width + 15) / 16;
  int mcu_height = (height + 7) / 8;
  int x, y;

  for (y = 0; y < mcu_height; y++)
  {
    int remain_height = height - y * 8;

    for (x = 0; x < mcu_width; x++)
    {
      int remain_width = width - x * 16;

      cvt(p_dst, p_src + x * 16 * byte_per_pel, src_pitch, MIN(remain_width, 16), MIN(remain_height, 8));
      p_dst += 256; /* 4 * (8 * 8 block). 2 Luma + 1 Cb + 1 Cr */
    }
    p_src += 8 * src_pitch;
  }
}

void USB_DISP_FormatInit()
{
  int i;

  for (i = 0; i <= 255; i++)
  {
    USB_DISP_RED_Y_LUT[i]           = ((  ((int32_t) ((0.299 )  * (1L << 16)))  * i) + ((int32_t) 1 << (16 - 1))) >> 16 ;
    USB_DISP_GREEN_Y_LUT[i]         = ((  ((int32_t) ((0.587 )  * (1L << 16)))  * i) + ((int32_t) 1 << (16 - 1))) >> 16 ;
    USB_DISP_BLUE_Y_LUT[i]          = ((  ((int32_t) ((0.114 )  * (1L << 16)))  * i) + ((int32_t) 1 << (16 - 1))) >> 16 ;
    USB_DISP_RED_CB_LUT[i]          = (((-((int32_t) ((0.1687 ) * (1L << 16)))) * i) + ((int32_t) 1 << (16 - 1))) >> 16 ;
    USB_DISP_GREEN_CB_LUT[i]        = (((-((int32_t) ((0.3313 ) * (1L << 16)))) * i) + ((int32_t) 1 << (16 - 1))) >> 16 ;
    /* BLUE_CB_LUT and RED_CR_LUT are identical */
    USB_DISP_BLUE_CB_RED_CR_LUT[i]  = ((  ((int32_t) ((0.5 )    * (1L << 16)))  * i) + ((int32_t) 1 << (16 - 1))) >> 16 ;
    USB_DISP_GREEN_CR_LUT[i]        = (((-((int32_t) ((0.4187 ) * (1L << 16)))) * i) + ((int32_t) 1 << (16 - 1))) >> 16 ;
    USB_DISP_BLUE_CR_LUT[i]         = (((-((int32_t) ((0.0813 ) * (1L << 16)))) * i) + ((int32_t) 1 << (16 - 1))) >> 16 ;
  }
}

void USB_DISP_FormatGreyToYuv422(uint8_t *p_dst, uint8_t *p_src, int width, int height)
{
  int32_t luma;
  int x, y;

  for (y = 0; y < height; y++)
  {
    for (x = 0; x < width; x += 2)
    {
      uint32_t p;

      p = p_src[x];
      RGB_2_Y(p, p, p, luma);
      *p_dst++ = luma;
      *p_dst++ = 0x80;
      p = p_src[x + 1];
      RGB_2_Y(p, p, p, luma);
      *p_dst++ = luma;
      *p_dst++ = 0x80;
    }
    p_src += width;
  }
}

void USB_DISP_FormatArgbToYuv422(uint8_t *p_dst, uint8_t *p_src, int width, int height)
{
  uint32_t *p_src_argb = (uint32_t *)p_src;
  int32_t luma[2];
  int32_t cb, cr;
  uint8_t b[2];
  uint8_t g[2];
  uint8_t r[2];
  int x, y;

  for (y = 0; y < height; y++)
  {
    for (x = 0; x < width; x += 2)
    {
      uint32_t p;

      p = p_src_argb[x];
      b[0] = (p >> 0) & 0xff;
      g[0] = (p >> 8) & 0xff;
      r[0] = (p >> 16) & 0xff;
      p = p_src_argb[x + 1];
      b[1] = (p >> 0) & 0xff;
      g[1] = (p >> 8) & 0xff;
      r[1] = (p >> 16) & 0xff;

      USB_DISP_DualPelRgbToYuv(r, g, b, luma, &cb, &cr);
      *p_dst++ = luma[0];
      *p_dst++ = cb;
      *p_dst++ = luma[1];
      *p_dst++ = cr;
    }
    p_src_argb += width;
  }
}

void USB_DISP_FormatRgb565ToYuv422(uint8_t *p_dst, uint8_t *p_src, int width, int height)
{
  uint32_t *p_src_dual_rgb565 = (uint32_t *)p_src;
  int32_t luma[2];
  int32_t cb, cr;
  uint8_t b[2];
  uint8_t g[2];
  uint8_t r[2];
  int x, y;

  for (y = 0; y < height; y++)
  {
    for (x = 0; x < width; x += 2)
    {
      uint32_t p = p_src_dual_rgb565[x / 2];

      b[0] = (p >> 0) & 0x1f;
      b[0] = (b[0] << 3) | (b[0] >> 2);
      g[0] = (p >> 5) & 0x3f;
      g[0] = (g[0] << 2) | (g[0] >> 4);
      r[0] = (p >> 11) & 0x1f;
      r[0] = (r[0] << 3) | (r[0] >> 2);
      b[1] = (p >> 16) & 0x1f;
      b[1] = (b[1] << 3) | (b[1] >> 2);
      g[1] = (p >> 21) & 0x3f;
      g[1] = (g[1] << 2) | (g[1] >> 4);
      r[1] = (p >> 27) & 0x1f;
      r[1] = (r[1] << 3) | (r[1] >> 2);

      USB_DISP_DualPelRgbToYuv(r, g, b, luma, &cb, &cr);
      *p_dst++ = luma[0];
      *p_dst++ = cb;
      *p_dst++ = luma[1];
      *p_dst++ = cr;
    }
    p_src_dual_rgb565 += width / 2;
  }
}

void USB_DISP_FormatGreyToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height)
{
  USB_DISP_FormatToYuv422Jpeg(p_dst, p_src, width, height, 1, USB_DISP_CvtGreyToMcu422);
}

void USB_DISP_FormatRgbArgbToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height)
{
  USB_DISP_FormatToYuv422Jpeg(p_dst, p_src, width, height, 4, USB_DISP_CvtArgbToMcu422);
}

void USB_DISP_FormatRgb565ToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height)
{
  USB_DISP_FormatToYuv422Jpeg(p_dst, p_src, width, height, 2, USB_DISP_CvtRgb565ToMcu422);
}

void USB_DISP_FormatYuv422ToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height)
{
  USB_DISP_FormatToYuv422Jpeg(p_dst, p_src, width, height, 2, USB_DISP_CvtYuv422ToMcu422);
}
