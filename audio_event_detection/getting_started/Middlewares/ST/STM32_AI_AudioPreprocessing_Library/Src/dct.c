/**
 ******************************************************************************
 * @file    dct.c
 * @author  MCD Application Team
 * @brief   Generation and processing functions of the Discrete Cosine Transform
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; Copyright (c) 2019 STMicroelectronics.
 * All rights reserved.</center></h2>
 *
 * This software component is licensed by ST under Software License Agreement
 * SLA0055, the "License"; You may not use this file except in compliance with
 * the License. You may obtain a copy of the License at:
 *        www.st.com/resource/en/license_agreement/dm00251784.pdf
 *
 ******************************************************************************
 */
#include "dct.h"

#ifndef M_PI
#define M_PI    3.14159265358979323846264338327950288 /*!< pi */
#endif


/**
 * @defgroup groupDCT Discrete Cosine Transform
 * @brief Generation and processing functions of the Discrete Cosine Transform
 *
 * Implementation based on SciPy's scipy.fftpack.dct.
 * - https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.fftpack.dct.html
 * - https://en.wikipedia.org/wiki/Discrete_cosine_transform
 * - https://github.com/ARM-software/ML-KWS-for-MCU/blob/master/Deployment/Source/MFCC/mfcc.cpp
 * - https://github.com/tensorflow/tensorflow/blob/r1.13/tensorflow/python/ops/signal/mfcc_ops.py
 *
 * \par Example
 * \code
 * float32_t pDCTCoefsBuffer[13 * 128];
 * float32_t pOutBuffer[13];
 * DCT_InstanceTypeDef S_DCT;
 *
 * S_DCT.NumFilters    = 13;
 * S_DCT.NumInputs     = 128;
 * S_DCT.Type          = DCT_TYPE_III;
 * S_DCT.RemoveDCTZero = 1;
 * S_DCT.pDCTCoefs     = pDCTCoefsBuffer;
 *
 * if (DCT_Init(&S_DCT) != 0)
 * {
 *   Error_Handler();
 * }
 *
 * DCT(&S_DCT, pInBuffer, pOutBuffer);
 *
 * \endcode
 *
 * \par DCT type-II
 * <pre>
 * y = scipy.fftpack.dct(x, type=2)[:n_filters]
 *              N-1
 * y[k] = 2.0 * sum cos(pi / N * (n + 0.5) * k), 0 <= k < N.
 *              n=0
 * </pre>
 *
 *\par DCT type-II normalized
 * <pre>
 * y = scipy.fftpack.dct(x, type=2, norm='ortho')[:n_filters]
 *             N-1
 *  y[k] = 2 * sum x[n] * cos(pi / N * k * (n + 0.5)), 0 <= k < N.
 *             n=0
 * If norm='ortho', y[k] is multiplied by a scaling factor f:
 *   f = sqrt(1/(4*N)) if k = 0,
 *   f = sqrt(1/(2*N)) otherwise.
 * </pre>
 *
 * \par DCT type-II scaled
 *
 * All bins are scaled to match the DCT operation used in TensorFlow's MFCC.
 * <pre>
 *                         N-1
 *  y[k] = sqrt(1/(2*N)) * sum x[n] * cos(pi / N * k * (n + 0.5)), 0 <= k < N.
 *                         n=0
 * </pre>
 *
 * \par DCT type-III
 * <pre>
 * y = scipy.fftpack.dct(x, type=3)[:n_filters]
 *                   N-1
 * y[k] = x[0] + 2 * sum x[n]*cos(pi*(k+0.5)*n/N), 0 <= k < N.
 *                   n=1
 * </pre>
 *
 * \par DCT type-III normalized
 * <pre>
 * y = librosa.filters.dct(n_filters, n_inputs)
 *   = scipy.fftpack.dct(x, type=3, norm='ortho')[:n_filters]
 *                                     N-1
 * y[k] = x[0] / sqrt(N) + sqrt(2/N) * sum x[n]*cos(pi*(k+0.5)*n/N)
 *                                     n=1
 * </pre>
 *  @{
 */

/* Uncomment out to use naive DCT implementations instead of cos tables */
// #define USE_NAIVE_DCT

/**
 * @brief      Initialization function for the floating-point DCT operation.
 *
 * @param      *S    points to an instance of the floating-point DCT structure.
 * @return     0 if successful or -1 if there is an error.
 */
