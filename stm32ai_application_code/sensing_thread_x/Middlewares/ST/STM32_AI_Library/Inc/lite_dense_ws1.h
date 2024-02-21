#ifndef LITE_DENSE_WS1_H
#define LITE_DENSE_WS1_H
#pragma once

#include "ai_lite_interface.h"


/*!
 * @brief Forward function for a dense layer with signed f32 input,
 * f32 output, binary weights and binary bias.
 * @ingroup lite_dense_ws1
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param bias The pointer to bias.
 * @param scratch The pointer to the scratch buffer (unused).
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_out The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_if32os1ws1(
  ai_pbits *output, const ai_float *input, const ai_pbits *weights,
  const ai_float *bias, ai_float *scratch,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out);


/*!
 * @brief Forward function for a dense layer with signed f32 input,
 * f32 output, binary weights.
 * The BN is fused, i.e., the layer requires weights, scale, and offset, where
 * weights are those of the dense layer, scale is that of the BN, and the offset
 * corresponds to dense bias * bn scale + bn offset. If the parameters do not
 * agree with such convention, the behavior is undefined.
 * @ingroup lite_dense_ws1
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param scale The pointer to scale.
 * @param offset The pointer to offset.
 * @param scratch The pointer to the scratch buffer (unused).
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_out The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_if32os1ws1_bn(
  ai_pbits *output, const ai_float *input, const ai_pbits *weights,
  const ai_float *scale, const ai_float *offset, ai_float *scratch,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out);


/*!
 * @brief Forward function for a dense layer with signed f32 input,
 * f32 output, and binary weights.
 * @ingroup lite_dense_ws1
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param bias The pointer to binary bias.
 * @param scratch The pointer to the scratch buffer (unused).
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_out The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_if32of32ws1(
  ai_float* output, const ai_float* input,
  const ai_pbits* weights,
  const ai_pbits* bias, ai_float* scratch,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out);

/*!
 * @brief Forward function for a dense layer with signed f32 input,
 * f32 output, and binary weights.
 * The BN is fused, i.e., the layer requires weights, scale, and offset, where
 * weights are those of the dense layer, scale is that of the BN, and the offset
 * corresponds to dense bias * bn scale + bn offset. If the parameters do not
 * agree with such convention, the behavior is undefined.
 * @ingroup lite_dense_ws1
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param scale The pointer to scale.
 * @param offset The pointer to offset.
 * @param scratch The pointer to the scratch buffer (unused).
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_out The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_if32of32ws1_bn(
  ai_float *output, const ai_float *input, const ai_pbits *weights,
  const ai_float *scale, const ai_float *offset, ai_float *scratch,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out);

#endif    /* LITE_DENSE_IS1WS1_H */
