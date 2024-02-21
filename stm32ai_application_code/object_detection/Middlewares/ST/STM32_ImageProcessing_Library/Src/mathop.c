/*
 * This file is part of the OpenMV project.
 *
 * Copyright (c) 2013-2019 Ibrahim Abdelkader <iabdalkader@openmv.io>
 * Copyright (c) 2013-2019 Kwabena W. Agyeman <kwagyeman@openmv.io>
 *
 * This work is licensed under the MIT license, see the file LICENSE for details.
 *
 * Image math operations.
 */
#include "imlib.h"

#ifdef IMLIB_ENABLE_MATH_OPS
void imlib_gamma_corr(image_t *img, float gamma, float contrast, float brightness)
{
    gamma = IM_DIV(1.0f, gamma);	// STM32IPL: f added to the constant.
    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            float pScale = COLOR_BINARY_MAX - COLOR_BINARY_MIN;
            float pDiv = 1 / pScale;
            int *p_lut = fb_alloc((COLOR_BINARY_MAX - COLOR_BINARY_MIN + 1) * sizeof(int), FB_ALLOC_NO_HINT);

            for (int i = COLOR_BINARY_MIN; i <= COLOR_BINARY_MAX; i++) {
                int p = (int)(((fast_powf(i * pDiv, gamma) * contrast) + brightness) * pScale); // STM32IPL: added cast.
                p_lut[i] = IM_MIN(IM_MAX(p , COLOR_BINARY_MIN), COLOR_BINARY_MAX);
            }

            for (int y = 0, yy = img->h; y < yy; y++) {
                uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, y);
                for (int x = 0, xx = img->w; x < xx; x++) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, x);
                    int p = p_lut[dataPixel];
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, x, p);
                }
            }

            fb_free();
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            float pScale = COLOR_GRAYSCALE_MAX - COLOR_GRAYSCALE_MIN;
            float pDiv = 1 / pScale;
            int *p_lut = fb_alloc((COLOR_GRAYSCALE_MAX - COLOR_GRAYSCALE_MIN + 1) * sizeof(int), FB_ALLOC_NO_HINT);

            for (int i = COLOR_GRAYSCALE_MIN; i <= COLOR_GRAYSCALE_MAX; i++) {
                int p = (int)(((fast_powf(i * pDiv, gamma) * contrast) + brightness) * pScale); // STM32IPL: added cast.
                p_lut[i] = IM_MIN(IM_MAX(p , COLOR_GRAYSCALE_MIN), COLOR_GRAYSCALE_MAX);
            }

            for (int y = 0, yy = img->h; y < yy; y++) {
                uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, y);
                for (int x = 0, xx = img->w; x < xx; x++) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, x);
                    int p = p_lut[dataPixel];
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, x, p);
                }
            }

            fb_free();
            break;
        }
        case IMAGE_BPP_RGB565: {
            float rScale = COLOR_R5_MAX - COLOR_R5_MIN;
            float gScale = COLOR_G6_MAX - COLOR_G6_MIN;
            float bScale = COLOR_B5_MAX - COLOR_B5_MIN;
            float rDiv = 1 / rScale;
            float gDiv = 1 / gScale;
            float bDiv = 1 / bScale;
            int *r_lut = fb_alloc((COLOR_R5_MAX - COLOR_R5_MIN + 1) * sizeof(int), FB_ALLOC_NO_HINT);
            int *g_lut = fb_alloc((COLOR_G6_MAX - COLOR_G6_MIN + 1) * sizeof(int), FB_ALLOC_NO_HINT);
            int *b_lut = fb_alloc((COLOR_B5_MAX - COLOR_B5_MIN + 1) * sizeof(int), FB_ALLOC_NO_HINT);

            for (int i = COLOR_R5_MIN; i <= COLOR_R5_MAX; i++) {
                int r = (int)(((fast_powf(i * rDiv, gamma) * contrast) + brightness) * rScale); // STM32IPL: added cast.
                r_lut[i] = IM_MIN(IM_MAX(r , COLOR_R5_MIN), COLOR_R5_MAX);
            }

            for (int i = COLOR_G6_MIN; i <= COLOR_G6_MAX; i++) {
                int g = (int)(((fast_powf(i * gDiv, gamma) * contrast) + brightness) * gScale); // STM32IPL: added cast.
                g_lut[i] = IM_MIN(IM_MAX(g , COLOR_G6_MIN), COLOR_G6_MAX);
            }

            for (int i = COLOR_B5_MIN; i <= COLOR_B5_MAX; i++) {
                int b = (int)(((fast_powf(i * bDiv, gamma) * contrast) + brightness) * bScale); // STM32IPL: added cast.
                b_lut[i] = IM_MIN(IM_MAX(b , COLOR_B5_MIN), COLOR_B5_MAX);
            }

            for (int y = 0, yy = img->h; y < yy; y++) {
                uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, y);
                for (int x = 0, xx = img->w; x < xx; x++) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, x);
                    int r = r_lut[COLOR_RGB565_TO_R5(dataPixel)];
                    int g = g_lut[COLOR_RGB565_TO_G6(dataPixel)];
                    int b = b_lut[COLOR_RGB565_TO_B5(dataPixel)];
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, x, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }

            fb_free();
            fb_free();
            fb_free();
            break;
        }

        case IMAGE_BPP_RGB888: { // STM32IPL
            float rScale = COLOR_R8_MAX - COLOR_R8_MIN;
            float gScale = COLOR_G8_MAX - COLOR_G8_MIN;
            float bScale = COLOR_B8_MAX - COLOR_B8_MIN;
            float rDiv = 1 / rScale;
            float gDiv = 1 / gScale;
            float bDiv = 1 / bScale;
            int *r_lut = fb_alloc((COLOR_R8_MAX - COLOR_R8_MIN + 1) * sizeof(int), FB_ALLOC_NO_HINT);
            int *g_lut = fb_alloc((COLOR_G8_MAX - COLOR_G8_MIN + 1) * sizeof(int), FB_ALLOC_NO_HINT);
            int *b_lut = fb_alloc((COLOR_B8_MAX - COLOR_B8_MIN + 1) * sizeof(int), FB_ALLOC_NO_HINT);

            for (int i = COLOR_R8_MIN; i <= COLOR_R8_MAX; i++) {
                int r = (int)(((fast_powf(i * rDiv, gamma) * contrast) + brightness) * rScale); // STM32IPL: cast added.
                r_lut[i] = IM_MIN(IM_MAX(r , COLOR_R8_MIN), COLOR_R8_MAX);
            }

            for (int i = COLOR_G8_MIN; i <= COLOR_G8_MAX; i++) {
                int g = (int)(((fast_powf(i * gDiv, gamma) * contrast) + brightness) * gScale); // STM32IPL: cast added.
                g_lut[i] = IM_MIN(IM_MAX(g , COLOR_G8_MIN), COLOR_G8_MAX);
            }

            for (int i = COLOR_B8_MIN; i <= COLOR_B8_MAX; i++) {
                int b = (int)(((fast_powf(i * bDiv, gamma) * contrast) + brightness) * bScale); // STM32IPL: cast added.
                b_lut[i] = IM_MIN(IM_MAX(b , COLOR_B8_MIN), COLOR_B8_MAX);
            }

            for (int y = 0, yy = img->h; y < yy; y++) {
                rgb888_t *data = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, y);
                for (int x = 0, xx = img->w; x < xx; x++) {
                    rgb888_t dataPixel888 = IMAGE_GET_RGB888_PIXEL_FAST(data, x);
                    int r = r_lut[dataPixel888.r];
                    int g = g_lut[dataPixel888.g];
                    int b = b_lut[dataPixel888.b];
                    dataPixel888.r = r;
                    dataPixel888.g = g;
                    dataPixel888.b = b;
                    IMAGE_PUT_RGB888_PIXEL_FAST(data, x, dataPixel888);
                }
            }

            fb_free();
            fb_free();
            fb_free();
            break;
        }

        default: {
            break;
        }
    }
}

