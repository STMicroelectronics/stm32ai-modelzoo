/**
 ******************************************************************************
 * @file    usb_disp_desc.c
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

#include "usb_disp_desc.h"

#include "usbd_ctlreq.h"

#define DEVICE_ID1                    (UID_BASE)
#define DEVICE_ID2                    (UID_BASE + 0x4U)
#define DEVICE_ID3                    (UID_BASE + 0x8U)

#define USB_SIZ_STRING_SERIAL         0x1AU

#define USBD_VID                      0x0483
#define USBD_PID                      0x5780
#define USBD_LANGID_STRING            0x409
#define USBD_MANUFACTURER_STRING      "STMicroelectronics"
#define USBD_PRODUCT_HS_STRING        "STM32 Usb HS Display"
#define USBD_PRODUCT_FS_STRING        "STM32 Usb FS Display"
#define USBD_CONFIGURATION_HS_STRING  "VIDEO Config"
#define USBD_INTERFACE_HS_STRING      "VIDEO Interface"
#define USBD_CONFIGURATION_FS_STRING  "VIDEO Config"
#define USBD_INTERFACE_FS_STRING      "VIDEO Interface"

static uint8_t USB_DISP_StrDesc[USBD_MAX_STR_DESC_SIZ];

static uint8_t USB_DISP_DeviceDesc[USB_LEN_DEV_DESC] =
{
  0x12,                       /* bLength */
  USB_DESC_TYPE_DEVICE,       /* bDescriptorType */
  #if ((USBD_LPM_ENABLED == 1) || (USBD_CLASS_BOS_ENABLED == 1))
  0x01,                       /*bcdUSB */     /* changed to USB version 2.01
                                            in order to support BOS Desc */
  #else
  0x00,                       /* bcdUSB */
  #endif /* (USBD_LPM_ENABLED == 1) || (USBD_CLASS_BOS_ENABLED == 1) */
  0x02,
  0x00,                       /* bDeviceClass */
  0x00,                       /* bDeviceSubClass */
  0x00,                       /* bDeviceProtocol */
  USB_MAX_EP0_SIZE,           /* bMaxPacketSize */
  LOBYTE(USBD_VID),           /* idVendor */
  HIBYTE(USBD_VID),           /* idVendor */
  LOBYTE(USBD_PID),           /* idVendor */
  HIBYTE(USBD_PID),           /* idVendor */
  0x00,                       /* bcdDevice rel. 2.00 */
  0x02,
  USBD_IDX_MFC_STR,           /* Index of manufacturer string */
  USBD_IDX_PRODUCT_STR,       /* Index of product string */
  USBD_IDX_SERIAL_STR,        /* Index of serial number string */
  USBD_MAX_NUM_CONFIGURATION  /* bNumConfigurations */
};

static uint8_t USB_DISP_LangIDDesc[USB_LEN_LANGID_STR_DESC] =
{
  USB_LEN_LANGID_STR_DESC,
  USB_DESC_TYPE_STRING,
  LOBYTE(USBD_LANGID_STRING),
  HIBYTE(USBD_LANGID_STRING),
};

static uint8_t USB_DISP_StringSerial[USB_SIZ_STRING_SERIAL] =
{
  USB_SIZ_STRING_SERIAL,
  USB_DESC_TYPE_STRING,
};

static void USB_DISP_IntToUnicode(uint32_t value, uint8_t *p_buf, uint8_t len)
{
  uint8_t idx = 0U;

  for (idx = 0U ; idx < len ; idx ++)
  {
    if (((value >> 28)) < 0xAU)
    {
      p_buf[ 2U * idx] = (value >> 28) + '0';
    }
    else
    {
      p_buf[2U * idx] = (value >> 28) + 'A' - 10U;
    }

    value = value << 4;
    p_buf[2U * idx + 1] = 0U;
  }
}

static void USB_DISP_GetSerialNum(void)
{
  uint32_t deviceserial0;
  uint32_t deviceserial1;
  uint32_t deviceserial2;

  deviceserial0 = *(uint32_t *)DEVICE_ID1;
  deviceserial1 = *(uint32_t *)DEVICE_ID2;
  deviceserial2 = *(uint32_t *)DEVICE_ID3;

  deviceserial0 += deviceserial2;

  USB_DISP_IntToUnicode(deviceserial0, &USB_DISP_StringSerial[2], 8U);
  USB_DISP_IntToUnicode(deviceserial1, &USB_DISP_StringSerial[18], 4U);
}

static uint8_t *USB_DISP_GetDeviceDescriptor(USBD_SpeedTypeDef speed, uint16_t *p_length)
{
  *p_length = sizeof(USB_DISP_DeviceDesc);

  return USB_DISP_DeviceDesc;
}

static uint8_t *USB_DISP_GetLangIDStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *p_length)
{
  *p_length = sizeof(USB_DISP_LangIDDesc);

  return USB_DISP_LangIDDesc;
}

static uint8_t *USB_DISP_GetManufacturerStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *p_length)
{
  USBD_GetString((uint8_t *)USBD_MANUFACTURER_STRING, USB_DISP_StrDesc, p_length);

  return USB_DISP_StrDesc;
}


static uint8_t *USB_DISP_GetProductStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *p_length)
{
  if (speed == USBD_SPEED_HIGH)
  {
    USBD_GetString((uint8_t *)USBD_PRODUCT_HS_STRING, USB_DISP_StrDesc, p_length);
  }
  else
  {
    USBD_GetString((uint8_t *)USBD_PRODUCT_FS_STRING, USB_DISP_StrDesc, p_length);
  }

  return USB_DISP_StrDesc;
}

static uint8_t *USB_DISP_GetSerialStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *p_length)
{
  *p_length = USB_SIZ_STRING_SERIAL;

  /* Update the serial number string descriptor with the data from the unique ID*/
  USB_DISP_GetSerialNum();

  return USB_DISP_StringSerial;
}

static uint8_t *USB_DISP_GetConfigurationStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *p_length)
{
  if (speed == USBD_SPEED_HIGH)
  {
    USBD_GetString((uint8_t *)USBD_CONFIGURATION_HS_STRING, USB_DISP_StrDesc, p_length);
  }
  else
  {
    USBD_GetString((uint8_t *)USBD_CONFIGURATION_FS_STRING, USB_DISP_StrDesc, p_length);
  }

  return USB_DISP_StrDesc;
}

static uint8_t *USB_DISP_GetInterfaceStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *p_length)
{
  if (speed == USBD_SPEED_HIGH)
  {
    USBD_GetString((uint8_t *)USBD_INTERFACE_HS_STRING, USB_DISP_StrDesc, p_length);
  }
  else
  {
    USBD_GetString((uint8_t *)USBD_INTERFACE_FS_STRING, USB_DISP_StrDesc, p_length);
  }

  return USB_DISP_StrDesc;
}

USBD_DescriptorsTypeDef USB_DISP_Desc = {
  USB_DISP_GetDeviceDescriptor,
  USB_DISP_GetLangIDStrDescriptor,
  USB_DISP_GetManufacturerStrDescriptor,
  USB_DISP_GetProductStrDescriptor,
  USB_DISP_GetSerialStrDescriptor,
  USB_DISP_GetConfigurationStrDescriptor,
  USB_DISP_GetInterfaceStrDescriptor,
#if (USBD_CLASS_USER_STRING_DESC == 1)
  #error "Not supported"
#endif
#if ((USBD_LPM_ENABLED == 1U) || (USBD_CLASS_BOS_ENABLED == 1))
  #error "Not supported"
#endif
};
