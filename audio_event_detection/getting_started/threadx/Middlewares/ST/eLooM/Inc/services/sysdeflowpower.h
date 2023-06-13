/**
 ******************************************************************************
 * @file    sysdeflowpower.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Oct 31, 2018
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2017 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef INCLUDE_SERVICES_SYSDEFLOWPOWER_H_
#define INCLUDE_SERVICES_SYSDEFLOWPOWER_H_

#if (SYS_CFG_USE_DEFAULT_PM_HELPER==1)

#define SYS_PM_EVT_SRC_SW                   0x1U  ///< Software event.
// Generic event parameters
#define SYS_PM_EVT_PARAM_ENTER_LP           0x1U  ///< Event parameter: enter low power mode command.
#define SYS_PM_EVT_PARAM_EXIT_LP            0x2U  ///< Event parameter: exit low power mode command.

// Inline functions definition
// ***************************


/**
 * Specifies the possible power states of the system.
 */
typedef enum {
  /**
   * The system is active.
   */
  E_POWER_MODE_STATE1 = 0,

  /**
   * The system is running in low power mode: the MCU is STOP mode, the USB bus is suspended,
   * the touch control is active to wake the system up and the Keyboard is configured to generate
   * an IRQ in order to wake the system up.
   */
  E_POWER_MODE_SLEEP_1 = 1,
}EPowerMode;

/**
 * Specifies some information about the current power mode of the system.
 */
typedef struct _SysPowerStatus {
  /**
   * Specifies the current power mode of the system. An application task can read this value.
   */
  EPowerMode m_eActivePowerMode;
}SysPowerStatus;


#endif



#endif /* INCLUDE_SERVICES_SYSDEFLOWPOWER_H_ */
