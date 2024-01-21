

import random


def hex_to_rgb(hex):
    return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def random_range(start, end):
    return start + random.random() * (end - start)


def clamp01(x):
    return max(0, min(1, x))


def lerp(a, b, t):
    return a + (b - a) * t
