/**
  ******************************************************************************
  * @file    PreProc_DPU.h
  * @author  STMicroelectronics - AIS - MCD Team
  * @brief
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

#ifndef DPU_INC_PREPROC_DPU_H_
#define DPU_INC_PREPROC_DPU_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "ADPU2.h"
#include "ADPU2_vtbl.h"
#include "user_mel_tables.h"
#include "feature_extraction.h"
#include "config.h"

/**
 * Create  type name for _PreProc_DPU_t.
 */
typedef enum {
  SPECTROGRAM_BYPASS,
  SPECTROGRAM_MEL,
  SPECTROGRAM_LOG_MEL,
  SPECTROGRAM_MFCC
}spectrogram_type_t;

typedef struct _PreProc_DPU PreProc_DPU_t;

/**
 * _PreProc_DPU_t internal state.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _PreProc_DPU {
  /**
   * Base class object.
   */
  ADPU2_t super;

  spectrogram_type_t         type;

  arm_rfft_fast_instance_f32 S_Rfft;
  MelFilterTypeDef           S_MelFilter;
  SpectrogramTypeDef         S_Spectr;
  MelSpectrogramTypeDef      S_MelSpectr;
  LogMelSpectrogramTypeDef   S_LogMelSpectr;
  DCT_InstanceTypeDef        S_DCT;
  MfccTypeDef                S_Mfcc;

  float32_t pSpectrScratchBuffer1[CTRL_X_CUBE_AI_SPECTROGRAM_NFFT];
  float32_t pSpectrScratchBuffer2[CTRL_X_CUBE_AI_SPECTROGRAM_NFFT];

  /**
   * Specifies the quantization parameters of the unique output preprocessing
   */
  float output_Q_inv_scale;
  int   output_Q_offset;
};


/* Public API declaration */
/**************************/

/**
 * Allocate an instance of PreProc_DPU_t in the eLooM framework heap.
 *
 * @return a pointer to the generic object ::IDPU2_t if success,
 * or NULL if out of memory error occurs.
 */
IDPU2_t *PreProc_DPUAlloc(void);

/**
 * Allocate an instance of PreProc_DPU_t in a memory block specified by the application.
 * The size of the memory block must be greater or equal to sizeof(PreProc_DPU_t).
 * This allocator allows the application to avoid the dynamic allocation.
 *
 * \code
 * PreProc_DPU_t dpu;
 * PreProc_DPUStaticAlloc(&dpu);
 * \endcode
 *
 * @param p_mem_block [IN] specify a memory block allocated by the application.
 *        The size of the memory block must be greater or equal to sizeof(PreProc_DPU_t).
 * @return a pointer to the generic object ::IDPU if success,
 * or NULL if out of memory error occurs.
 */
IDPU2_t *PreProc_DPUStaticAlloc(void *p_mem_block);

/**
 * Initialize the DPU. Most of the DPU parameters are constant and defined at the beginning of this header file
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param mfcc_data_input_user [IN] specifies the size of the ... [TBD]
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t PreProc_DPUInit(PreProc_DPU_t *_this, uint16_t mfcc_data_input_user);

/**
 * Partial reset of the DPU internal state: all input and output buffers are re-initialized to prepare
 * the DPU to process a new stream of data.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
sys_error_code_t PreProc_DPUPrepareToProcessData(PreProc_DPU_t *_this);


/* Inline functions definition */
/*******************************/

#ifdef __cplusplus
}
#endif

#endif /* DPU_INC_PREPROC_DPU_H_ */

