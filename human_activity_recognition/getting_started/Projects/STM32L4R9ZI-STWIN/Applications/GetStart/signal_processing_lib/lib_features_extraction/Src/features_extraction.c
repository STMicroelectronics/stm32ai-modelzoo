/**
 ******************************************************************************
 * @file    features_extraction.c
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
 * @brief   Features extraction routines
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

#include "features_extraction_if.h"
#include "features_extraction_loc.h"


#ifdef NDEBUG
#include "stm32_crc_lock.h"
#endif


/*----------------------------------------------------------------------------*/
/* static routines                                                            */
/*----------------------------------------------------------------------------*/
static
int32_t fmtCheckFloat32(uint32_t fmt_in,
                        uint32_t fmt_out)
{
  uint32_t ref_fmt = 0;
  uint32_t ref_fmt_msk;
  ref_fmt |= (AI_SP_FMT_SET_SIGN(1) |
              AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_FLOAT) |
              AI_SP_FMT_SET_BITS(32));
  ref_fmt_msk = (AI_SP_FMT_SET_SIGN(_FMT_SIGN_MASK) |
                 AI_SP_FMT_SET_TYPE(_FMT_TYPE_MASK) |
                 AI_SP_FMT_SET_BITS(_FMT_BITS_MASK));
  if ((((fmt_in & ref_fmt_msk)^ref_fmt) != 0) ||
      (((fmt_out & ref_fmt_msk)^ref_fmt) != 0))
  {
    return (AI_SP_ERROR_UNSUPPORTED_FMT);
  }
  else
  {
    return (AI_SP_ERROR_NO);
  }
}

/* unused (yet) functions

static
int32_t fmtCheckInt32(uint32_t fmt_in,
                      uint32_t fmt_out)
{
  uint32_t ref_fmt = 0;
  uint32_t ref_fmt_msk;
  ref_fmt |= (AI_SP_FMT_SET_SIGN(1) |
              AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_Q) |
              AI_SP_FMT_SET_BITS(32));
  ref_fmt_msk = (AI_SP_FMT_SET_SIGN(_FMT_SIGN_MASK) |
                 AI_SP_FMT_SET_TYPE(_FMT_TYPE_MASK) |
                 AI_SP_FMT_SET_BITS(_FMT_BITS_MASK));
  if ((((fmt_in & ref_fmt_msk)^ref_fmt) != 0) ||
      (((fmt_out & ref_fmt_msk)^ref_fmt) != 0))
  {
    return (AI_SP_ERROR_UNSUPPORTED_FMT);
  }
  else
  {
    return (AI_SP_ERROR_NO);
  }
}


static
int32_t fmtCheckInt16(uint32_t fmt_in,
                      uint32_t fmt_out)
{
  uint32_t ref_fmt = 0;
  uint32_t ref_fmt_msk;
  ref_fmt |= (AI_SP_FMT_SET_SIGN(1) |
              AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_Q) |
              AI_SP_FMT_SET_BITS(16));
  ref_fmt_msk = (AI_SP_FMT_SET_SIGN(_FMT_SIGN_MASK) |
                 AI_SP_FMT_SET_TYPE(_FMT_TYPE_MASK) |
                 AI_SP_FMT_SET_BITS(_FMT_BITS_MASK));
  if ((((fmt_in & ref_fmt_msk)^ref_fmt) != 0) ||
      (((fmt_out & ref_fmt_msk)^ref_fmt) != 0))
  {
    return (AI_SP_ERROR_UNSUPPORTED_FMT);
  }
  else
  {
    return (AI_SP_ERROR_NO);
  }
}


static
int32_t fmtCheckUint32(uint32_t fmt_in,
                       uint32_t fmt_out)
{
  uint32_t ref_fmt = 0;
  uint32_t ref_fmt_msk;
  ref_fmt |= (AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_Q) |
              AI_SP_FMT_SET_BITS(32));
  ref_fmt_msk = (AI_SP_FMT_SET_SIGN(_FMT_SIGN_MASK) |
                 AI_SP_FMT_SET_TYPE(_FMT_TYPE_MASK) |
                 AI_SP_FMT_SET_BITS(_FMT_BITS_MASK));
  if ((((fmt_in & ref_fmt_msk)^ref_fmt) != 0) ||
      (((fmt_out & ref_fmt_msk)^ref_fmt) != 0))
  {
    return (AI_SP_ERROR_UNSUPPORTED_FMT);
  }
  else
  {
    return (AI_SP_ERROR_NO);
  }
}



static
int32_t fmtCheckUint16(uint32_t fmt_in,
                      uint32_t fmt_out)
{
  uint32_t ref_fmt = 0;
  uint32_t ref_fmt_msk;
  ref_fmt |= (AI_SP_FMT_SET_TYPE(AI_SP_FMT_TYPE_Q) |
              AI_SP_FMT_SET_BITS(16));
  ref_fmt_msk = (AI_SP_FMT_SET_SIGN(_FMT_SIGN_MASK) |
                 AI_SP_FMT_SET_TYPE(_FMT_TYPE_MASK) |
                 AI_SP_FMT_SET_BITS(_FMT_BITS_MASK));
  if ((((fmt_in & ref_fmt_msk)^ref_fmt) != 0) ||
      (((fmt_out & ref_fmt_msk)^ref_fmt) != 0))
  {
    return (AI_SP_ERROR_UNSUPPORTED_FMT);
  }
  else
  {
    return (AI_SP_ERROR_NO);
  }
}

*/

