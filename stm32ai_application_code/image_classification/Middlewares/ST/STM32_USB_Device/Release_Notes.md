---
pagetitle: Release Notes for STM32Cube USB Device Library
lang: en
header-includes: <link rel="icon" type="image/x-icon" href="_htmresc/favicon.png" />
---

::: {.row}
::: {.col-sm-12 .col-lg-4}

<center>
# Release Notes for <mark>STM32Cube USB Device Library</mark>
Copyright &copy; 2015 STMicroelectronics\

[![ST logo](_htmresc/st_logo_2020.png)](https://www.st.com){.logo}
</center>

# Purpose

The USB device library comes on top of the STM32Cube™ USB device HAL driver and
offers all the APIs required to develop an USB device application.

The main USB device library features are:

 - Support of multi packet transfer features allowing sending big amount of data without
   splitting it into max packet size transfers.
 - Support of most common USB Class drivers (HID, MSC, DFU, CDC-ACM, CDC-ECM, RNDIS, MTP, AUDIO1.0, Printer, Video, Composite)
 - Configuration files to interface with Cube HAL and change the library configuration without changing
   the library code (Read Only).
 - 32-bits aligned data structures to handle DMA based transfer in High speed modes.

Here is the list of references to user documents:

-   [UM1734](https://www.st.com/resource/en/user_manual/DM00108129.pdf) : STM32Cube USB device library User Manual
-   [Wiki Page](https://wiki.st.com/stm32mcu/wiki/USB_overview) : STM32Cube USB Wiki Page

:::

::: {.col-sm-12 .col-lg-8}
# Update History
::: {.collapse}
<input type="checkbox" id="collapse-section23" checked aria-hidden="true">
<label for="collapse-section23" aria-hidden="true">V2.11.1 / 27-September-2022</label>
<div>

## Main Changes

 Headline
 ---------
 Improvement of the memory management
 **USB Core:**
 Fix some compilation warnings related to unused parameters
 Improve some code parts style
 Add check on the USB Device status in USBD_LL_Suspend before suspending it
 **USB CDC-ACM Class:**
 Remove redundant prototype declaration of USBD_CDC_GetOtherSpeedCfgDesc()
 **USB CompositeBuilder, CCID, CDC_ECM, CDC_RNDIS, CustomHID, MSC & Video Classes:**
 Improve some code parts style

</div>
:::

::: {.col-sm-12 .col-lg-8}
# Update History
::: {.collapse}
<input type="checkbox" id="collapse-section22" checked aria-hidden="true">
<label for="collapse-section22" aria-hidden="true">V2.11.0 / 25-March-2022</label>
<div>

## Main Changes

 Headline
 ---------
 **USB VIDEO Class:**
 Correction of the support of VS_PROBE_CONTROL & VS_COMMIT_CONTROL requets
 **USB AUDIO Class:**
 Correction of the check on AUDIO_TOTAL_BUF_SIZE to avoid vulnerabilities
 **USB HID Class:**
 Modification of some constants names to avoid duplication versus USB host library
 **USB CustomHID Class:**
 Add support of Get Report control request
 Allow disabling EP OUT prepare receive using a dedicated macros that can be defined in usbd_conf.h application file
 Add support of Report Descriptor with length greater than 255 bytes
 **USB CCID Class:**
 Fix minor Code Spelling warning
 **USB All Classes:**
 Update all classes to support composite multi-instance using the class id parameter
 Fix code spelling and improve code style
 fix misraC 2012 rule 10.3


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section21" checked aria-hidden="true">
<label for="collapse-section21" aria-hidden="true">V2.10.0 / 03-Sept-2021</label>
<div>

## Main Changes

 Headline
 ---------
 **Integration of  new USB device Class driver:**
 Adding support of Composite devices with an auto generation of composite device configuration descriptors
 **USB All Classes:**
 Fix Code Spelling and improve Code Style
 Update device class drivers to support Composite devices
 Improve declaration of USB configuration descriptor table which is allocated if the composite builder is not selected


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section20" checked aria-hidden="true">
<label for="collapse-section20" aria-hidden="true">V2.9.0 / 06-July-2021</label>
<div>

## Main Changes

 Headline
 ---------
 **Integration of  new USB device Class driver:**
 USB CCID Class driver based on Universal Serial Bus Device Class Definition for Integrated Circuit(s) Cards Interface Devices Revision 1.1
 USB MTP Class driver based on Universal Serial Bus Device Class Media Transfer Protocol Revision 1.1
 **USB All Classes:**
 Fix Code Spelling and improve Code Style
 Update the way to declare licenses
 **USB CDC/RNDIS/ECM Classes:**
 Fix compilation warning with C++ due to missing casting during class handler allocation


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section19" checked aria-hidden="true">
<label for="collapse-section19" aria-hidden="true">V2.8.0 / 10-Mars-2021</label>
<div>

## Main Changes

 Headline
 ---------
 **Integration of  new USB device Class driver:**
 USB Printer Class driver based on Universal Serial Bus Device Class Definition for Printing Devices Version 1.1
 **USB All Classes:**
 Fix USB buffer overflow vulnerability for CDC, CDC-ECM, CDC-RNDIS, DFU, AUDIO, CustomHID, and Video Classes
 Fix compilation warning with C++ due to missing casting during class handler allocation
 Enhance comments of USB configuration descriptors fields
 **USB Video Class:**
 Fix missing closing bracket for extern "C" in usbd_video.h
 Fix USBCV test with Uncompressed video format support


</div>
:::


::: {.collapse}
<input type="checkbox" id="collapse-section17" checked aria-hidden="true">
<label for="collapse-section17" aria-hidden="true">V2.7.1 / 18-August-2020</label>
<div>

## Main Changes

 Headline
 ---------
 USB All Class: Add NULL pointer access check to Class handler


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section16" checked aria-hidden="true">
<label for="collapse-section16" aria-hidden="true">V2.7.0 / 12-August-2020</label>
<div>

## Main Changes

 Headline
 ---------
 **Integration of  new USB device Class driver:**
 USB video Class driver based on USB-IF video class definition version 1.1
 **USB Core:**
 Enhance NULL pointer check in Core APIs
 Allow supporting both USER and USER Class string desc
 Add support of USB controller which handles packet-size splitting by hardware
 Avoid compilation warning due macro redefinition
 change added to USBD_HandleTypeDef structure: dev_state, old_dev_state and ep0_state declaration become volatile to disable compiler optimization
 Word spelling correction and file indentation improved
 usbd_conf.h/c Template file updated to suggest using by default a static memory allocation for Class handler
 **USB All Classes:**
 Word spelling correction and file indentation improved
 Allow updating device config descriptor Max power from user code usbd_conf.h using USBD_MAX_POWER define
 Fix device config descriptor bmAttributes value which depends on user code define USBD_SELF_POWERED
 **USB CDC Class:**
 Class specific request, add protection to limit the maximum data length to be sent by the CDC device
 **USB CustomHID Class:**
 Allow changing CustomHID data EP size from user code


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section15" checked aria-hidden="true">
<label for="collapse-section15" aria-hidden="true">V2.6.1 / 05-June-2020</label>
<div>

## Main Changes

 Headline
 ---------
 Fix minor misra-c 2012 violations
 **USB Core:**
 minor rework on USBD_Init() USBD_DeInit()
 Fix warning issue with Keil due to missing return value of setup API
 **USB CDC Class:**
 Fix file indentation
 Avoid accessing to NULL pointer in case TransmitCplt() user fops is not defined to allow application compatibility with device library version below v2.6.0

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section14" checked aria-hidden="true">
<label for="collapse-section14" aria-hidden="true">V2.6.0 / 27-December-2019</label>
<div>

## Main Changes

 Headline
 ---------
 Integration of three new USB device Class drivers:CDC ECM , CDC RNDIS Microsoft, USB Billboard
 Fix mandatory misra-c 2012 violations
 update user core and class template files
 **USB Core:**
 Fix unexpected EP0 stall during enumeration phase
 Improve APIs error management and prevent accessing NULL pointers
 **USB MSC Class:**
 Fix USBCV specific class tests
 Fix multiple error with SCSI commands handling
 Protect medium access when host ask for medium ejection
 **USB CDC Class:**
 Add new function to inform user that current IN transfer is completed
 update transmit and receive APIs to transfer up to 64KB
 **USB AUDIO Class:**
 Fix audio sync start buffer size
 update user callback periodicTC args by adding pointer to user buffer and size
 **USB CustomHID Class:**
 Rework the OUT transfer complete and prevent automatically re-enabling the OUT EP
 Add new user API to restart the OUT transfer: USBD_CUSTOM_HID_ReceivePacket()


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section13" checked aria-hidden="true">
<label for="collapse-section13" aria-hidden="true">V2.5.3 / 30-April-2019</label>
<div>

## Main Changes

 Headline
 ---------
 Fix misra-c 2012 high severity violations
 **Core driver:**
 protect shared macros __ALIGN_BEGIN, __ALIGN_END with C directive #ifndef
 update Core driver and DFU Class driver to use USBD_SUPPORT_USER_STRING_DESC instead of  USBD_SUPPORT_USER_STRING
 prevent accessing to NULL pointer if the get descriptor functions are not defined
 Update on USBD_LL_Resume(),  restore the device state only if the current state is USBD_STATE_SUSPENDED


</div>
:::


::: {.collapse}
<input type="checkbox" id="collapse-section12" checked aria-hidden="true">
<label for="collapse-section12" aria-hidden="true">V2.5.2 / 27-Mars-2019</label>
<div>

## Main Changes

 Headline
 ---------
 DFU Class: fix compilation warning due to unreachable instruction code introduced with CMSIS V5.4.0 NVIC_SystemReset() prototype change


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section11" checked aria-hidden="true">
<label for="collapse-section11" aria-hidden="true">V2.5.1 / 03-August-2018</label>
<div>

## Main Changes

 Headline
 ---------
 Update license section by adding path to get copy of ST Ultimate Liberty license
 Core: Fix unexpected stall during status OUT phase
 DFU Class: rework hdfu struct to prevent unaligned addresses
 MSC Class: fix lba address overflow during large file transfers greater than 4Go
 Template Class: add missing Switch case Break on USBD_Template_Setup API

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section10" checked aria-hidden="true">
<label for="collapse-section10" aria-hidden="true">V2.5.0 / 15-December-2017</label>
<div>

## Main Changes

 Headline
 ---------
 Update license section
 Update some functions to be MISRAC 2004 compliant
 Add HS and OtherSpeed configuration descriptor for HID and CustomHID classes
 Correct error handling in all class setup function
 Add usbd_desc_template.c/ usbd_desc_template.h templates files
 Add support of class and vendor request
 CDC Class: fix zero-length packet issue in bulk IN transfer
 Fix compilation warning with unused arguments for some functions
 Improve USB Core enumeration state machine


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section9" checked aria-hidden="true">
<label for="collapse-section9" aria-hidden="true">V2.4.2 / 11-December-2015</label>
<div>

## Main Changes

 Headline
 ---------
 **CDC Class**
 usbd_cdc.c: change #include "USBD_CDC.h" by #include "usbd_cdc.h"


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section8" checked aria-hidden="true">
<label for="collapse-section8" aria-hidden="true">V2.4.1 / 19-June-2015</label>
<div>

## Main Changes

 Headline
 ---------
 **CDC Class**
 usbd_cdc.c: comments update
 **MSC Class**
 usbd_msc_bot.h: update to be C++ compliant
 **AUDIO Class**
 usbd_audio.c: fix issue when Host sends GetInterface command it gets a wrong value
 usbd_audio.c: remove useless management of DMA half transfer


</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section7" checked aria-hidden="true">
<label for="collapse-section7" aria-hidden="true">V2.4.0 / 28-February-2015</label>
<div>

## Main Changes

 Headline
 ---------
 **Core Driver**
 Add support of Link Power Management (LPM): add new API GetBOSDescriptor(), that is used only if USBD_LPM_ENABLED switch is enabled in usbd_conf.h file
 usbd_core.c: Fix bug of unsupported premature Host Out stage during data In stage (ie. when endpoint 0 maximum data size is 8 and Host requests GetDeviceDescriptor for the first time)
 usbd_ctlreq.c: Fix bug of unsupported Endpoint Class requests (ie. Audio SetCurrent request for endpoint sampling rate setting)
 **HID Class**
 Updating Polling time API USBD_HID_GetPollingInterval() to query this period for HS and FS
 usbd_hid.c: Fix USBD_LL_CloseEP() function call in USBD_HID_DeInit() replacing endpoint size by endpoint address.
 **CDC Class**
 usbd_cdc.c: Add missing GetInterface request management in USBD_CDC_Setup() function
 usbd_cdc.c: Update USBD_CDC_Setup() function to allow correct user implementation of CDC_SET_CONTROL_LINE_STATE and similar no-data setup requests.

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section6" checked aria-hidden="true">
<label for="collapse-section6" aria-hidden="true">V2.3.0 / 04-November-2014</label>
<div>

## Main Changes

 Headline
 ---------
 Update all drivers to be C++ compliant
 **CDC Class**
 usbd_cdc.c: fix clear flag issue in USBD_CDC_TransmitPacket() function
 usbd_cdc_if_template.c: update TEMPLATE_Receive() function header comment
 Miscellaneous source code comments update

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section5" checked aria-hidden="true">
<label for="collapse-section5" aria-hidden="true">V2.2.0 / 13-June-2014</label>
<div>

## Main Changes

 Headline
 ---------
 Source code comments review and update
 **HID class**
  Remove unused API USBD_HID_DeviceQualifierDescriptor()
  Add a new API in the HID class to query the poll time USBD_HID_GetPollingInterval()
 **CDC class**
  Bug fix: missing handling ZeroLength Setup request
 **All classes**
 Add alias for the class definition, it's defined as macro with capital letter
 ex. for the HID, the USBD_HID_CLASS macro is defined this way #define USBD_HID_CLASS  &USBD_HID
 and the application code can use the previous definition: &USBD_HID ex. USBD_RegisterClass(&USBD_Device, &USBD_HID) or the new USBD_HID_CLASS ex. USBD_RegisterClass(&USBD_Device, USBD_HID_CLASS)

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section4" checked aria-hidden="true">
<label for="collapse-section4" aria-hidden="true">V2.1.0 / 22-April-2014</label>
<div>

## Main Changes

 Headline
 ---------
 usbd_conf_template.c: update file with the right content (it was using MSC memory management layer)
 usbd_conf_template.h: change include of stm32f4xx.h by stm32xxx.h and add comment to inform user to adapt it to the device used
 Several enhancements in CustomHID class
 Update the Custom HID class driver to simplify the link with user processes
 Optimize the Custom HID class driver and reduce footprint
 Add USBD_CUSTOM_HID_RegisterInterface() API to link user process to custom HID class
 Add Custom HID interface template file usbd_customhid_if_template.c/h
 Miscellaneous comments update

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section3" checked aria-hidden="true">
<label for="collapse-section3" aria-hidden="true">V2.0.0 / 18-February-2014</label>
<div>

## Main Changes

Major update based on STM32Cube specification.

 Headline
 ---------
 Library Core, Classes architecture and APIs modified vs. V1.1.0, and thus the 2 versions are not compatible.


**This version has to be used only with STM32Cube based development**

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section2" checked aria-hidden="true">
<label for="collapse-section2" aria-hidden="true">V1.1.0 / 19-March-2012</label>
<div>

## Main Changes

 Headline
 ---------
 Official support of STM32F4xx devices
 All source files: license disclaimer text update and add link to the License file on ST Internet.
 Handle test mode in the set feature request
 Handle dynamically the USB SELF POWERED feature
 Handle correctly the USBD_CtlError process to take into account error during Control OUT stage
 Miscellaneous bug fix

</div>
:::

::: {.collapse}
<input type="checkbox" id="collapse-section1" checked aria-hidden="true">
<label for="collapse-section1" aria-hidden="true">V1.0.0 / 22-July-2011</label>
<div>

## Main Changes

First official version for STM32F105/7xx and STM32F2xx devices

</div>
:::

:::
:::

<footer class="sticky">
::: {.columns}
::: {.column width="95%"}
:::
::: {.column width="5%"}
<abbr title="Based on template cx566953 version 2.1">Info</abbr>
:::
:::
</footer>
