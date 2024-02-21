/**
 ******************************************************************************
 * @file    usb_disp.h
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

#ifndef USB_DISP
#define USB_DISP 1

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include "usbd_conf.h"

typedef void * USB_DISP_Hdl_t;

/* USB_DISP_MODE_* define how usb disp stack will handle input buffers
 * - USB_DISP_MODE_LCD : This mode will mimic LCD display that use double buffering mode. User has to provided
 *                       p_frame_buffers[0] and p_frame_buffers[1] that will hold result of format conversion to
 *                       payload_type format. Host application will see a constant frame rate.
 * - USB_DISP_MODE_ON_DEMAND : This mode will reduce USB bandwidth and CPU load by sending user frame only once. User
 *                             has to provided p_frame_buffers[0] and p_frame_buffers[1] that will hold result of format
 *                             conversion to payload_type format. Host application may see a variable frame rate.
 * - USB_DISP_MODE_LCD_SINGLE_BUFFER : Same as USB_DISP_MODE_LCD but user as to provide only p_frame_buffers[0]. Some
 *                                     tearing may appear.
 * - USB_DISP_MODE_ON_DEMAND_SINGLE_BUFFER : Same as USB_DISP_MODE_ON_DEMAND but user as to provide only
 *                                           p_frame_buffers[0].
 * - USB_DISP_MODE_RAW : User will provide directly a frame with payload_type format that will be sent as is.
 *                       p_frame_buffers[0] and p_frame_buffers[1] are not used. User must only call USB_DISP_ShowRaw()
 *                       API.
 */
#define USB_DISP_MODE_LCD 0
#define USB_DISP_MODE_ON_DEMAND 1
#define USB_DISP_MODE_LCD_SINGLE_BUFFER 2
#define USB_DISP_MODE_ON_DEMAND_SINGLE_BUFFER 3
#define USB_DISP_MODE_RAW 4

/* Use USB_DISP_PAYLOAD_UNCOMPRESSED or USB_DISP_PAYLOAD_JPEG for maximal compatibility */
#define USB_DISP_PAYLOAD_UNCOMPRESSED 0
#define USB_DISP_PAYLOAD_JPEG 1
/* Frame based formats */
#define USB_DISP_PAYLOAD_FB_RGB565 2
#define USB_DISP_PAYLOAD_FB_BGR3 3
#define USB_DISP_PAYLOAD_FB_GREY 4
#define USB_DISP_PAYLOAD_FB_H264 5

#define USB_DISP_INPUT_FORMAT_UNKNOWN 0
#define USB_DISP_INPUT_FORMAT_GREY 1
#define USB_DISP_INPUT_FORMAT_ARGB 2
#define USB_DISP_INPUT_FORMAT_RGB565 3
#define USB_DISP_INPUT_FORMAT_YUV422 4

/**
 * @brief Configuration of USB display
 */
typedef struct {
  void *p_hpcd; /**< Pointer on PCD_HandleTypeDef type for USB instance */
  void *p_hjpeg; /**< Pointer on JPEG_HandleTypeDef type for jpeg instance */
  int is_iso; /**< Use isochronous or bulk transfert */
  int width; /**< Width of USB display. Must be a an even number */
  int height; /**< Height of USB display */
  int fps; /**< Required frame per second of USB display */
  int frame_buffer_size; /**< give size of p_frame_buffers. For uncompressed payload format it must be of the
                              uncompressed frame size */
  uint8_t *p_frame_buffers[2]; /**< Frame buffers that will be used internally to store raw data to be sent by
                                    USB */
  int mode; /**< USB display running mode. Select one among USB_DISP_MODE_* */
  int payload_type; /**< Select USB display payload type. Select one among USB_DISP_PAYLOAD_* */
  int input_format_hint; /**< Give hint about intended input buffer format. Select one among USB_DISP_INPUT_FORMAT_* */
  uint8_t *p_jpeg_scratch_buffer; /**< Scratch buffer use when payload_type is USB_DISP_PAYLOAD_JPEG. It will hold
                                       intermediate YUV mcu line. It's size must be int((width + 15) / 16) * 256 bytes */
} USB_DISP_Conf_t;

USB_DISP_Hdl_t USB_DISP_Init(USB_DISP_Conf_t *p_conf);
int USB_DISP_ShowGrey(USB_DISP_Hdl_t hdl, uint8_t *p_frame);
int USB_DISP_ShowArgb(USB_DISP_Hdl_t hdl, uint8_t *p_frame);
int USB_DISP_ShowRgb565(USB_DISP_Hdl_t hdl, uint8_t *p_frame);
int USB_DISP_ShowYuv422(USB_DISP_Hdl_t hdl, uint8_t *p_frame);
int USB_DISP_ShowRaw(USB_DISP_Hdl_t hdl, uint8_t *p_frame, int frame_size, void (*cb)(uint8_t *, void *), void *cb_args);

#ifdef __cplusplus
}
#endif

#endif