int32_t DCT_Init(DCT_InstanceTypeDef *S)
{
  int32_t status;
  uint32_t n_filters = S->NumFilters;
  uint32_t n_inputs = S->NumInputs;
  float32_t *M = S->pDCTCoefs;

  float64_t sample;
  float64_t normalizer;

  uint32_t shift;

  /* RemoveDCTZero only implemented for DCT Type-III non-normalized with COS tables */
  if (S->RemoveDCTZero != 0)
  {
    if (S->Type != DCT_TYPE_III)
    {
      status = -1;
      return status;
    }
    shift = 1;
  }
  else
  {
    shift = 0;
  }

  /* Compute DCT matrix coefficients */
  switch (S->Type)
  {
    case DCT_TYPE_II:
      for (uint32_t i = 0; i < n_filters; i++)
      {
        for (uint32_t j = 0; j < n_inputs; j++)
        {
          sample = M_PI * (j + 0.5) / n_inputs;
          M[i * n_inputs + j] = 2.0 * cos(sample * i);
        }
      }
      status = 0;
      break;

    case DCT_TYPE_II_ORTHO:
      normalizer = 2.0 * sqrt(1.0 / (4 * n_inputs));
      for (uint32_t i = 0; i < n_inputs; i++)
      {
        M[i] = normalizer;
      }
      normalizer = 2.0 / sqrt(2 * n_inputs);
      for (uint32_t i = 1; i < n_filters; i++)
      {
        for (uint32_t j = 0; j < n_inputs; j++)
        {
          sample = M_PI * (j + 0.5) / n_inputs;
          M[i * n_inputs + j] = normalizer * cos(sample * i);
        }
      }
      status = 0;
      break;

    case DCT_TYPE_II_SCALED:
      normalizer = 2.0 / sqrt(2 * n_inputs);
      for (uint32_t i = 0; i < n_filters; i++)
      {
        for (uint32_t j = 0; j < n_inputs; j++)
        {
          sample = M_PI * (j + 0.5) / n_inputs;
          M[i * n_inputs + j] = normalizer * cos(sample * i);
        }
      }
      status = 0;
      break;

    case DCT_TYPE_III:
      for (uint32_t i = 0; i < n_filters; i++)
      {
        sample = M_PI * (i + shift + 0.5) / n_inputs;
        for (uint32_t j = 0; j < n_inputs; j++)
        {
          M[i * n_inputs + j] = 2.0 * cos(sample * j);
        }
      }
      status = 0;
      break;

    case DCT_TYPE_III_ORTHO:
      normalizer = 1.0 / sqrt(n_inputs);
      for (uint32_t i = 0; i < n_inputs; i++)
      {
        M[i] = normalizer;
      }
      normalizer = sqrt(2.0 / n_inputs);
      for (uint32_t i = 0; i < n_filters; i++)
      {
        for (uint32_t j = 1; j < n_inputs; j++)
        {
          sample = M_PI * (i + 0.5) / n_inputs;
          M[i * n_inputs + j] = cos(sample * j) * normalizer;
        }
      }
      status = 0;
      break;

    default:
      /* Other DCT types not implemented or unsupported */
      status = -1;
      break;
  }

  return status;
}

/**
 * @brief      Processing function for the floating-point DCT.
 *
 * @param      *S    points to an instance of the floating-point DCT structure.
 * @param      *pIn  points to state buffer.
 * @param      *pOut points to the output buffer.
 * @return none.
 */
