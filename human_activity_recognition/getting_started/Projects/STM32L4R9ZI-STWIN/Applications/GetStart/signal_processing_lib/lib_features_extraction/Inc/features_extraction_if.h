/**
 ******************************************************************************
 * @file    FEAT_EXTRACT_if.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version $Version$
 * @date    $Date$
 *
 * @brief   global interface for features extraction routines
 *
 * <DESCRIPTIOM>
 *
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __FEAT_EXTRACT_IF_H__
#define __FEAT_EXTRACT_IF_H__


#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "arm_math.h"
#include "ai_sp_dataformat.h"
#include "ai_logging.h"


/* Exported constants --------------------------------------------------------*/
/* Exported defines ----------------------------------------------------------*/
#define   AI_SP_MODE_FULL     (0)
#define   AI_SP_MODE_LINE     (1)
#define   AI_SP_MODE_COLUMN   (2)


#define   AI_SP_STAT               (0)
#define   AI_SP_STAT_STD           (1)
#define   AI_SP_STAT_VAR           (2)
#define   AI_SP_STAT_LOGVAR        (3)
#define   AI_SP_STAT_STD_VAR       (4)
#define   AI_SP_STAT_STD_LOGVAR    (5)

#define   AI_SP_CENTROID                          (0)
#define   AI_SP_CENTROID_SPREAD                   (1)
#define   AI_SP_CENTROID_SPREAD_SKEWNESS          (2)
#define   AI_SP_CENTROID_SPREAD_KURTOSIS          (3)
#define   AI_SP_CENTROID_SPREAD_SKEWNESS_KURTOSIS (4)

#define   AI_SP_PEAK_POWER        (0)
#define   AI_SP_PEAK_FREQ         (1)
#define   AI_SP_PEAK_SNR          (2)


/* Error return codes */
#define   AI_SP_ERROR_NO                    (0)
#define   AI_SP_ERROR_BAD_HW                (-1)
#define   AI_SP_ERROR_BAD_FMT               (-2)
#define   AI_SP_ERROR_UNSUPPORTED_FMT       (-3)
#define   AI_SP_ERROR_NOT_ENOUGH_DATA       (-4)
#define   AI_SP_ERROR_WRONG_BINS_IDX        (-5)


/* Exported macros -----------------------------------------------------------*/
/* Exported types ------------------------------------------------------------*/

 typedef struct _AI_SP_StreamEx {
   ai_logging_packet_t   packet;
   uint16_t    mode;
 } AI_SP_Stream_t;

/* Statistics */
#define AI_SP_STAT_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                             AI_SP_FMT_SET_CONST(1))
#define AI_SP_STAT_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_StatDataOut {
    float32_t   min;
    float32_t   max;
    float32_t   mean;
    float32_t   std;          /* Standard deviation */
    float32_t   var;          /* Unbiased variance */
} AI_SP_StatDataOut_t;

typedef struct AI_SP_StatIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    uint16_t    out_selection;
} AI_SP_StatIn_t;

typedef struct AI_SP_StatOut {
    ai_logging_packet_t  packet;
} AI_SP_StatOut_t;


/* Magnitude */
#define AI_SP_MAG_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                            AI_SP_FMT_SET_CONST(1))
#define AI_SP_MAG_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_MagDataOut {
    float32_t   mag;
} AI_SP_MagDataOut_t;

typedef struct AI_SP_MagIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
} AI_SP_MagIn_t;

typedef struct AI_SP_MagOut {
    ai_logging_packet_t  packet;
} AI_SP_MagOut_t;


/* RMS */
#define AI_SP_RMS_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                            AI_SP_FMT_SET_CONST(1))
#define AI_SP_RMS_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_RmsDataOut {
    float32_t   rms;
} AI_SP_RmsDataOut_t;

typedef struct AI_SP_RmsIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
} AI_SP_RmsIn_t;

typedef struct AI_SP_RmsOut {
    ai_logging_packet_t  packet;
} AI_SP_RmsOut_t;