#ifndef STM32IPL
void imlib_negate(image_t *img)
{
    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            for (int y = 0, yy = img->h; y < yy; y++) {
                uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, y);
                int x = 0, xx = img->w;
                uint32_t *s = data;
                for (; x < xx-31; x += 32) { // do it faster with bit access
                    s[0] = ~s[0]; // invert 32 bits (pixels) in one shot
                    s++;
                }
                for (; x < xx; x++) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, x);
                    int p = (COLOR_BINARY_MAX - COLOR_BINARY_MIN) - dataPixel;
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, x, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            for (int y = 0, yy = img->h; y < yy; y++) {
                uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, y);
                int x = 0, xx = img->w;
                uint32_t a, b, *s = (uint32_t *)data;
                for (; x < xx-7; x+= 8) { // process a pair of 4 pixels at a time
                    a = s[0]; b = s[1]; // read 8 pixels
                    s[0] = ~a; s[1] = ~b;
                    s += 2;
                }
                for (; x < xx; x++) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, x);
                    int p = (COLOR_GRAYSCALE_MAX - COLOR_GRAYSCALE_MIN) - dataPixel;
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, x, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            for (int y = 0, yy = img->h; y < yy; y++) {
                uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, y);
                for (int x = 0, xx = img->w; x < xx; x++) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, x);
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, x, ~dataPixel);
                }
            }
            break;
        }
        default: {
            break;
        }
    }
}
#endif // STM32IPL

