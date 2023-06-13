/**
 ******************************************************************************
 * @file    aiTestHelper.h
 * @author  MCD/AIS Team
 * @brief   STM32 Helper functions for STM32 AI test application
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; Copyright (c) 2019,2021 STMicroelectronics.
 * All rights reserved.</center></h2>
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

#ifndef __AI_TEST_HELPER_H__
#define __AI_TEST_HELPER_H__

#include <stdint.h>

#if !defined(TFLM_RUNTIME)

#include <ai_platform.h>


#ifdef __cplusplus
extern "C" {
#endif


void aiPlatformVersion(void);

ai_u32 aiBufferSize(const ai_buffer* buffer);
void aiLogErr(const ai_error err, const char *fct);
void aiPrintNetworkInfo(const ai_network_report* report);
void aiPrintBufferInfo(const ai_buffer *buffer);

#ifdef __cplusplus
}
#endif

#endif /* !TFLM_RUNTIME */

#endif /* __AI_TEST_HELPER_H__ */
