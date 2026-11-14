# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-14

First public release.

### Added

- Water level measurement with an US-015 / HC-SR04 ultrasonic sensor, averaged over several measurements with outlier filtering.
- Display of the level in percent with a colored ring (blue / orange / red) on the Waveshare RP2040-Touch-LCD-1.28, updated incrementally without flicker.
- Screen wake-up via motion (QMI8658 IMU) and tap (CST816T / CST816G touch controller); screen turns off after a configurable timeout.
- Background measurements at a longer interval while the screen is off.
- `config.py` as the single place for all user settings: tank calibration (`DISTANCE_FULL_CM`, `DISTANCE_EMPTY_CM`), colors and thresholds, timings, wake-up options, motion sensitivity, pins.
- Calibration mode (`CALIBRATION_MODE`) that shows the measured distance in cm on the display.
- Validation of the calibration values with a clear error message.
- Graceful fallback when the IMU or touch controller is not detected.
- `DEBUG` switch for detailed serial output.
- README in English and German with wiring diagram (including the Echo voltage divider), calibration diagram and photos.
- MIT license, third-party notices and license texts; display font Inter Bold (SIL Open Font License).

[Unreleased]: https://github.com/marcelrebmann/espresso-machine-waterlevel/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/marcelrebmann/espresso-machine-waterlevel/releases/tag/v1.0.0