typedef struct imlib_replace_line_op_state {
    bool hmirror, vflip, transpose;
    image_t *mask;
} imlib_replace_line_op_state_t;

static void imlib_replace_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    bool hmirror = ((imlib_replace_line_op_state_t *) data)->hmirror;
    bool vflip = ((imlib_replace_line_op_state_t *) data)->vflip;
    bool transpose = ((imlib_replace_line_op_state_t *) data)->transpose;
    image_t *mask = ((imlib_replace_line_op_state_t *) data)->mask;

    image_t target;
    memcpy(&target, img, sizeof(image_t));

    if (transpose) {
        int w = target.w;
        int h = target.h;
        target.w = h;
        target.h = w;
    }

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            int v_line = vflip ? (img->h - line - 1) : line;
            for (int i = 0, j = img->w; i < j; i++) {
                int h_i = hmirror ? (img->w - i - 1) : i;

                if ((!mask) || image_get_mask_pixel(mask, h_i, v_line)) {
                    int pixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), h_i);
                    IMAGE_PUT_BINARY_PIXEL(&target, transpose ? v_line : i, transpose ? i : v_line, pixel);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            int v_line = vflip ? (img->h - line - 1) : line;
            for (int i = 0, j = img->w; i < j; i++) {
                int h_i = hmirror ? (img->w - i - 1) : i;

                if ((!mask) || image_get_mask_pixel(mask, h_i, v_line)) {
                    int pixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), h_i);
                    IMAGE_PUT_GRAYSCALE_PIXEL(&target, transpose ? v_line : i, transpose ? i : v_line, pixel);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            int v_line = vflip ? (img->h - line - 1) : line;
            for (int i = 0, j = img->w; i < j; i++) {
                int h_i = hmirror ? (img->w - i - 1) : i;

                if ((!mask) || image_get_mask_pixel(mask, h_i, v_line)) {
                    int pixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), h_i);
                    IMAGE_PUT_RGB565_PIXEL(&target, transpose ? v_line : i, transpose ? i : v_line, pixel);
                }
            }
            break;
        }
		case IMAGE_BPP_RGB888: { // STM32IPL
			int v_line = vflip ? (img->h - line - 1) : line;
			for (int i = 0, j = img->w; i < j; i++) {
				int h_i = hmirror ? (img->w - i - 1) : i;

				if ((!mask) || image_get_mask_pixel(mask, h_i, v_line)) {
					rgb888_t pixel = IMAGE_GET_RGB888_PIXEL_FAST(((rgb888_t* ) other), h_i);
					IMAGE_PUT_RGB888_PIXEL(&target, transpose ? v_line : i, transpose ? i : v_line, pixel);
				}
			}
			break;
		}
        default: {
            break;
        }
    }
}

void imlib_replace(image_t *img, const char *path, image_t *other, int scalar, bool hmirror, bool vflip, bool transpose, image_t *mask)
{
    bool in_place = img->data == other->data;
    image_t temp;

    if (in_place) {
        memcpy(&temp, other, sizeof(image_t));
        temp.data = fb_alloc(image_size(&temp), FB_ALLOC_NO_HINT);
        memcpy(temp.data, other->data, image_size(&temp));
        other = &temp;
    }

    imlib_replace_line_op_state_t state;
    state.hmirror = hmirror;
    state.vflip = vflip;
    state.mask = mask;
    state.transpose = transpose;
    imlib_image_operation(img, path, other, scalar, imlib_replace_line_op, &state);

    if (in_place) {
        fb_free();
    }

    if (transpose) {
        int w = img->w;
        int h = img->h;
        img->w = h;
        img->h = w;
    }
}

static void imlib_add_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    image_t *mask = (image_t *) data;

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), i);
                    int p = dataPixel | otherPixel; //dataPixel + otherPixel;
