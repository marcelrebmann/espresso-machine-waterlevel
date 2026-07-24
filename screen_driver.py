import math
import time
import helvetica_neue_bold_64 as helvetica
from colors import Colors
from machine import Pin, SPI
import gc9a01

class ScreenDriver:
    arc_width_px = 10
    arc_resolution = 1

    # TFT options
    TFA = 0
    BFA = 0
    WIDE = 0
    TALL = 1

    def __init__(self):
        """Configure the display and return an instance of gc9a01.GC9A01."""
        spi = SPI(1, baudrate=60000000, sck=Pin(10), mosi=Pin(11))
        self.tft = gc9a01.GC9A01(
            spi,
            240,
            240,
            reset=Pin(13, Pin.OUT),
            cs=Pin(9, Pin.OUT),
            dc=Pin(8, Pin.OUT),
            backlight=Pin(25, Pin.OUT),
            rotation=0,
            options=self.WIDE,
            buffer_size=0
        )
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

        if start_angle == end_angle:
            return

        # Define the inner and outer radii for the arc
        inner_radius = radius - self.arc_width_px  # Inner edge of the arc
        outer_radius = radius  # Outer edge of the arc
        step = self.arc_resolution  # Step size to draw bigger segments (arc resolution)

        # Create a list of points for the outer and inner arcs
        outer_points = []
        inner_points = []

        for angle in range(start_angle, end_angle, step):
            # Current and next angle in radians
            angle_rad = math.radians(angle)
            next_angle_rad = math.radians(angle + step)

            # Calculate the coordinates for the outer arc points
            x1_outer = x + int(outer_radius * math.cos(angle_rad))
            y1_outer = y + int(outer_radius * math.sin(angle_rad))
            x2_outer = x + int(outer_radius * math.cos(next_angle_rad))
            y2_outer = y + int(outer_radius * math.sin(next_angle_rad))

            # Calculate the coordinates for the inner arc points
            x1_inner = x + int(inner_radius * math.cos(angle_rad))
            y1_inner = y + int(inner_radius * math.sin(angle_rad))
            x2_inner = x + int(inner_radius * math.cos(next_angle_rad))
            y2_inner = y + int(inner_radius * math.sin(next_angle_rad))

            # Add the points for the outer arc (clockwise direction)
            outer_points.append((x1_outer, y1_outer))
            outer_points.append((x2_outer, y2_outer))
            # points.append((x, y))  # Add center point for outer triangle

            # Add the points for the inner arc (counter-clockwise direction)
            # points.append((x, y))  # Add center point for inner triangle
            inner_points.append((x1_inner, y1_inner))
            inner_points.append((x2_inner, y2_inner))


            self.tft.fill_polygon([(x1_outer, y1_outer), (x2_outer, y2_outer),(x2_inner, y2_inner), (x1_inner, y1_inner), (x1_outer, y1_outer)], 0, 0, color)  # Fill the entire 10-pixel wide arc
            time.sleep_ms(5)

        # points = outer_points + inner_points[::-1]
        # points.append(outer_points[0])
        # Fill the arc: First fill the outer area, then "cut out" the inner area by filling black
        # tft.fill_polygon(points, 0, 0, color)  # Fill the entire 10-pixel wide arc

    def draw_score(self, center_x, center_y, score, color=Colors.WHITE):
        scale = 2
        text = "{0}%".format(score)
        # offset_x = tft.draw_len(meteo, text, scale) // 2
        # tft.draw(meteo, text, center_x - offset_x, center_y, Colors.WHITE, scale)
        offset_x = self.tft.write_len(helvetica, text) // 2
        self.tft.write(helvetica, text, center_x - offset_x, center_y - (helvetica.HEIGHT // 2), color)

    def update_score(self, center_x, center_y, new_score, last_score, color=Colors.WHITE):
        # Always clear the full width of "100%" so no old digits remain
        text = "{0}%".format(100)
        text_length = self.tft.write_len(helvetica, text)
        offset_x = text_length // 2
        self.draw_rectangle(center_x - offset_x, center_y - (helvetica.HEIGHT // 2), text_length, helvetica.HEIGHT, Colors.BLACK)
        self.draw_score(center_x, center_y, new_score, color)