/* Skewness */
#define AI_SP_SKEWNESS_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                                 AI_SP_FMT_SET_CONST(1))
#define AI_SP_SKEWNESS_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_SkewnessDataOut {
    float32_t   skewness;
} AI_SP_SkewnessDataOut_t;

typedef struct AI_SP_SkewnessIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    int16_t     unbiased;     /* 0 means this uses biased variance, else it is unbiased */
} AI_SP_SkewnessIn_t;

typedef struct AI_SP_SkewnessOut {
    ai_logging_packet_t  packet;
} AI_SP_SkewnessOut_t;


/* Flatness */
#define AI_SP_FLATNESS_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                                 AI_SP_FMT_SET_CONST(1))
#define AI_SP_FLATNESS_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_FlatnessDataOut {
    float32_t   flatness;
} AI_SP_FlatnessDataOut_t;

typedef struct AI_SP_FlatnessIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
} AI_SP_FlatnessIn_t;

typedef struct AI_SP_FlatnessOut {
    ai_logging_packet_t  packet;
} AI_SP_FlatnessOut_t;


/* AR models */
#define AI_SP_AR3_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                            AI_SP_FMT_SET_CONST(1))
#define AI_SP_AR3_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_Ar3DataOut {
    float32_t   ar2;
    float32_t   ar3;
} AI_SP_Ar3DataOut_t;

typedef struct AI_SP_Ar3In {
    ai_logging_packet_t  packet;
    uint16_t    mode;
} AI_SP_Ar3In_t;

typedef struct AI_SP_Ar3Out {
    ai_logging_packet_t  packet;
} AI_SP_Ar3Out_t;


/* ZCR */
#define AI_SP_ZCR_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                            AI_SP_FMT_SET_CONST(1))
#define AI_SP_ZCR_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_ZcrDataOut {
    float32_t   zcr;
} AI_SP_ZcrDataOut_t;

typedef struct AI_SP_ZcrIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    float32_t   threshold;    /* For Threshold Crossing Rate...*/
} AI_SP_ZcrIn_t;

typedef struct AI_SP_ZcrOut {
    ai_logging_packet_t  packet;
} AI_SP_ZcrOut_t;


/* Entropy */
#define AI_SP_ENTROPY_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                                AI_SP_FMT_SET_CONST(1))
#define AI_SP_ENTROPY_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_EntropyDataOut {
    float32_t   entropy;
} AI_SP_EntropyDataOut_t;

typedef struct AI_SP_EntropyIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    int16_t     nb_bars;    /* histogram size : if set to -1, default value = min(32, input size) is used */
} AI_SP_EntropyIn_t;

typedef struct AI_SP_EntropyOut {
    ai_logging_packet_t  packet;
} AI_SP_EntropyOut_t;


/* Spectral Flatness */
#define AI_SP_SPECTRAL_FLATNESS_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                                          AI_SP_FMT_SET_CONST(1))
#define AI_SP_SPECTRAL_FLATNESS_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_SpectralFlatnessDataOut {
    float32_t   flatness;
} AI_SP_SpectralFlatnessDataOut_t;

typedef struct AI_SP_SpectralFlatnessIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    int16_t     b1;     /* first bin index to consider */
    int16_t     b2;     /* last bin index to consider */
} AI_SP_SpectralFlatnessIn_t;

typedef struct AI_SP_SpectralFlatnessOut {
    ai_logging_packet_t  packet;
} AI_SP_SpectralFlatnessOut_t;


/* Spectral Centroid, Spread, Skewness and Kurtosis */
#define AI_SP_SPECTRAL_CENTROID_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                                          AI_SP_FMT_SET_CONST(1))
#define AI_SP_SPECTRAL_CENTROID_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_SpectralCentroidDataOut {
    float32_t   centroid;
    float32_t   spread;
    float32_t   skewness;
    float32_t   kurtosis;
} AI_SP_SpectralCentroidDataOut_t;

