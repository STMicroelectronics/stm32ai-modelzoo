#ifndef LITE_NL_GENERIC_INTEGER_H
#define LITE_NL_GENERIC_INTEGER_H
#pragma once

#include "ai_lite_interface.h"

/**
 * @brief forward lite function for a s8 softmax non-linearity where the softmax is applied per channel.
 * @ingroup lite_nl_generic_integer
 * @param output The pointer to output buffer (s8).
 * @param input The pointer to input buffer (s8).
 * @param in_size. The size of the input (including channels).
 * @param ch_size The nsize of each channel.
 * @param in_ch_step    The step between consecutive elements (inputs)
 * @param out_ch_step   The step between consecutive elements (outputs)
 * @param mult
 * @param shift
 * @param min_diff
 */
LITE_API_ENTRY
void forward_lite_nl_softmax_is8os8(
  ai_i8* out_ptr, const ai_i8* in_ptr,
  const ai_size in_size, const ai_size ch_size,
  const ai_i32 in_ch_step, const ai_i32 out_ch_step,
  const ai_i32 mult, const ai_i32 shift, const ai_i32 min_diff,
  ai_i32* scratch);


/**
 * @brief forward lite function for a u8 softmax non-linearity where the softmax is applied per channel.
 * @ingroup lite_nl_generic_integer
 * @param output The pointer to output buffer (s8).
 * @param input The pointer to input buffer (s8).
 * @param in_size. The size of the input (including channels).
 * @param ch_size The nsize of each channel.
 * @param in_ch_step    The step between consecutive elements (inputs)
 * @param out_ch_step   The step between consecutive elements (outputs)
 * @param mult
 * @param shift
 * @param min_diff
 */
LITE_API_ENTRY
void forward_lite_nl_softmax_iu8ou8(
  ai_u8* out_ptr, const ai_u8* in_ptr,
  const ai_size in_size, const ai_size ch_size,
  const ai_i32 in_ch_step, const ai_i32 out_ch_step,
  const ai_i32 mult, const ai_i32 shift, const ai_i32 min_diff,
  ai_i32* scratch);

#endif    /* LITE_NL_GENERIC_INTEGER_H */
