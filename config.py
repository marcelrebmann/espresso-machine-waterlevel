# User configuration.
#
# This is the only file you should need to edit to adapt the water level
# indicator to your machine. All distances are measured from the front of the
# ultrasonic sensor down to the water surface.
#
#     ====[sensor]====   <- tank lid
#     |              |      ^                 ^
#     |              |      | DISTANCE_FULL   |
#     |~~~~~~~~~~~~~~|      v  (100 %)        | DISTANCE_EMPTY
#     |    water     |                        |
#     |~~~~~~~~~~~~~~|                        v  (0 %)
#     |______________|
#
# How to calibrate:
#   1. Set CALIBRATION_MODE = True and upload the code.
#   2. The display now shows the measured distance in cm.
#   3. Fill the tank to the level you consider "full" -> note the value.
#   4. Drain it to the level you consider "empty"    -> note the value.
#   5. Enter both values below and set CALIBRATION_MODE = False again.

# --------------------------------------------------------------------------
# Tank calibration
# --------------------------------------------------------------------------

# Distance (cm) between sensor and water surface when the tank is full (100 %).
# The HC-SR04 cannot measure closer than ~2-3 cm, so keep this above that.
DISTANCE_FULL_CM = 3

# Distance (cm) between sensor and water surface when the tank is empty (0 %).
DISTANCE_EMPTY_CM = 17

# Show the raw distance in cm instead of the level in percent (see above).
CALIBRATION_MODE = False

# Number of single measurements averaged into one reading (outliers removed).
MEASUREMENTS_PER_READING = 10

# Measurements above this distance (cm) are treated as sensor errors.
# The HC-SR04 reports very large values when no echo is received.
MAX_PLAUSIBLE_DISTANCE_CM = 100

# --------------------------------------------------------------------------
# Display
# --------------------------------------------------------------------------

# Level thresholds (percent) for the arc color.
LEVEL_CRITICAL_PERCENT = 10   # at or below: COLOR_CRITICAL
LEVEL_LOW_PERCENT = 25        # at or below: COLOR_LOW, above: COLOR_OK

# Arc colors as (R, G, B), 0-255.
COLOR_OK = (3, 169, 244)       # blue
COLOR_LOW = (255, 152, 0)      # orange
COLOR_CRITICAL = (244, 67, 54) # red
COLOR_TEXT = (255, 255, 255)   # white

# Display rotation: 0, 1, 2 or 3 (steps of 90 degrees).
DISPLAY_ROTATION = 0

# Width of the level arc in pixels.
ARC_WIDTH_PX = 10

# --------------------------------------------------------------------------
# Timing (seconds)
# --------------------------------------------------------------------------

# Turn the screen off after this many seconds without motion or touch.
# Set to 0 to keep the screen on permanently.
SCREEN_TIMEOUT_S = 180

# How often the water level is measured while the screen is on / off.
READOUT_INTERVAL_ACTIVE_S = 10
READOUT_INTERVAL_INACTIVE_S = 60

# --------------------------------------------------------------------------
# Wake-up
# --------------------------------------------------------------------------

# Wake the screen when the machine is moved or vibrates (e.g. pump, lever).
WAKE_ON_MOTION = True

# Wake the screen with a single tap on the display.
WAKE_ON_TOUCH = True

# Acceleration (g) that counts as motion. Lower = more sensitive.
# Range 0.03 - 7.9 g.
MOTION_THRESHOLD_G = 0.25

# Number of consecutive samples above the threshold before motion is reported.
# Higher = fewer false wake-ups from short knocks.
MOTION_WINDOW_SAMPLES = 10

# --------------------------------------------------------------------------
# Debugging
# --------------------------------------------------------------------------

# Print detailed measurement and event logs to the serial console.
DEBUG = False

# --------------------------------------------------------------------------
# Pins — defaults match the Waveshare RP2040-Touch-LCD-1.28.
# Only the ultrasonic sensor pins usually need to be changed.
# --------------------------------------------------------------------------

# HC-SR04 ultrasonic sensor
PIN_ULTRASONIC_TRIGGER = 16
PIN_ULTRASONIC_ECHO = 17

# I2C bus shared by the IMU (QMI8658) and the touch controller (CST816)
I2C_ID = 1
PIN_I2C_SDA = 6
PIN_I2C_SCL = 7
I2C_FREQ_HZ = 400_000

# Touch controller
PIN_TOUCH_INT = 21
PIN_TOUCH_RST = 22

# GC9A01 display (SPI)
SPI_ID = 1
PIN_LCD_SCK = 10
PIN_LCD_MOSI = 11
PIN_LCD_RST = 13
PIN_LCD_CS = 9
PIN_LCD_DC = 8
PIN_LCD_BACKLIGHT = 25