typedef struct AI_SP_SpectralCentroidIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    int16_t     b1;             /* first bin index to consider */
    int16_t     b2;             /* last bin index to consider */
    uint16_t    out_selection;
    int32_t     sampling_freq;  /* Fe or -1 for a results in bins */
} AI_SP_SpectralCentroidIn_t;

typedef struct AI_SP_SpectralCentroidOut {
    ai_logging_packet_t  packet;
} AI_SP_SpectralCentroidOut_t;


/* Spectral Crest Factor */
#define AI_SP_SPECTRAL_CREST_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                                       AI_SP_FMT_SET_CONST(1))
#define AI_SP_SPECTRAL_CREST_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_SpectralCrestDataOut {
    float32_t   crest;
} AI_SP_SpectralCrestDataOut_t;

typedef struct AI_SP_SpectralCrestIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    int16_t     b1;     /* first bin index to consider */
    int16_t     b2;     /* last bin index to consider */
} AI_SP_SpectralCrestIn_t;

typedef struct AI_SP_SpectralCrestOut {
    ai_logging_packet_t  packet;
} AI_SP_SpectralCrestOut_t;


/* Spectral Entropy */
#define AI_SP_SPECTRAL_ENTROPY_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                                         AI_SP_FMT_SET_CONST(1))
#define AI_SP_SPECTRAL_ENTROPY_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_SpectralEntropyDataOut {
    float32_t   entropy;
} AI_SP_SpectralEntropyDataOut_t;

typedef struct AI_SP_SpectralEntropyIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    int16_t     b1;     /* first bin index to consider */
    int16_t     b2;     /* last bin index to consider */
} AI_SP_SpectralEntropyIn_t;

typedef struct AI_SP_SpectralEntropyOut {
    ai_logging_packet_t  packet;
} AI_SP_SpectralEntropyOut_t;


/* Spectral Peak power and SNR */
#define AI_SP_SPECTRAL_PEAK_FMT_IN   (AI_SP_FMT_FLOAT32_RESET() |   \
                                      AI_SP_FMT_SET_CONST(1))
#define AI_SP_SPECTRAL_PEAK_FMT_OUT  (AI_SP_FMT_FLOAT32_RESET())
typedef struct AI_SP_SpectralPeakDataOut {
    float32_t   peak_power;
    float32_t   peak_freq;
    float32_t   peak_snr;
} AI_SP_SpectralPeakDataOut_t;

typedef struct AI_SP_SpectralPeakIn {
    ai_logging_packet_t  packet;
    uint16_t    mode;
    int16_t     b1;             /* first bin index to consider */
    int16_t     b2;             /* last bin index to consider */
    uint16_t    out_selection;
    int32_t     sampling_freq;  /* Fe or -1 for a results in bins */
} AI_SP_SpectralPeakIn_t;

typedef struct AI_SP_SpectralPeakOut {
    ai_logging_packet_t  packet;
} AI_SP_SpectralPeakOut_t;


