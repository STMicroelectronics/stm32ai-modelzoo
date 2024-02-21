/**
******************************************************************************
* @file    user_mel_tables.h
* @author  MCD Application Team
* @brief   Header for mel_user_tables.c module******************************************************************************
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
#ifndef _MEL_USER_TABLES_H
#define _MEL_USER_TABLES_H
#include "arm_math.h"
extern const float32_t userWin[400];
extern const uint32_t  user_melFiltersStartIndices[64];
extern const uint32_t  user_melFiltersStopIndices[64];
extern const float32_t user_melFilterLut[461];

#endif /* _MEL_USER_TABLES_H */