//                    p = IM_MIN(p, COLOR_BINARY_MAX);
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), i);
                    int p = dataPixel + otherPixel;
                    p = IM_MIN(p, COLOR_GRAYSCALE_MAX);
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), i);
                    int r = COLOR_RGB565_TO_R5(dataPixel) + COLOR_RGB565_TO_R5(otherPixel);
                    int g = COLOR_RGB565_TO_G6(dataPixel) + COLOR_RGB565_TO_G6(otherPixel);
                    int b = COLOR_RGB565_TO_B5(dataPixel) + COLOR_RGB565_TO_B5(otherPixel);
                    r = IM_MIN(r, COLOR_R5_MAX);
                    g = IM_MIN(g, COLOR_G6_MAX);
                    b = IM_MIN(b, COLOR_B5_MAX);
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, i, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }
            break;
        }
		case IMAGE_BPP_RGB888: {  // STM32IPL
			rgb888_t *data = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, line);
			for (int i = 0, j = img->w; i < j; i++) {
				if ((!mask) || image_get_mask_pixel(mask, i, line)) {
					rgb888_t dataPixel = IMAGE_GET_RGB888_PIXEL_FAST(data, i);
					rgb888_t otherPixel = IMAGE_GET_RGB888_PIXEL_FAST(((rgb888_t* ) other), i);
					rgb888_t pixel;
					int r = dataPixel.r + otherPixel.r;
					int g = dataPixel.g + otherPixel.g;
					int b = dataPixel.b + otherPixel.b;
					pixel.r = IM_MIN(r, COLOR_R8_MAX);
					pixel.g = IM_MIN(g, COLOR_G8_MAX);
					pixel.b = IM_MIN(b, COLOR_B8_MAX);
					IMAGE_PUT_RGB888_PIXEL_FAST(data, i, pixel);
				}
			}
			break;
		}

        default: {
            break;
        }
    }
}

void imlib_add(image_t *img, const char *path, image_t *other, int scalar, image_t *mask)
{
    imlib_image_operation(img, path, other, scalar, imlib_add_line_op, mask);
}

typedef struct imlib_sub_line_op_state {
    bool reverse;
    image_t *mask;
} imlib_sub_line_op_state_t;

static void imlib_sub_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    bool reverse = ((imlib_sub_line_op_state_t *) data)->reverse;
    image_t *mask = ((imlib_sub_line_op_state_t *) data)->mask;

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), i);
                    int p = reverse ? (otherPixel - dataPixel) : (dataPixel - otherPixel);
                    p = IM_MAX(p, COLOR_BINARY_MIN);
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), i);
                    int p = reverse ? (otherPixel - dataPixel) : (dataPixel - otherPixel);
                    p = IM_MAX(p, COLOR_GRAYSCALE_MIN);
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), i);
                    int dR = COLOR_RGB565_TO_R5(dataPixel);
                    int dG = COLOR_RGB565_TO_G6(dataPixel);
                    int dB = COLOR_RGB565_TO_B5(dataPixel);
                    int oR = COLOR_RGB565_TO_R5(otherPixel);
                    int oG = COLOR_RGB565_TO_G6(otherPixel);
                    int oB = COLOR_RGB565_TO_B5(otherPixel);
                    int r = reverse ? (oR - dR) : (dR - oR);
                    int g = reverse ? (oG - dG) : (dG - oG);
                    int b = reverse ? (oB - dB) : (dB - oB);
                    r = IM_MAX(r, COLOR_R5_MIN);
                    g = IM_MAX(g, COLOR_G6_MIN);
                    b = IM_MAX(b, COLOR_B5_MIN);
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, i, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }
            break;
        }
		case IMAGE_BPP_RGB888: {  // STM32IPL
			rgb888_t *data = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, line);
			for (int i = 0, j = img->w; i < j; i++) {
				if ((!mask) || image_get_mask_pixel(mask, i, line)) {
					rgb888_t dataPixel = IMAGE_GET_RGB888_PIXEL_FAST(data, i);
					rgb888_t otherPixel = IMAGE_GET_RGB888_PIXEL_FAST(((rgb888_t* ) other), i);
					rgb888_t pixel;
					int dR = dataPixel.r;
					int dG = dataPixel.g;
					int dB = dataPixel.b;
					int oR = otherPixel.r;
					int oG = otherPixel.g;
					int oB = otherPixel.b;
					int r = reverse ? (oR - dR) : (dR - oR);
					int g = reverse ? (oG - dG) : (dG - oG);
					int b = reverse ? (oB - dB) : (dB - oB);
					pixel.r = IM_MAX(r, COLOR_R8_MIN);
					pixel.g = IM_MAX(g, COLOR_G8_MIN);
					pixel.b = IM_MAX(b, COLOR_B8_MIN);
					IMAGE_PUT_RGB888_PIXEL_FAST(data, i, pixel);
				}
			}
			break;
		}

        default: {
            break;
        }
    }
}

