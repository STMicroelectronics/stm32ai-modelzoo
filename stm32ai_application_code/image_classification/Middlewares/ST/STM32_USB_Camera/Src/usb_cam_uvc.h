 /**
 ******************************************************************************
 * @file    usb_cam_uvc.h
 * @author  MDG Application Team
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
#ifndef __UVC_CODES__
#define __UVC_CODES__ 1

/*
 * Video Class specification release 1.1
 * Appendix A. Video Device Class Codes defines
 */

#define CC_VIDEO                                      0x0EU

/* Video Interface Subclass values */
#define SC_UNDEFINED                                  0x00U
#define SC_VIDEOCONTROL                               0x01U
#define SC_VIDEOSTREAMING                             0x02U
#define SC_VIDEO_INTERFACE_COLLECTION                 0x03U

#define PC_PROTOCOL_UNDEFINED                         0x00U
#define PC_PROTOCOL_15                                0x01U

/* Video Class-Specific Descriptor Types */
#define CS_UNDEFINED                                  0x20U
#define CS_DEVICE                                     0x21U
#define CS_CONFIGURATION                              0x22U
#define CS_STRING                                     0x23U
#define CS_INTERFACE                                  0x24U
#define CS_ENDPOINT                                   0x25U

/* Video Class-Specific VideoControl Interface Descriptor Subtypes */
#define VC_DESCRIPTOR_UNDEFINED                       0x00U
#define VC_HEADER                                     0x01U
#define VC_INPUT_TERMINAL                             0x02U
#define VC_OUTPUT_TERMINAL                            0x03U
#define VC_SELECTOR_UNIT                              0x04U
#define VC_PROCESSING_UNIT                            0x05U
#define VC_EXTENSION_UNIT                             0x06U

/* Video Class-Specific VideoStreaming Interface Descriptor Subtypes */
#define VS_UNDEFINED                                  0x00U
#define VS_INPUT_HEADER                               0x01U
#define VS_OUTPUT_HEADER                              0x02U
#define VS_STILL_IMAGE_FRAME                          0x03U
#define VS_FORMAT_UNCOMPRESSED                        0x04U
#define VS_FRAME_UNCOMPRESSED                         0x05U
#define VS_FORMAT_MJPEG                               0x06U
#define VS_FRAME_MJPEG                                0x07U
#define VS_FORMAT_MPEG2TS                             0x0AU
#define VS_FORMAT_DV                                  0x0CU
#define VS_COLORFORMAT                                0x0DU
#define VS_FORMAT_FRAME_BASED                         0x10U
#define VS_FRAME_FRAME_BASED                          0x11U
#define VS_FORMAT_STREAM_BASED                        0x12U

/* Video Class-Specific Request values */
#define UVC_RQ_UNDEFINED                               0x00U
#define UVC_SET_CUR                                    0x01U
#define UVC_GET_CUR                                    0x81U
#define UVC_GET_MIN                                    0x82U
#define UVC_GET_MAX                                    0x83U
#define UVC_GET_RES                                    0x84U
#define UVC_GET_LEN                                    0x85U
#define UVC_GET_INFO                                   0x86U
#define UVC_GET_DEF                                    0x87U

/* VideoControl Interface Control Selectors */
#define VC_CONTROL_UNDEFINED                           0x00U
#define VC_VIDEO_POWER_MODE_CONTROL                    0x01U
#define VC_REQUEST_ERROR_CODE_CONTROL                  0x02U

/* Request Error Code Control */
#define UVC_NO_ERROR_ERR                               0x00U
#define UVC_NOT_READY_ERR                              0x01U
#define UVC_WRONG_STATE_ERR                            0x02U
#define UVC_POWER_ERR                                  0x03U
#define UVC_OUT_OF_RANGE_ERR                           0x04U
#define UVC_INVALID_UNIT_ERR                           0x05U
#define UVC_INVALID_CONTROL_ERR                        0x06U
#define UVC_INVALID_REQUEST_ERR                        0x07U
#define UVC_UNKNOWN_ERR                                0xFFU

/*Terminal Control Selectors*/
#define TE_CONTROL_UNDEFINED                           0x00U

/* Selector Unit Control Selectors */
#define SU_CONTROL_UNDEFINED                           0x00U
#define SU_INPUT_SELECT_CONTROL                        0x01U

