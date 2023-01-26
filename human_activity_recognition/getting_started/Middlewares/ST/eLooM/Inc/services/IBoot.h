/**
 ******************************************************************************
 * @file    IBoot.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Nov 21, 2017
 *
 * @brief The Boot interface integrates support for the bootloader into the
 *        framework.
 *
 * This interface is implemented by applications that need to jump to another
 * application during the startup sequence. The typical example is a
 * bootloader. The IBoot interface is used by the system during the startup
 * before the scheduler is running (this means that there is not INIT task
 * yet). The algorithm is displayed in Fig. 16.
 *
 * \anchor fig16 \image html 16_boot_if_1.png "Fig.16 - Boot IF"
 *
 * The system reset all peripherals and it initializes the minimum set of
 * resources (like the clock three). At this point if the SysInit() has been
 * called with the parameter `TRUE` the system uses the SysGetBootIF() in
 * order to obtain a pointer to an application object that implement the
 * ::IBoot interface. Then the system initialize the Boot IF by calling the
 * IBootInit() function. The the system check if the DFU trigger condition -
 * IBootCheckDFUTrigger(). If it it is `FALSE` then the system prepare the
 * jump to the application. First it retrieves the jump address by calling the
 * IBootGetAppAdderss() function. Then it uses the IBootOnJampToApp() in order
 * to perform some other tasks before the jump. Finally the system check if the
 * application address is valid and make the jump.
 *
 * In order to optimize the memory footprint of the framework the ::IBoot
 * interface can be disabled by the linker with the following definition:
 *
 *     #define INIT_TASK_CFG_ENABLE_BOOT_IF  0
 *
 * It can be added in the sysconfig.h file.
 *
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
#ifndef INCLUDE_SERVICES_IBOOT_H_
#define INCLUDE_SERVICES_IBOOT_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "systp.h"
#include "systypes.h"
#include "syserror.h"

/**
 * Create  type name for _IBoot.
 */
typedef struct _IBoot IBoot;


// Public API declaration
//***********************

/**
 * Initialize the interface IBoot. It should be called after the object allocation and before using the object.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IBootInit(IBoot *_this);

/**
 * Check if the DFU condition occurs. If it is TRUE the bootloader enters the DFU mode,
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return TRUE if the system must enter the DFU mode, FALSE otherwise.
 */
static inline boolean_t IBootCheckDFUTrigger(IBoot *_this);

/**
 * Used by the system to retrieve the address of the application to start.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return the address where is located the application to start.
 */
static inline uint32_t IBootGetAppAdderss(IBoot *_this);

/**
 * Called by the system before the jump to the other application. It can be used
 * to perform some operations before the jump and also to stop the system from jump,.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param nAppDress [IN] specifies the address of the application to start.
 * @return SYS_NO_ERROR_CODE if the system can continue with the jump, an application
 * specific error code otherwise.
 */
static inline sys_error_code_t IBootOnJampToApp(IBoot *_this, uint32_t nAppDress);

// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_IBOOT_H_ */
