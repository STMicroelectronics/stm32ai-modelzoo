/**
 ******************************************************************************
 * @file    common_tables.h
 * @author  MCD Application Team
 * @brief   Header for common_tables.c module
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
#ifndef _COMMON_TABLES_H
#define _COMMON_TABLES_H

#include "arm_math.h"

extern const float32_t hannWin_1024[1024];
extern const float32_t hannWin_2048[2048];
extern const float32_t hammingWin_1024[1024];
extern const float32_t blackmanWin_1024[1024];

extern const uint32_t  melFiltersStartIndices_1024_30[30];
extern const uint32_t  melFiltersStopIndices_1024_30[30];
extern const float32_t melFilterLut_1024_30[968];

extern const uint32_t  melFiltersStartIndices_2048_128[128];
extern const uint32_t  melFiltersStopIndices_2048_128[128];
extern const float32_t melFilterLut_2048_128[2020];

#endif /* _COMMON_TABLES_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