/* Camera Terminal Control Selectors */
#define CT_CONTROL_UNDEFINED                           0x00U
#define CT_SCANNING_MODE_CONTROL                       0x01U
#define CT_AE_MODE_CONTROL                             0x02U
#define CT_AE_PRIORITY_CONTROL                         0x03U
#define CT_EXPOSURE_TIME_ABSOLUTE_CONTROL              0x04U
#define CT_EXPOSURE_TIME_RELATIVE_CONTROL              0x05U
#define CT_FOCUS_ABSOLUTE_CONTROL                      0x06U
#define CT_FOCUS_RELATIVE_CONTROL                      0x07U
#define CT_FOCUS_AUTO_CONTROL                          0x08U
#define CT_IRIS_ABSOLUTE_CONTROL                       0x09U
#define CT_IRIS_RELATIVE_CONTROL                       0x0AU
#define CT_ZOOM_ABSOLUTE_CONTROL                       0x0BU
#define CT_ZOOM_RELATIVE_CONTROL                       0x0CU
#define CT_PANTILT_ABSOLUTE_CONTROL                    0x0DU
#define CT_PANTILT_RELATIVE_CONTROL                    0x0EU
#define CT_ROLL_ABSOLUTE_CONTROL                       0x0FU
#define CT_ROLL_RELATIVE_CONTROL                       0x10U
#define CT_PRIVACY_CONTROL                             0x11U

/* Processing Unit Control Selectors */
#define PU_CONTROL_UNDEFINED                           0x00U
#define PU_BACKLIGHT_COMPENSATION_CONTROL              0x01U
#define PU_BRIGHTNESS_CONTROL                          0x02U
#define PU_CONTRAST_CONTROL                            0x03U
#define PU_GAIN_CONTROL                                0x04U
#define PU_POWER_LINE_FREQUENCY_CONTROL                0x05U
#define PU_HUE_CONTROL                                 0x06U
#define PU_SATURATION_CONTROL                          0x07U
#define PU_SHARPNESS_CONTROL                           0x08U
#define PU_GAMMA_CONTROL                               0x09U
#define PU_WHITE_BALANCE_TEMPERATURE_CONTROL           0x0AU
#define PU_WHITE_BALANCE_TEMPERATURE_AUTO_CONTROL      0x0BU
#define PU_WHITE_BALANCE_COMPONENT_CONTROL             0x0CU
#define PU_WHITE_BALANCE_COMPONENT_AUTO_CONTROL        0x0DU
#define PU_DIGITAL_MULTIPLIER_CONTROL                  0x0EU
#define PU_DIGITAL_MULTIPLIER_LIMIT_CONTROL            0x0FU
#define PU_HUE_AUTO_CONTROL                            0x10U
#define PU_ANALOG_VIDEO_STANDARD_CONTROL               0x11U
#define PU_ANALOG_LOCK_STATUS_CONTROL                  0x12U

/*Extension Unit Control Selectors */
#define XU_CONTROL_UNDEFINED                           0x00U

/* VideoStreaming Interface Control Selectors */
#define VS_CONTROL_UNDEFINED                           0x00U
#define VS_PROBE_CONTROL                               0x100U
#define VS_COMMIT_CONTROL                              0x200U
#define VS_PROBE_CONTROL_CS                            0x01U
#define VS_COMMIT_CONTROL_CS                           0x02U
#define VS_STILL_PROBE_CONTROL                         0x03U
#define VS_STILL_COMMIT_CONTROL                        0x04U
#define VS_STILL_IMAGE_TRIGGER_CONTROL                 0x05U
#define VS_STREAM_ERROR_CODE_CONTROL                   0x06U
#define VS_GENERATE_KEY_FRAME_CONTROL                  0x07U
#define VS_UPDATE_FRAME_SEGMENT_CONTROL                0x08U
#define VS_SYNC_DELAY_CONTROL                          0x09U

/* Control Capabilities */
#define UVC_SUPPORTS_GET                               0x01U
#define UVC_SUPPORTS_SET                               0x02U
#define UVC_STATE_DISABLED                             0x04U
#define UVC_AUTOUPDATE_CONTROL                         0x08U
#define UVC_ASYNCHRONOUS_CONTROL                       0x10U

/* USB Terminal Types */
#define TT_VENDOR_SPECIFIC                             0x0100U
#define TT_STREAMING                                   0x0101U

/* Input Terminal Types */
#define ITT_VENDOR_SPECIFIC                            0x0200U
#define ITT_CAMERA                                     0x0201U
#define ITT_MEDIA_TRANSPORT_INPUT                      0x0202U

/*Output Terminal Types */
#define OTT_VENDOR_SPECIFIC                            0x0300U
#define OTT_DISPLAY                                    0x0301U
#define OTT_MEDIA_TRANSPORT_OUTPUT                     0x0302U

/* External Terminal Types */
#define EXTERNAL_VENDOR_SPECIFIC                       0x0400U
#define COMPOSITE_CONNECTOR                            0x0401U
#define SVIDEO_CONNECTOR                               0x0402U
#define COMPONENT_CONNECTOR                            0x0403U

#endif