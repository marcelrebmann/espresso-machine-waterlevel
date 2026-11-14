# Third-Party Notices

This project includes or is based on the following third-party work.
Unless noted otherwise below, all other files are licensed under the
[MIT License](LICENSE).

| File | Origin | License |
|------|--------|---------|
| `hcsr04.py` | [rsc1975/micropython-hcsr04](https://github.com/rsc1975/micropython-hcsr04) by Roberto Sánchez (v0.2.1, unmodified) | Apache License 2.0 — see [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt) |
| `accelerometer.py` | Based on the Waveshare [RP2040-Touch-LCD-1.28](https://www.waveshare.com/wiki/RP2040-Touch-LCD-1.28) MicroPython demo (QMI8658 driver), modified for this project | See [Waveshare demo code](#waveshare-demo-code) |
| `touch_engine.py` | Based on the Waveshare [RP2040-Touch-LCD-1.28](https://www.waveshare.com/wiki/RP2040-Touch-LCD-1.28) MicroPython demo (CST816T driver), modified for this project | See [Waveshare demo code](#waveshare-demo-code) |
| `inter_bold_64.py` | Bitmap font generated from **Inter Bold** v4.1, © 2016 The Inter Project Authors ([rsms/inter](https://github.com/rsms/inter)) | SIL Open Font License 1.1 — see [LICENSES/OFL-1.1.txt](LICENSES/OFL-1.1.txt) |

## Waveshare demo code

`accelerometer.py` and `touch_engine.py` are derived from the MicroPython
example code that Waveshare publishes for the RP2040-Touch-LCD-1.28 board.
Waveshare provides this demo code publicly for use with its hardware.
The original code is © Waveshare; the modifications made in this project
(motion-detection configuration, CTRL9 command timeout, signed 16-bit
conversion fix, CST816G chip detection, I2C error handling) are licensed
under the MIT License.

If you are the rights holder and have concerns about this use, please open
an issue.

## Font

`inter_bold_64.py` contains a bitmap rendering (digits, `%`, `.` and `-` only) of the
Inter Bold typeface, generated with `write_font_converter.py` from
[russhughes/gc9a01_mpy](https://github.com/russhughes/gc9a01_mpy) (MIT):

```
write_font_converter.py Inter-Bold.ttf 64 -s "1234567890%.-"
```

As a derivative of the Font Software, this file is distributed under the
SIL Open Font License 1.1, not the MIT License.

## Runtime dependencies (not included)

- [russhughes/gc9a01_mpy](https://github.com/russhughes/gc9a01_mpy) (MIT) —
  MicroPython firmware with the built-in `gc9a01` display driver module.
- [MicroPython](https://micropython.org/) (MIT).
