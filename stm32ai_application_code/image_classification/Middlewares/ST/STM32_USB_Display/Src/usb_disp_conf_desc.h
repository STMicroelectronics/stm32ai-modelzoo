/**
 ******************************************************************************
 * @file    usb_disp_conf_desc.h
 * @author  GPM Application Team
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */

static uint8_t USB_DISP_CfgFsIso[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(168), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(77), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     27, /* bLength */
     0x24, /* bDescriptorType */
     0x4, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     0x59, /* guidFormat[0] */
     0x55, /* guidFormat[1] */
     0x59, /* guidFormat[2] */
     0x32, /* guidFormat[3] */
     0x00, /* guidFormat[4] */
     0x00, /* guidFormat[5] */
     0x10, /* guidFormat[6] */
     0x00, /* guidFormat[7] */
     0x80, /* guidFormat[8] */
     0x00, /* guidFormat[9] */
     0x00, /* guidFormat[10] */
     0xaa, /* guidFormat[11] */
     0x00, /* guidFormat[12] */
     0x38, /* guidFormat[13] */
     0x9b, /* guidFormat[14] */
     0x71, /* guidFormat[15] */
     16, /* bBitsPerPixel */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */

      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x5, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(153600), /* dwMaxVideoFrameBufferSize */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =1 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   1, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Std VS isochronous video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x5, /* bmAttributes */
    WBVAL(1023), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgHsIso[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(168), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(77), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     27, /* bLength */
     0x24, /* bDescriptorType */
     0x4, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     0x59, /* guidFormat[0] */
     0x55, /* guidFormat[1] */
     0x59, /* guidFormat[2] */
     0x32, /* guidFormat[3] */
     0x00, /* guidFormat[4] */
     0x00, /* guidFormat[5] */
     0x10, /* guidFormat[6] */
     0x00, /* guidFormat[7] */
     0x80, /* guidFormat[8] */
     0x00, /* guidFormat[9] */
     0x00, /* guidFormat[10] */
     0xaa, /* guidFormat[11] */
     0x00, /* guidFormat[12] */
     0x38, /* guidFormat[13] */
     0x9b, /* guidFormat[14] */
     0x71, /* guidFormat[15] */
     16, /* bBitsPerPixel */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */

      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x5, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(153600), /* dwMaxVideoFrameBufferSize */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =1 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   1, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Std VS isochronous video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x5, /* bmAttributes */
    WBVAL(1024), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgFsBulk[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(159), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(77), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     27, /* bLength */
     0x24, /* bDescriptorType */
     0x4, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     0x59, /* guidFormat[0] */
     0x55, /* guidFormat[1] */
     0x59, /* guidFormat[2] */
     0x32, /* guidFormat[3] */
     0x00, /* guidFormat[4] */
     0x00, /* guidFormat[5] */
     0x10, /* guidFormat[6] */
     0x00, /* guidFormat[7] */
     0x80, /* guidFormat[8] */
     0x00, /* guidFormat[9] */
     0x00, /* guidFormat[10] */
     0xaa, /* guidFormat[11] */
     0x00, /* guidFormat[12] */
     0x38, /* guidFormat[13] */
     0x9b, /* guidFormat[14] */
     0x71, /* guidFormat[15] */
     16, /* bBitsPerPixel */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */

      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x5, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(153600), /* dwMaxVideoFrameBufferSize */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

    /* Std VS bulk video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x2, /* bmAttributes */
    WBVAL(64), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgHsBulk[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(159), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(77), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     27, /* bLength */
     0x24, /* bDescriptorType */
     0x4, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     0x59, /* guidFormat[0] */
     0x55, /* guidFormat[1] */
     0x59, /* guidFormat[2] */
     0x32, /* guidFormat[3] */
     0x00, /* guidFormat[4] */
     0x00, /* guidFormat[5] */
     0x10, /* guidFormat[6] */
     0x00, /* guidFormat[7] */
     0x80, /* guidFormat[8] */
     0x00, /* guidFormat[9] */
     0x00, /* guidFormat[10] */
     0xaa, /* guidFormat[11] */
     0x00, /* guidFormat[12] */
     0x38, /* guidFormat[13] */
     0x9b, /* guidFormat[14] */
     0x71, /* guidFormat[15] */
     16, /* bBitsPerPixel */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */

      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x5, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(153600), /* dwMaxVideoFrameBufferSize */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

    /* Std VS bulk video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x2, /* bmAttributes */
    WBVAL(512), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgFsIsoJpeg[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(152), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(61), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     11, /* bLength */
     0x24, /* bDescriptorType */
     0x6, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     1, /* bmFlags */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */
      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x7, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(153600), /* dwMaxVideoFrameBufferSize */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =1 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   1, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Std VS isochronous video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x5, /* bmAttributes */
    WBVAL(1023), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgHsIsoJpeg[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(152), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(61), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     11, /* bLength */
     0x24, /* bDescriptorType */
     0x6, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     1, /* bmFlags */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */
      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x7, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(153600), /* dwMaxVideoFrameBufferSize */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =1 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   1, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Std VS isochronous video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x5, /* bmAttributes */
    WBVAL(1024), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgFsBulkJpeg[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(143), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(61), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     11, /* bLength */
     0x24, /* bDescriptorType */
     0x6, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     1, /* bmFlags */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */
      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x7, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(153600), /* dwMaxVideoFrameBufferSize */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

    /* Std VS bulk video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x2, /* bmAttributes */
    WBVAL(64), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgHsBulkJpeg[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(143), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(61), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     11, /* bLength */
     0x24, /* bDescriptorType */
     0x6, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     1, /* bmFlags */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */
      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x7, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(153600), /* dwMaxVideoFrameBufferSize */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

    /* Std VS bulk video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x2, /* bmAttributes */
    WBVAL(512), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgFsIsoFb[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(169), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(78), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     28, /* bLength */
     0x24, /* bDescriptorType */
     0x10, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     0x52, /* guidFormat[0] */
     0x47, /* guidFormat[1] */
     0x42, /* guidFormat[2] */
     0x50, /* guidFormat[3] */
     0x00, /* guidFormat[4] */
     0x00, /* guidFormat[5] */
     0x10, /* guidFormat[6] */
     0x00, /* guidFormat[7] */
     0x80, /* guidFormat[8] */
     0x00, /* guidFormat[9] */
     0x00, /* guidFormat[10] */
     0xaa, /* guidFormat[11] */
     0x00, /* guidFormat[12] */
     0x38, /* guidFormat[13] */
     0x9b, /* guidFormat[14] */
     0x71, /* guidFormat[15] */
     16, /* bBitsPerPixel */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */
     0, /* bVariableSize */

      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x11, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(640), /* dwBytesPerLine */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =1 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   1, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Std VS isochronous video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x5, /* bmAttributes */
    WBVAL(1023), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgHsIsoFb[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(169), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(78), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     28, /* bLength */
     0x24, /* bDescriptorType */
     0x10, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     0x52, /* guidFormat[0] */
     0x47, /* guidFormat[1] */
     0x42, /* guidFormat[2] */
     0x50, /* guidFormat[3] */
     0x00, /* guidFormat[4] */
     0x00, /* guidFormat[5] */
     0x10, /* guidFormat[6] */
     0x00, /* guidFormat[7] */
     0x80, /* guidFormat[8] */
     0x00, /* guidFormat[9] */
     0x00, /* guidFormat[10] */
     0xaa, /* guidFormat[11] */
     0x00, /* guidFormat[12] */
     0x38, /* guidFormat[13] */
     0x9b, /* guidFormat[14] */
     0x71, /* guidFormat[15] */
     16, /* bBitsPerPixel */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */
     0, /* bVariableSize */

      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x11, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(640), /* dwBytesPerLine */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =1 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   1, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Std VS isochronous video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x5, /* bmAttributes */
    WBVAL(1024), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgFsBulkFb[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(160), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(78), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     28, /* bLength */
     0x24, /* bDescriptorType */
     0x10, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     0x52, /* guidFormat[0] */
     0x47, /* guidFormat[1] */
     0x42, /* guidFormat[2] */
     0x50, /* guidFormat[3] */
     0x00, /* guidFormat[4] */
     0x00, /* guidFormat[5] */
     0x10, /* guidFormat[6] */
     0x00, /* guidFormat[7] */
     0x80, /* guidFormat[8] */
     0x00, /* guidFormat[9] */
     0x00, /* guidFormat[10] */
     0xaa, /* guidFormat[11] */
     0x00, /* guidFormat[12] */
     0x38, /* guidFormat[13] */
     0x9b, /* guidFormat[14] */
     0x71, /* guidFormat[15] */
     16, /* bBitsPerPixel */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */
     0, /* bVariableSize */

      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x11, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(640), /* dwBytesPerLine */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

    /* Std VS bulk video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x2, /* bmAttributes */
    WBVAL(64), /* wMaxPacketSize */
    1, /* bInterval */

};

static uint8_t USB_DISP_CfgHsBulkFb[] = {
 /* Configuration 1 */
 9, /* bLength */
 0x2, /* bDescriptorType */
 WBVAL(160), /* wTotalLength */
 2, /* bNumInterfaces */
 1, /* bConfigurationValue */
 0, /* iConfiguration */
 0xc0, /* bmAttributes */
 50, /* bMaxPower */

  /* Interface Association Descriptor */
  8, /* bLength */
  0xb, /* bDescriptorType */
  0, /* bFirstInterface */
  2, /* bInterfaceCount */
  0xe, /* bFunctionClass */
  0x3, /* bFunctionSubClass */
  0x0, /* bFunctionProtocol */
  0, /* iFunction */

   /* Standard VC (Video Control) Interface Descriptor  = interface 0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   0, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   0, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x1, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VC Interface Descriptor */
    13, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    WBVAL(0x110), /* bcdUVC */
    WBVAL(40), /* wTotalLength */
    0x0, /* dwClockFrequency 48000000 */
    0x6c,
    0xdc,
    0x2,
    0x1, /* bInCollection */
    0x1, /* baInterfaceNr[0] */

     /* Input Terminal Descriptor */
     18, /* bLength */
     0x24, /* bDescriptorType */
     0x2, /* bDescriptorSubType */
     1, /* bTerminalID */
     WBVAL(0x201), /* wTerminalType */
     0, /* bAssocTerminal */
     0, /* iTerminal */
     WBVAL(0), /* wObjectiveFocalLengthMin */
     WBVAL(0), /* wObjectiveFocalLengthMax */
     WBVAL(0), /* wOcularFocalLength */
     3, /* bControlSize */
     0, /* bmControls */
     0,
     0,

     /* Output Terminal Descriptor */
     9, /* bLength */
     0x24, /* bDescriptorType */
     0x3, /* bDescriptorSubType */
     2, /* bTerminalID */
     WBVAL(0x101), /* wTerminalType */
     0, /* bAssocTerminal */
     1, /* bSourceID */
     0, /* iTerminal */

   /* Standard VS (Video Streaming) Interface Descriptor  = interface 1 / alt =0 */
   9, /* bLength */
   0x4, /* bDescriptorType */
   1, /* bInterfaceNumber */
   0, /* bAlternateSetting */
   1, /* bNumEndpoints */
   0xe, /* bInterfaceClass */
   0x2, /* bInterfaceSubClass */
   0x0, /* bInterfaceProtocol */
   0, /* iInterface */

    /* Class-specific VS Header Descriptor (Input) */
    14, /* bLength */
    0x24, /* bDescriptorType */
    0x1, /* bDescriptorSubType */
    1, /* bNumFormats */
    WBVAL(78), /* wTotalLength */
    0x81, /* bEndpointAddress */
    0, /* bmInfo */
    2, /* bTerminalLink */
    0, /* bStillCaptureMethod */
    0, /* bTriggerSupport */
    0, /* bTriggerUsage */
    1, /* bControlSize */
    0, /* bmaControls[0] */

     /* Payload Format Descriptor */
     28, /* bLength */
     0x24, /* bDescriptorType */
     0x10, /* bDescriptorSubType */
     1, /* bFormatIndex */
     1, /* bNumFrameDescriptors */
     0x52, /* guidFormat[0] */
     0x47, /* guidFormat[1] */
     0x42, /* guidFormat[2] */
     0x50, /* guidFormat[3] */
     0x00, /* guidFormat[4] */
     0x00, /* guidFormat[5] */
     0x10, /* guidFormat[6] */
     0x00, /* guidFormat[7] */
     0x80, /* guidFormat[8] */
     0x00, /* guidFormat[9] */
     0x00, /* guidFormat[10] */
     0xaa, /* guidFormat[11] */
     0x00, /* guidFormat[12] */
     0x38, /* guidFormat[13] */
     0x9b, /* guidFormat[14] */
     0x71, /* guidFormat[15] */
     16, /* bBitsPerPixel */
     1, /* bDefaultFrameIndex */
     0, /* bAspectRatioX */
     0, /* bAspectRatioY */
     0, /* bmInterlaceFlags */
     0, /* bCopyProtect */
     0, /* bVariableSize */

      /* Frame Descriptor */
      30, /* bLength */
      0x24, /* bDescriptorType */
      0x11, /* bDescriptorSubType */
      1, /* bFrameIndex */
      0x2, /* bmCapabilities */
      WBVAL(320), /* wWidth */
      WBVAL(240), /* wHeight */
      DBVAL(6144000), /* dwMinBitRate */
      DBVAL(6144000), /* dwMaxBitRate */
      DBVAL(2000000), /* dwDefaultFrameInterval (in 100 ns units) */
      1, /* bFrameIntervalType */
      DBVAL(640), /* dwBytesPerLine */
      DBVAL(2000000), /* dwFrameInterval[0] (in 100 ns units) */

     /* Color Descriptor */
     6, /* bLength */
     0x24, /* bDescriptorType */
     0xd, /* bDescriptorSubType */
     1, /* bColorPrimaries */
     1, /* bTransferCharacteristics */
     4, /* bMatrixCoefficients */

    /* Std VS bulk video data endpoint Descriptor */
    7, /* bLength */
    0x5, /* bDescriptorType */
    0x81, /* bEndpointAddress */
    0x2, /* bmAttributes */
    WBVAL(512), /* wMaxPacketSize */
    1, /* bInterval */

};