static
int32_t getOutputDim2D(const ai_logging_packet_t  *pPacketIn,
                       uint16_t  mode,
                       uint32_t  element_size,
                       ai_logging_packet_t  *pPacketOut)
{
  uint16_t data_n_shapes_in = pPacketIn->shape.n_shape;
  uint16_t data_height_in;
  uint16_t data_width_in;
  uint16_t data_width_out, data_height_out, data_n_shapes_out;

  if (data_n_shapes_in == 1)
  {
      data_height_in = 1;
  }
  else
  {
      data_height_in = pPacketIn->shape.shapes[AI_LOGGING_SHAPES_HEIGHT];
  }
  data_width_in = pPacketIn->shape.shapes[AI_LOGGING_SHAPES_WIDTH];

  if (mode == AI_SP_MODE_FULL)
  {
    /* processing on the full array */
    data_height_out = 1;
    data_width_out = 1;
    data_n_shapes_out = 1;
  }
  else if (mode == AI_SP_MODE_LINE)
  {
    /* Line processing */
    data_height_out = 1;
    data_width_out = data_height_in;
    data_n_shapes_out = 1;
  }
  else if (mode == AI_SP_MODE_COLUMN)
  {
    /* Column processing */
    data_height_out = 1;
    data_width_out = data_width_in;
    data_n_shapes_out = 1;
  }
  else
  {
    return (AI_SP_ERROR_BAD_FMT);
  }

  pPacketOut->shape.n_shape = data_n_shapes_out;
  pPacketOut->shape.shapes[AI_LOGGING_SHAPES_HEIGHT] = data_height_out;
  pPacketOut->shape.shapes[AI_LOGGING_SHAPES_WIDTH] = data_width_out;
  pPacketOut->payload_size = data_width_out * data_height_out * element_size;
  return (AI_SP_ERROR_NO);
}


/*----------------------------------------------------------------------------*/
/* Features extraction :  Statistical calculation routines                    */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_Stat_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                uint16_t  mode,
                                ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_StatDataOut_t),
                         pPacketOut);
  return (error);
}


