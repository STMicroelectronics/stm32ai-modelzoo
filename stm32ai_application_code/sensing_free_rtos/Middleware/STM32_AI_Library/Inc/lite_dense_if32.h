#ifndef _LITE_DENSE_IFR32_H
#define _LITE_DENSE_IFR32_H
#pragma once

#include "ai_lite_interface.h"

/*!
 * @brief Forward function for a dense layer with signed float input,
 * signed float output, and float weights.
 * @ingroup lite_dense_if32
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param bias The pointer to bias (NULL if not available).
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_out The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_if32of32wf32(
  ai_float* output, const ai_float* input,
  const ai_float* weights, const ai_float* bias,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out);


#endif    /*_LITE_DENSE_IFR32_H*/
