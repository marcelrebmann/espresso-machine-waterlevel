import gc9a01

class Colors:
    BLUE = gc9a01.color565(3, 169, 244)
    ORANGE = gc9a01.color565(255, 152, 0)
    RED = gc9a01.color565(244, 67, 54)
    BLACK = gc9a01.color565(0, 0, 0)
    WHITE = gc9a01.color565(255, 255, 255)

    def get_arc_color(self, waterlevel_percent):
        if waterlevel_percent <= 10:
            return Colors.RED
        elif waterlevel_percent <= 25:
            return Colors.ORANGE
        else:
            return Colors.BLUE