int32_t AI_SP_Stat_Process(AI_SP_StatIn_t  *pInput,
                           AI_SP_StatOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Stat process init */
  AI_SP_StatDataOut_t *pDataOut;

  /* Then processing with supported formats can start */
  pDataOut = (AI_SP_StatDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      float32_t min = *pDataIn;
      float32_t max = *pDataIn;
      float32_t sum = *pDataIn;
      float32_t mean = 0.0f;
      float32_t std = 0.0f;
      float32_t var = 0.0f;
      float32_t sum2 = 0.0f;
      pDataIn += inner_data_stride;
      for (i = 0; i < inner_data_loop-1; i++)
      {
        min = (min < *pDataIn) ? min : *pDataIn;
        max = (max > *pDataIn) ? max : *pDataIn;
        sum += *pDataIn;
        pDataIn += inner_data_stride;
      }
      mean = sum / inner_data_loop;
      pDataOut->min = min;
      pDataOut->max = max;
      pDataOut->mean = mean;

      /* Needed for Std and Var */
      if ((pInput->out_selection == AI_SP_STAT_STD) ||
          (pInput->out_selection == AI_SP_STAT_STD_VAR) ||
          (pInput->out_selection == AI_SP_STAT_STD_LOGVAR))
      {
        pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
        for (i = 0; i < inner_data_loop; i++)
        {
          sum2 += (*pDataIn - mean) * (*pDataIn - mean);
          pDataIn += inner_data_stride;
        }
      }

      /* Standard deviation */
      if ((pInput->out_selection == AI_SP_STAT_STD) ||
          (pInput->out_selection == AI_SP_STAT_STD_VAR) ||
          (pInput->out_selection == AI_SP_STAT_STD_LOGVAR))
      {
        std = sqrtf(sum2/inner_data_loop);
      }
      pDataOut->std = std;

      /* Variance */
      if ((pInput->out_selection == AI_SP_STAT_VAR) ||
          (pInput->out_selection == AI_SP_STAT_STD_VAR))
      {
        /* complete variance calculation */
        var = sum2 / (inner_data_loop - 1);
      }
      else if ((pInput->out_selection == AI_SP_STAT_LOGVAR) ||
               (pInput->out_selection == AI_SP_STAT_STD_LOGVAR))
      {
        /* complete variance calculation */
        var = sum2 / (inner_data_loop - 1);
        var = log10f(var + AI_SP_EPSILON);
      }
      pDataOut->var = var;
      pDataOut++;
  }

  return (AI_SP_ERROR_NO);
}


/*----------------------------------------------------------------------------*/
/* Features extraction :  Magnitude calculation routine                       */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_Mag_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                               uint16_t  mode,
                               ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_MagDataOut_t),
                         pPacketOut);
  return (error);
}


int32_t AI_SP_Mag_Process(AI_SP_MagIn_t *pInput,
                          AI_SP_MagOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Stat process init */
  AI_SP_MagDataOut_t *pDataOut;
  float32_t mag;

  /* Then processing with supported formats can start */
  pDataOut = (AI_SP_MagDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      mag = 0.0f;
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      for (i = 0; i < inner_data_loop; i++)
      {
        mag += *pDataIn * *pDataIn;
        pDataIn += inner_data_stride;
      }
      pDataOut->mag = sqrtf(mag);
      pDataOut++;
  }

  return (AI_SP_ERROR_NO);
}


/*----------------------------------------------------------------------------*/
/* Features extraction :  RMS calculation routine                        */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_Rms_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                               uint16_t  mode,
                               ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_RmsDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_Rms_Process(AI_SP_RmsIn_t *pInput,
                         AI_SP_RmsOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Stat process init */
  AI_SP_RmsDataOut_t *pDataOut;
  float32_t rms;

  /* Then processing with supported formats can start */
  pDataOut = (AI_SP_RmsDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      rms = 0.0f;
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      for (i = 0; i < inner_data_loop; i++)
      {
        rms += *pDataIn * *pDataIn;
        pDataIn += inner_data_stride;
      }
      pDataOut->rms = sqrtf(rms / inner_data_loop);
      pDataOut++;
  }

  return (AI_SP_ERROR_NO);
}


