import math
import utime
from machine import Pin, I2C

import config
import log
from accelerometer import QMI8658
from colors import Colors
from screen_driver import ScreenDriver
from touch_engine import Touch_CST816T
from ultrasonic_sensor import UltrasonicSensor

# Display geometry: the arc runs along the edge of the round 240x240 display
CENTER_X = 120
CENTER_Y = 120
RADIUS = 120

CALIBRATION_INTERVAL_MS = 1000


class LevelView:
    """Draws the level arc and a centered text, updating only what changed to avoid flicker."""

    def __init__(self, lcd):
        self.lcd = lcd
        self.level = None

    @staticmethod
    def _angle(level):
        return math.ceil((level / 100) * 360)

    def invalidate(self):
        """Force a full redraw on the next show() (e.g. after the screen was off)."""
        self.level = None

    def show(self, level, text):
        lcd = self.lcd
        previous = self.level
        self.level = level
        color = Colors.get_arc_color(level)

        if previous is None or Colors.get_arc_color(previous) != color:
            # First draw or color change: full redraw
            lcd.fill_screen()
            lcd.draw_text(CENTER_X, CENTER_Y, text)
            lcd.draw_arc_perf(CENTER_X, CENTER_Y, RADIUS, 0, self._angle(level), color)
            return

        lcd.update_text(CENTER_X, CENTER_Y, text)
        old_angle = self._angle(previous)
        new_angle = self._angle(level)
        if new_angle > old_angle:
            lcd.draw_arc_perf(CENTER_X, CENTER_Y, RADIUS, old_angle, new_angle, color)
        elif new_angle < old_angle:
            lcd.draw_arc_perf(CENTER_X, CENTER_Y, RADIUS, new_angle, old_angle, Colors.BLACK)


def init_motion_sensor(i2c):
    if not config.WAKE_ON_MOTION:
        return None
    try:
        imu = QMI8658(i2c)
        imu.configure_motion_detection(config.MOTION_THRESHOLD_G, config.MOTION_WINDOW_SAMPLES)
        return imu
    except OSError as ex:
        log.warn("IMU not available -- motion wake disabled:", ex)
        return None


def init_touch_sensor(i2c):
    if not config.WAKE_ON_TOUCH:
        return None
    touch = Touch_CST816T(i2c, int_pin=config.PIN_TOUCH_INT, rst_pin=config.PIN_TOUCH_RST)
    if not touch.detected:
        log.warn("touch not available -- touch wake disabled")
        return None
    touch.Set_Mode(0)
    return touch


def run_calibration(lcd, sensor):
    """Show the raw distance in cm so DISTANCE_FULL_CM / DISTANCE_EMPTY_CM can be determined."""
    print("CALIBRATION MODE: showing measured distance in cm")
    view = LevelView(lcd)
    lcd.screen_on()
    while True:
        distance = sensor.read_distance(clamp=False)
        if distance is None:
            view.invalidate()
            lcd.fill_screen()
            lcd.draw_text(CENTER_X, CENTER_Y, "--")
        else:
            level = sensor.distance_to_level(distance)
            print("Distance: {:.1f} cm -> level {} %".format(distance, level))
            view.show(level, "{:.1f}".format(distance))
        utime.sleep_ms(CALIBRATION_INTERVAL_MS)


def run(lcd, sensor, imu, touch):
    view = LevelView(lcd)
    screen_timeout_enabled = config.SCREEN_TIMEOUT_S > 0 and (imu is not None or touch is not None)
    if config.SCREEN_TIMEOUT_S > 0 and not screen_timeout_enabled:
        log.warn("no wake-up source available -- keeping the screen on permanently")

    last_level = None
    last_reading_time = None
    # Start with the screen on so the first reading is visible after boot
    lcd.screen_on()
    is_active = True
    last_interaction = utime.time()

    while True:
        utime.sleep_ms(250)

        touched = touch.is_touch_detected() if touch else False
        motion = False
        if imu:
            try:
                motion = imu.is_any_motion_detected()
            except OSError as ex:
                log.warn("IMU read error:", ex)

        if motion or touched:
            log.debug("Interaction: motion={} touch={}".format(motion, touched))
            if not is_active:
                log.debug("Screen on")
                # The screen is not updated while it is off, so redraw the last reading
                lcd.fill_screen()
                lcd.screen_on()
                view.invalidate()
                if last_level is not None:
                    view.show(last_level, "{}%".format(last_level))
                is_active = True
            last_interaction = utime.time()

        elif (screen_timeout_enabled and is_active
              and utime.time() - last_interaction > config.SCREEN_TIMEOUT_S):
            log.debug("No interaction -- screen off")
            lcd.screen_off()
            is_active = False

        interval = config.READOUT_INTERVAL_ACTIVE_S if is_active else config.READOUT_INTERVAL_INACTIVE_S
        if last_reading_time is not None and utime.time() - last_reading_time < interval:
            continue

        level = sensor.read_waterlevel()
        last_reading_time = utime.time()

        # Skip invalid readings and readings equal to the last one
        if level is None or level == last_level:
            continue
        last_level = level

        # Don't draw while the screen is off; it is fully redrawn on wake-up
        if is_active:
            view.show(level, "{}%".format(level))


def main():
    utime.sleep_ms(500)

    lcd = ScreenDriver()
    sensor = UltrasonicSensor(
        trigger_pin=config.PIN_ULTRASONIC_TRIGGER,
        echo_pin=config.PIN_ULTRASONIC_ECHO,
        distance_full_cm=config.DISTANCE_FULL_CM,
        distance_empty_cm=config.DISTANCE_EMPTY_CM,
        measurements_per_reading=config.MEASUREMENTS_PER_READING,
        max_plausible_distance_cm=config.MAX_PLAUSIBLE_DISTANCE_CM,
    )

    try:
        if config.CALIBRATION_MODE:
            run_calibration(lcd, sensor)
        else:
            i2c = I2C(config.I2C_ID, scl=Pin(config.PIN_I2C_SCL), sda=Pin(config.PIN_I2C_SDA),
                      freq=config.I2C_FREQ_HZ)
            imu = init_motion_sensor(i2c)
            touch = init_touch_sensor(i2c)
            run(lcd, sensor, imu, touch)
    except KeyboardInterrupt:
        print("Exiting...")
        lcd.screen_off()


if __name__ == "__main__":
    main()
