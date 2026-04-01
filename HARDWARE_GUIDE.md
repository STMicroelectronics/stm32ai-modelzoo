# STM32N6 Hardware Setup

Notes on setting up the hardware side of this project. Covers board connections, boot modes, flashing, and a few things that tripped me up along the way.

---

## STM32N6 — A Few Things Worth Knowing Upfront

The STM32N6 is ST's first MCU with a built-in NPU (Neural-ART accelerator, up to 600 GOPS INT8). The core is a Cortex-M55 with Helium SIMD support, running up to 800 MHz. For this project the important specs are:

- **4.2 MB internal SRAM, no internal flash** — firmware lives in external Octo-SPI NOR Flash
- **MIPI CSI-2** camera interface (2 lanes)
- **STLINK-V3EC** is built into both dev boards, no external probe needed

The no-internal-flash part catches people off guard. In dev mode the firmware loads into SRAM directly and disappears on power off. To keep it after a reset you have to program the external flash and boot from there. More on this below.

---

## Supported Boards

Two boards work with this project:

- **[STM32N6570-DK](https://www.st.com/en/evaluation-tools/stm32n6570-dk.html)** — discovery kit, has an LCD and camera connector built in, easiest to get started with
- **[NUCLEO-N657X0-Q](https://www.st.com/en/evaluation-tools/nucleo-n657x0-q.html)** — nucleo board, no display by default, more flexible if you want to customize things

---

## What You Need

- One of the boards above
- A camera module — tested with:
  - **MB1854** (IMX335, comes with the DK)
  - [STEVAL-55G1MBI](https://www.st.com/en/evaluation-tools/steval-55g1mbi.html)
  - [STEVAL-66GYMAI1](https://www.st.com/en/evaluation-tools/steval-66gymai1.html)
- **USB-C to USB-C cable** for the STLINK port — USB-A to USB-C sometimes doesn't deliver enough current and causes weird resets
- STM32CubeIDE and STEdgeAI Core installed on your PC

If you're using the NUCLEO board and want a display: [X-NUCLEO-GFX01M2](https://www.st.com/en/evaluation-tools/x-nucleo-gfx01m2.html) plugs into the Arduino headers and works over SPI. Alternatively the NUCLEO can output over USB as a UVC device.

Camera detection is automatic in firmware, no config needed for that.

---

## Boot Modes

This is probably the most confusing part if you haven't used STM32N6 before.

**STM32N6570-DK** has two physical switches on the board:
- Both switches **right** → Dev Mode (loads from SRAM, use this when flashing)
- Both switches **left** → Boot from Flash (loads from external NOR Flash, use this during normal operation)

**NUCLEO-N657X0-Q** uses jumpers JP1 (BOOT0) and JP2 (BOOT1):
- JP1 pos 1 + JP2 pos 2 → Dev Mode
- JP1 pos 1 + JP2 pos 1 → Boot from Flash

The switches/jumpers are only read at power-on reset, so **after changing them you have to disconnect and reconnect the power cable**. Pressing reset alone won't pick up the new boot mode.

### Deployment flow

```
1. Set board to Dev Mode → power cycle
2. Run stm32ai_main.py → compiles and flashes to external NOR Flash
3. Set board to Boot from Flash → power cycle
4. Board boots and runs the application
```

---

## Board Setup

### STM32N6570-DK

1. Plug the camera module into the CSI connector with the flat ribbon cable — make sure both ends are fully seated
2. Connect the **STLINK-V3EC USB-C port** to your PC (this is the one used for both power and debug, not the other USB port)
3. Set boot switches to Dev Mode before running the deployment script

### NUCLEO-N657X0-Q

1. (Optional) Attach the X-NUCLEO-GFX01M2 display shield on the Arduino headers
2. Connect the camera with a flat ribbon cable
3. Connect the STLINK USB-C port to your PC
4. Set JP1/JP2 jumpers to Dev Mode (JP1: pos 1, JP2: pos 2)

---

## Debug Console

The STLINK connection creates a virtual COM port (VCP) on your PC automatically, no extra wiring needed. Settings: **115200 8N1**, no flow control.

On Linux/macOS:
```bash
screen /dev/ttyACM0 115200
```

On Windows, open Device Manager to find the COM port number, then use PuTTY or Tera Term.

---

## Flashing

The deployment script handles everything automatically:

```bash
cd object_detection
python stm32ai_main.py --config-path ./config_file_examples/ --config-name deployment_n6_yolov8_config.yaml
```

If you want to flash a pre-built binary manually, use STM32CubeProgrammer. Set the board to Dev Mode, power cycle, then flash to the external flash start address: `0x70000000`.

Before starting, it's worth checking your STLINK firmware is up to date. Open STM32CubeProgrammer or CubeIDE and accept the upgrade prompt if it appears — outdated STLINK firmware is a common source of phantom connection issues.

---

## Common Issues

**Board not showing up in CubeIDE/CubeProgrammer**
Most likely either the wrong USB port (use the STLINK port, not the device USB), an outdated STLINK firmware, or a USB-A to USB-C cable dropping power. Try a USB-C to USB-C cable first.

**Firmware disappears after power off**
The board is still in Dev Mode. Switch to Boot from Flash and power cycle.

**Flashing completes but board won't boot**
Same as above — boot mode wasn't changed after flashing. Set switches/jumpers to Boot from Flash, then reconnect power.

**Black screen / camera not working**
Re-seat the ribbon cable, both ends. It's easy to have it look connected but not actually clicked in.

**No output in serial terminal**
Check you have the right COM port selected and baud rate is 115200. On Windows, Device Manager → Ports (COM & LPT) shows the VCP number.

**Very few or no detections**
`confidence_thresh` in the YAML might be set too high. Try lowering it to 0.3 and see if that helps. If the board crashes on startup, the model might be too large for SRAM — use yolov8n at 256×256 as a baseline.

---

*For YAML config, quantization settings and deployment parameters see [object_detection/docs/](object_detection/docs/).*