/*----------------------------------------------------------------------------*/
/* Features extraction :  Temporal Skewness calculation routine               */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_Skewness_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                    uint16_t  mode,
                                    ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_SkewnessDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_Skewness_Process(AI_SP_SkewnessIn_t *pInput,
                               AI_SP_SkewnessOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Skewness process init */
  AI_SP_SkewnessDataOut_t *pDataOut;
  int16_t unbiased = pInput->unbiased;
  float32_t data, mean, s2, m3, skewness;

  /* Then processing with supported formats can start */
  if (inner_data_loop < 2)
  {
    return (AI_SP_ERROR_NOT_ENOUGH_DATA);
  }

  pDataOut = (AI_SP_SkewnessDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      /* Computation of the mean */
      mean = 0.0f;
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      for (i = 0; i < inner_data_loop; i++)
      {
        mean += *pDataIn;
        pDataIn += inner_data_stride;
      }
      mean /= inner_data_loop;

      /* 2nd and 3rd order computation */
      s2 = 0.0f;
      m3 = 0.0f;
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      for (i = 0; i < inner_data_loop; i++)
      {
        data = *pDataIn - mean;
        s2 += (data * data);
        m3 += (data * data * data);
        pDataIn += inner_data_stride;
      }
      s2 /= inner_data_loop;
      m3 /= inner_data_loop;
      if (s2 > AI_SP_EPSILON)
      {
        skewness = m3 / (sqrtf(s2*s2*s2) + AI_SP_EPSILON);
      }
      else
      {
        skewness = 0.0f;
      }
      if (unbiased != 0)
      {
        if (inner_data_loop < 3)
        {
          return (AI_SP_ERROR_NOT_ENOUGH_DATA);
        }
        skewness = skewness * (sqrtf(inner_data_loop*(inner_data_loop-1))/(inner_data_loop-2));
      }
      pDataOut->skewness = skewness;
      pDataOut++;
  }

  return (AI_SP_ERROR_NO);
}


/*----------------------------------------------------------------------------*/
/* Features extraction :  Temporal Flatness calculation routine               */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_Flatness_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                    uint16_t  mode,
                                    ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_FlatnessDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_Flatness_Process(AI_SP_FlatnessIn_t *pInput,
                               AI_SP_FlatnessOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Flatness process init */
  AI_SP_FlatnessDataOut_t *pDataOut;
  float32_t mean, mean_log, flatness;

  /* Then processing with supported formats can start */
  pDataOut = (AI_SP_FlatnessDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      /* Computes E[X] and E[log(X)] */
      mean = 0.0f;
      mean_log = 0.0f;
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      for (i = 0; i < inner_data_loop; i++)
      {
        mean_log += logf(*pDataIn + AI_SP_EPSILON);
        mean += *pDataIn;
        pDataIn += inner_data_stride;
      }

      /* Flatness calculation */
      mean /= inner_data_loop;
      mean_log /= inner_data_loop;
      flatness = expf(mean_log) / mean;
      pDataOut->flatness = flatness;
      pDataOut++;
  }

  return (error);
}


/*----------------------------------------------------------------------------*/
/* Features extraction : Zero Crossing Rate (ZCR) calculation routine         */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_Zcr_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                               uint16_t  mode,
                               ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_ZcrDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_Zcr_Process(AI_SP_ZcrIn_t *pInput,
                          AI_SP_ZcrOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Zcr process init */
  AI_SP_ZcrDataOut_t *pDataOut;
  float32_t data1, data2, tmp, zcr;
  float32_t threshold = pInput->threshold;

  /* Then processing with supported formats can start */
  pDataOut = (AI_SP_ZcrDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      zcr = 0;
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      data1 = *pDataIn - threshold;
      pDataIn += inner_data_stride;
      data1 = (data1 > 0) ? 1 : ((data1 < 0) ? -1 : 0);
      for (i = 0; i < inner_data_loop; i++)
      {
        data2 = *pDataIn - threshold;
        pDataIn += inner_data_stride;
        data2 = (data2 > 0) ? 1 : ((data2 < 0) ? -1 : 0);
        tmp = data2 - data1;
        tmp = (tmp == 0) ? 0 : 1;
        zcr += tmp;
        data1 = data2;
      }
      pDataOut->zcr = zcr;
      pDataOut++;
  }

  return (error);
}


