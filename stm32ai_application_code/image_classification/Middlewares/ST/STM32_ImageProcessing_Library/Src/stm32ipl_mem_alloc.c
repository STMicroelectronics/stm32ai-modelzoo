/**
 ******************************************************************************
 * @file   stm32ipl_mem_alloc.c
 * @author SRA AI Application Team
 * @brief  STM32 Image Processing Library - memory allocation module
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

#ifdef STM32IPL

#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "stm32ipl_mem_alloc.h"
#include "umm_malloc.h"

#ifdef __cplusplus
extern "C" {
#endif

///@cond
#define FB_ALLOC_MAX_ENTRY		64	/* Max number of entries managed with fb_alloc. */

static uint32_t g_fb_alloc_stack[FB_ALLOC_MAX_ENTRY];
static uint32_t g_fb_alloc_inext = 0;
static uint32_t g_fb_alloc_imark = 0;

/* Prototypes. */
void* STM32Ipl_Alloc(uint32_t size);
void* STM32Ipl_Alloc0(uint32_t size);
void STM32Ipl_Free(void *mem);
void* STM32Ipl_Realloc(void *mem, uint32_t size);
__attribute__((weak)) void STM32Ipl_FaultHandler(const char *error);
///@endcond

/*
 * Exported functions.
 */

/**
 * @brief Allocates a memory buffer of size bytes from the bunch of memory reserved by STM32Ipl_InitLib().
 * Such buffer must be released with STM32Ipl_Free().
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @return		The allocated memory buffer, null in case of errors.
 */
void* STM32Ipl_Alloc(uint32_t size)
{
	return xalloc(size);
}

/**
 * @brief Same as STM32Ipl_Alloc(), but the allocated buffer is set to zero.
 * Such buffer must be released with STM32Ipl_Free().
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @return		The allocated memory buffer, null in case of errors.
 */
void* STM32Ipl_Alloc0(uint32_t size)
{
	return xalloc0(size);
}

/**
 * @brief Frees a memory buffer previously allocated with STM32Ipl_Alloc() or STM32Ipl_Alloc0().
 * @param mem	Pointer to the the memory buffer to be released.
 * @return		void
 */
void STM32Ipl_Free(void *mem)
{
	xfree(mem);
}

/**
 * @brief Re-sizes an existing memory buffer to the given of size.
 * Such buffer must be released with STM32Ipl_Free().
 * @param mem	Pointer to the the memory buffer.
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @return		The allocated memory buffer, null in case of errors.
 */
void* STM32Ipl_Realloc(void *mem, uint32_t size)
{
	return xrealloc(mem, size);
}

///@cond
__attribute__((weak)) void STM32Ipl_FaultHandler(const char *error)
{
	while (1)
		;
}

/* xalloc and fb_alloc are used by Openmv functions.
 * STM32IPL re-implements such functions by wrapping UMM functions.
 */

/*
 * @brief Trap function called when the UMM allocator fails.
 * @return		void.
 */
void umm_alloc_fail(void)
{
	STM32Ipl_FaultHandler("umm_alloc() failure");
}

/*
 * @brief Allocates a memory buffer of size bytes from the bunch of memory reserved by STM32Ipl_InitLib().
 * Such buffer must be released with xfree().
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @return		The allocated memory buffer, null in case of errors.
 */
void* xalloc(uint32_t size)
{
	return umm_malloc(size);
}

/* Not used.
 void *xalloc_try_alloc(uint32_t size)
 {
 return umm_malloc(size);
 }
 */

/*
 * @brief Same as xalloc(), but the allocated buffer is set to zero.
 * Such buffer must be released with xfree().
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @return		The allocated memory buffer, null in case of errors.
 */
void* xalloc0(uint32_t size)
{
	void *mem = umm_malloc(size);

	if (mem == NULL)
		return NULL;

	memset(mem, 0, size);

	return mem;
}

/*
 * @brief Frees a memory buffer previously allocated with xalloc() or xalloc0().
 * @param mem	Pointer to the the memory buffer to be released.
 * @return		void
 */
void xfree(void *mem)
{
	umm_free(mem);
}

/*
 * @brief Re-sizes an existing memory buffer to the given of size.
 * Such buffer must be released with xfree().
 * @param mem	Pointer to the the memory buffer.
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @return		The allocated memory buffer, null in case of errors.
 */
void* xrealloc(void *mem, uint32_t size)
{
	return umm_realloc(mem, size);
}

