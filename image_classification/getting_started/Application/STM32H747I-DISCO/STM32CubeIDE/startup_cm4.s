/**
  ******************************************************************************
  * @file      startup_cm4.s
  * @author    MCD Application Team
  * @brief     STM32H747xx Devices: Cortex-M4 vector table for GCC based toolchain. 
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under Apache License, Version 2.0,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/Apache-2.0
  *
  ******************************************************************************
  * This module performs:
  * - Set the initial SP
  * - Set the initial PC == Reset_Handler_m4,
  * - Reset_Handler consists in an infinite loop so to boot CM4 core properly 
  * and keep it in a known state.
  *
  */
    


.global  g_pfnVectors_m4

/**
 * @brief  This is the code that gets called when the CM4 processor first
 *         starts execution following a reset event. The CM4 stays in an 
 *         infinite loop.
 * @param  None
 * @retval : None
*/

    .section  .text.Reset_Handler_m4
  .weak  Reset_Handler_m4
  .type  Reset_Handler_m4, %function
Reset_Handler_m4:
 Infinite_Loop:
  b  Infinite_Loop

.size  Reset_Handler_m4, .-Reset_Handler_m4


/******************************************************************************
*
* The minimal vector table for a Cortex M. Note that the proper constructs
* must be placed on this to ensure that it ends up at physical address
* 0x0000.0000.
* 
*******************************************************************************/
   .section  .isr_vector_m4,"a",%progbits
  .type  g_pfnVectors_m4, %object
  .size  g_pfnVectors_m4, .-g_pfnVectors_m4
   
   
g_pfnVectors_m4:
  .word  _estack
  .word  Reset_Handler_m4

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/        
 