/*----------------------------------------------------------------------------*/
/* Features extraction : Temporal entropy calculation routine                 */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_Entropy_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                   uint16_t  mode,
                                   ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_EntropyDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_Entropy_Process(AI_SP_EntropyIn_t *pInput,
                              AI_SP_EntropyOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Entropy process init */
  AI_SP_EntropyDataOut_t *pDataOut;
  float32_t data, min, max, entropy, range;
  int16_t nb_bars = pInput->nb_bars;
  int16_t tmp_16;

  /* Then processing with supported formats can start */
  /* nb_bars between min(nb_bars, inner_data_loop) and 256 for entropy calculation */
  nb_bars = (nb_bars == -1) ? 32 : nb_bars;
  nb_bars = (nb_bars < inner_data_loop) ? nb_bars : inner_data_loop;
  nb_bars = (nb_bars > 256) ? 256 : nb_bars;

  float32_t pdf_bar_a[nb_bars];
  /* Initializes the histogram */
  for (i = 0; i < nb_bars; i++)
  {
    pdf_bar_a[i] = AI_SP_EPSILON;
  }

  pDataOut = (AI_SP_EntropyDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      /* Find min and max of the histogram bars */
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      min = max = logf(*pDataIn + AI_SP_EPSILON);
      pDataIn += inner_data_stride;
      for (i = 1; i < inner_data_loop; i++)
      {
        data = logf(*pDataIn + AI_SP_EPSILON);
        pDataIn += inner_data_stride;
        min = (data < min) ? data : min;
        max = (data >= max) ? data : max;

      }
      range = max - min;

      /* Fills histogram bars */
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      for (i = 0; i < inner_data_loop; i++)
      {
        data = logf(*pDataIn + AI_SP_EPSILON);
        pDataIn += inner_data_stride;
        tmp_16 = (int16_t)(nb_bars * (data - min) / range );
        tmp_16 = (tmp_16 >= nb_bars) ? (nb_bars - 1) : tmp_16;
        pdf_bar_a[tmp_16]++;
      }

      /* Calculates entropy */
      entropy = 0.0f;
      for (i = 0; i < nb_bars; i++)
      {
        entropy -= pdf_bar_a[i]/inner_data_loop * log2f(pdf_bar_a[i]/inner_data_loop);
      }

      pDataOut->entropy = entropy;
      pDataOut++;
  }

  return (error);
}


/*----------------------------------------------------------------------------*/
/* Features extraction : AR coefs 2 and 3 calculation routine                 */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_Ar3_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                               uint16_t  mode,
                               ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_Ar3DataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_Ar3_Process(AI_SP_Ar3In_t *pInput,
                          AI_SP_Ar3Out_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Ar3 process init */
  AI_SP_Ar3DataOut_t *pDataOut;
  const float32_t *pData2, *pData3;
  float32_t data, data2, data3;
  float32_t mean;
  float32_t r_1, r_2, r_3;
  float32_t lambda, comput_error;
  float32_t ar1, ar2;

  /* Then processing with supported formats can start */
  pDataOut = (AI_SP_Ar3DataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      /* Computation of the mean */
      mean = 0.0f;
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      for (i = 0; i < inner_data_loop; i++)
      {
        mean += *pDataIn;
        pDataIn += inner_data_stride;
      }
      mean /= inner_data_loop;

      /* Correlation values */
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      pData2 = (const float32_t *)pDataIn;
      pData3 = (const float32_t *)pDataIn;
      data = *pDataIn - mean;
      pDataIn += inner_data_stride;
      data2 = data;
      r_1 = data * data;
      data = *pDataIn - mean;
      pDataIn += inner_data_stride;
      r_1 += data * data;
      r_2 = data2 * data;
      pData2 += inner_data_stride;
      r_3 = 0.0f;
      for (i = 2; i < inner_data_loop; i++)
      {
        data = *pDataIn - mean;
        pDataIn += inner_data_stride;
        data2 = *pData2 - mean;
        pData2 += inner_data_stride;
        data3 = *pData3 - mean;
        pData3 += inner_data_stride;
        r_1 += data * data;
        r_2 += data2 * data;
        r_3 += data3 * data;
      }

      /* AR Coefficients calculation */
      ar1 = 1.0f;
      /* -- Iteration 1 -- */
      lambda = -r_2/(r_1 + AI_SP_EPSILON);
      ar2 = lambda;
      comput_error = r_1 * (1.0f - lambda*lambda);
      /* -- Iteration 2 -- */
      lambda = -((r_3*ar1) + (r_2 * ar2)) / (comput_error + AI_SP_EPSILON);

      pDataOut->ar2 = ar2 * (1.0F + lambda);
      pDataOut->ar3 = lambda;
      pDataOut++;
  }

  return (error);
}



