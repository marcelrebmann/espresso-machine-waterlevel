import math
import time
from machine import Pin, SPI
import gc9a01
import inter_bold_64 as font
import config
from colors import Colors


class ScreenDriver:
    WIDTH = 240
    HEIGHT = 240
    arc_resolution = 1

    # Widest text that is ever drawn; used to clear the text area before redrawing
    WIDEST_TEXT = "100%"

    def __init__(self):
        """Configure the GC9A01 display from the pins in config.py."""
        spi = SPI(config.SPI_ID, baudrate=60_000_000,
                  sck=Pin(config.PIN_LCD_SCK), mosi=Pin(config.PIN_LCD_MOSI))
        self.tft = gc9a01.GC9A01(
            spi,
            self.WIDTH,
            self.HEIGHT,
            reset=Pin(config.PIN_LCD_RST, Pin.OUT),
            cs=Pin(config.PIN_LCD_CS, Pin.OUT),
            dc=Pin(config.PIN_LCD_DC, Pin.OUT),
            backlight=Pin(config.PIN_LCD_BACKLIGHT, Pin.OUT),
            rotation=config.DISPLAY_ROTATION,
            options=0,
            buffer_size=0
        )
        self.arc_width_px = config.ARC_WIDTH_PX
        self.tft.init()
        self.tft.fill(0)

    def screen_on(self):
        self.tft.on()

    def screen_off(self):
        self.tft.off()

    def fill_screen(self, color=Colors.BLACK):
        self.tft.fill(color)

    # x_start, y_start: top left corner
    def draw_rectangle(self, x_start, y_start, width, height, color):
        self.tft.fill_rect(x_start, y_start, width, height, color)

    def draw_arc_perf(self, x, y, radius, start_angle, end_angle, color):
        """Draw a ring segment from start_angle to end_angle (degrees, clockwise from 3 o'clock)."""
        if start_angle == end_angle:
            return

        inner_radius = radius - self.arc_width_px
        outer_radius = radius
        step = self.arc_resolution

        for angle in range(start_angle, end_angle, step):
            angle_rad = math.radians(angle)
            next_angle_rad = math.radians(angle + step)

            x1_outer = x + int(outer_radius * math.cos(angle_rad))
            y1_outer = y + int(outer_radius * math.sin(angle_rad))
            x2_outer = x + int(outer_radius * math.cos(next_angle_rad))
            y2_outer = y + int(outer_radius * math.sin(next_angle_rad))

            x1_inner = x + int(inner_radius * math.cos(angle_rad))
            y1_inner = y + int(inner_radius * math.sin(angle_rad))
            x2_inner = x + int(inner_radius * math.cos(next_angle_rad))
            y2_inner = y + int(inner_radius * math.sin(next_angle_rad))

            self.tft.fill_polygon(
                [(x1_outer, y1_outer), (x2_outer, y2_outer), (x2_inner, y2_inner),
                 (x1_inner, y1_inner), (x1_outer, y1_outer)],
                0, 0, color)
            time.sleep_ms(5)

    def draw_text(self, center_x, center_y, text, color=Colors.TEXT):
        """Draw text centered on (center_x, center_y). Only glyphs contained in the font are rendered."""
        offset_x = self.tft.write_len(font, text) // 2
        self.tft.write(font, text, center_x - offset_x, center_y - (font.HEIGHT // 2), color)

    def update_text(self, center_x, center_y, text, color=Colors.TEXT):
        """Clear the text area and draw new text, without touching the arc."""
        clear_width = self.tft.write_len(font, self.WIDEST_TEXT)
        self.draw_rectangle(center_x - clear_width // 2, center_y - (font.HEIGHT // 2),
                            clear_width, font.HEIGHT, Colors.BLACK)
        self.draw_text(center_x, center_y, text, color)

    def draw_score(self, center_x, center_y, score, color=Colors.TEXT):
        self.draw_text(center_x, center_y, "{0}%".format(score), color)

    def update_score(self, center_x, center_y, new_score, color=Colors.TEXT):
        self.update_text(center_x, center_y, "{0}%".format(new_score), color)
