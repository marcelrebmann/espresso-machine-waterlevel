# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

MicroPython firmware for a Raspberry Pi Pico (RP2040) that monitors water level via an ultrasonic sensor and displays it as a colored circular progress arc on a 240x240 GC9A01 TFT display. Motion detection (QMI8658 IMU) wakes the screen; touch input (CST816T) provides interaction.

## Hardware wiring

| Component | Interface | Pins |
|-----------|-----------|------|
| HC-SR04 ultrasonic | GPIO | TRIG=16, ECHO=17 |
| GC9A01 TFT display | SPI(1) | SCK=10, MOSI=11, RESET=13, CS=9, DC=8, backlight=25 |
| QMI8658 IMU | I2C(1) | SDA=6, SCL=7 |
| CST816T touch | I2C(1) | SDA=6, SCL=7 (shared bus), INT=21, RST=22 |

Board: Waveshare RP2040-Touch-LCD-1.28 (display, IMU and touch on-board). The ultrasonic sensor actually used is a US-015 (pin- and protocol-compatible with HC-SR04, driven by `hcsr04.py`), powered from 5 V; its ECHO output is 5 V while RP2040 GPIOs are 3.3 V only.

## Key files

- **`config.py`** — Single user-facing configuration file: tank calibration (`DISTANCE_FULL_CM` / `DISTANCE_EMPTY_CM`), `CALIBRATION_MODE`, color thresholds, timings, wake-up options, `DEBUG`, and all pins (defaults for Waveshare RP2040-Touch-LCD-1.28). Other modules read from it; no values should be hardcoded elsewhere.
- **`main.py`** — Entry point. Creates the shared I2C bus, initializes sensors, runs either the normal loop (`run`) or the calibration loop (`run_calibration`). `LevelView` handles incremental arc/text drawing.
- **`log.py`** — `debug()` (only when `config.DEBUG`) and `warn()` (always).
- **`ultrasonic_sensor.py`** | `UltrasonicSensor` class — wraps `HCSR04`, implements distance measurement with std-dev outlier rejection, converts distance to percentage water level.
- **`hcsr04.py`** — HC-SR04 driver (external, from https://github.com/rsc1975/micropython-hcsr04). Provides `distance_mm()` and `distance_cm()`.
- **`screen_driver.py`** — `ScreenDriver` class — configures GC9A01 display and provides arc drawing (`draw_arc_perf`), score/text rendering, and animated updates (`update_score`).
- **`accelerometer.py`** — `QMI8658` class — IMU driver with two-stage motion detection configuration via CTRL9 protocol. Reads raw/calibrated accelerometer + gyroscope data. Motion thresholds: 0.2g any-motion, 100ms window.
- **`touch_engine.py`** — `Touch_CST816T` class — touch controller via I2C with IRQ handler. Supports gesture modes (single click used as interaction trigger).
- **`colors.py`** — RGB565 color definitions + `get_arc_color()` logic: red ≤10%, orange ≤25%, blue >25%.
- **`inter_bold_64.py`** — Bitmap font (Inter Bold, OFL-1.1) for the percentage text display, generated with `write_font_converter.py` from gc9a01_mpy.

## Architecture notes

- The main loop checks motion/touch each iteration, then reads water level at intervals (10s when screen active, 60s background). New readings only render if the percentage changed.
- Arc rendering uses incremental updates: full redraw on color change, partial arc expansion/shrink for value changes — avoids flicker.
- Both IMU and touch share I2C(1) on pins 6/7; they are separate chip addresses (0x6B and 0x15).
- Use `log.debug()` / `log.warn()` instead of `print()` in modules.
- The bitmap font only contains the glyphs `1234567890%.-`; any other character drawn on the display is silently skipped.

## Deployment

Deploy to the Pico via MicroPico (VS Code extension): the Pico should be in bootloader mode (USB mass storage at `/Volumes/RPI-RP2`). Copy all `.py` files to the mounted drive. No build step or test framework — this is bare embedded MicroPython.