/*----------------------------------------------------------------------------*/
/* Features extraction : Spectral Flatness calculation routine                */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_SpectralFlatness_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                            uint16_t  mode,
                                            ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_SpectralFlatnessDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_SpectralFlatness_Process(AI_SP_SpectralFlatnessIn_t *pInput,
                                       AI_SP_SpectralFlatnessOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Spectral Flatness process init */
  AI_SP_SpectralFlatnessDataOut_t *pDataOut;
  float32_t mean, mean_log, flatness;
  int16_t b1 = pInput->b1;
  int16_t b2 = pInput->b2;
  int16_t n_freq = b2 - b1 + 1;

  /* Then processing with supported formats can start */
  if ((b2 <= b1) ||
      (b1 < 0)  ||
      (b2 >= inner_data_loop))
  {
    return (AI_SP_ERROR_WRONG_BINS_IDX);
  }

  pDataOut = (AI_SP_SpectralFlatnessDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
      /* Computes E[X] and E[log(X)] */
      mean = 0.0f;
      mean_log = 0.0f;
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      for (i = b1; i <= b2; i++)
      {
        mean_log += logf(*pDataIn + AI_SP_EPSILON);
        mean += *pDataIn;
        pDataIn += inner_data_stride;
      }

      /* Flatness calculation */
      mean /= n_freq;
      mean_log /= n_freq;
      flatness = expf(mean_log) / mean;
      pDataOut->flatness = flatness;
      pDataOut++;
  }

  return (error);
}


/*----------------------------------------------------------------------------*/
/* Features extraction : Spectral Centroid, Spread, Skewness and Kurtosis     */
/*                       calculation routine                                  */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_SpectralCentroid_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                            uint16_t  mode,
                                            ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_SpectralCentroidDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_SpectralCentroid_Process(AI_SP_SpectralCentroidIn_t *pInput,
                                       AI_SP_SpectralCentroidOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Spectral Centroid process init */
  AI_SP_SpectralCentroidDataOut_t *pDataOut;
  float32_t power_sum, disp_centroid, m3, m4;
  float32_t centroid;
  float32_t spread = 0.0F;
  float32_t skewness = 0.0f;
  float32_t kurtosis = 0.0f;
  int16_t b1 = pInput->b1;
  int16_t b2 = pInput->b2;

  /* Then processing with supported formats can start */
  if ((b2 <= b1) ||
      (b1 < 0)  ||
      (b2 >= inner_data_loop))
  {
    return (AI_SP_ERROR_WRONG_BINS_IDX);
  }

  pDataOut = (AI_SP_SpectralCentroidDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
    /* 1st order moment calculation for Centroid */
    pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
    centroid = 0.0f;
    power_sum = AI_SP_EPSILON;
    for (i = b1; i <= b2; i++)
    {
      centroid += (i * *pDataIn);
      power_sum += *pDataIn;
      pDataIn += inner_data_stride;
    }
    centroid /= power_sum;

    /* Spread computation */
    if (pInput->out_selection >= AI_SP_CENTROID_SPREAD)
    {
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      spread = 0.0f;
      m3 = 0.0f;
      m4 = 0.0f;
      for (i = b1; i <= b2; i++)
      {
        disp_centroid = (i - centroid);
        spread += disp_centroid * disp_centroid * *pDataIn;
        pDataIn += inner_data_stride;
      }
      spread /= power_sum;
    }

    /* Skewness computation */
    /* Fisher Coefficient calculation :
        - skewness < 0 =>  right asymmetry
        - skewness = 0 =>  symmetric
        - skewness > 0 =>  left asymmetry
    */
    if ((pInput->out_selection == AI_SP_CENTROID_SPREAD_SKEWNESS) ||
        (pInput->out_selection == AI_SP_CENTROID_SPREAD_SKEWNESS_KURTOSIS))
    {
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      m3 = 0.0f;
      for (i = b1; i <= b2; i++)
      {
        disp_centroid = (i - centroid);
        m3 += disp_centroid * disp_centroid * disp_centroid * *pDataIn;
        pDataIn += inner_data_stride;
      }
      m3 /= power_sum;
      skewness = m3 / sqrtf(spread * spread * spread + AI_SP_EPSILON);
    }

    /* Kurtosis computation */
    if ((pInput->out_selection == AI_SP_CENTROID_SPREAD_KURTOSIS) ||
        (pInput->out_selection == AI_SP_CENTROID_SPREAD_SKEWNESS_KURTOSIS))
    {
      pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
      m4 = 0.0f;
      for (i = b1; i <= b2; i++)
      {
        disp_centroid = (i - centroid);
        m4 += disp_centroid * disp_centroid * disp_centroid * disp_centroid * *pDataIn;
        pDataIn += inner_data_stride;
      }
      m4 /= power_sum;
      kurtosis = m4 / (spread * spread + AI_SP_EPSILON);
    }

    /* Output formating */
    if (pInput->out_selection >= AI_SP_CENTROID_SPREAD)
    {
      spread = sqrtf(spread + AI_SP_EPSILON);
      if (pInput->sampling_freq > 0)
      {
        /* Results from sampling frequency */
        spread *= (float32_t)(pInput->sampling_freq/(2.0f * inner_data_loop));
      }
    }

    if (pInput->sampling_freq > 0)
    {
      /* Results from sampling frequency */
      centroid *= (float32_t)(pInput->sampling_freq/(2.0f * inner_data_loop));
    }

    pDataOut->centroid = centroid;
    pDataOut->spread   = spread;
    pDataOut->skewness = skewness;
    pDataOut->kurtosis = kurtosis;
    pDataOut++;
  }

  return (error);
}


