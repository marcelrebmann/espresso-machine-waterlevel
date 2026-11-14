# Minimal logging helpers controlled by config.DEBUG.

import config


def debug(*args):
    """Print only when config.DEBUG is enabled."""
    if config.DEBUG:
        print(*args)


def warn(*args):
    """Always print: problems the user should see on the serial console."""
    print("WARNING:", *args)