void imlib_sub(image_t *img, const char *path, image_t *other, int scalar, bool reverse, image_t *mask)
{
    imlib_sub_line_op_state_t state;
    state.reverse = reverse;
    state.mask = mask;
    imlib_image_operation(img, path, other, scalar, imlib_sub_line_op, &state);
}

typedef struct imlib_mul_line_op_state {
    bool invert;
    image_t *mask;
} imlib_mul_line_op_state_t;

static void imlib_mul_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    bool invert = ((imlib_mul_line_op_state_t *) data)->invert;
    image_t *mask = ((imlib_mul_line_op_state_t *) data)->mask;

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, line);
            float pScale = COLOR_BINARY_MAX - COLOR_BINARY_MIN;
            float pDiv = 1 / pScale;
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), i);
                    int p = (int)(invert ? (pScale - ((pScale - dataPixel) * (pScale - otherPixel) * pDiv))
                                   : (dataPixel * otherPixel * pDiv)); // STM32IPL: added cast.
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, line);
            float pScale = COLOR_GRAYSCALE_MAX - COLOR_GRAYSCALE_MIN;
            float pDiv = 1 / pScale;
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), i);
                    int p = (int)(invert ? (pScale - ((pScale - dataPixel) * (pScale - otherPixel) * pDiv))
                                   : (dataPixel * otherPixel * pDiv)); // STM32IPL: added cast.
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, line);
            float rScale = COLOR_R5_MAX - COLOR_R5_MIN;
            float gScale = COLOR_G6_MAX - COLOR_G6_MIN;
            float bScale = COLOR_B5_MAX - COLOR_B5_MIN;
            float rDiv = 1 / rScale;
            float gDiv = 1 / gScale;
            float bDiv = 1 / bScale;
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), i);
                    int dR = COLOR_RGB565_TO_R5(dataPixel);
                    int dG = COLOR_RGB565_TO_G6(dataPixel);
                    int dB = COLOR_RGB565_TO_B5(dataPixel);
                    int oR = COLOR_RGB565_TO_R5(otherPixel);
                    int oG = COLOR_RGB565_TO_G6(otherPixel);
                    int oB = COLOR_RGB565_TO_B5(otherPixel);
                    int r = (int)(invert ? (rScale - ((rScale - dR) * (rScale - oR) * rDiv))
                                   : (dR * oR * rDiv)); // STM32IPL: added cast.
                    int g = (int)(invert ? (gScale - ((gScale - dG) * (gScale - oG) * gDiv))
                                   : (dG * oG * gDiv)); // STM32IPL: added cast.
                    int b = (int)(invert ? (bScale - ((bScale - dB) * (bScale - oB) * bDiv))
                                   : (dB * oB * bDiv)); // STM32IPL: added cast.
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, i, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }
            break;
        }
		case IMAGE_BPP_RGB888: {  // STM32IPL
			rgb888_t *data = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, line);
			float rScale = COLOR_R8_MAX - COLOR_R8_MIN;
			float gScale = COLOR_G8_MAX - COLOR_G8_MIN;
			float bScale = COLOR_B8_MAX - COLOR_B8_MIN;
			float rDiv = 1 / rScale;
			float gDiv = 1 / gScale;
			float bDiv = 1 / bScale;
			for (int i = 0, j = img->w; i < j; i++) {
				if ((!mask) || image_get_mask_pixel(mask, i, line)) {
					rgb888_t dataPixel = IMAGE_GET_RGB888_PIXEL_FAST(data, i);
					rgb888_t otherPixel = IMAGE_GET_RGB888_PIXEL_FAST(((rgb888_t* ) other), i);
					rgb888_t pixel888;
					int dR = dataPixel.r;
					int dG = dataPixel.g;
					int dB = dataPixel.b;
					int oR = otherPixel.r;
					int oG = otherPixel.g;
					int oB = otherPixel.b;
					pixel888.r = (int)(invert ? (rScale - ((rScale - dR) * (rScale - oR) * rDiv)) : (dR * oR * rDiv));
					pixel888.g = (int)(invert ? (gScale - ((gScale - dG) * (gScale - oG) * gDiv)) : (dG * oG * gDiv));
					pixel888.b = (int)(invert ? (bScale - ((bScale - dB) * (bScale - oB) * bDiv)) : (dB * oB * bDiv));
					IMAGE_PUT_RGB888_PIXEL_FAST(data, i, pixel888);
				}
			}
			break;
		}

        default: {
            break;
        }
    }
}

