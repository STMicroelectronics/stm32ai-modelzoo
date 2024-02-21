/**
 ******************************************************************************
 * @file   stm32ipl_image_io_jpg_sw.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - JPEG SW codec
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

///@cond

#include "stm32ipl_image_io_jpg_sw.h"

#ifdef STM32IPL_ENABLE_IMAGE_IO
#ifdef STM32IPL_ENABLE_JPEG
#ifndef STM32IPL_ENABLE_HW_JPEG_CODEC

#include "jpeglib.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint16_t rgb565_t;
typedef void (*ConvertLineFunction)(const uint8_t *src, uint8_t *dst, uint32_t width);

/*
 * Converts a line of the source image pixels from RGB888 to RGB565 and stores the converted data to the destination.
 * Assuming the two given data pointers point to valid buffers.
 * param src	Source image data.
 * param dst   	Destination image data.
 * param width	Width of the two images.
 * return 		void.
 */
static void ConvertLineRGB888ToRGB565(const uint8_t *src, uint8_t *dst, uint32_t width)
{
	rgb888_t *rgb888 = (rgb888_t*)src;
	rgb565_t *rgb565 = (uint16_t*)dst;

	for (uint32_t i = 0; i < width; i++) {
		uint16_t r = (rgb888[i].r >> 3) & 0x1f;
		uint16_t g = ((rgb888[i].g >> 2) & 0x3f) << 5;
		uint16_t b = ((rgb888[i].b >> 3) & 0x1f) << 11;

		*rgb565++ = (rgb565_t)(r | g | b);
	}
}

/*
 * Converts a line of the source image pixels from RGB565 to RGB888 and stores the converted data to the destination.
 * Assuming the two given data pointers point to valid buffers.
 * param src	Source image data.
 * param dst   	Destination image data.
 * param width	Width of the two images.
 * return 		void.
 */
static void ConvertLineRGB565ToRGB888(const uint8_t *src, uint8_t *dst, uint32_t width)
{
	rgb565_t *rgb565 = (rgb565_t*)src;
	rgb888_t *rgb888 = (rgb888_t*)dst;

	for (uint32_t i = 0; i < width; i++) {
		rgb565_t val = *rgb565++;

		uint32_t r = (val & 0x001F);
		uint32_t g = (val & 0x07E0) >> 5;
		uint32_t b = (val & 0xF800) >> 11;

		rgb888[i].r = (r << 3) | (r >> 2);
		rgb888[i].g = (g << 2) | (g >> 4);
		rgb888[i].b = (b << 3) | (b >> 2);
	}
}

/*
 * Converts a line of the source image pixels from RGB888 to RGB888 and stores the converted data to the destination.
 * Assuming the two given data pointers point to valid buffers.
 * param src	Source image data.
 * param dst   	Destination image data.
 * param width	Width of the two images.
 * return 		void.
 */
static void ConvertLineRGB888ToRGB888(const uint8_t *src, uint8_t *dst, uint32_t width)
{
	rgb888_t *src888 = (rgb888_t*)src;
	rgb888_t *dst888 = (rgb888_t*)dst;

	for (uint32_t i = 0; i < width; i++) {
		dst888[i].r = src888[i].b;
		dst888[i].g = src888[i].g;
		dst888[i].b = src888[i].r;
	}
}

/*
 * Converts a line of the source image pixels from Grayscale to RGB565 and stores the converted data to the destination.
 * Assuming the two given data pointers point to valid buffers.
 * param src	Source image data.
 * param dst   	Destination image data.
 * param width	Width of the two images.
 * return 		void.
 */
// NOT USED.
//static void ConvertLineGrayToRGB565(const uint8_t* src, uint8_t *dst, uint32_t width)
//{
//	uint8_t *gray = (uint8_t *)src;
//	rgb565_t *rgb565 = (rgb565_t*)dst;
//
//	for (uint32_t i = 0; i < width; i++) {
//		uint8_t val = *gray++;
//
//		rgb565_t b = ( val >> 3) & 0x1f;
//		rgb565_t g = ((val >> 2) & 0x3f) << 5;
//		rgb565_t r = b << 11;
//
//		*rgb565++ = (rgb565_t)(r | g | b);
//	}
//}

/*
 * Converts a line of the source image pixels from Grayscale to Grayscale and stores the converted data to the destination.
 * Assuming the two given data pointers point to valid buffers.
 * param src	Source image data.
 * param dst   	Destination image data.
 * param width	Width of the two images.
 * return 		void.
 */