/*----------------------------------------------------------------------------*/
/* Features extraction : Spectral Crest factor calculation routine            */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_SpectralCrest_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                         uint16_t  mode,
                                         ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_SpectralCrestDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_SpectralCrest_Process(AI_SP_SpectralCrestIn_t *pInput,
                                    AI_SP_SpectralCrestOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Spectral Crest process init */
  AI_SP_SpectralCrestDataOut_t *pDataOut;
  float32_t max, mean, crest;
  int16_t b1 = pInput->b1;
  int16_t b2 = pInput->b2;
  int16_t n_freq = b2 - b1 + 1;

  /* Then processing with supported formats can start */
  if ((b2 <= b1) ||
      (b1 < 0)  ||
      (b2 >= inner_data_loop))
  {
    return (AI_SP_ERROR_WRONG_BINS_IDX);
  }

  pDataOut = (AI_SP_SpectralCrestDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
    /* Max and mean in [b1 b2] interval */
    pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
    crest = 0.0f;
    max = *pDataIn;
    pDataIn += inner_data_stride;
    mean = max;
    for (i = b1+1; i <= b2; i++)
    {
      max = (max < *pDataIn) ? *pDataIn : max;
      mean += *pDataIn;
      pDataIn += inner_data_stride;
    }
    mean /= n_freq;

    /* Crest factor calculation */
    crest = max / (mean + AI_SP_EPSILON);
    pDataOut->crest = crest;
    pDataOut++;
  }

  return (error);
}


/*----------------------------------------------------------------------------*/
/* Features extraction : Spectral Entropy calculation routine                 */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_SpectralEntropy_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                           uint16_t  mode,
                                           ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_SpectralEntropyDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_SpectralEntropy_Process(AI_SP_SpectralEntropyIn_t *pInput,
                                      AI_SP_SpectralEntropyOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Spectral Entropy process init */
  AI_SP_SpectralEntropyDataOut_t *pDataOut;
  float32_t entropy;
  int16_t b1 = pInput->b1;
  int16_t b2 = pInput->b2;
  int16_t n_freq = b2 - b1 + 1;

  /* Then processing with supported formats can start */
  if ((b2 <= b1) ||
      (b1 < 0)  ||
      (b2 >= inner_data_loop))
  {
    return (AI_SP_ERROR_WRONG_BINS_IDX);
  }

  pDataOut = (AI_SP_SpectralEntropyDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
    pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
    entropy = 0.0f;
    for (i = b1; i <= b2; i++)
    {
      entropy += (*pDataIn * logf(*pDataIn + AI_SP_EPSILON));
      pDataIn += inner_data_stride;
    }
    entropy = -entropy / (logf(n_freq));
    pDataOut->entropy = entropy;
    pDataOut++;
  }

  return (error);
}


