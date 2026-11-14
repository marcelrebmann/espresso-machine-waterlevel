# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

MicroPython firmware for the Waveshare RP2040-Touch-LCD-1.28 that measures the water level in an espresso machine tank with an ultrasonic sensor and displays it as a colored circular arc on the round 240x240 GC9A01 display. Motion detection (QMI8658 IMU) and a tap on the touch screen (CST816) wake the screen. Originally built for a Quick Mill Rubino; published as an open source project that others adapt to their machine via `config.py`.

## Hardware wiring

Board: Waveshare RP2040-Touch-LCD-1.28 — display, IMU and touch are on-board. Only the ultrasonic sensor is wired externally.

| Component | Interface | Pins |
|-----------|-----------|------|
| US-015 / HC-SR04 ultrasonic | GPIO | TRIG=16, ECHO=17 (via 1 kΩ / 2 kΩ voltage divider), VCC=VSYS (5 V) |
| GC9A01 TFT display | SPI(1) | SCK=10, MOSI=11, RESET=13, CS=9, DC=8, backlight=25 |
| QMI8658 IMU | I2C(1) | SDA=6, SCL=7, address 0x6B |
| CST816T / CST816G touch | I2C(1) | SDA=6, SCL=7 (shared bus), INT=21, RST=22, address 0x15 |

The sensor used is a US-015 (pin- and protocol-compatible with HC-SR04, driven by `hcsr04.py`). Powered from 5 V its ECHO output is 5 V, but RP2040 GPIOs are not 5 V tolerant — the voltage divider is part of the documented circuit (`docs/wiring.svg`).

## Key files

- **`config.py`** — Single user-facing configuration file: tank calibration (`DISTANCE_FULL_CM` / `DISTANCE_EMPTY_CM`), `CALIBRATION_MODE`, color thresholds, timings, wake-up options, `DEBUG`, and all pins. Other modules read from it; no values should be hardcoded elsewhere.
- **`main.py`** — Entry point. Creates the shared I2C bus, initializes sensors, runs either the normal loop (`run`) or the calibration loop (`run_calibration`). `LevelView` handles incremental arc/text drawing.
- **`log.py`** — `debug()` (only when `config.DEBUG`) and `warn()` (always).
- **`ultrasonic_sensor.py`** — `UltrasonicSensor`: wraps `HCSR04`, averages several measurements with std-dev outlier rejection, converts distance to percent (`distance_to_level`).
- **`hcsr04.py`** — Third-party HC-SR04 driver (rsc1975/micropython-hcsr04, Apache-2.0). Keep unmodified.
- **`screen_driver.py`** — `ScreenDriver`: GC9A01 setup from `config`, ring drawing (`draw_arc_perf`), centered text (`draw_text` / `update_text`).
- **`accelerometer.py`** — `QMI8658`: IMU driver with any-motion detection configured via the CTRL9 protocol. Threshold in g (register value = g × 32), window in samples. Based on Waveshare demo code.
- **`touch_engine.py`** — `Touch_CST816T`: touch controller with IRQ handler; single tap is the wake trigger. Accepts chip IDs 0xB3 (CST816G) and 0xB5 (CST816T). Based on Waveshare demo code.
- **`colors.py`** — RGB565 colors from `config` + `Colors.get_arc_color()`.
- **`inter_bold_64.py`** — Generated bitmap font (Inter Bold, OFL-1.1). Do not edit by hand; regenerate with `write_font_converter.py` (command in `THIRD_PARTY_NOTICES.md`).

## Architecture notes

- The main loop polls motion/touch every 250 ms, then reads the water level at intervals (`READOUT_INTERVAL_ACTIVE_S` / `_INACTIVE_S`). New readings only render if the percentage changed and the screen is on; on wake-up the last reading is fully redrawn.
- Arc rendering is incremental: full redraw on color change, partial arc expansion/shrink otherwise — avoids flicker.
- If no wake-up source is available (IMU/touch missing or disabled), the screen stays on permanently.
- Use `log.debug()` / `log.warn()` instead of `print()` in modules.
- The bitmap font only contains the glyphs `1234567890%.-`; any other character is silently skipped. Add glyphs by regenerating the font.

## Licensing

- Project code: MIT (`LICENSE`). Third-party parts and their licenses are listed in `THIRD_PARTY_NOTICES.md`; full texts in `LICENSES/`.
- Never add proprietary fonts or code without a redistributable license.
- When modifying the Waveshare-based drivers, update the modification list in their file header.

## Deployment

No build step or test framework — this is bare embedded MicroPython.

1. One-time: flash a MicroPython firmware **with the built-in `gc9a01` module** (russhughes/gc9a01_mpy). Hold BOOT while plugging in USB; the board mounts as `/Volumes/RPI-RP2`; copy the `.uf2` there. Only the firmware goes onto this drive.
2. Upload the `.py` files to the board's filesystem with MicroPico (VS Code: "Upload project to Pico"), `mpremote cp *.py :`, or Thonny. `main.py` runs on boot.

## Documentation

- `README.md` (English) and `README.de.md` (German) must be kept in sync.
- Record user-visible changes in `CHANGELOG.md` (Keep a Changelog format).
