## Components

### SensorManager

- Requires
    - ai_data_format
- Provides at app level
    - SMPinConfig.h

### CLISSensorStreamer

- Requires
- Provides at app level
- Contributes

## Other SW Unit

- ST USB Library
    - Requires
        - App Messages (app_messages_parser.h/c)
    - Provides at app level
        - usb_device.h/c
        - usb_cdc_if.h/c
        - usb_conf.h/c
        - usb_desc.h/c
        - MX: contribution to stm32wbxx_it.c, SystemClock_Config()
- FreeRTOSCLI
    - Provides at components level
        - FreeRTOSCLI.h/c