void imlib_mul(image_t *img, const char *path, image_t *other, int scalar, bool invert, image_t *mask)
{
    imlib_mul_line_op_state_t state;
    state.invert = invert;
    state.mask = mask;
    imlib_image_operation(img, path, other, scalar, imlib_mul_line_op, &state);
}

typedef struct imlib_div_line_op_state {
    bool invert, mod;
    image_t *mask;
} imlib_div_line_op_state_t;

static void imlib_div_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    bool invert = ((imlib_div_line_op_state_t *) data)->invert;
    bool mod = ((imlib_div_line_op_state_t *) data)->mod;
    image_t *mask = ((imlib_div_line_op_state_t *) data)->mask;

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, line);
            int pScale = COLOR_BINARY_MAX - COLOR_BINARY_MIN;
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), i);
                    int p = mod
                        ? IM_MOD((invert?otherPixel:dataPixel) * pScale, (invert?dataPixel:otherPixel))
                        : IM_DIV((invert?otherPixel:dataPixel) * pScale, (invert?dataPixel:otherPixel));
                    p = IM_MIN(p, COLOR_BINARY_MAX);
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, line);
            int pScale = COLOR_GRAYSCALE_MAX - COLOR_GRAYSCALE_MIN;
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), i);
                    int p = mod
                        ? IM_MOD((invert?otherPixel:dataPixel) * pScale, (invert?dataPixel:otherPixel))
                        : IM_DIV((invert?otherPixel:dataPixel) * pScale, (invert?dataPixel:otherPixel));
                    p = IM_MIN(p, COLOR_GRAYSCALE_MAX);
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, line);
            int rScale = COLOR_R5_MAX - COLOR_R5_MIN;
            int gScale = COLOR_G6_MAX - COLOR_G6_MIN;
            int bScale = COLOR_B5_MAX - COLOR_B5_MIN;
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), i);
                    int dR = COLOR_RGB565_TO_R5(dataPixel);
                    int dG = COLOR_RGB565_TO_G6(dataPixel);
                    int dB = COLOR_RGB565_TO_B5(dataPixel);
                    int oR = COLOR_RGB565_TO_R5(otherPixel);
                    int oG = COLOR_RGB565_TO_G6(otherPixel);
                    int oB = COLOR_RGB565_TO_B5(otherPixel);
                    int r = mod
                        ? IM_MOD((invert?oR:dR) * rScale, (invert?dR:oR))
                        : IM_DIV((invert?oR:dR) * rScale, (invert?dR:oR));
                    int g = mod
                        ? IM_MOD((invert?oG:dG) * gScale, (invert?dG:oG))
                        : IM_DIV((invert?oG:dG) * gScale, (invert?dG:oG));
                    int b = mod
                        ? IM_MOD((invert?oB:dB) * bScale, (invert?dB:oB))
                        : IM_DIV((invert?oB:dB) * bScale, (invert?dB:oB));
                    r = IM_MIN(r, COLOR_R5_MAX);
                    g = IM_MIN(g, COLOR_G6_MAX);
                    b = IM_MIN(b, COLOR_B5_MAX);
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, i, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }
            break;
        }
		case IMAGE_BPP_RGB888: {  // STM32IPL
			rgb888_t *data = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, line);
			int rScale = COLOR_R8_MAX - COLOR_R8_MIN;
			int gScale = COLOR_G8_MAX - COLOR_G8_MIN;
			int bScale = COLOR_B8_MAX - COLOR_B8_MIN;
			for (int i = 0, j = img->w; i < j; i++) {
				if ((!mask) || image_get_mask_pixel(mask, i, line)) {
					rgb888_t dataPixel = IMAGE_GET_RGB888_PIXEL_FAST(data, i);
					rgb888_t otherPixel = IMAGE_GET_RGB888_PIXEL_FAST(((rgb888_t* ) other), i);
					rgb888_t pixel888;
					int dR = dataPixel.r;
					int dG = dataPixel.g;
					int dB = dataPixel.b;
					int oR = otherPixel.r;
					int oG = otherPixel.g;
					int oB = otherPixel.b;
					int r = mod ?
							IM_MOD((invert ? oR : dR) * rScale, (invert ? dR : oR)) :
							IM_DIV((invert ? oR : dR) * rScale, (invert ? dR : oR));
					int g = mod ?
							IM_MOD((invert ? oG : dG) * gScale, (invert ? dG : oG)) :
							IM_DIV((invert ? oG : dG) * gScale, (invert ? dG : oG));
					int b = mod ?
							IM_MOD((invert ? oB : dB) * bScale, (invert ? dB : oB)) :
							IM_DIV((invert ? oB : dB) * bScale, (invert ? dB : oB));
					pixel888.r = IM_MIN(r, COLOR_R8_MAX);
					pixel888.g = IM_MIN(g, COLOR_G8_MAX);
					pixel888.b = IM_MIN(b, COLOR_B8_MAX);
					IMAGE_PUT_RGB565_PIXEL_FAST(data, i, pixel888);
				}
			}
			break;
		}

        default: {
            break;
        }
    }
}

