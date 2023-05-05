/**
  ******************************************************************************
  * @file    PreProc_DPU.c
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

#include "PreProc_DPU.h"
#include "PreProc_DPU_vtbl.h"
#include "user_mel_tables.h"
#include "ai_platform.h"
#include "services/sysmem.h"
#include "services/sysdebug.h"
#include "services/SysTimestamp.h"
#include <stdio.h>
//#define MFCC_GEN_LUT

#define SYS_DEBUGF(level, message)      SYS_DEBUGF3(SYS_DBG_PRE_PROC, level, message)

/**
 * Class object declaration.
 */
typedef struct _PreProc_DPUClass
{
  /**
   * IDPU2_t class virtual table.
   */
  IDPU2_vtbl vtbl;

} PreProc_DPUClass_t;


/* Objects instance */
/********************/

/**
 * The class object.
 */
static const PreProc_DPUClass_t sTheClass = {
    /* class virtual table */
    {
        ADPU2_vtblAttachToDataSource,
        ADPU2_vtblDetachFromDataSource,
        ADPU2_vtblAttachToDPU,
        ADPU2_vtblDetachFromDPU,
        ADPU2_vtblDispatchEvents,
        ADPU2_vtblRegisterNotifyCallback,
        PreProc_DPU_vtblProcess
    }
};


/* Private member functions declaration */
/****************************************/

#ifdef MFCC_GEN_LUT
#define NUM_MEL      CTRL_X_CUBE_AI_SPECTROGRAM_NMEL
#define NUM_MEL_COEF 462
#define NUM_MFCC     32
#define FFT_LEN      CTRL_X_CUBE_AI_SPECTROGRAM_NFFT
#define SMP_RATE     CTRL_X_CUBE_AI_SENSOR_ODR

float32_t Win [FFT_LEN];
uint32_t  start_indices[NUM_MEL];
uint32_t  stop_indices [NUM_MEL];
float32_t melFilterLut [NUM_MEL_COEF];
float32_t dct[NUM_MEL*NUM_MFCC];
static void genLUT(void)
{

  MelFilterTypeDef           S_MelFilter;
  DCT_InstanceTypeDef        S_DCT;
  int i;

  /* Init window function */
  if (Window_Init(Win, FFT_LEN , WINDOW_HANN) != 0){
  while(1);
  }
  printf("Hanning window: %d \n\r",FFT_LEN);
  for (i=0;i<FFT_LEN;i++) {
  printf("%.10e,",Win[i]);
  if(!((i+1)%8)) printf("\r\n");
  }

  S_MelFilter.pStartIndices = &start_indices[0];
  S_MelFilter.pStopIndices  = &stop_indices[0];
  S_MelFilter.pCoefficients = &melFilterLut[0];
  S_MelFilter.NumMels       = NUM_MEL;
  S_MelFilter.FFTLen        = FFT_LEN;
  S_MelFilter.SampRate      = SMP_RATE;
  S_MelFilter.FMin          = CTRL_X_CUBE_AI_SPECTROGRAM_FMIN;
  S_MelFilter.FMax          = CTRL_X_CUBE_AI_SPECTROGRAM_FMAX;
  S_MelFilter.Formula       = CTRL_X_CUBE_AI_SPECTROGRAM_FORMULA;
  S_MelFilter.Normalize     = CTRL_X_CUBE_AI_SPECTROGRAM_NORMALIZE;
  S_MelFilter.Mel2F         = 1;

  MelFilterbank_Init(&S_MelFilter);
  if (S_MelFilter.CoefficientsLength != NUM_MEL_COEF){
  while(1); /* Adjust NUM_MEL_COEFS to match S_MelFilter.CoefficientsLength */
  }
  printf("Mel coefs : \r\n");
  for (i=0;i<NUM_MEL_COEF;i++)
  {
    printf("%.10e,",melFilterLut[i]);
    if(!((i+1)%8)) printf("\r\n");
  }
  printf("\nstart idx : \r\n");
  for (i=0;i<NUM_MEL;i++)
  {
    printf("%4lu,",start_indices[i]);
    if(!((i+1)%8)) printf("\r\n");
  }
  printf("stop  idx : \r\n");
  for (i=0;i<NUM_MEL;i++)
  {
    printf("%4lu,",stop_indices[i]);
    if(!((i+1)%8)) printf("\r\n");
  }
  printf("\r\n DCT table \r\n");

  S_DCT.NumFilters      = NUM_MFCC;
  S_DCT.NumInputs       = NUM_MEL;
  S_DCT.Type            = DCT_TYPE_II_ORTHO;
  S_DCT.RemoveDCTZero   = 0;
  S_DCT.pDCTCoefs       = dct;
  if (DCT_Init(&S_DCT) != 0)
  {
  while(1);
  }
  for (i=0;i<NUM_MEL * NUM_MFCC;i++)
  {
    printf("%.10e,",dct[i]);
    if(!((i+1)%8)) printf("\r\n");
  }
  printf("\r\n");
}
#endif


