# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

First public release, planned as **1.0.0**.

### Added

- `config.py` as the single place for all user settings: tank calibration, colors and thresholds, timings, wake-up options, pins.
- Calibration mode (`CALIBRATION_MODE`) that shows the measured distance in cm on the display.
- Configurable motion sensitivity in g (`MOTION_THRESHOLD_G`, `MOTION_WINDOW_SAMPLES`).
- Wake-up via motion and touch can be disabled individually; `SCREEN_TIMEOUT_S = 0` keeps the screen on permanently.
- Validation of the calibration values with a clear error message.
- `DEBUG` switch for detailed serial output (`log.py`).
- Support for the CST816G touch controller used on newer Waveshare boards.
- README in English and German with wiring diagram, calibration diagram and photos.
- MIT license, third-party notices and license texts.

### Changed

- Calibration constants renamed: `UPPER_WATER_LVL_CM` → `DISTANCE_FULL_CM`, `BOTTOM_WATER_LVL_CM` → `DISTANCE_EMPTY_CM`.
- Display font replaced with Inter Bold (SIL Open Font License); the previously used Helvetica Neue is not freely redistributable.
- IMU and touch controller share one I2C bus instance.
- The screen is on after boot so the first reading is visible immediately.
- Readings are taken every 60 s while the screen is off (previously always every 10 s).
- Motion threshold raised to 0.25 g with a 10-sample window to reduce false wake-ups.

### Fixed

- Display could stay off after boot or not wake reliably.
- Device hung during startup when the IMU did not confirm a configuration command (now times out).
- Wrong sign conversion of negative IMU readings.
- Sensor timeouts (no echo) were treated as valid ~500 cm readings.
- Program crashed when no touch controller was detected; touch wake is now disabled instead.