void imlib_div(image_t *img, const char *path, image_t *other, int scalar, bool invert, bool mod, image_t *mask)
{
    imlib_div_line_op_state_t state;
    state.invert = invert;
    state.mod = mod;
    state.mask = mask;
    imlib_image_operation(img, path, other, scalar, imlib_div_line_op, &state);
}

static void imlib_min_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    image_t *mask = (image_t *) data;

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), i);
                    int p = IM_MIN(dataPixel, otherPixel);
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), i);
                    int p = IM_MIN(dataPixel, otherPixel);
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), i);
                    int r = IM_MIN(COLOR_RGB565_TO_R5(dataPixel), COLOR_RGB565_TO_R5(otherPixel));
                    int g = IM_MIN(COLOR_RGB565_TO_G6(dataPixel), COLOR_RGB565_TO_G6(otherPixel));
                    int b = IM_MIN(COLOR_RGB565_TO_B5(dataPixel), COLOR_RGB565_TO_B5(otherPixel));
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, i, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }
            break;
        }
		case IMAGE_BPP_RGB888: {  // STM32IPL
			rgb888_t *data = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, line);
			for (int i = 0, j = img->w; i < j; i++) {
				if ((!mask) || image_get_mask_pixel(mask, i, line)) {
					rgb888_t dataPixel = IMAGE_GET_RGB888_PIXEL_FAST(data, i);
					rgb888_t otherPixel = IMAGE_GET_RGB888_PIXEL_FAST(((rgb888_t* ) other), i);
					rgb888_t pixel888;
					pixel888.r = IM_MIN(dataPixel.r, otherPixel.r);
					pixel888.g = IM_MIN(dataPixel.g, otherPixel.g);
					pixel888.b = IM_MIN(dataPixel.b, otherPixel.b);
					IMAGE_PUT_RGB888_PIXEL_FAST(data, i, pixel888);
				}
			}
			break;
		}

        default: {
            break;
        }
    }
}

void imlib_min(image_t *img, const char *path, image_t *other, int scalar, image_t *mask)
{
    imlib_image_operation(img, path, other, scalar, imlib_min_line_op, mask);
}

static void imlib_max_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    image_t *mask = (image_t *) data;

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), i);
                    int p = IM_MAX(dataPixel, otherPixel);
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), i);
                    int p = IM_MAX(dataPixel, otherPixel);
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), i);
                    int r = IM_MAX(COLOR_RGB565_TO_R5(dataPixel), COLOR_RGB565_TO_R5(otherPixel));
                    int g = IM_MAX(COLOR_RGB565_TO_G6(dataPixel), COLOR_RGB565_TO_G6(otherPixel));
                    int b = IM_MAX(COLOR_RGB565_TO_B5(dataPixel), COLOR_RGB565_TO_B5(otherPixel));
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, i, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }
            break;
        }
		case IMAGE_BPP_RGB888: {  // STM32IPL
			rgb888_t *data = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, line);
			for (int i = 0, j = img->w; i < j; i++) {
				if ((!mask) || image_get_mask_pixel(mask, i, line)) {
					rgb888_t dataPixel = IMAGE_GET_RGB888_PIXEL_FAST(data, i);
					rgb888_t otherPixel = IMAGE_GET_RGB888_PIXEL_FAST(((rgb888_t* ) other), i);
					rgb888_t pixel888;
					pixel888.r = IM_MAX(dataPixel.r, otherPixel.r);
					pixel888.g = IM_MAX(dataPixel.g, otherPixel.g);
					pixel888.b = IM_MAX(dataPixel.b, otherPixel.b);
					IMAGE_PUT_RGB888_PIXEL_FAST(data, i, pixel888);
				}
			}
			break;
		}

        default: {
            break;
        }
    }
}

void imlib_max(image_t *img, const char *path, image_t *other, int scalar, image_t *mask)
{
    imlib_image_operation(img, path, other, scalar, imlib_max_line_op, mask);
}

