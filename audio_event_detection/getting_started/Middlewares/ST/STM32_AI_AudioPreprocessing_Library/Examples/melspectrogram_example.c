/**
 ******************************************************************************
 * @file    melspectrogram_example.c
 * @author  MCD Application Team
 * @brief   Melspectrogram computation example
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
#include "feature_extraction.h"

/*
 * y = librosa.load('bus.wav', sr=None, duration=1)[0] # Keep native 16kHz sampling rate
 * librosa.feature.melspectrogram(y, sr=16000, n_mels=30, n_fft=1024, hop_length=512, center=False)
 */

#define SAMPLE_RATE  16000U /* Input signal sampling rate */
#define FFT_LEN       1024U /* Number of FFT points. Must be greater or equal to FRAME_LEN */
#define FRAME_LEN   FFT_LEN /* Window length and then padded with zeros to match FFT_LEN */
#define HOP_LEN        512U /* Number of overlapping samples between successive frames */
#define NUM_MELS        30U /* Number of mel bands */
#define NUM_MEL_COEFS  968U /* Number of mel filter weights. Returned by MelFilterbank_Init */

arm_rfft_fast_instance_f32 S_Rfft;
MelFilterTypeDef           S_MelFilter;
SpectrogramTypeDef         S_Spectr;
MelSpectrogramTypeDef      S_MelSpectr;
LogMelSpectrogramTypeDef   S_LogMelSpectr;

float32_t pInFrame[FRAME_LEN];
float32_t pOutColBuffer[NUM_MELS];
float32_t pWindowFuncBuffer[FRAME_LEN];
float32_t pSpectrScratchBuffer[FFT_LEN];
float32_t pMelFilterCoefs[NUM_MEL_COEFS];
uint32_t pMelFilterStartIndices[NUM_MELS];
uint32_t pMelFilterStopIndices[NUM_MELS];

void Preprocessing_Init(void)
{
  /* Init window function */
  if (Window_Init(pWindowFuncBuffer, FRAME_LEN, WINDOW_HANN) != 0)
  {
    while(1);
  }

  /* Init RFFT */
  arm_rfft_fast_init_f32(&S_Rfft, FFT_LEN);

  /* Init Spectrogram */
  S_Spectr.pRfft    = &S_Rfft;
  S_Spectr.Type     = SPECTRUM_TYPE_POWER;
  S_Spectr.pWindow  = pWindowFuncBuffer;
  S_Spectr.SampRate = SAMPLE_RATE;
  S_Spectr.FrameLen = FRAME_LEN;
  S_Spectr.FFTLen   = FFT_LEN;
  S_Spectr.pScratch = pSpectrScratchBuffer;

  /* Init Mel filter */
  S_MelFilter.pStartIndices = pMelFilterStartIndices;
  S_MelFilter.pStopIndices  = pMelFilterStopIndices;
  S_MelFilter.pCoefficients = pMelFilterCoefs;
  S_MelFilter.NumMels   = NUM_MELS;
  S_MelFilter.FFTLen    = FFT_LEN;
  S_MelFilter.SampRate  = SAMPLE_RATE;
  S_MelFilter.FMin      = 0.0;
  S_MelFilter.FMax      = S_MelFilter.SampRate / 2.0;
  S_MelFilter.Formula   = MEL_SLANEY;
  S_MelFilter.Normalize = 1;
  S_MelFilter.Mel2F     = 1;
  MelFilterbank_Init(&S_MelFilter);

  /* Init MelSpectrogram */
  S_MelSpectr.SpectrogramConf = &S_Spectr;
  S_MelSpectr.MelFilter       = &S_MelFilter;
}

void AudioPreprocessing_Run(int16_t *pInSignal, float32_t *pOut, uint32_t signal_len)
{
  const uint32_t num_frames = 1 + (signal_len - FRAME_LEN) / HOP_LEN;

  for (uint32_t frame_index = 0; frame_index < num_frames; frame_index++)
  {
    buf_to_float_normed(&pInSignal[HOP_LEN * frame_index], pInFrame, FRAME_LEN);
    MelSpectrogramColumn(&S_MelSpectr, pInFrame, pOutColBuffer);
    /* Reshape column into pOut */
    for (uint32_t i = 0; i < NUM_MELS; i++)
    {
      pOut[i * num_frames + frame_index] = pOutColBuffer[i];
    }
  }
}
