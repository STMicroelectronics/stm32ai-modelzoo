# Middleware USB Display Component

## Description

This component will allow to emulate a display that can be displayed onto a PC using an USB cable.

## How it works

We will impersonate USB UVC device with user given width and size so user can connect any host
to display screen buffer.

## Minimal usage

Call USB_DISP_Init() to initialize USB stack. Note that user has to provide USB display internal
YUV422 buffers.

Then according to your frame buffer composition format use one of USB_DISP_ShowGrey(), USB_DISP_ShowArgb()
or USB_DISP_ShowRgb565() API.

## Isochronous versus bulk mode

Each of this mode as it's own advantage / disadvantage.

Isochronous mode will guarantee frame rate since USB host will reserve needed bandwidth to sustain it.
But due to USB device software stack limitation (only one packet per micro-frame) frame rate will be
lower than bulk mode.

On the other side bulk mode will not guarantee frame rate but it can reach higher frame rate since it's then
possible to use more USB bandwidth.

## Display mode description

In all modes USB frame rate will never be greater that fps parameter given by user.

### USB_DISP_MODE_LCD

LCD mode will emulate a screen with a constant frame rate. So if user has not yet push a new frame since last USB frame
transfer, previously transmit frame will be transmit again. From host side refresh rate will be constant even if we still
display same frame.

User must provide p_frame_buffers[0] and p_frame_buffers[1].

### USB_DISP_MODE_ON_DEMAND

On demand mode will only transfer an USB frame when a new frame has been push by user. In other words user frame are only
displayed once. So from host side refresh rate is link to frequency of user frame push. This may result on less USB
bandwidth utilization and less CPU time used for MCU.

User must provide p_frame_buffers[0] and p_frame_buffers[1].

### USB_DISP_MODE_LCD_SINGLE_BUFFER

Same as USB_DISP_MODE_LCD but user as to provide only p_frame_buffers[0]. Some tearing may appear.

### USB_DISP_MODE_ON_DEMAND_SINGLE_BUFFER

Same as USB_DISP_MODE_ON_DEMAND but user as to provide only p_frame_buffers[0].

### USB_DISP_MODE_RAW

User will provide directly a frame with payload_type format that will be sent as is.
p_frame_buffers[0] and p_frame_buffers[1] are not used. User must only call USB_DISP_ShowRaw() API.
