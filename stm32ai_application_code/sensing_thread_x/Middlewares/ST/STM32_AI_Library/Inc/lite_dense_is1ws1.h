#ifndef _LITE_DENSE_IS1WS1_H
#define _LITE_DENSE_IS1WS1_H
#pragma once

#include "ai_lite_interface.h"

/*!
 * @brief Forward function for a dense layer with signed binary input,
 * signed binary output, and signed binary weights.
 * @ingroup lite_dense_is1ws1
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param bias The pointer to bias (NULL if not available).
 * @param scratch The pointer to the scratch buffer.
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_ouy The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_is1os1ws1(
  ai_pbits *output, const ai_pbits *input, const ai_pbits *weights,
  const ai_pbits *bias, ai_i32 *scratch,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out
);

/*!
 * @brief Forward function for a dense layer with signed binary input,
 * signed binary output, and signed binary weights.
 * The BN is fused, i.e., the layer requires weights, scale, and offset, where
 * weights are those of the dense layer, scale is that of the BN, and the offset
 * corresponds to dense bias * bn scale + bn offset. If the parameters do not
 * agree with such convention, the behavior is undefined.
 * @ingroup lite_dense_is1ws1
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param scale The pointer to scale.
 * @param offset The pointer to offset.
 * @param scratch The pointer to the scratch buffer.
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_ouy The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_is1os1ws1_bn(
  ai_pbits *output, const ai_pbits *input, const ai_pbits *weights,
  const ai_float *scale, const ai_float *offset, ai_i32 *scratch,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out
);

/*!
 * @brief Forward function for a dense layer with signed binary input,
 * signed float output, and signed binary weights.
 * @ingroup lite_dense_is1ws1
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param bias The pointer to bias (NULL if not available).
 * @param scratch The pointer to the scratch buffer (unused).
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_ouy The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_is1of32ws1(
  ai_float *output, const ai_pbits *input, const ai_pbits *weights,
  const ai_pbits *bias, ai_i32 *scratch,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out
);


/*!
 * @brief Forward function for a dense layer with signed binary input,
 * signed float output, and signed binary weights.
 * The BN is fused, i.e., the layer requires weights, scale, and offset, where
 * weights are those of the dense layer, scale is that of the BN, and the offset
 * corresponds to dense bias * bn scale + bn offset. If the parameters do not
 * agree with such convention, the behavior is undefined.
 * @ingroup lite_dense_is1ws1
 * @param output The pointer to output buffer.
 * @param input The pointer to input buffer.
 * @param weights The pointer to weights.
 * @param scale The pointer to scale.
 * @param offset The pointer to offset.
 * @param scratch The pointer to the scratch buffer (unused).
 * @param n_channel_in The number of channels of the input.
 * @param n_channel_ouy The number of channels of the output, i.e.,
 *        the number of dense hidden neurons.
 */
LITE_API_ENTRY
void lite_dense_is1of32ws1_bn(
  ai_float *output, const ai_pbits *input, const ai_pbits *weights,
  const ai_float *scale, const ai_float *offset, ai_i32 *scratch,
  const ai_u32 n_channel_in, const ai_u32 n_channel_out
);

#endif    /*_LITE_DENSE_IS1WS1_H*/
