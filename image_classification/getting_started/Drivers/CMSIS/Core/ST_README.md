# cmsis_core

## Overview

The **cmsis_core** repo is delivered to STM32 users. This is a project cloned from ARM Limited, strictly compatible. 

**STM32Cube** is an STMicroelectronics original initiative to ease the developers life by reducing efforts, time and cost.

**STM32Cube** covers the overall STM32 products portfolio. It includes a comprehensive embedded software platform, delivered for each STM32 series.
   * The CMSIS modules (core and device) corresponding to the ARM(tm) core implemented in this STM32 product
   * The STM32 HAL-LL drivers : an abstraction drivers layer, the API ensuring maximized portability across the STM32 portfolio 
   * The BSP Drivers of each evaluation or demonstration board provided by this STM32 series 
   * A consistent set of middlewares components such as RTOS, USB, FatFS, Graphics, STM32_TouchSensing_Library ...
   * A full set of software projects (basic examples, applications or demonstrations) for each board provided by this STM32 series

Two models of publication are proposed for the STM32Cube embedded software : 
   * The monolithic **MCU Package** : all STM32Cube software modules of one STM32 series are present (Drivers, Middlewares, Projects, Utilities) in the repo (usual name **STM32Cubexx**, xx corresponding to the STM32 series)
   * The **MCU component** : progressively from November 2019, each STM32Cube software module being part of the STM32Cube MCU Package, will be delivered as an individual repo, allowing the user to select and get only the required software functions. The **cmsis_core** repo is one of these components.

## Description
   
This **cmsis_core** MCU component repo is one element of the STM32Cube MCUs embedded software packages, providing the **cmsis core** part. 

During the successive deliveries from ARM Limited, an update has been introduced with the version 5.0. A break of directory tree compatibility has been introduced : the files under the Include directory have been transfered as Core/Include directory.
In order to keep compatibility, the **cmsis_core** repos provided by STMicroelectronics introduce an Include directory at the root of the module and copy the content of the Core/Include provided by ARM.

From the version 5.1.0, a Core_A/Include has been introduced to support Cortex_A series. However, this has no impact on Cortex-M-based user applications.

With each official Tag (e.g. v4.5), STMicroelectronics proposes specific CMSIS Core packages for all supported Cortex-M cores. These specific packages are size-optimized as each one contains only the CMSIS Core files for the targeted Cortex-M. Each specific package is identified by a tag suffixed _cmX (e.g. tag v4.5_cm3 refers to a package containing only version 4.5.0 of CMSIS Core files specific to Cortex-M3 cores, files specific to other Cortex-M cores having been removed).

### Caution 
It is mandatory to select one Tag version of the **cmsis_core**, never select the default master branch in your projects.

## Compatibility information

In this table, you can find the successive versions of STMicroelectronics **cmsis_core* versions  

CMSIS core ARM  | CMSIS Core ST | contains also specific Cortex_M Tags 
--------------- | ------------- | ------------------------------------
Tag v4.5.0 | Tag v4.5   | v4.5_cm0, v4.5_cm3, v4.5_cm4, v4.5_cm7
Tag v5.4.0 | Tag v5.4.0 | v5.4.0_cm0, v5.4.0_cm3, v5.4.0_cm4, v5.4.0_cm7, v5.4.0_cm33
Tag v5.6.0 | Tag v5.6.0 | v5.6.0_cm0, v5.6.0_cm4, v5.6.0_cm7, v5.6.0_cm33

## Troubleshooting
If you have any issue with the **Software content** of the **cmsis_core** repo, you shall address it directly to Arm (tm) by [filing an issue on Github](https://github.com/ARM-software/CMSIS_5/issues/new)