void DCT(DCT_InstanceTypeDef *S, float32_t *pIn, float32_t *pOut)
{
  float32_t sum;
  uint32_t n_inputs = S->NumInputs;
  uint32_t n_filters = S->NumFilters;

#ifndef USE_NAIVE_DCT
  float32_t *cosFact = S->pDCTCoefs;
  uint32_t row;
#else
  float32_t normalizer;
#endif /* USE_NAIVE_DCT */

  /* Compute DCT matrix coefficients */
  switch (S->Type)
  {
    case DCT_TYPE_II:
    #ifdef USE_NAIVE_DCT
      for (uint32_t k = 0; k < n_filters; k++)
      {
        sum = 0.0f;
        for (uint32_t n = 0; n < n_inputs; n++)
        {
          sum += pIn[n] * cos(M_PI * k * (n + 0.5) / n_inputs);
        }
        pOut[k] = 2.0f * sum;
      }
    #else
      for (uint32_t k = 0; k < n_filters; k++)
      {
        pOut[k] = 0.0f;
        row = k * n_inputs;
        for (uint32_t n = 0; n < n_inputs; n++)
        {
          // pOut[k] += pIn[n] * 2.0f * cos(M_PI * k * (n + 0.5) / n_inputs);
          pOut[k] += pIn[n] * cosFact[row + n];
        }
      }
    #endif /* USE_NAIVE_DCT */
      break;

    case DCT_TYPE_II_ORTHO:
    #ifdef USE_NAIVE_DCT
      normalizer = sqrtf(1.0f / (4 * n_inputs));
      sum = 0.0f;
      for (uint32_t n = 0; n < n_inputs; n++)
      {
        sum += pIn[n];
      }
      pOut[0] = normalizer * 2.0f * sum;

      normalizer = sqrtf(1.0f / (2 * n_inputs));
      for (uint32_t k = 1; k < n_filters; k++)
      {
        sum = 0.0f;
        for (uint32_t n = 0; n < n_inputs; n++)
        {
          sum += pIn[n] * cos(M_PI * k * (n + 0.5) / n_inputs);
        }
        pOut[k] = normalizer * 2.0f * sum;
      }
    #else
      sum = 0.0f;
      for (uint32_t n = 0; n < n_inputs; n++)
      {
        sum += pIn[n];
      }
      pOut[0] = cosFact[0] * sum;
      for (uint32_t k = 1; k < n_filters; k++)
      {
        pOut[k] = 0.0f;
        row = k * n_inputs;
        for (uint32_t n = 0; n < n_inputs; n++)
        {
          // pOut[k] += 2.0f / sqrtf(2 * n_inputs) * pIn[n] * cosf(M_PI * k * (n + 0.5) / n_inputs);
          pOut[k] += pIn[n] * cosFact[row + n];
        }
      }
    #endif /* USE_NAIVE_DCT */
      break;

    case DCT_TYPE_II_SCALED:
    #ifdef USE_NAIVE_DCT
      normalizer = 2.0f / sqrt(2 * n_inputs);
      for (uint32_t k = 0; k < n_filters; k++)
      {
        sum = 0.0f;
        for (uint32_t n = 0; n < n_inputs; n++)
        {
          sum += pIn[n] * cos(M_PI * k * (n + 0.5) / n_inputs);
        }
        pOut[k] = normalizer * sum;
      }
    #else
      for (uint32_t k = 0; k < n_filters; k++)
      {
        pOut[k] = 0.0f;
        row = k * n_inputs;
        for (uint32_t n = 0; n < n_inputs; n++)
        {
          // pOut[k] += pIn[n] * 2.0f * cos(M_PI * k * (n + 0.5) / n_inputs);
          pOut[k] += pIn[n] * cosFact[row + n];
        }
      }
    #endif /* USE_NAIVE_DCT */
      break;

    case DCT_TYPE_III:
    #ifdef USE_NAIVE_DCT
      for (uint32_t k = 0; k < n_filters; k++)
      {
        sum = 0.0f;
        for (uint32_t n = 1; n < n_inputs; n++)
        {
          sum += pIn[n] * cos(M_PI * (k + 0.5) * n / n_inputs);
        }
        pOut[k] = pIn[0] + 2.0f * sum;
      }
    #else
      for (uint32_t k = 0; k < n_filters; k++)
      {
        sum = 0.0f;
        row = k * n_inputs;
        for (uint32_t n = 1; n < n_inputs; n++)
        {
          // sum += pIn[n] * cos(M_PI * (k + 0.5) * n / n_inputs);
          sum += pIn[n] * cosFact[row + n];
        }
        pOut[k] = pIn[0] + sum;
      }
    #endif /* USE_NAIVE_DCT */
      break;

    case DCT_TYPE_III_ORTHO:
    #ifdef USE_NAIVE_DCT
      for (uint32_t k = 0; k < n_filters; k++)
      {
        sum = 0.0f;
        for (uint32_t n = 1; n < n_inputs; n++)
        {
          sum += pIn[n] * cos(M_PI * (k + 0.5) * n / n_inputs);
        }
        pOut[k] = pIn[0] / sqrtf(n_inputs) + sqrtf(2.0 / n_inputs) * sum;
      }
    #else
      sum = pIn[0] * cosFact[0];
      for (uint32_t k = 0; k < n_filters; k++)
      {
        pOut[k] = sum;
        row = k * n_inputs;
        for (uint32_t n = 1; n < n_inputs; n++)
        {
          // pOut[k] += pIn[n] * sqrtf(2.0 / n_inputs) * cos(M_PI * (k + 0.5) * n / n_inputs);
          pOut[k] += pIn[n] * cosFact[row + n];
        }
      }
    #endif /* USE_NAIVE_DCT */
      break;

    default:
      break;
  }
}

/**
 * @} end of groupDCT
 */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
