# Middleware USB Camera Component

## Description

This component will allow to capture video stream of an USB camera which is UVC compliant.

## Minimal usage

Call USB_CAM_Init() to initialize USB stack.

Then call USB_CAM_SetupDevice() to detect and configure webcam given request configuration.

You can then call USB_CAM_PushBuffer() / USB_CAM_PopBuffer() to capture video buffers.