static void ConvertLineGrayToGray(const uint8_t *src, uint8_t *dst, uint32_t width)
{
	memcpy(dst, src, width);
}

/*
 * Reads and decodes a JPEG file by using the libJPEG software decoder. The decoded image
 * will be Grayscale or RGB565 depending on the file content.
 * img		Decoded image; the image data buffer is allocated internally; it is up to
 * the caller to release the image data when done with it with STM32Ipl_ReleaseData().
 * fp		Pointer to the file object.
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t readJPEGSW(image_t *img, FIL *fp)
{
	struct jpeg_error_mgr jerr;
	struct jpeg_decompress_struct cinfo;
	JSAMPROW buffer[1] = { 0 };
	uint8_t *auxLine;
	uint8_t *imgData;
	uint8_t *imgLine;
	uint32_t bpp = 0;
	ConvertLineFunction convertFn = 0;

	if (!img || !fp)
		return stm32ipl_err_InvalidParameter;

	STM32Ipl_Init(img, 0, 0, (image_bpp_t)0, 0);

	if (f_lseek(fp, 0) != FR_OK)
		return stm32ipl_err_SeekingFile;

	cinfo.err = jpeg_std_error(&jerr);
	jpeg_create_decompress(&cinfo);
	jpeg_stdio_src(&cinfo, fp);
	jpeg_read_header(&cinfo, TRUE);
	cinfo.dct_method = JDCT_FLOAT;
	jpeg_start_decompress(&cinfo);

	switch (cinfo.out_color_space) {
		case JCS_RGB:
			convertFn = ConvertLineRGB888ToRGB565;
			bpp = IMAGE_BPP_RGB565;
			break;

		case JCS_GRAYSCALE:
			convertFn = ConvertLineGrayToGray;
			bpp = IMAGE_BPP_GRAYSCALE;
			break;

		case JCS_YCbCr:
		case JCS_CMYK:
		case JCS_YCCK:
		case JCS_UNKNOWN:
			jpeg_finish_decompress(&cinfo);
			jpeg_destroy_decompress(&cinfo);
			return stm32ipl_err_UnsupportedFormat;
	}

	auxLine = xalloc(cinfo.output_width * cinfo.out_color_components);
	if (!auxLine) {
		jpeg_finish_decompress(&cinfo);
		jpeg_destroy_decompress(&cinfo);
		return stm32ipl_err_OutOfMemory;
	}

	imgData = xalloc(STM32Ipl_DataSize(cinfo.output_width, cinfo.output_height, (image_bpp_t)bpp));
	if (!imgData) {
		xfree(auxLine);
		jpeg_finish_decompress(&cinfo);
		jpeg_destroy_decompress(&cinfo);
		return stm32ipl_err_OutOfMemory;
	}

	buffer[0] = auxLine;
	imgLine = imgData;

	while (cinfo.output_scanline < cinfo.output_height) {
		jpeg_read_scanlines(&cinfo, buffer, 1);
		convertFn(auxLine, imgLine, cinfo.output_width);
		imgLine += cinfo.output_width * bpp;
	}

	STM32Ipl_Init(img, cinfo.output_width, cinfo.output_height, (image_bpp_t)bpp, imgData);

	xfree(auxLine);

	jpeg_finish_decompress(&cinfo);
	jpeg_destroy_decompress(&cinfo);

	return stm32ipl_err_Ok;
}

/*
 * Encodes the given image to a JPEG file by using the libJPEG software encoder.
 * img		Image to be encoded (supported formats are: RGB565, RGB888 and Grayscale).
 * fp		Pointer to the file object.
 * chromaSS	Chroma subsampling; 4:4:4, 4:2:2, 4:2:0 are supported.
 * quality	Quality value used by the encoder (0-100), 100 means best quality.
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
static stm32ipl_err_t encodeJPEG(const image_t *img, FIL *fp, uint32_t chromaSS, uint32_t quality)
{
	struct jpeg_error_mgr jerr;
	struct jpeg_compress_struct cinfo;
	JSAMPROW buffer[1] = { 0 };
	uint8_t *auxLine;
	uint8_t *imgLine;
	ConvertLineFunction convertFn;
	uint8_t bpp;

	cinfo.err = jpeg_std_error(&jerr);
	jpeg_create_compress(&cinfo);
	jpeg_stdio_dest(&cinfo, fp);

	cinfo.image_width = img->w;
	cinfo.image_height = img->h;

	switch (img->bpp) {
		case IMAGE_BPP_RGB565:
			convertFn = ConvertLineRGB565ToRGB888;
			cinfo.input_components = 3;
			cinfo.in_color_space = JCS_RGB;
			bpp = 2;
			break;

		case IMAGE_BPP_RGB888:
			convertFn = ConvertLineRGB888ToRGB888;
			cinfo.input_components = 3;
			cinfo.in_color_space = JCS_RGB;
			bpp = 3;
			break;

		case IMAGE_BPP_GRAYSCALE:
			convertFn = ConvertLineGrayToGray;
			cinfo.input_components = 1;
			cinfo.in_color_space = JCS_GRAYSCALE;
			bpp = 1;
			break;

		default:
			jpeg_destroy_compress(&cinfo);
			return stm32ipl_err_UnsupportedFormat;
	}

	switch (chromaSS) {
		case STM32IPL_JPEG_444_SUBSAMPLING:
			cinfo.comp_info[0].h_samp_factor = 1;
			cinfo.comp_info[0].v_samp_factor = 1;
			cinfo.comp_info[1].h_samp_factor = 1;
			cinfo.comp_info[1].v_samp_factor = 1;
			cinfo.comp_info[2].h_samp_factor = 1;
			cinfo.comp_info[2].v_samp_factor = 1;
			break;

		case STM32IPL_JPEG_420_SUBSAMPLING:
			cinfo.comp_info[0].h_samp_factor = 2;
			cinfo.comp_info[0].v_samp_factor = 2;
			cinfo.comp_info[1].h_samp_factor = 1;
			cinfo.comp_info[1].v_samp_factor = 1;
			cinfo.comp_info[2].h_samp_factor = 1;
			cinfo.comp_info[2].v_samp_factor = 1;
			break;

		case STM32IPL_JPEG_422_SUBSAMPLING:
			cinfo.comp_info[0].h_samp_factor = 2;
			cinfo.comp_info[0].v_samp_factor = 1;
			cinfo.comp_info[1].h_samp_factor = 1;
			cinfo.comp_info[1].v_samp_factor = 1;
			cinfo.comp_info[2].h_samp_factor = 1;
			cinfo.comp_info[2].v_samp_factor = 1;
			break;

		default:
			jpeg_destroy_compress(&cinfo);
			return stm32ipl_err_UnsupportedFormat;
	}

	auxLine = xalloc(img->w * cinfo.input_components);
	if (!auxLine) {
		jpeg_destroy_compress(&cinfo);
		return stm32ipl_err_OutOfMemory;
	}

	jpeg_set_defaults(&cinfo);

	cinfo.dct_method = JDCT_FLOAT;

	jpeg_set_quality(&cinfo, quality, TRUE);
	jpeg_start_compress(&cinfo, TRUE);

	buffer[0] = auxLine;
	imgLine = img->data;

	while (cinfo.next_scanline < cinfo.image_height) {
		convertFn(imgLine, auxLine, cinfo.image_width);

		imgLine += cinfo.image_width * bpp;

		jpeg_write_scanlines(&cinfo, buffer, 1);
	}

	xfree(auxLine);

	jpeg_finish_compress(&cinfo);
	jpeg_destroy_compress(&cinfo);

	return stm32ipl_err_Ok;
}

/* Encodes the given image to a JPEG file by using the libJPEG software encoder.
 * img		Image to be encoded (supported formats are: RGB565, Grayscale).
 * filename	Name of the output file.
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t saveJPEGSW(const image_t *img, const char *filename)
{
	stm32ipl_err_t res;
	FIL fp;

	if (!img || !filename)
		return stm32ipl_err_InvalidParameter;

	if ((img->bpp != IMAGE_BPP_RGB565) && (img->bpp != IMAGE_BPP_RGB888) && (img->bpp != IMAGE_BPP_GRAYSCALE))
		return stm32ipl_err_UnsupportedFormat;

	if (f_open(&fp, (const TCHAR*)filename, FA_WRITE | FA_CREATE_ALWAYS) != FR_OK)
		return stm32ipl_err_OpeningFile;

	res = encodeJPEG(img, &fp, STM32IPL_JPEG_SUBSAMPLING, STM32IPL_JPEG_QUALITY);

	f_close(&fp);

	return res;
}

#ifdef __cplusplus
}
#endif

#endif /* STM32IPL_ENABLE_HW_JPEG_CODEC */
#endif /* STM32IPL_ENABLE_JPEG */
#endif /* STM32IPL_ENABLE_IMAGE_IO */

///@endcond

