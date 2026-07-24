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
    # cst816s.Set_Mode(0)

    # Initialize the ultrasonic sensor
    ultrasonicSensor = UltrasonicSensor(UPPER_WATER_LVL_CM, BOTTOM_WATER_LVL_CM)

    # Center of the display
    center_x = 120
    center_y = 120

    # The radii of the arcs are equal to the half of the display's dimensions
    radius = 120

    colors = Colors()

    last_reading = 0
    screen_last_turnedon = 0
    last_reading_time = 0
    is_active = False

    try:
        while True:

            touched = cst816s.is_touch_detected()
            motion = qmi8658.is_any_motion_detected()

            if motion:
                print("Motion detected: ", motion)
            if touched:
                print("Touch detected: ", touched)

            if motion or touched:
                print("Interaction detected -- Set active: ")
                if not is_active:
                    # Redraw the last reading arc with the new color
                    lcd.fill_screen()
                    arc_color = colors.get_arc_color(last_reading)
                    arc_end_angle = math.ceil((last_reading / 100) * 360)
                    lcd.screen_on()
                    lcd.draw_score(center_x, center_y, last_reading)
                    lcd.draw_arc_perf(center_x, center_y, radius, 0, arc_end_angle, arc_color)
                    is_active = True
                screen_last_turnedon = utime.time()

            else:
                # Turn off the screen if no motion is detected for 180 seconds
                if utime.time() - screen_last_turnedon > LCD_NO_MOTION_TIMEOUT:
                    lcd.screen_off()
                    is_active = False

            # Readout waterlvl when the screen is on every 10 seconds, otherwise every 60 seconds in the background.
            current_time = utime.time()
            seconds_since_last_reading = current_time - last_reading_time
            waterlvl_readout_interval = WATERLVL_READOUT_INTERVAL_ACTIVE

            # Skip if not enough time has passed since the last reading
            if seconds_since_last_reading < waterlvl_readout_interval:        
                continue

            waterlevel_percent = ultrasonicSensor.read_waterlevel()
            last_reading_time = utime.time()

            # Skip if the reading is the same as the last one
            if waterlevel_percent == last_reading:
                continue
            
            # Turn the screen on if it's off but a new different waterlevel has been detected
            # if not is_active:
            #     lcd.screen_on()
            #     is_active = True
            #     screen_last_turnedon = utime.time()
            
            # Store last reading information
            last_reading_arc_end_angle = math.ceil((last_reading / 100) * 360)
            arc_color_last_reading = colors.get_arc_color(last_reading) 

            # Update last reading with current reading
            last_reading = waterlevel_percent

            arc_color = colors.get_arc_color(waterlevel_percent)

            arc_end_angle = math.ceil((waterlevel_percent / 100) * 360)

            if arc_color_last_reading != arc_color:
                # Redraw the last reading arc with the new color
                lcd.fill_screen()
                lcd.draw_score(center_x, center_y, waterlevel_percent, colors.WHITE)
                lcd.draw_arc_perf(center_x, center_y, radius, 0, arc_end_angle, arc_color)
            elif arc_end_angle > last_reading_arc_end_angle:
                # Expand the arc
                # lcd.draw_rectangle(40, 60, 160, 120, colors.BLACK)
                # lcd.draw_score(center_x, center_y, waterlevel_percent)
                lcd.update_score(center_x, center_y, waterlevel_percent, last_reading, colors.WHITE)
                lcd.draw_arc_perf(center_x, center_y, radius, last_reading_arc_end_angle, arc_end_angle, arc_color)
            elif arc_end_angle < last_reading_arc_end_angle:
                # Shrink the arc
                # lcd.draw_rectangle(40, 60, 160, 120, colors.BLACK)
                # lcd.draw_score(center_x, center_y, waterlevel_percent)
                lcd.update_score(center_x, center_y, waterlevel_percent, last_reading, colors.WHITE)
                lcd.draw_arc_perf(center_x, center_y, radius, arc_end_angle, last_reading_arc_end_angle, colors.BLACK)

            time.sleep_ms(250)
    except KeyboardInterrupt:
        print("Exiting...")
        is_active = False
        lcd.screen_off()


if __name__ == "__main__":
    main()
