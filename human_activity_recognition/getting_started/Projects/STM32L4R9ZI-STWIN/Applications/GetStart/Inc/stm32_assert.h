/**
 ******************************************************************************
 * @file    stm32_assert.h
 * @author  MCD Application Team
 * @version V1.7.0
 * @date    31-May-2016
 * @brief   STM32 assert template file.
 *          This file should be copied to the application folder and renamed
 *          to stm32_assert.h.
 *********************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *********************************************************************************
 */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __STM32_ASSERT_H
#define __STM32_ASSERT_H

#ifdef __cplusplus
 extern "C" {
#endif

/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/
/* Includes ------------------------------------------------------------------*/
/* Exported macro ------------------------------------------------------------*/

  void assert_failed(uint8_t* file, uint32_t line);

#ifdef __cplusplus
}
#endif

#endif /* __STM32_ASSERT_H */