/*
 * @brief Initialized the fb mechanism, that is a stack based memory allocator that, under the
 * hood, uses heap memory .
 * @return		void.
 */
void fb_init(void)
{
	memset(g_fb_alloc_stack, 0, sizeof(uint32_t) * FB_ALLOC_MAX_ENTRY);
	g_fb_alloc_inext = 0;
	g_fb_alloc_imark = 0;
}

/*
 * @brief Can be called by the user in case of memory allocation errors.
 * @return		void.
 */
void fb_alloc_fail(void)
{
	STM32Ipl_FaultHandler("fb_alloc() failure");
}

/*
 * @brief Returns the size (bytes) of the biggest memory block available from the fb stack.
 * @return		void.
 */
uint32_t fb_avail(void)
{
	return umm_max_free_block_size();
}

/*
 * @brief Allocates a memory buffer of size bytes from the fb stack.
 * Such buffer must be released with fb_free().
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @param hints	Argument not used.
 * @return		The allocated memory buffer, null in case of errors.
 */
void* fb_alloc(uint32_t size, int hints)
{
	void *p = NULL;

	if (g_fb_alloc_inext == FB_ALLOC_MAX_ENTRY) {
		fb_alloc_fail();
		return NULL;
	}

	p = umm_malloc(size);
	if (p)
		g_fb_alloc_stack[g_fb_alloc_inext++] = (uint32_t)p;
	else
		fb_alloc_fail();

	return p;
}

/*
 * @brief Same as fb_alloc(), but the allocated buffer is set to zero.
 * Such buffer must be released with fb_free().
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @param hints	Argument not used.
 * @return		Allocated memory buffer, null in case of errors.
 */
void* fb_alloc0(uint32_t size, int hints)
{
	void *p = NULL;

	p = fb_alloc(size, hints);
	if (p)
		memset(p, 0, size);
	else
		fb_alloc_fail();

	return p;
}

/*
 * @brief Allocates the biggest memory buffer from the fb stack.
 * Such buffer must be released with fb_free().
 * @param size	Used to return the size of the allocated memory buffer (bytes).
 * @param hints	Argument not used.
 * @return		The allocated memory buffer, null in case of errors.
 */
void* fb_alloc_all(uint32_t *size, int hints)
{
	uint32_t max_size = fb_avail();
	void *p = NULL;

	p = fb_alloc(max_size, hints);
	*size = (p == NULL) ? 0 : max_size;

	return p;
}

/*
 * @brief Same as fb_alloc_all(), but the allocated buffer is set to zero.
 * Such buffer must be released with fb_free().
 * @param size	Size of the memory buffer to be allocated (bytes).
 * @param hints	Argument not used.
 * @return		Allocated memory buffer, null in case of errors.
 */
void* fb_alloc0_all(uint32_t *size, int hints)
{
	uint32_t max_size = fb_avail();
	void *p = NULL;

	p = fb_alloc0(max_size, hints);
	*size = (p == NULL) ? 0 : max_size;

	return p;
}

/*
 * @brief Frees the last memory buffer allocated with fb_alloc(), fb_alloc_all() or fb_alloc0_all().
 * @return		void
 */
void fb_free(void)
{
	if (g_fb_alloc_inext == 0)
		return;

	g_fb_alloc_inext--;
	umm_free((void*)g_fb_alloc_stack[g_fb_alloc_inext]);
	g_fb_alloc_stack[g_fb_alloc_inext] = 0;
}

/*
 * @brief Frees all the memory buffers allocated with fb_alloc(), fb_alloc_all() or fb_alloc0_all().
 * @return		void
 */
void fb_free_all(void)
{
	uint32_t e = g_fb_alloc_inext;
	for (int i = 0; i < e; i++)
		fb_free();
}

/*
 * @brief Marks the current stack pointer.
 * @return		void.
 */
void fb_alloc_mark(void)
{
	g_fb_alloc_imark = g_fb_alloc_inext;
}

/*
 * @brief Frees all the memory buffers allocated on the stack after the last call to fb_alloc_mark().
 * @return		void.
 */
void fb_alloc_free_till_mark(void)
{
	int32_t e = g_fb_alloc_inext - g_fb_alloc_imark;

	for (int i = 0; i < e; i++)
		fb_free();
}
///@endcond

#ifdef __cplusplus
}
#endif

#endif // STM32IPL
