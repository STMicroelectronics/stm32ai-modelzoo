/**
 ******************************************************************************
 * @file   stm32ipl_image_io.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - image read/write functions
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

#ifdef STM32IPL_ENABLE_IMAGE_IO
#ifdef STM32IPL_ENABLE_JPEG
#ifdef STM32IPL_ENABLE_HW_JPEG_CODEC
#include "stm32ipl_image_io_jpg_hw.h"
#else /* STM32IPL_ENABLE_HW_JPEG_CODEC */
#include "stm32ipl_image_io_jpg_sw.h"
#endif /* STM32IPL_ENABLE_HW_JPEG_CODEC */
#endif /* STM32IPL_ENABLE_JPEG */

#include <stdio.h>
#include <ctype.h>
#include "ff.h"

#ifdef __cplusplus
extern "C" {
#endif

#define BI_RGB              0
#define BI_RLE8             1
#define BI_RLE4             2
#define BI_BITFIELDS        3

#define RGB555_RED_MASK     0x7C00
#define RGB555_GREEN_MASK   0x03E0
#define RGB555_BLUE_MASK    0x001F

#define RGB565_RED_MASK     0xF800
#define RGB565_GREEN_MASK   0x07E0
#define RGB565_BLUE_MASK    0x001F

typedef enum _ImageFileFormatType
{
	iplFileFormatUnknown, iplFileFormatBMP,
	// TODO: iplFileFormatPBM. Not supported.
	iplFileFormatPPM,
	iplFileFormatPGM,
	iplFileFormatJPG,
} ImageFileFormatType;

/* Returns the image file format by analyzing the file extension.
 * BMP, PPM, PGM, JPEG formats are supported.
 * filename	Name of the input file.
 * return	image file format.
 */
static ImageFileFormatType getImageFileFormat(const char *filename)
{
	ImageFileFormatType format = iplFileFormatUnknown;
	size_t len;
	char *upFilename;
	char *ptr;

	if (!filename)
		return iplFileFormatUnknown;

	len = strlen(filename);

	/* Convert to upper case. */
	upFilename = xalloc(len);
	strcpy(upFilename, filename);

	for (size_t i = 0; i < len; i++)
		upFilename[i] = toupper(upFilename[i]);

	ptr = upFilename + len;

	if (len >= 5) {
		if ((ptr[-1] == 'G') && (ptr[-2] == 'E') && (ptr[-3] == 'P') && (ptr[-4] == 'J') && (ptr[-5] == '.'))
			format = iplFileFormatJPG;
	}
	if (len >= 4) {
		if ((ptr[-1] == 'G') && (ptr[-2] == 'P') && (ptr[-3] == 'J') && (ptr[-4] == '.'))
			format = iplFileFormatJPG;
		else
			if ((ptr[-1] == 'P') && (ptr[-2] == 'M') && (ptr[-3] == 'B') && (ptr[-4] == '.'))
				format = iplFileFormatBMP;
			else
				if ((ptr[-1] == 'M') && (ptr[-2] == 'P') && (ptr[-3] == 'P') && (ptr[-4] == '.'))
					format = iplFileFormatPPM;
				else
					if ((ptr[-1] == 'M') && (ptr[-2] == 'G') && (ptr[-3] == 'P') && (ptr[-4] == '.'))
						format = iplFileFormatPGM;
	}

	xfree(upFilename);

	return format;
}

/* Checks if the given palette contains grayscale items.
 * palette		Palette to be checked.
 * colorUsed	Number of items to be considered.
 * return		true if the palette has grayscale items, false otherwise.
 */
static bool grayscalePalette(uint32_t *palette, uint32_t colorUsed)
{
	if (!palette)
		return false;

	for (uint32_t i = 0; i < colorUsed; i++) {
		uint8_t b = palette[i];
		uint8_t g = palette[i] >> 8;
		uint8_t r = palette[i] >> 16;
		if ((b != g) | (b != r))
			return false;
	}

	return true;
}

/* Reads BMP image file; supported files are: 1, 4, 8 bits/pixel with palette;
 * 16 bits/pixels with or without BITFIELDS; 24 bits/pixels; compressed BI_RGB and BI_BITFIELDS.
 * The generated image will be:
 * 	- Binary in case the input file has 1 bit/pixel with black and white palette.
 * 	- Grayscale in case the input file has 8 bits/pixel with a complete grayscale.
 * palette (equal RGB channels for all the palette items).
 * 	- RGB888 in case the input file has 24 bits/pixel.
 * 	- RGB565 for the remaining cases.
 * img		Image read. The pixel data is allocated internally and must be released
 * with STM32Ipl_ReleaseData(); assuming that input img->data is null.
 * fp		Pointer to the input file structure.
 * return	stm32ipl_err_Ok on success, errors otherwise.
 */
static stm32ipl_err_t readBmp(image_t *img, FIL *fp)
{
	uint32_t dataOffset; /* The offset, in bytes, from the beginning of the file to the image pixels. */
	uint32_t infoHeaderSize; /* The number of bytes of the header. */
	int32_t width; /* The width of the bitmap, in pixels. */
	int32_t height; /* The height of the bitmap, in pixels. */
	uint16_t bitCount; /* The number of bits per pixel (bpp). */
	uint32_t compression; /* The type of compression used. */
	uint32_t colorUsed; /* The number of colors used. */
	uint32_t lineSize; /* The size of a bitmap line (in bytes). */
	uint8_t header[54];
	uint8_t *pHeader;
	uint32_t bytesRead;
	uint8_t *outData;
	uint32_t paletteSize;
	uint8_t *lineData;
	uint32_t line;
	uint8_t *ptr;
	uint32_t rMask;
	uint32_t gMask;
	uint32_t bMask;

	if (!img || !fp)
		return stm32ipl_err_InvalidParameter;

	STM32Ipl_Init(img, 0, 0, (image_bpp_t)0, 0);

	if (f_lseek(fp, 0) != FR_OK)
		return stm32ipl_err_SeekingFile;

	/* Read file header and info header (54 bytes). */
	if ((f_read(fp, header, sizeof(header), (UINT*)&bytesRead) != FR_OK) || bytesRead != sizeof(header))
		return stm32ipl_err_ReadingFile;

	pHeader = (uint8_t*)header;

	/* Read the data offset. */
	dataOffset = pHeader[10] + (pHeader[11] << 8) + (pHeader[12] << 16) + (pHeader[13] << 24);

	/* Read the size of the info header. */
	infoHeaderSize = pHeader[14] + (pHeader[15] << 8) + (pHeader[16] << 16) + (pHeader[17] << 24);
	if ((infoHeaderSize != 40) /* BITMAPINFOHEADER */
	&& (infoHeaderSize != 52) /* BITMAPV2INFOHEADER */
	&& (infoHeaderSize != 56) /* BITMAPV3INFOHEADER */
	&& (infoHeaderSize != 108) /* BITMAPV4HEADER */
	&& (infoHeaderSize != 124)) /* BITMAPV5HEADER */
		return stm32ipl_err_UnsupportedFormat;

	/* Read the bitmap width. */
	width = pHeader[18] + (pHeader[19] << 8) + (pHeader[20] << 16) + (pHeader[21] << 24);

	/* Read the bitmap height. */
	height = pHeader[22] + (pHeader[23] << 8) + (pHeader[24] << 16) + (pHeader[25] << 24);

	/* Read the bpp. */
	bitCount = pHeader[28] + (pHeader[29] << 8);
	if ((bitCount != 1) && (bitCount != 4) && (bitCount != 8) && (bitCount != 16) && (bitCount != 24))
		return stm32ipl_err_UnsupportedFormat;

	/* Read the compression. Only BI_RGB and BI_BITFIELDS are supported. */
	compression = pHeader[30] + (pHeader[31] << 8) + (pHeader[32] << 16) + (pHeader[33] << 24);
	if (compression != BI_RGB && compression != BI_BITFIELDS)
		return stm32ipl_err_UnsupportedFormat;

	/* Read the number of colors used in the palette. */
	colorUsed = pHeader[46] + (pHeader[47] << 8) + (pHeader[48] << 16) + (pHeader[49] << 24);
	if (colorUsed == 0)
		colorUsed = 1 << bitCount;

	lineSize = (((width * bitCount) + 31) / 32) * 4;

	/* Evaluate eventual bit fields. */
	if ((compression == BI_BITFIELDS) && (bitCount == 16)) {
		uint8_t mask[4];
		/* Read the three bit masks. */
		if ((f_read(fp, mask, sizeof(mask), (UINT*)&bytesRead) != FR_OK) || bytesRead != sizeof(mask))
			return stm32ipl_err_ReadingFile;

		rMask = mask[0] + (mask[1] << 8) + (mask[2] << 16) + (mask[3] << 24);

		if ((f_read(fp, mask, sizeof(mask), (UINT*)&bytesRead) != FR_OK) || bytesRead != sizeof(mask))
			return stm32ipl_err_ReadingFile;

		gMask = mask[0] + (mask[1] << 8) + (mask[2] << 16) + (mask[3] << 24);

		if ((f_read(fp, mask, sizeof(mask), (UINT*)&bytesRead) != FR_OK) || bytesRead != sizeof(mask))
			return stm32ipl_err_ReadingFile;

		bMask = mask[0] + (mask[1] << 8) + (mask[2] << 16) + (mask[3] << 24);
	} else {
		/* Default for no compression is RGB555. */
		rMask = RGB555_RED_MASK;
		gMask = RGB555_GREEN_MASK;
		bMask = RGB555_BLUE_MASK;
	}

	switch (bitCount) {
		case 1: {
			uint32_t palette[2];

			paletteSize = colorUsed * sizeof(uint32_t);

			/* Skip the header. */
			if (f_lseek(fp, dataOffset - paletteSize) != FR_OK)
				return stm32ipl_err_SeekingFile;

			/* Read the palette. */
			if ((f_read(fp, palette, paletteSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != paletteSize)
				return stm32ipl_err_ReadingFile;

			/* If the palette is made of black and white colors, the output image will be binary, RGB565 otherwise. */
			if ((palette[0] == 0x0 && palette[1] == 0xFFFFFF) || (palette[0] == 0xFFFFFF && palette[1] == 0x0)) {
				/* Black and white colors --> binary output. */

				uint32_t *outRow;
				uint32_t offset = lineSize / 4;

				/* Allocate memory for pixel data (binary). */
				outData = xalloc0(STM32Ipl_DataSize(width, abs(height), IMAGE_BPP_BINARY));
				if (!outData)
					return stm32ipl_err_OutOfMemory;

				lineData = xalloc(lineSize);
				if (!lineData) {
					xfree(outData);
					return stm32ipl_err_OutOfMemory;
				}

				/* Jump to the first or last line. */
				line = dataOffset + ((height > 0) ? (lineSize * (height - 1)) : 0);
				if (f_lseek(fp, line) != FR_OK) {
					xfree(lineData);
					xfree(outData);
					return stm32ipl_err_SeekingFile;
				}

				outRow = (uint32_t*)outData;

				for (uint32_t i = 0; i < abs(height); i++) {
					uint8_t value;
					uint8_t k;
					uint8_t *inData;

					value = 0;
					k = 0;
					inData = (uint8_t*)lineData;

					if ((f_read(fp, lineData, lineSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != lineSize) {
						xfree(lineData);
						xfree(outData);
						return stm32ipl_err_ReadingFile;
					}

					for (uint32_t j = 0; j < width; k--, j++) {
						if (!(j % 8)) {
							value = (*inData++);
							k = 7;
						}
						IMAGE_PUT_BINARY_PIXEL_FAST(outRow, j, palette[(value >> k) & 1]);
					}

					outRow += offset;

					if (height > 0) {
						line -= lineSize;
						if (line >= dataOffset) {
							if (f_lseek(fp, line) != FR_OK) {
								xfree(lineData);
								xfree(outData);
								return stm32ipl_err_SeekingFile;
							}
						}
					} else {
						line += lineSize;
					}
				}

				xfree(lineData);
				lineData = 0;

				STM32Ipl_Init(img, width, abs(height), IMAGE_BPP_BINARY, outData);
			} else {
				/* Not black and white colors --> RGB565 output. */

				uint16_t *outPixel;

				/* Allocate memory for pixel data (RGB565). */
				outData = xalloc(width * abs(height) * 2);
				if (!outData)
					return stm32ipl_err_OutOfMemory;

				lineData = xalloc(lineSize);
				if (!lineData) {
					xfree(outData);
					return stm32ipl_err_OutOfMemory;
				}

				/* Jump to the first or last line. */
				line = dataOffset + ((height > 0) ? (lineSize * (height - 1)) : 0);
				if (f_lseek(fp, line) != FR_OK) {
					xfree(lineData);
					xfree(outData);
					return stm32ipl_err_SeekingFile;
				}

				outPixel = (uint16_t*)outData;
				for (uint32_t i = 0; i < abs(height); i++) {
					uint8_t value = 0;
					uint8_t k = 0;

					if ((f_read(fp, lineData, lineSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != lineSize) {
						xfree(lineData);
						xfree(outData);
						return stm32ipl_err_ReadingFile;
					}

					ptr = lineData;

					for (uint32_t j = 0; j < width; k--, j++) {
						uint8_t index;
						uint8_t r;
						uint8_t g;
						uint8_t b;

						if (!(j % 8)) {
							value = (*ptr++);
							k = 7;
						}

						index = (value >> k) & 0x1;
						r = palette[index] >> 16;
						g = palette[index] >> 8;
						b = palette[index];

						*outPixel++ = (uint16_t)COLOR_R8_G8_B8_TO_RGB565(r, g, b);
					}

					if (height > 0) {
						line -= lineSize;
						if (line >= dataOffset) {
							if (f_lseek(fp, line) != FR_OK) {
								xfree(lineData);
								xfree(outData);
								return stm32ipl_err_SeekingFile;
							}
						}
					} else {
						line += lineSize;
					}
				}

				xfree(lineData);
				lineData = 0;

				STM32Ipl_Init(img, width, abs(height), IMAGE_BPP_RGB565, outData);
			}

			break;
		}

		case 4: {
			uint16_t *outPixel;
			uint32_t palette[16];

			paletteSize = colorUsed * sizeof(uint32_t);

			/* Skip the header. */
			if (f_lseek(fp, dataOffset - paletteSize) != FR_OK)
				return stm32ipl_err_SeekingFile;

			/* Read the palette. */
			if ((f_read(fp, palette, paletteSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != paletteSize)
				return stm32ipl_err_ReadingFile;

			/* Allocate memory for pixel data (RGB565). */
			outData = xalloc(width * abs(height) * 2);
			if (!outData)
				return stm32ipl_err_OutOfMemory;

			lineData = xalloc(lineSize);
			if (!lineData) {
				xfree(outData);
				return stm32ipl_err_OutOfMemory;
			}

			/* Jump to the first or last line. */
			line = dataOffset + ((height > 0) ? (lineSize * (height - 1)) : 0);
			if (f_lseek(fp, line) != FR_OK) {
				xfree(lineData);
				xfree(outData);
				return stm32ipl_err_SeekingFile;
			}

			outPixel = (uint16_t*)outData;
			for (uint32_t i = 0; i < abs(height); i++) {
				if ((f_read(fp, lineData, lineSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != lineSize) {
					xfree(lineData);
					xfree(outData);
					return stm32ipl_err_ReadingFile;
				}

				ptr = lineData;
				for (uint32_t j = 0; j < width;) {
					uint8_t value = (*ptr++);
					uint8_t index = value >> 4;
					uint8_t r = palette[index] >> 16;
					uint8_t g = palette[index] >> 8;
					uint8_t b = palette[index];

					*outPixel++ = (uint16_t)COLOR_R8_G8_B8_TO_RGB565(r, g, b);

					j++;
					if (j < width) {
						index = value & 0xF;
						r = palette[index] >> 16;
						g = palette[index] >> 8;
						b = palette[index];

						*outPixel++ = (uint16_t)COLOR_R8_G8_B8_TO_RGB565(r, g, b);
					}
					j++;
				}

				if (height > 0) {
					line -= lineSize;
					if (line >= dataOffset) {
						if (f_lseek(fp, line) != FR_OK) {
							xfree(lineData);
							xfree(outData);
							return stm32ipl_err_SeekingFile;
						}
					}
				} else {
					line += lineSize;
				}
			}

			xfree(lineData);
			lineData = 0;

			STM32Ipl_Init(img, width, abs(height), IMAGE_BPP_RGB565, outData);

			break;
		}

		case 8: {
			uint32_t palette[256];

			paletteSize = colorUsed * sizeof(uint32_t);

			/* Skip the header. */
			if (f_lseek(fp, dataOffset - paletteSize) != FR_OK)
				return stm32ipl_err_SeekingFile;

			/* Read the palette. */
			if ((f_read(fp, palette, paletteSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != paletteSize)
				return stm32ipl_err_ReadingFile;

			/* In case of grayscale palette, the output image will be Grayscale, RGB565 otherwise. */
			if (grayscalePalette(palette, colorUsed)) {
				/* Grayscale palette --> Grayscale output. */
				uint8_t *outPixel;

				/* Allocate memory for pixel data (Grayscale). */
				outData = xalloc(width * abs(height));
				if (!outData)
					return stm32ipl_err_OutOfMemory;

				lineData = xalloc(lineSize);
				if (!lineData) {
					xfree(outData);
					return stm32ipl_err_OutOfMemory;
				}

				/* Jump to the first or last line. */
				line = dataOffset + ((height > 0) ? (lineSize * (height - 1)) : 0);
				if (f_lseek(fp, line) != FR_OK) {
					xfree(lineData);
					xfree(outData);
					return stm32ipl_err_SeekingFile;
				}

				outPixel = (uint8_t*)outData;
				for (uint32_t i = 0; i < abs(height); i++) {
					if ((f_read(fp, lineData, lineSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != lineSize) {
						xfree(lineData);
						xfree(outData);
						return stm32ipl_err_ReadingFile;
					}

					ptr = lineData;
					for (uint32_t j = 0; j < width; j++)
						*outPixel++ = palette[*ptr++];

					if (height > 0) {
						line -= lineSize;
						if (line >= dataOffset) {
							if (f_lseek(fp, line) != FR_OK) {
								xfree(lineData);
								xfree(outData);
								return stm32ipl_err_SeekingFile;
							}
						}
					} else {
						line += lineSize;
					}
				}

				xfree(lineData);
				lineData = 0;

				STM32Ipl_Init(img, width, abs(height), IMAGE_BPP_GRAYSCALE, outData);
			} else {
				/* Not grayscale palette --> RGB565 output. */

				uint16_t *outPixel;

				/* Allocate memory for pixel data (RGB565). */
				outData = xalloc(width * abs(height) * 2);
				if (!outData)
					return stm32ipl_err_OutOfMemory;

				lineData = xalloc(lineSize);
				if (!lineData) {
					xfree(outData);
					return stm32ipl_err_OutOfMemory;
				}

				/* Jump to the first or last line. */
				line = dataOffset + ((height > 0) ? (lineSize * (height - 1)) : 0);
				if (f_lseek(fp, line) != FR_OK) {
					xfree(lineData);
					xfree(outData);
					return stm32ipl_err_SeekingFile;
				}

				outPixel = (uint16_t*)outData;
				for (uint32_t i = 0; i < abs(height); i++) {
					if ((f_read(fp, lineData, lineSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != lineSize) {
						xfree(lineData);
						xfree(outData);
						return stm32ipl_err_ReadingFile;
					}

					ptr = lineData;
					for (uint32_t j = 0; j < width; j++) {
						uint8_t index = (*ptr++);
						uint8_t r = palette[index] >> 16;
						uint8_t g = palette[index] >> 8;
						uint8_t b = palette[index];

						*outPixel++ = (uint16_t)COLOR_R8_G8_B8_TO_RGB565(r, g, b);
					}

					if (height > 0) {
						line -= lineSize;
						if (line >= dataOffset) {
							if (f_lseek(fp, line) != FR_OK) {
								xfree(lineData);
								xfree(outData);
								return stm32ipl_err_SeekingFile;
							}
						}
					} else {
						line += lineSize;
					}
				}

				xfree(lineData);
				lineData = 0;

				STM32Ipl_Init(img, width, abs(height), IMAGE_BPP_RGB565, outData);
			}

			break;
		}

		case 16: {
			uint16_t *outPixel;
			uint16_t *inPixel;

			/* Skip the header. */
			if (f_lseek(fp, dataOffset) != FR_OK)
				return stm32ipl_err_SeekingFile;

			/* Allocate memory for pixel data (RGB565). */
			outData = xalloc(width * abs(height) * 2);
			if (!outData)
				return stm32ipl_err_OutOfMemory;

			lineData = xalloc(lineSize);
			if (!lineData) {
				xfree(outData);
				return stm32ipl_err_OutOfMemory;
			}

			/* Jump to the first or last line. */
			line = dataOffset + ((height > 0) ? (lineSize * (height - 1)) : 0);

			if (f_lseek(fp, line) != FR_OK) {
				xfree(outData);
				return stm32ipl_err_SeekingFile;
			}

			outPixel = (uint16_t*)outData;

			for (uint32_t i = 0; i < abs(height); i++) {
				if ((f_read(fp, lineData, lineSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != lineSize) {
					xfree(lineData);
					xfree(outData);
					return stm32ipl_err_ReadingFile;
				}

				inPixel = (uint16_t*)lineData;

				for (uint32_t j = 0; j < width; j++) {
					uint16_t value = *inPixel;

					if (compression && (rMask == RGB565_RED_MASK) && (gMask == RGB565_GREEN_MASK)
							&& (bMask == RGB565_BLUE_MASK))
						/* RGB565 case. */
						*outPixel++ = value;
					else
						/* RGB555 case. */
						*outPixel++ = ((value & rMask) << 1) | ((value & gMask) << 1) | (value & bMask);

					inPixel++;
				}

				if (height > 0) {
					line -= lineSize;
					if (line >= dataOffset) {
						if (f_lseek(fp, line) != FR_OK) {
							xfree(lineData);
							xfree(outData);
							return stm32ipl_err_SeekingFile;
						}
					}
				} else {
					line += lineSize;
				}
			}

			xfree(lineData);
			lineData = 0;

			STM32Ipl_Init(img, width, abs(height), IMAGE_BPP_RGB565, outData);

			break;
		}

		case 24: {
			uint8_t *outPixel;
			uint32_t outLineSize = width * 3;

			/* Skip the header. */
			if (f_lseek(fp, dataOffset) != FR_OK)
				return stm32ipl_err_SeekingFile;

			/* Allocate memory for pixel data (RGB888). */
			outData = xalloc(outLineSize * abs(height));
			if (!outData)
				return stm32ipl_err_OutOfMemory;

			lineData = xalloc(lineSize);
			if (!lineData) {
				xfree(outData);
				return stm32ipl_err_OutOfMemory;
			}

			/* Jump to the first or last line. */
			line = dataOffset + ((height > 0) ? (lineSize * (height - 1)) : 0);

			if (f_lseek(fp, line) != FR_OK) {
				xfree(lineData);
				xfree(outData);
				return stm32ipl_err_SeekingFile;
			}

			outPixel = (uint8_t*)outData;

			for (uint32_t i = 0; i < abs(height); i++) {
				if ((f_read(fp, lineData, lineSize, (UINT*)&bytesRead) != FR_OK) || bytesRead != lineSize) {
					xfree(lineData);
					xfree(outData);
					return stm32ipl_err_ReadingFile;
				}

				memcpy(outPixel, lineData, outLineSize);

				outPixel += outLineSize;

				if (height > 0) {
					line -= lineSize;
					if (line >= dataOffset) {
						if (f_lseek(fp, line) != FR_OK) {
							xfree(lineData);
							xfree(outData);
							return stm32ipl_err_SeekingFile;
						}
					}
				} else {
					line += lineSize;
				}
			}

			xfree(lineData);
			lineData = 0;

			STM32Ipl_Init(img, width, abs(height), IMAGE_BPP_RGB888, outData);

			break;
		}

		default:
			return stm32ipl_err_UnsupportedFormat;
	};

	return stm32ipl_err_Ok;
}

/* Reads PNM image file. The supported formats are:
 * - plain PGM (Grayscale, ASCII).
 * - raw PGM (Grayscale, binary).
 * - plain PPM (RGB888, ASCII).
 * - raw PPM (RGB888, binary).
 * The generated image will be IMAGE_BPP_GRAYSCALE or IMAGE_BPP_RGB888, depending
 * on the actual image content.
 * img		Image read; the pixel data is allocated internally and must be released
 * with STM32Ipl_ReleaseData(); assuming that input img->data is null.
 * fp 		Pointer to the input file structure.
 * return	stm32ipl_err_Ok on success, errors otherwise.
 */
static stm32ipl_err_t readPnm(image_t *img, FIL *fp)
{
	uint32_t size;
	uint32_t width;
	uint32_t height;
	UINT bytesRead;
	uint32_t number;
	uint8_t sector[512];
	uint8_t number_ppm;
	bool valid = false;
	uint8_t *outData;

	enum
	{
		EAT_WHITESPACE, EAT_COMMENT, EAT_NUMBER
	} mode = EAT_WHITESPACE;

	if (!img || !fp)
		return stm32ipl_err_InvalidParameter;

	STM32Ipl_Init(img, 0, 0, (image_bpp_t)0, 0);

	if (f_lseek(fp, 0) != FR_OK)
		return stm32ipl_err_SeekingFile;

	if ((f_read(fp, sector, 2, (UINT*)&bytesRead) != FR_OK) || bytesRead != 2)
		return stm32ipl_err_ReadingFile;

	number = 0;

	/* Read bpp. */
	number_ppm = sector[1];

	/* "P1" = plain PBM (binary, ASCII, not supported)
	 * "P2" = plain PGM (Grayscale, ASCII)
	 * "P3" = plain PPM (RGB888, ASCII)
	 * "P4" = raw PBM (binary, not supported)
	 * "P5" = raw PGM (Grayscale)
	 * "P6" = raw PPM (RGB888)
	 */
	if ((number_ppm != '2') && (number_ppm != '3') && (number_ppm != '5') && (number_ppm != '6'))
		return stm32ipl_err_UnsupportedFormat;

	do {
		if ((f_read(fp, sector, 1, &bytesRead) != FR_OK) || bytesRead != 1)
			return stm32ipl_err_ReadingFile;

		if (mode == EAT_WHITESPACE) {
			if (sector[0] == '#') {
				mode = EAT_COMMENT;
			} else
				if (('0' <= sector[0]) && (sector[0] <= '9')) {
					number = sector[0] - '0';
					mode = EAT_NUMBER;
				}
		} else
			if (mode == EAT_COMMENT) {
				if ((sector[0] == '\n') || (sector[0] == '\r')) {
					mode = EAT_WHITESPACE;
				}
			} else
				if (mode == EAT_NUMBER) {
					if (('0' <= sector[0]) && (sector[0] <= '9')) {
						number = (number * 10) + sector[0] - '0';
					} else {
						valid = true;
					}
				}
	} while (!valid);

	width = number;
	number = 0;
	mode = EAT_WHITESPACE;

	do {
		if (valid) {
			valid = false;
		} else {
			if ((f_read(fp, sector, 1, &bytesRead) != FR_OK) || bytesRead != 1)
				return stm32ipl_err_ReadingFile;
		}

		if (mode == EAT_WHITESPACE) {
			if (sector[0] == '#') {
				mode = EAT_COMMENT;
			} else
				if (('0' <= sector[0]) && (sector[0] <= '9')) {
					number = sector[0] - '0';
					mode = EAT_NUMBER;
				}
		} else
			if (mode == EAT_COMMENT) {
				if ((sector[0] == '\n') || (sector[0] == '\r')) {
					mode = EAT_WHITESPACE;
				}
			} else
				if (mode == EAT_NUMBER) {
					if (('0' <= sector[0]) && (sector[0] <= '9')) {
						number = (number * 10) + sector[0] - '0';
					} else {
						valid = true;
					}
				}
	} while (!valid);

	height = number;
	number = 0;
	mode = EAT_WHITESPACE;

	if (height == 0 || width == 0)
		return stm32ipl_err_InvalidParameter;

	do {
		if (valid) {
			valid = false;
		} else {
			if ((f_read(fp, sector, 1, &bytesRead) != FR_OK) || bytesRead != 1)
				return stm32ipl_err_ReadingFile;
		}

		if (mode == EAT_WHITESPACE) {
			if (sector[0] == '#') {
				mode = EAT_COMMENT;
			} else
				if (('0' <= sector[0]) && (sector[0] <= '9')) {
					number = sector[0] - '0';
					mode = EAT_NUMBER;
				}
		} else
			if (mode == EAT_COMMENT) {
				if ((sector[0] == '\n') || (sector[0] == '\r')) {
					mode = EAT_WHITESPACE;
				}
			} else
				if (mode == EAT_NUMBER) {
					if (('0' <= sector[0]) && (sector[0] <= '9')) {
						number = (number * 10) + sector[0] - '0';
					} else {
						valid = true;
					}
				}
	} while (!valid);

	if (number > 255)
		return stm32ipl_err_Generic;

	switch (number_ppm) {
		case '2': {
			/* "P2" = plain PGM (Grayscale, ASCII). */

			outData = xalloc(width * height);
			if (!outData)
				return stm32ipl_err_OutOfMemory;

			for (uint32_t i = 0; i < height; i++) {
				uint32_t offset = i * width;

				for (uint32_t j = 0; j < width; j++) {
					number = 0;
					mode = EAT_WHITESPACE;

					do {
						if (valid) {
							valid = false;
						} else {
							if ((f_read(fp, sector, 1, &bytesRead) != FR_OK) || bytesRead != 1)
								return stm32ipl_err_ReadingFile;
						}
						if (mode == EAT_WHITESPACE) {
							if (sector[0] == '#') {
								mode = EAT_COMMENT;
							} else
								if (('0' <= sector[0]) && (sector[0] <= '9')) {
									number = sector[0] - '0';
									mode = EAT_NUMBER;
								}
						} else
							if (mode == EAT_COMMENT) {
								if ((sector[0] == '\n') || (sector[0] == '\r')) {
									mode = EAT_WHITESPACE;
								}
							} else
								if (mode == EAT_NUMBER) {
									if (('0' <= sector[0]) && (sector[0] <= '9')) {
										number = (number * 10) + sector[0] - '0';
									} else {
										valid = true;
									}
								}
					} while (!valid);

					outData[offset + j] = (uint8_t)number;
				}
			}

			STM32Ipl_Init(img, width, height, IMAGE_BPP_GRAYSCALE, outData);

			break;
		}

		case '3': {
			/* "P3" = plain PPM (RGB888, ASCII). */

			uint8_t *outPixel;

			outData = xalloc(width * height * 3);
			if (!outData)
				return stm32ipl_err_OutOfMemory;

			outPixel = outData;

			for (uint32_t i = 0; i < height; i++) {
				for (uint32_t j = 0; j < width; j++) {
					uint8_t pixel[3];

					for (uint8_t counter = 0; counter < 3; counter++) {
						number = 0;
						mode = EAT_WHITESPACE;

						do {
							if (valid) {
								valid = false;
							} else {
								if ((f_read(fp, sector, 1, &bytesRead) != FR_OK) || bytesRead != 1)
									return stm32ipl_err_ReadingFile;
							}

							if (mode == EAT_WHITESPACE) {
								if (sector[0] == '#') {
									mode = EAT_COMMENT;
								} else
									if (('0' <= sector[0]) && (sector[0] <= '9')) {
										number = sector[0] - '0';
										mode = EAT_NUMBER;
									}
							} else
								if (mode == EAT_COMMENT) {
									if ((sector[0] == '\n') || (sector[0] == '\r')) {
										mode = EAT_WHITESPACE;
									}
								} else
									if (mode == EAT_NUMBER) {
										if (('0' <= sector[0]) && (sector[0] <= '9')) {
											number = (number * 10) + sector[0] - '0';
										} else {
											valid = true;
										}
									}
						} while (!valid);

						pixel[counter] = number;
					}

					*outPixel++ = pixel[2];
					*outPixel++ = pixel[1];
					*outPixel++ = pixel[0];

				}
			}

			STM32Ipl_Init(img, width, height, IMAGE_BPP_RGB888, outData);

			break;
		}

		case '5': {
			/* "P5" = raw PGM (Grayscale). */

			size = width * height;
			outData = xalloc(size);
			if (!outData)
				return stm32ipl_err_OutOfMemory;

			if ((f_read(fp, outData, size, &bytesRead) != FR_OK) || bytesRead != size)
				return stm32ipl_err_ReadingFile;

			STM32Ipl_Init(img, width, height, IMAGE_BPP_GRAYSCALE, outData);

			break;
		}

		case '6': {
			/* "P6" = raw PPM (RGB888). */

			size = width * height * 3;

			outData = xalloc(size);
			if (!outData)
				return stm32ipl_err_OutOfMemory;

			if ((f_read(fp, outData, size, &bytesRead) != FR_OK) || bytesRead != size)
				return stm32ipl_err_ReadingFile;

			for (uint32_t i = 0; i < size; i += 3) {
				uint8_t tmp = outData[i];
				outData[i] = outData[i + 2];
				outData[i + 2] = tmp;
			}

			STM32Ipl_Init(img, width, height, IMAGE_BPP_RGB888, outData);

			break;
		}

		default:
			return stm32ipl_err_UnsupportedFormat;
	}

	return stm32ipl_err_Ok;
}

#ifdef STM32IPL_ENABLE_JPEG
/* Reads JPEG image file; the generated image will be Grayscale or RGB565 depending on the actual
 * image content; depending on the configuration file (stm32ipl_conf.h) the SW or the HW JPEG
 * decoder will be used.
 * img		Image read; the pixel data is allocated internally and must be released
 * with STM32Ipl_ReleaseData(); assuming that input img->data is null.
 * fp		Pointer to the input file structure.
 * return	stm32ipl_err_Ok on success, errors otherwise.
 */
static stm32ipl_err_t readJpg(image_t *img, FIL *fp)
{
#ifdef STM32IPL_ENABLE_HW_JPEG_CODEC
	return readJPEGHW(img, fp);
#else
	return readJPEGSW(img, fp);
#endif
}
#endif /* STM32IPL_ENABLE_JPEG */

/**
 * @brief Reads image file; supported file formats are: BMP, PPM, PGM, JPG.
 * - BMP: supported files are: 1, 4, 8 bits/pixel with palette; 16 bits/pixels
 * with or without BITFIELDS; 24 bits/pixels; compressed BI_RGB and BI_BITFIELDS.
 * The generated image will be:
 * 	* Binary in case the input file has 1 bit/pixel with black and white palette.
 * 	* Grayscale in case the input file has 8 bits/pixel with a complete grayscale
 * 	palette (equal RGB channels for all the palette items).
 * 	* RGB565 in case the input file has 16 bits/pixel (RGB555 or RGB565).
 * 	* RGB888 in case the input file has 24 bits/pixel.
 * - PPM: the generated image will be RGB888.
 * - PGM: the generated image will be Grayscale.
 * - JPEG: the generated image will be Grayscale or RGB565, depending on the actual image content.
 * Depending on the configuration file (stm32ipl_conf.h) the SW or the HW JPEG decoder will be used.
 * @param img		Image: if it is not valid, an error is returned; the given img->data is considered null.
 * The pixel data buffer is allocated internally and must be released with STM32Ipl_ReleaseData() by the caller.
 * @param filename	Name of the input file.
 * @return			stm32ipl_err_Ok on success, errors otherwise.
 */
stm32ipl_err_t STM32Ipl_ReadImage(image_t *img, const char *filename)
{
	FIL fp;
	uint32_t bytesRead = 0;
	uint8_t magic[2];
	stm32ipl_err_t res;

	const uint8_t bmp[2] = { 0x42, 0x4D }; /* BM */
	const uint8_t p2[2] = { 0x50, 0x32 }; /* P2 */
	const uint8_t p3[2] = { 0x50, 0x33 }; /* P3 */
	const uint8_t p5[2] = { 0x50, 0x35 }; /* P5 */
	const uint8_t p6[2] = { 0x50, 0x36 }; /* P6 */
#ifdef STM32IPL_ENABLE_JPEG
	const uint8_t jpg[2] = { 0xFF, 0xD8 }; /* FFD8 */
#endif /* STM32IPL_ENABLE_JPEG */

	if (!img || !filename)
		return stm32ipl_err_InvalidParameter;

	if (f_open(&fp, (const TCHAR*)filename, FA_OPEN_EXISTING | FA_READ) != FR_OK)
		return stm32ipl_err_OpeningFile;

	if ((f_read(&fp, magic, 2, (UINT*)&bytesRead) != FR_OK) || bytesRead != 2) {
		f_close(&fp);
		return stm32ipl_err_ReadingFile;
	}

	if (memcmp(bmp, magic, 2) == 0)
		res = readBmp(img, &fp);
	else
		if ((memcmp(p2, magic, 1) == 0)
				&& ((memcmp(p2, magic, 2) == 0) || (memcmp(p3, magic, 2) == 0) || (memcmp(p5, magic, 2) == 0)
						|| (memcmp(p6, magic, 2) == 0)))
			res = readPnm(img, &fp);
		else
#ifdef STM32IPL_ENABLE_JPEG
			if (memcmp(jpg, magic, 2) == 0)
				res = readJpg(img, &fp);
			else
#endif /* STM32IPL_ENABLE_JPEG */
				res = stm32ipl_err_UnsupportedFormat;

	f_close(&fp);

	return res;
}

/* Writes the BMP header to the file.
 * fp			Pointer to the input file structure.
 * width		Width of the image.
 * height		Height of the image.
 * dataOffset	Offset, in bytes, from the beginning of the file to the image pixels.
 * lineSize		Size of a bitmap line (in bytes).
 * bitsPP		Number of bits per pixel.
 * compression	The type of compression used (0 or BI_BITFIELDS).
 * paletteColorUsed	The number of palette items used.
 * return stm32ipl_err_Ok on success, errors otherwise.
 */
static stm32ipl_err_t writeBmpHeader(FIL *fp, uint32_t width, uint32_t height, uint32_t dataOffset, uint32_t lineSize,
		uint32_t bitsPP, uint32_t compression, uint32_t paletteColorUsed)
{
	FRESULT res;
	uint8_t header[54];
	uint32_t fileSize;
	uint32_t imageSize;
	UINT bytesWritten;

	memset(&header, 0, 54);

	imageSize = lineSize * height;
	fileSize = dataOffset + imageSize;

	/* Write header. */

	/* Signature. */
	header[0] = 'B';
	header[1] = 'M';

	/* File size. */
	header[2] = (uint8_t)((fileSize & 0XFF));
	header[3] = (uint8_t)((fileSize >> 8) & 0XFF);
	header[4] = (uint8_t)((fileSize >> 16) & 0xFF);
	header[5] = (uint8_t)((fileSize >> 24) & 0xFF);

	/* Data offset. */
	header[10] = (uint8_t)((dataOffset & 0XFF));
	header[11] = (uint8_t)((dataOffset >> 8) & 0XFF);
	header[12] = (uint8_t)((dataOffset >> 16) & 0xFF);
	header[13] = (uint8_t)((dataOffset >> 24) & 0xFF);

	/* biSize (version 3). */
	header[14] = 40;

	/* biWidth. */
	header[18] = (uint8_t)((width & 0XFF));
	header[19] = (uint8_t)((width >> 8) & 0xFF);
	header[20] = (uint8_t)((width >> 16) & 0xFF);
	header[21] = (uint8_t)((width >> 24) & 0xFF);

	/* biHeight. */
	header[22] = (uint8_t)((height & 0XFF));
	header[23] = (uint8_t)((height >> 8) & 0xFF);
	header[24] = (uint8_t)((height >> 16) & 0xFF);
	header[25] = (uint8_t)((height >> 24) & 0xFF);

	/* biPlanes. */
	header[26] = 1;

	/* biBitCount. */
	header[28] = (uint8_t)((bitsPP & 0XFF));
	header[29] = (uint8_t)((bitsPP >> 8) & 0xFF);

	/* biCompression. */
	header[30] = (uint8_t)compression;

	/* biSizeImage. */
	header[34] = (uint8_t)((imageSize & 0XFF));
	header[35] = (uint8_t)((imageSize >> 8) & 0xFF);
	header[36] = (uint8_t)((imageSize >> 16) & 0xFF);
	header[37] = (uint8_t)((imageSize >> 24) & 0xFF);

	/* biXPelsPerMeter. */
	header[38] = (uint8_t)((2835 & 0XFF));
	header[39] = (uint8_t)((2835 >> 8) & 0xFF);
	header[40] = (uint8_t)((2835 >> 16) & 0xFF);
	header[41] = (uint8_t)((2835 >> 24) & 0xFF);

	/* biYPelsPerMeter. */
	header[42] = (uint8_t)((2835 & 0XFF));
	header[43] = (uint8_t)((2835 >> 8) & 0xFF);
	header[44] = (uint8_t)((2835 >> 16) & 0xFF);
	header[45] = (uint8_t)((2835 >> 24) & 0xFF);

	/* biClrUsed. */
	header[46] = (uint8_t)((paletteColorUsed & 0XFF));
	header[47] = (uint8_t)((paletteColorUsed >> 8) & 0xFF);
	header[48] = (uint8_t)((paletteColorUsed >> 16) & 0xFF);
	header[49] = (uint8_t)((paletteColorUsed >> 24) & 0xFF);

	/* biClrImportant. */
	//header[50] = 0;
	/* Write header */
	res = f_write(fp, header, 14, &bytesWritten);
	if (res != FR_OK || bytesWritten != 14)
		return stm32ipl_err_WritingFile;

	res = f_write(fp, header + 14, 40, &bytesWritten);
	if (res != FR_OK || bytesWritten != 40)
		return stm32ipl_err_WritingFile;

	return stm32ipl_err_Ok;
}

/* Reverse the input bits.
 * val 		Input value to be reversed.
 * return	Reversed input.
 */
static uint8_t reverse8(uint8_t val)
{
	int size = sizeof(val) * CHAR_BIT - 1;
	uint8_t rev = val;

	for (val >>= 1; val; val >>= 1) {
		rev <<= 1;
		rev |= val & 1;
		size--;
	}
	rev <<= size;

	return rev;
}

/*
 * Write the given image to BMP file; the supported source image formats are:
 * Binary, Grayscale, RGB565, RGB888:
 * - Binary image is saved as 1 bit B&W BMP.
 * - Grayscale image is saved as 8 bits grayscale BMP.
 * - RGB565 image is saved as 16 bits BMP with BITFIELDS.
 * - RGB888 image is saved as 24 bits BMP.
 * img		Image to be saved.
 * filename	Name of the output file.
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
static stm32ipl_err_t saveBmp(const image_t *img, const char *filename)
{
	FIL fp;
	FRESULT res;
	uint32_t width;
	uint32_t height;
	uint32_t lineSize;
	uint32_t padding;
	UINT bytesWritten;

	width = img->w;
	height = img->h;

	if (f_open(&fp, (const TCHAR*)filename, FA_WRITE | FA_CREATE_ALWAYS) != FR_OK)
		return stm32ipl_err_OpeningFile;

	switch (img->bpp) {
		case IMAGE_BPP_BINARY: {
			uint32_t palette = 0;
			lineSize = (((width) + 31) / 32) * 4;

			/* Header. */
			if (stm32ipl_err_Ok != writeBmpHeader(&fp, width, height, 54 + 8, lineSize, 1, 0, 2)) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}

			/* Palette. */
			res = f_write(&fp, &palette, sizeof(palette), &bytesWritten);
			if (res != FR_OK || bytesWritten != sizeof(palette)) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}
			palette = 0xFFFFFF;
			res = f_write(&fp, &palette, sizeof(palette), &bytesWritten);
			if (res != FR_OK || bytesWritten != sizeof(palette)) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}

			for (int32_t i = height - 1; i >= 0; i--) {
				uint32_t offset = i * lineSize;
				uint8_t *srcData = img->data + offset;

				/* Image data. */
				for (uint32_t j = 0; j < lineSize; j++) {
					uint8_t dstData = reverse8(*(srcData + j));

					res = f_write(&fp, &dstData, 1, &bytesWritten);
					if (res != FR_OK || bytesWritten != 1) {
						f_close(&fp);
						return stm32ipl_err_WritingFile;
					}
				}
			}
			break;
		}

		case IMAGE_BPP_GRAYSCALE: {
			lineSize = (((width * 8) + 31) / 32) * 4;
			padding = lineSize - width;

			/* Header. */
			if (stm32ipl_err_Ok != writeBmpHeader(&fp, width, height, 54 + 1024, lineSize, 8, 0, 256)) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}

			/* Palette. */
			for (uint32_t i = 0; i < 256; i++) {
				uint32_t value = (i << 16) | (i << 8) | i;
				res = f_write(&fp, &value, sizeof(value), &bytesWritten);
				if (res != FR_OK || bytesWritten != 4) {
					f_close(&fp);
					return stm32ipl_err_WritingFile;
				}
			}

			for (int32_t i = height - 1; i >= 0; i--) {
				uint32_t offset = i * width;

				/* Image data. */
				res = f_write(&fp, img->data + offset, width, &bytesWritten);
				if (res != FR_OK || bytesWritten != width) {
					f_close(&fp);
					return stm32ipl_err_WritingFile;
				}

				/* Padding. */
				for (uint32_t j = 0; j < padding; j++) {
					if (1 != f_putc(0, &fp)) {
						f_close(&fp);
						return stm32ipl_err_WritingFile;
					}
				}
			}
			break;
		}

		case IMAGE_BPP_RGB565: {
			uint32_t mask;
			uint32_t dataLen = width << 1;
			lineSize = (((width * 16) + 31) / 32) * 4;
			padding = lineSize - dataLen;

			/* Header. */
			if (stm32ipl_err_Ok != writeBmpHeader(&fp, width, height, 14 + 40 + 12, lineSize, 16, BI_BITFIELDS, 0)) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}

			/* Bit masks. */
			mask = 0xF800;
			res = f_write(&fp, &mask, 4, &bytesWritten);
			if (res != FR_OK || bytesWritten != 4) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}
			mask = 0x7E0;
			res = f_write(&fp, &mask, 4, &bytesWritten);
			if (res != FR_OK || bytesWritten != 4) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}
			mask = 0x1F;
			res = f_write(&fp, &mask, 4, &bytesWritten);
			if (res != FR_OK || bytesWritten != 4) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}

			for (int32_t i = height - 1; i >= 0; i--) {
				uint32_t offset = i * width;

				/* Image data. */
				res = f_write(&fp, ((uint16_t*)img->data) + offset, dataLen, &bytesWritten);
				if (res != FR_OK || bytesWritten != dataLen) {
					f_close(&fp);
					return stm32ipl_err_WritingFile;
				}

				/* Padding. */
				for (uint32_t j = 0; j < padding; j++) {
					if (1 != f_putc(0, &fp)) {
						f_close(&fp);
						return stm32ipl_err_WritingFile;
					}
				}
			}

			break;
		}

		case IMAGE_BPP_RGB888: {
			uint32_t dataLen = width * 3;
			lineSize = (((width * 24) + 31) / 32) * 4;
			padding = lineSize - dataLen;

			/* Header. */
			if (stm32ipl_err_Ok != writeBmpHeader(&fp, width, height, 14 + 40, lineSize, 24, 0, 0)) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}

			for (int32_t i = height - 1; i >= 0; i--) {
				uint8_t *data = img->data + i * dataLen;

				/* Image data. */
				res = f_write(&fp, data, dataLen, &bytesWritten);
				if (res != FR_OK || bytesWritten != dataLen) {
					f_close(&fp);
					return stm32ipl_err_WritingFile;
				}

				/* Padding. */
				for (uint32_t j = 0; j < padding; j++) {
					if (1 != f_putc(0, &fp)) {
						f_close(&fp);
						return stm32ipl_err_WritingFile;
					}
				}
			}

			break;
		}

		default: {
			f_close(&fp);
			return stm32ipl_err_InvalidParameter;
		}
	};

	f_close(&fp);

	return stm32ipl_err_Ok;
}

/*
 * Writes the given image to raw PNM file (PPM or PGM); the supported source image formats are:
 * Grayscale, RGB565, RGB888:
 * - Binary is not supported.
 * - Grayscale is saved as 8 bits PGM.
 * - RGB565 is saved as 24 bits PPM.
 * - RGB888 is saved as 24 bits PPM.
 * img		Image to be saved.
 * filename	Name of the output file.
 * format	Format of the PNM file (6 if the input image is RGB565 or RGB888, 5 if it's Grayscale).
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
static stm32ipl_err_t savePnm(const image_t *img, const char *filename, uint8_t format)
{
	FIL fp;
	FRESULT res;
	uint32_t size;
	int32_t width;
	int32_t height;
	char text[64];
	UINT bytesWritten;
	uint32_t offset;

	width = img->w;
	height = img->h;

	/* Write header. */
	size = snprintf(text, sizeof(text), "P%d\n# Created by STM32IPL\n%ld %ld\n255\n", format, width, height);

	if (f_open(&fp, (const TCHAR*)filename, FA_WRITE | FA_CREATE_ALWAYS) != FR_OK)
		return stm32ipl_err_OpeningFile;

	res = f_write(&fp, text, size, &bytesWritten);
	if (res != FR_OK || bytesWritten != size) {
		f_close(&fp);
		return stm32ipl_err_WritingFile;
	}

	switch (img->bpp) {
		/* TODO: case IMAGE_BPP_BINARY */

		case IMAGE_BPP_GRAYSCALE: {
			size = width * height;

			res = f_write(&fp, img->data, size, &bytesWritten);
			if (res != FR_OK || bytesWritten != size) {
				f_close(&fp);
				return stm32ipl_err_WritingFile;
			}
			break;
		}

		case IMAGE_BPP_RGB565: {
			for (uint32_t i = 0; i < height; i++) {
				offset = i * width;

				for (uint32_t j = 0; j < width; j++) {
					rgb888_t rgb888;
					uint16_t rgb565 = *(((uint16_t*)img->data) + offset + j);

					/* R and B must be swapped. */
					rgb888.r = COLOR_RGB565_TO_B8(rgb565);
					rgb888.g = COLOR_RGB565_TO_G8(rgb565);
					rgb888.b = COLOR_RGB565_TO_R8(rgb565);

					res = f_write(&fp, &rgb888, 3, &bytesWritten);
					if (res != FR_OK || bytesWritten != 3) {
						f_close(&fp);
						return stm32ipl_err_WritingFile;
					}
				}
			}
			break;
		}

		case IMAGE_BPP_RGB888: {
			uint8_t *data = img->data;
			size = width * height;

			for (uint32_t i = 0; i < size; i++) {
				rgb888_t rgb888;

				/* R and B must be swapped. */
				rgb888.r = *data++;
				rgb888.g = *data++;
				rgb888.b = *data++;

				res = f_write(&fp, &rgb888, 3, &bytesWritten);
				if (res != FR_OK || bytesWritten != 3) {
					f_close(&fp);
					return stm32ipl_err_WritingFile;
				}
			}

			break;
		}

		default: {
			f_close(&fp);
			return stm32ipl_err_UnsupportedFormat;
		}
	}

	f_close(&fp);

	return stm32ipl_err_Ok;
}

/* Checks if the format of the input image is compatible with the PPM file extension.
 * In case of success, it writes the given image to raw PPM;
 * the supported source image formats are RGB565, RGB888:
 * - Binary is not supported.
 * - Grayscale is not compatible with PGM.
 * - RGB565 is saved as 24 bits PPM.
 * - RGB888 is saved as 24 bits PPM.
 * img		Image to be saved.
 * filename	Name of the output file.
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
static stm32ipl_err_t savePpm(const image_t *img, const char *filename)
{
	uint8_t format;

	switch (img->bpp) {
		case IMAGE_BPP_BINARY:
		case IMAGE_BPP_GRAYSCALE:
			return stm32ipl_err_UnsupportedFormat;

		case IMAGE_BPP_RGB565:
		case IMAGE_BPP_RGB888: {
			format = 6;
			break;
		}

		default:
			return stm32ipl_err_UnsupportedFormat;
	}

	return savePnm(img, filename, format);
}

/* Checks if the format of the input image is compatible with the PGM file extension.
 * In case of success, it writes the given image to raw PGM;
 * the supported source image format is Grayscale:
 * - Binary is not supported.
 * - Grayscale is saved as 8 bits PGM.
 * - RGB565 is not compatible with PGM.
 * - RGB888 is not compatible with PGM.
 * img		Image to be saved.
 * filename	Name of the output file.
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
static stm32ipl_err_t savePgm(const image_t *img, const char *filename)
{
	uint8_t format;

	switch (img->bpp) {
		case IMAGE_BPP_BINARY:
			return stm32ipl_err_UnsupportedFormat;

		case IMAGE_BPP_GRAYSCALE:
			format = 5;
			break;

		case IMAGE_BPP_RGB565:
		case IMAGE_BPP_RGB888: {
			return stm32ipl_err_UnsupportedFormat;
		}

		default:
			return stm32ipl_err_UnsupportedFormat;
	}

	return savePnm(img, filename, format);
}

#ifdef STM32IPL_ENABLE_JPEG
/* Writes the given image to JPEG file; the supported source image formats are:
 * Grayscale, RGB565 and RGB888:
 * - Binary is not supported.
 * - Grayscale is saved as grayscale JPEG.
 * - RGB565 is saved as full-color JPEG.
 * - RGB888 is saved as full-color JPEG.
 * Depending on the configuration file (stm32ipl_conf.h) the SW or the HW
 * JPEG encoder will be used.
 * img		Image to be saved.
 * filename	Name of the output file.
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
static stm32ipl_err_t saveJpg(const image_t *img, const char *filename)
{
	if (img->bpp == IMAGE_BPP_BINARY)
		return stm32ipl_err_UnsupportedFormat;

#ifdef STM32IPL_ENABLE_HW_JPEG_CODEC
	stm32ipl_err_t res;
	/* If input image has RGB888 format, due to the jpeg_util implementation,
	 * a formal conversion to RGB565 is needed. */
	if (img->bpp == IMAGE_BPP_RGB888) {
		image_t tmpImg;
		if (STM32Ipl_AllocData(&tmpImg, img->w, img->h, IMAGE_BPP_RGB565))
			return stm32ipl_err_OutOfMemory;

		if (STM32Ipl_Convert(img, &tmpImg))
			return stm32ipl_err_UnsupportedFormat;

		res = saveJPEGHW(&tmpImg, filename);

		STM32Ipl_ReleaseData(&tmpImg);

		return res;
	} else
		return saveJPEGHW(img, filename);
#else
	return saveJPEGSW(img, filename);
#endif
}
#endif /* STM32IPL_ENABLE_JPEG */

/**
 * @brief Writes the given image to file; the target file format is determined
 * by the filename extension; the supported output file formats are: BMP, PPM, PGM, JPG.
 * The supported source image formats are: Binary, Grayscale, RGB565 and RGB888:
 * - Binary can be saved to BMP only
 * - Grayscale can be saved to BMP, raw PGM or JPEG
 * - RGB565 can be saved to BMP, PPM or JPEG
 * - RGB888 can be saved to BMP, PPM or JPEG
 * Depending on the configuration file (stm32ipl_conf.h) the SW or the HW
 * JPEG encoder will be used.
 * img		Image to be saved; if it is not valid, an error is returned.
 * filename	Name of the output file; if it is not valid, an error is returned.
 * return	stm32ipl_err_Ok on success, error otherwise.
 */
stm32ipl_err_t STM32Ipl_WriteImage(const image_t *img, const char *filename)
{
	if (!img || !img->data || !filename)
		return stm32ipl_err_InvalidParameter;

	if (img->bpp != IMAGE_BPP_BINARY && img->bpp != IMAGE_BPP_GRAYSCALE && img->bpp != IMAGE_BPP_RGB565
			&& img->bpp != IMAGE_BPP_RGB888)
		return stm32ipl_err_UnsupportedFormat;

	switch (getImageFileFormat(filename)) {
		case iplFileFormatBMP:
			return saveBmp(img, filename);

		case iplFileFormatPPM:
			return savePpm(img, filename);

		case iplFileFormatPGM:
			return savePgm(img, filename);

#ifdef STM32IPL_ENABLE_JPEG
		case iplFileFormatJPG:
			return saveJpg(img, filename);
#endif /* STM32IPL_ENABLE_JPEG */

		default:
			break;
	}

	return stm32ipl_err_UnsupportedFormat;
}

#ifdef __cplusplus
}
#endif

#else  /* STM32IPL_ENABLE_IMAGE_IO */

#ifdef __cplusplus
extern "C" {
#endif

stm32ipl_err_t STM32Ipl_ReadImage(image_t *img, const char *filename)
{
	/* Prevent unused argument(s) compilation warning. */
	STM32IPL_UNUSED(img);
	STM32IPL_UNUSED(filename);

	/* Void implementation. */
	return stm32ipl_err_NotImplemented;
}

stm32ipl_err_t STM32Ipl_WriteImage(const image_t *img, const char *filename)
{
	/* Prevent unused argument(s) compilation warning. */
	STM32IPL_UNUSED(img);
	STM32IPL_UNUSED(filename);

	/* Void implementation. */
	return stm32ipl_err_NotImplemented;
}

#ifdef __cplusplus
}
#endif

#endif /* STM32IPL_ENABLE_IMAGE_IO */