/*----------------------------------------------------------------------------*/
/* Features extraction : Peak freq and SNR calculation routine                */
/*----------------------------------------------------------------------------*/
int32_t AI_SP_SpectralPeak_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                        uint16_t  mode,
                                        ai_logging_packet_t  *pPacketOut)
{
  int32_t error = AI_SP_ERROR_NO;
  error = getOutputDim2D(pPacketIn,
                         mode,
                         sizeof(AI_SP_SpectralPeakDataOut_t),
                         pPacketOut);
  return (error);
}

int32_t AI_SP_SpectralPeak_Process(AI_SP_SpectralPeakIn_t *pInput,
                                   AI_SP_SpectralPeakOut_t *pOutput)
{
  /* Generic AI_SP features extraction macro init */
  AI_SP_GENERIC_PROCESS_INIT()

  /* Specific Spectral Peak process init */
  AI_SP_SpectralPeakDataOut_t *pDataOut;
  float32_t peak_power, peak_freq, noise_power, power_sum;
  float32_t peak_snr = 0.0f;
  int32_t peak_power_idx;
  int16_t b1 = pInput->b1;
  int16_t b2 = pInput->b2;
  int16_t n_freq = b2 - b1 + 1;

  /* Then processing with supported formats can start */
  if ((b2 <= b1) ||
      (b1 < 0)  ||
      (b2 >= inner_data_loop))
  {
    return (AI_SP_ERROR_WRONG_BINS_IDX);
  }

  pDataOut = (AI_SP_SpectralPeakDataOut_t *)packetOut.payload;
  for (uint32_t outer_idx = 0; outer_idx < outer_data_loop; outer_idx++)
  {
    /* Extracts frequency peak and power */
    peak_power_idx = b1;
    pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
    power_sum = *pDataIn;
    peak_power = *pDataIn;
    pDataIn += inner_data_stride;
    for (i = b1+1; i <= b2; i++)
    {
      if (*pDataIn > peak_power)
      {
        peak_power = *pDataIn;
        peak_power_idx = i;
      }
      power_sum += *pDataIn;
      pDataIn += inner_data_stride;
    }
    if (pInput->sampling_freq > 0)
    {
      /* Results from sampling frequency */
      peak_freq = (float32_t)((peak_power_idx * (float32_t)(pInput->sampling_freq)) / (2.0f * (float32_t)inner_data_loop));
    }
    else
    {
      peak_freq = peak_power_idx;
    }

    /* Calculates noise power and SNR */
    pDataIn = (const float32_t *)packetIn.payload + outer_idx*outer_data_stride;
    if (peak_power_idx == b1)
    {
      noise_power = power_sum - peak_power - pDataIn[inner_data_stride];
      noise_power /= (n_freq - 2);
    }
    else if (peak_power_idx == b2)
    {
      noise_power = power_sum - pDataIn[(b2 - b1 - 1)*inner_data_stride] - peak_power;
      noise_power /= (n_freq - 2);
    }
    else
    {
      noise_power = power_sum - pDataIn[(peak_power_idx - b1 - 1)*inner_data_stride] - peak_power - pDataIn[(peak_power_idx - b1 + 1)*inner_data_stride];
      noise_power /= (n_freq - 3);
    }
    if (noise_power > 0)
    {
      peak_snr = 10.0f * log10f(peak_power / noise_power);
    }
    else
    {
      peak_snr = (peak_power > 0) ? 1.0f : 0.0f;
      peak_snr *= AI_SP_SPECTRAL_PEAK_SNR_MAX;
    }

    /* Outputs frequency power, peak and SNR */
    pDataOut->peak_snr = peak_snr;
    if (peak_power < AI_SP_EPSILON)
    {
      pDataOut->peak_power = AI_SP_SPECTRAL_PEAK_MIN;  /* min in dB */
    }
    else
    {
      pDataOut->peak_power = log10f(peak_power);
    }
    pDataOut->peak_freq = peak_freq;
    pDataOut++;
  }

  return (error);
}