/* External variables --------------------------------------------------------*/
/* Exported functions ------------------------------------------------------- */
/**
  * @brief  AI_SP_Stat_Process
  *         Computes statistics of the input
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_Stat_Process(AI_SP_StatIn_t  *pInput,
                           AI_SP_StatOut_t *pOutput);
/**
  * @brief  AI_SP_Stat_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_Stat_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                uint16_t  mode,
                                ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_Mag_Process
  *         Computes Magnitude of the input
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_Mag_Process(AI_SP_MagIn_t  *pInput,
                          AI_SP_MagOut_t *pOutput);
/**
  * @brief  AI_SP_Mag_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_Mag_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                               uint16_t  mode,
                               ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_Rms_Process
  *         Computes RMS of the input
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_Rms_Process(AI_SP_RmsIn_t  *pInput,
                          AI_SP_RmsOut_t *pOutput);
/**
  * @brief  AI_SP_Rms_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_Rms_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                               uint16_t  mode,
                               ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_Skewness_Process
  *         Computes Temporal Skewness of the input
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_Skewness_Process(AI_SP_SkewnessIn_t  *pInput,
                               AI_SP_SkewnessOut_t *pOutput);
/**
  * @brief  AI_SP_Skewness_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_Skewness_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                    uint16_t  mode,
                                    ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_Flatness_Process
  *         Computes Temporal Flatness of the input
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_Flatness_Process(AI_SP_FlatnessIn_t  *pInput,
                               AI_SP_FlatnessOut_t *pOutput);
/**
  * @brief  AI_SP_Flatness_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_Flatness_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                    uint16_t  mode,
                                    ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_Ar3_Process
  *         Computes AR order 3 values of the input
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_Ar3_Process(AI_SP_Ar3In_t  *pInput,
                          AI_SP_Ar3Out_t *pOutput);
/**
  * @brief  AI_SP_Ar3_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_Ar3_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                               uint16_t  mode,
                               ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_Zcr_Process
  *         Computes zero crossing rate of the input
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_Zcr_Process(AI_SP_ZcrIn_t  *pInput,
                          AI_SP_ZcrOut_t *pOutput);
/**
  * @brief  AI_SP_Zcr_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_Zcr_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                               uint16_t  mode,
                               ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_Entropy_Process
  *         Computes the entropy of the input
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_Entropy_Process(AI_SP_EntropyIn_t  *pInput,
                              AI_SP_EntropyOut_t *pOutput);
/**
  * @brief  AI_SP_Entropy_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_Entropy_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                   uint16_t  mode,
                                   ai_logging_packet_t  *pPacketOut);
/**
  * @brief  AI_SP_SpectralFlatness_Process
  *         Computes Spectral Flatness of the spectrum
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_SpectralFlatness_Process(AI_SP_SpectralFlatnessIn_t  *pInput,
                                       AI_SP_SpectralFlatnessOut_t *pOutput);
/**
  * @brief  AI_SP_SpectralFlatness_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_SpectralFlatness_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                            uint16_t  mode,
                                            ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_SpectralCentroid_Process
  *         Computes Spectral Centroid, spread, skewness and kurtosis of the spectrum
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_SpectralCentroid_Process(AI_SP_SpectralCentroidIn_t  *pInput,
                                       AI_SP_SpectralCentroidOut_t *pOutput);
/**
  * @brief  AI_SP_SpectralCentroid_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_SpectralCentroid_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                            uint16_t  mode,
                                            ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_SpectralCrest_Process
  *         Computes crest factor of the spectrum
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_SpectralCrest_Process(AI_SP_SpectralCrestIn_t  *pInput,
                                    AI_SP_SpectralCrestOut_t *pOutput);
/**
  * @brief  AI_SP_SpectralCrest_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_SpectralCrest_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                         uint16_t  mode,
                                         ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_SpectralEntropy_Process
  *         Computes entropy of the spectrum
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_SpectralEntropy_Process(AI_SP_SpectralEntropyIn_t  *pInput,
                                      AI_SP_SpectralEntropyOut_t *pOutput);
/**
  * @brief  AI_SP_SpectralEntropy_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_SpectralEntropy_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                           uint16_t  mode,
                                           ai_logging_packet_t  *pPacketOut);

/**
  * @brief  AI_SP_SpectralPeak_Process
  *         Computes Peak power and freq and SNR around the peak of the spectrum
  * @param  pInput: Pointer to input structure
  * @param  pOuput: Pointer to output structure
  * @retval error value
  */
int32_t AI_SP_SpectralPeak_Process(AI_SP_SpectralPeakIn_t  *pInput,
                                   AI_SP_SpectralPeakOut_t *pOutput);
/**
  * @brief  AI_SP_SpectralPeak_GetOutputDim
  *         Computes output dimensions from chosen mode and input format
  * @param  pPacketIn: pointer to input data packet
  * @param  mode: processing mode
  * @param  pPacketOut: pointer to output data packet
  * @retval error value
  */
int32_t AI_SP_SpectralPeak_GetOutputDim(ai_logging_packet_t  *pPacketIn,
                                        uint16_t  mode,
                                        ai_logging_packet_t  *pPacketOut);


#ifdef __cplusplus
}
#endif

#endif      /* __FEAT_EXTRACT_IF_H__  */


