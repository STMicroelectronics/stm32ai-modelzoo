/* ----------------------------------------------------------------------------
 * umm_malloc.h - a memory allocator for embedded systems (microcontrollers)
 *
 * See copyright notice in LICENSE.TXT
 * ----------------------------------------------------------------------------
 */

#ifndef UMM_MALLOC_H
#define UMM_MALLOC_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ------------------------------------------------------------------------ */

extern void  umm_init( void *UMM_MALLOC_CFG_HEAP_ADDR, uint32_t UMM_MALLOC_CFG_HEAP_SIZE );
extern void *umm_malloc( size_t size );
extern void *umm_calloc( size_t num, size_t size );
extern void *umm_realloc( void *ptr, size_t size );
extern void  umm_free( void *ptr );

extern void  umm_uninit( void );
extern size_t umm_free_heap_size( void );
extern size_t umm_max_free_block_size( void );

/* ------------------------------------------------------------------------ */

#ifdef __cplusplus
}
#endif

#endif /* UMM_MALLOC_H */
