import gc9a01
import config


class Colors:
    OK = gc9a01.color565(*config.COLOR_OK)
    LOW = gc9a01.color565(*config.COLOR_LOW)
    CRITICAL = gc9a01.color565(*config.COLOR_CRITICAL)
    TEXT = gc9a01.color565(*config.COLOR_TEXT)
    BLACK = gc9a01.color565(0, 0, 0)
    WHITE = gc9a01.color565(255, 255, 255)

    @staticmethod
    def get_arc_color(waterlevel_percent):
        if waterlevel_percent <= config.LEVEL_CRITICAL_PERCENT:
            return Colors.CRITICAL
        elif waterlevel_percent <= config.LEVEL_LOW_PERCENT:
            return Colors.LOW
        else:
            return Colors.OK
