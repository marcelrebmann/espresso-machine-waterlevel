import time
import math
from ultrasonic_sensor import UltrasonicSensor
from accelerometer import QMI8658
import utime
from screen_driver import ScreenDriver
from colors import Colors
from touch_engine import Touch_CST816T


BOTTOM_WATER_LVL_CM = 17
UPPER_WATER_LVL_CM = 3
DEBUG_MODE = True

# Intervals and thresholds in seconds
LCD_NO_MOTION_TIMEOUT = 180
WATERLVL_READOUT_INTERVAL_ACTIVE = 10
WATERLVL_READOUT_INTERVAL_INACTIVE = 60

def main():

    utime.sleep_ms(500)

    # Initialize the accelerometer
    qmi8658 = QMI8658()
    qmi8658.configure_motion_detection()
    utime.sleep_ms(500)

    # Initialize the TFT display and fill it with black color
    lcd = ScreenDriver()

    # Initialize the touch sensor
    cst816s = Touch_CST816T()
    touch_available = cst816s.detected
    if touch_available:
        cst816s.Set_Mode(0)
    else:
        print("Touch sensor not available -- using motion-only wake")

    # Initialize the ultrasonic sensor
    ultrasonicSensor = UltrasonicSensor(UPPER_WATER_LVL_CM, BOTTOM_WATER_LVL_CM)

    # Center of the display
    center_x = 120
    center_y = 120

    # The radii of the arcs are equal to the half of the display's dimensions
    radius = 120

    colors = Colors()

    def redraw(level, clear=True):
        if clear:
            lcd.fill_screen()
        lcd.draw_score(center_x, center_y, level, colors.WHITE)
        lcd.draw_arc_perf(center_x, center_y, radius, 0, math.ceil((level / 100) * 360), colors.get_arc_color(level))

    last_reading = None
    last_reading_time = None
    # Start with the screen on so the first reading is visible after boot
    lcd.screen_on()
    is_active = True
    screen_last_turnedon = utime.time()

    try:
        while True:
            time.sleep_ms(250)

            touched = cst816s.is_touch_detected() if touch_available else False
            try:
                motion = qmi8658.is_any_motion_detected()
            except OSError as ex:
                print("IMU read error: ", ex)
                motion = False

            if motion:
                print("Motion detected: ", motion)
            if touched:
                print("Touch detected: ", touched)

            if motion or touched:
                if not is_active:
                    print("Interaction detected -- Set active")
                    # Redraw the last reading (the screen is not updated while it is off)
                    lcd.fill_screen()
                    lcd.screen_on()
                    if last_reading is not None:
                        redraw(last_reading, clear=False)
                    is_active = True
                screen_last_turnedon = utime.time()

            elif is_active and utime.time() - screen_last_turnedon > LCD_NO_MOTION_TIMEOUT:
                # Turn off the screen if no interaction happened for LCD_NO_MOTION_TIMEOUT seconds
                print("No interaction -- Set inactive")
                lcd.screen_off()
                is_active = False

            # Readout waterlvl when the screen is on every 10 seconds, otherwise every 60 seconds in the background.
            waterlvl_readout_interval = WATERLVL_READOUT_INTERVAL_ACTIVE if is_active else WATERLVL_READOUT_INTERVAL_INACTIVE
            if last_reading_time is not None and utime.time() - last_reading_time < waterlvl_readout_interval:
                continue

            waterlevel_percent = ultrasonicSensor.read_waterlevel()
            last_reading_time = utime.time()

            # Skip invalid readings and readings equal to the last one
            if waterlevel_percent is None or waterlevel_percent == last_reading:
                continue

            previous_reading = last_reading
            last_reading = waterlevel_percent

            # The screen is fully redrawn on wake-up, so don't draw while it is off
            if not is_active:
                continue

            if previous_reading is None or colors.get_arc_color(previous_reading) != colors.get_arc_color(waterlevel_percent):
                # First reading or color change: full redraw
                redraw(waterlevel_percent)
                continue

            last_arc_end_angle = math.ceil((previous_reading / 100) * 360)
            arc_end_angle = math.ceil((waterlevel_percent / 100) * 360)
            lcd.update_score(center_x, center_y, waterlevel_percent, previous_reading, colors.WHITE)
            if arc_end_angle > last_arc_end_angle:
                # Expand the arc
                lcd.draw_arc_perf(center_x, center_y, radius, last_arc_end_angle, arc_end_angle, colors.get_arc_color(waterlevel_percent))
            elif arc_end_angle < last_arc_end_angle:
                # Shrink the arc
                lcd.draw_arc_perf(center_x, center_y, radius, arc_end_angle, last_arc_end_angle, colors.BLACK)
    except KeyboardInterrupt:
        print("Exiting...")
        lcd.screen_off()


if __name__ == "__main__":
    main()
