#ifndef LITE_NL_GENERIC_FLOAT_H
#define LITE_NL_GENERIC_FLOAT_H
#pragma once

#include "ai_lite_interface.h"


#define LITE_NL_ENTRY(nl_id_, nl_name_, nl_op_, nl_op_args_) \
/** \
 * @brief lite function for a templated non-linearity nl_op_. \
 * @ingroup lite_nl_generic_float \
 * @param out_ptr The pointer to output buffer. \
 * @param in_ptr The pointer to input buffer. \
 * @param in_size. The size of the input. \
 * @param params opaque handler to optional NL params (not used). \
 */ \
LITE_API_ENTRY \
void lite_nl_ ## nl_name_ ## _if32of32( \
  ai_float* out_ptr, const ai_float* in_ptr, const ai_size in_size, const ai_handle params);

#include "lite_nl_list.h"

/**
 * @brief lite function for a float softmax non-linearity where the softmax is applied per channel.
 * @ingroup lite_nl_generic_float
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param in_size. The size of the input.
 * @param channel_size The nsize of each channel.
 * @param in_channel_step
 * @param out_channel_step
 */
LITE_API_ENTRY
void lite_nl_softmax_if32of32(
  ai_float* out_ptr, const ai_float* in_ptr, const ai_size in_size, const ai_size ch_size,
  const ai_i32 in_ch_step, const ai_i32 out_ch_step);


/**
 * @brief lite function for a float softmax zero channel non-linearity where the softmax is applied per channel.
 * @ingroup lite_nl_generic_float
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param in_size. The size of the input.
 * @param channel_size The nsize of each channel.
 * @param in_channel_step
 * @param out_channel_step
 */
LITE_API_ENTRY
void lite_nl_softmax_zero_channel_if32of32(
  ai_float* out_ptr, const ai_float* in_ptr, const ai_size in_size, const ai_size ch_size,
  const ai_i32 in_ch_step, const ai_i32 out_ch_step);


#endif    /* LITE_NL_GENERIC_FLOAT_H */