/* Public API functions definition */
/***********************************/

IDPU2_t *PreProc_DPUAlloc() {
  IDPU2_t *p_obj = (IDPU2_t*) SysAlloc(sizeof(PreProc_DPU_t));

  if (p_obj != NULL)
  {
    p_obj->vptr = &sTheClass.vtbl;
  }

  return p_obj;
}

IDPU2_t *PreProc_DPUStaticAlloc(void *p_mem_block)
{
  IDPU2_t *p_obj = (IDPU2_t*)p_mem_block;
  if (p_obj != NULL)
  {
    p_obj->vptr = &sTheClass.vtbl;
  }

  return p_obj;
}

sys_error_code_t PreProc_DPUInit(PreProc_DPU_t *_this, uint16_t data_input_user)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  uint32_t pad;

  assert_param(CTRL_X_CUBE_AI_SPECTROGRAM_NFFT >= CTRL_X_CUBE_AI_SPECTROGRAM_WINDOW_LENGTH );
  assert_param(CTRL_X_CUBE_AI_SPECTROGRAM_NFFT >= CTRL_X_CUBE_AI_SPECTROGRAM_NMEL);

  /*initialize the base class*/
  EMData_t in_data, out_data;

  _this->output_Q_inv_scale = 0.0F;
  _this->output_Q_offset    = 0;

  res = EMD_1dInit(&in_data, NULL, /*E_EM_FLOAT*/ E_EM_INT16, data_input_user);
  if (SYS_IS_ERROR_CODE(res))
  {
    sys_error_handler();
  }
  res = EMD_Init(&out_data, NULL, E_EM_INT8, E_EM_MODE_LINEAR, 2U,\
       CTRL_X_CUBE_AI_SPECTROGRAM_COL,CTRL_X_CUBE_AI_SPECTROGRAM_NMEL);
  if (SYS_IS_ERROR_CODE(res))
  {
    sys_error_handler();
  }
  res = ADPU2_Init((ADPU2_t*)_this, in_data, out_data);
  if (SYS_IS_ERROR_CODE(res))
  {
    sys_error_handler();
  }

  // take the ownership of the Sensor Event IF
  (void)IEventListenerSetOwner((IEventListener *) ADPU2_GetEventListenerIF(&_this->super), &_this->super);

  /*initialize AI preprocessing (MFCC computation)*/
#ifdef MFCC_GEN_LUT
  genLUT();