static void imlib_difference_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    image_t *mask = (image_t *) data;

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), i);
                    int p = dataPixel ^ otherPixel; // abs(dataPixel - otherPixel);
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), i);
                    int p = abs(dataPixel - otherPixel);
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), i);
                    int r = abs(COLOR_RGB565_TO_R5(dataPixel) - COLOR_RGB565_TO_R5(otherPixel));
                    int g = abs(COLOR_RGB565_TO_G6(dataPixel) - COLOR_RGB565_TO_G6(otherPixel));
                    int b = abs(COLOR_RGB565_TO_B5(dataPixel) - COLOR_RGB565_TO_B5(otherPixel));
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, i, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }
            break;
        }
		case IMAGE_BPP_RGB888: {  // STM32IPL
			rgb888_t *data = IMAGE_COMPUTE_RGB888_PIXEL_ROW_PTR(img, line);
			for (int i = 0, j = img->w; i < j; i++) {
				if ((!mask) || image_get_mask_pixel(mask, i, line)) {
					rgb888_t dataPixel = IMAGE_GET_RGB888_PIXEL_FAST(data, i);
					rgb888_t otherPixel = IMAGE_GET_RGB888_PIXEL_FAST(((rgb888_t* ) other), i);
					rgb888_t pixel888;
					pixel888.r = abs(dataPixel.r - otherPixel.r);
					pixel888.g = abs(dataPixel.g - otherPixel.g);
					pixel888.b = abs(dataPixel.b - otherPixel.b);
					IMAGE_PUT_RGB888_PIXEL_FAST(data, i, pixel888);
				}
			}
			break;
		}

        default: {
            break;
        }
    }
}

void imlib_difference(image_t *img, const char *path, image_t *other, int scalar, image_t *mask)
{
    imlib_image_operation(img, path, other, scalar,imlib_difference_line_op,  mask);
}

#ifndef STM32IPL
typedef struct imlib_blend_line_op_state {
    float alpha;
    image_t *mask;
} imlib_blend_line_op_t;

static void imlib_blend_line_op(image_t *img, int line, void *other, void *data, bool vflipped)
{
    float alpha = ((imlib_blend_line_op_t *) data)->alpha, beta = 1 - alpha;
    image_t *mask = ((imlib_blend_line_op_t *) data)->mask;

    switch(img->bpp) {
        case IMAGE_BPP_BINARY: {
            uint32_t *data = IMAGE_COMPUTE_BINARY_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_BINARY_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_BINARY_PIXEL_FAST(((uint32_t *) other), i);
                    int p = (int)((dataPixel * alpha) + (otherPixel * beta)); // STM32IPL: added cast.
                    IMAGE_PUT_BINARY_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_GRAYSCALE: {
            uint8_t *data = IMAGE_COMPUTE_GRAYSCALE_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_GRAYSCALE_PIXEL_FAST(((uint8_t *) other), i);
                    int p = (int)((dataPixel * alpha) + (otherPixel * beta)); // STM32IPL: added cast.
                    IMAGE_PUT_GRAYSCALE_PIXEL_FAST(data, i, p);
                }
            }
            break;
        }
        case IMAGE_BPP_RGB565: {
            uint16_t *data = IMAGE_COMPUTE_RGB565_PIXEL_ROW_PTR(img, line);
            for (int i = 0, j = img->w; i < j; i++) {
                if ((!mask) || image_get_mask_pixel(mask, i, line)) {
                    int dataPixel = IMAGE_GET_RGB565_PIXEL_FAST(data, i);
                    int otherPixel = IMAGE_GET_RGB565_PIXEL_FAST(((uint16_t *) other), i);
                    int r = (int)((COLOR_RGB565_TO_R5(dataPixel) * alpha) + (COLOR_RGB565_TO_R5(otherPixel) * beta)); // STM32IPL: added cast.
                    int g = (int)((COLOR_RGB565_TO_G6(dataPixel) * alpha) + (COLOR_RGB565_TO_G6(otherPixel) * beta)); // STM32IPL: added cast.
                    int b = (int)((COLOR_RGB565_TO_B5(dataPixel) * alpha) + (COLOR_RGB565_TO_B5(otherPixel) * beta)); // STM32IPL: added cast.
                    IMAGE_PUT_RGB565_PIXEL_FAST(data, i, COLOR_R5_G6_B5_TO_RGB565(r, g, b));
                }
            }
            break;
        }
        default: {
            break;
        }
    }
}

void imlib_blend(image_t *img, const char *path, image_t *other, int scalar, float alpha, image_t *mask)
{
    imlib_blend_line_op_t state;
    state.alpha = alpha;
    state.mask = mask;
    imlib_image_operation(img, path, other, scalar, imlib_blend_line_op, &state);
}
#endif // STM32IPL
#endif //IMLIB_ENABLE_MATH_OPS