#endif

  /* Init RFFT */
  arm_rfft_fast_init_f32(&_this->S_Rfft, CTRL_X_CUBE_AI_SPECTROGRAM_NFFT);

  /* Init Spectrogram */
  _this->S_Spectr.pRfft                    = &_this->S_Rfft;
  _this->S_Spectr.Type                     = CTRL_X_CUBE_AI_SPECTROGRAM_TYPE;
  _this->S_Spectr.pWindow                  = (float32_t *) CTRL_X_CUBE_AI_SPECTROGRAM_WIN;
  _this->S_Spectr.SampRate                 = CTRL_X_CUBE_AI_SENSOR_ODR;
  _this->S_Spectr.FrameLen                 = CTRL_X_CUBE_AI_SPECTROGRAM_WINDOW_LENGTH;
  _this->S_Spectr.FFTLen                   = CTRL_X_CUBE_AI_SPECTROGRAM_NFFT;
  _this->S_Spectr.pScratch1                = _this->pSpectrScratchBuffer1;
  _this->S_Spectr.pScratch2                = _this->pSpectrScratchBuffer2;

  pad                                      = CTRL_X_CUBE_AI_SPECTROGRAM_NFFT - CTRL_X_CUBE_AI_SPECTROGRAM_WINDOW_LENGTH;
  _this->S_Spectr.pad_left                 = pad/2;
  _this->S_Spectr.pad_right                = pad/2 + (pad & 1);

  /* Init mel filterbank */
  _this->S_MelFilter.pStartIndices         = (uint32_t *)  CTRL_X_CUBE_AI_SPECTROGRAM_MEL_START_IDX;
  _this->S_MelFilter.pStopIndices          = (uint32_t *)  CTRL_X_CUBE_AI_SPECTROGRAM_MEL_STOP_IDX;
  _this->S_MelFilter.pCoefficients         = (float32_t *) CTRL_X_CUBE_AI_SPECTROGRAM_MEL_LUT;
  _this->S_MelFilter.NumMels               = CTRL_X_CUBE_AI_SPECTROGRAM_NMEL;
  _this->S_MelFilter.FFTLen                = CTRL_X_CUBE_AI_SPECTROGRAM_NFFT;
  _this->S_MelFilter.SampRate              = (uint32_t) CTRL_X_CUBE_AI_SENSOR_ODR;
  _this->S_MelFilter.FMin                  = (float32_t) CTRL_X_CUBE_AI_SPECTROGRAM_FMIN;
  _this->S_MelFilter.FMax                  = (float32_t) CTRL_X_CUBE_AI_SPECTROGRAM_FMAX;
  _this->S_MelFilter.Formula               = CTRL_X_CUBE_AI_SPECTROGRAM_FORMULA;
  _this->S_MelFilter.Normalize             = CTRL_X_CUBE_AI_SPECTROGRAM_NORMALIZE;
  _this->S_MelFilter.Mel2F                 = 1U;

  /* Init MelSpectrogram */
  _this->S_MelSpectr.SpectrogramConf       = &_this->S_Spectr;
  _this->S_MelSpectr.MelFilter             = &_this->S_MelFilter;

  /* Init LogMelSpectrogram */
  _this->S_LogMelSpectr.MelSpectrogramConf = &_this->S_MelSpectr;
  _this->S_LogMelSpectr.LogFormula         = CTRL_X_CUBE_AI_SPECTROGRAM_LOG_FORMULA;
  _this->S_LogMelSpectr.Ref                = 1.0f;
  _this->S_LogMelSpectr.TopdB              = HUGE_VALF;

  return res;
}

sys_error_code_t PreProc_DPUPrepareToProcessData(PreProc_DPU_t *_this)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  ADPU2_Reset((ADPU2_t*)_this);

  return res;
}

/* IDPU2 virtual functions definition */
/**************************************/

sys_error_code_t PreProc_DPU_vtblProcess(IDPU2_t *_this, EMData_t in_data, EMData_t out_data)
{
  assert_param(_this != NULL);
  sys_error_code_t res = SYS_NO_ERROR_CODE;
  PreProc_DPU_t *p_obj = (PreProc_DPU_t*)_this;

  int16_t *p_in;
  int8_t  out[CTRL_X_CUBE_AI_SPECTROGRAM_NMEL];
  int8_t *p_spectro = (int8_t *)EMD_Data(&out_data);

  assert_param (p_obj->type == SPECTROGRAM_LOG_MEL);
  assert_param (p_obj->S_MelFilter.NumMels == CTRL_X_CUBE_AI_SPECTROGRAM_NMEL);

  /* Create a quantized Mel-scaled spectrogram column */
  for (int i = 0; i < CTRL_X_CUBE_AI_SPECTROGRAM_COL; i++ )
  {
    p_in = (int16_t *)EMD_Data(&in_data)+CTRL_X_CUBE_AI_SPECTROGRAM_HOP_LENGTH*i;
    LogMelSpectrogramColumn_q15_Q8(&p_obj->S_LogMelSpectr, p_in,out,p_obj->output_Q_offset,p_obj->output_Q_inv_scale);
    /* transpose */
    for (int j=0 ; j < p_obj->S_MelFilter.NumMels ; j++ ){
      p_spectro[i+CTRL_X_CUBE_AI_SPECTROGRAM_COL*j]= out[j];
    }
  }
  return res;
}
