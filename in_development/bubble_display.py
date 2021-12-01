# LED bubble display widget
# based on the HP QDSP-6064 4-Digit Micro 7 Segment Numeric Indicator
# 2021-11-30 v0.66

import displayio
import vectorio
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect

# 8-bit to 7 segment
#  bits: dp g f e d c b a
NUMBERS = {
    '0': 0b00111111,  # 0
    '1': 0b00000110,  # 1
    '2': 0b01011011,  # 2
    '3': 0b01001111,  # 3
    '4': 0b01100110,  # 4
    '5': 0b01101101,  # 5
    '6': 0b01111101,  # 6
    '7': 0b00000111,  # 7
    '8': 0b01111111,  # 8
    '9': 0b01101111,  # 9
    'a': 0b01110111,  # a
    'b': 0b01111100,  # b
    'c': 0b00111001,  # C
    'd': 0b01011110,  # d
    'e': 0b01111001,  # E
    'f': 0b01110001,  # F
    '-': 0b01000000,  # -
    '.': 0b10000000,  # .
    " ": 0b00000000,  # <space>
    'x': 0b00001000,  # _ (replace x with underscore for hexadecimal text)
}


class Colors:
    # Define a few colors (https://en.wikipedia.org/wiki/Web_colors)
    BLACK = 0x000000
    RED = 0xFF0000
    RED_PKG = 0x701010
    RED_BKG = 0x501010
    RED_LENS = 0x901010
    WHITE = 0xFFFFFF


class BubbleDisplay:
    def __init__(self, units=0, mode='Normal', center=(0, 0), size=1, display_size=(None, None)):
        self._mode = mode
        self._size = size
        self._cluster_group = displayio.Group(scale=self._size)
        self._cluster = displayio.Group(scale=size)
        self._digits = displayio.Group(scale=size)

        self._units = units
        self._origin = center

        for chip in range(0, self._units):
            upper_left_corner = (self._origin[0] + (60 * chip), self._origin[1])
            dip_package = Rect(
                upper_left_corner[0],
                upper_left_corner[1],
                60,
                25,
                fill=Colors.RED_PKG,
            )
            self._cluster.append(dip_package)

            dip_index = Rect(
                2 + upper_left_corner[0],
                24 + upper_left_corner[1],
                2,
                2,
                fill=Colors.BLACK,
            )
            self._cluster.append(dip_index)

            for i in range(0, 4):
                lens = RoundRect(
                    upper_left_corner[0] + (i * 15),
                    0 + upper_left_corner[1],
                    15,
                    25,
                    7,
                    fill=Colors.RED_BKG,
                    outline=Colors.RED_LENS,
                )
                self._cluster.append(lens)

                seg_a = Line(
                    4 + upper_left_corner[0] + (i * 15) + 1,
                    6 + upper_left_corner[1],
                    4 + upper_left_corner[0] + (i * 15) + 6 + 1,
                    6 + upper_left_corner[1],
                    color=Colors.RED_BKG,
                )
                self._digits.append(seg_a)

                seg_b = Line(
                    4 + upper_left_corner[0] + (i * 15) + 6 + 1,
                    6 + upper_left_corner[1],
                    4 + upper_left_corner[0] + (i * 15) + 6,
                    12 + upper_left_corner[1],
                    color=Colors.RED_BKG,
                )
                self._digits.append(seg_b)

                seg_c = Line(
                    4 + upper_left_corner[0] + (i * 15) + 6,
                    12 + upper_left_corner[1],
                    4 + upper_left_corner[0] + (i * 15) + 6 - 1,
                    18 + upper_left_corner[1],
                    color=Colors.RED_BKG,
                )
                self._digits.append(seg_c)

                seg_d = Line(
                    4 + upper_left_corner[0] + (i * 15) - 1,
                    18 + upper_left_corner[1],
                    4 + upper_left_corner[0] + (i * 15) + 6 - 1,
                    18 + upper_left_corner[1],
                    color=Colors.RED_BKG,
                )
                self._digits.append(seg_d)

                seg_e = Line(
                    4 + upper_left_corner[0] + (i * 15),
                    12 + upper_left_corner[1],
                    4 + upper_left_corner[0] + (i * 15) - 1,
                    18 + upper_left_corner[1],
                    color=Colors.RED_BKG,
                )
                self._digits.append(seg_e)

                seg_f = Line(
                    4 + upper_left_corner[0] + (i * 15) + 1,
                    6 + upper_left_corner[1],
                    4 + upper_left_corner[0] + (i * 15),
                    12 + upper_left_corner[1],
                    color=Colors.RED_BKG,
                )
                self._digits.append(seg_f)

                seg_g = Line(
                    4 + upper_left_corner[0] + (i * 15),
                    12 + upper_left_corner[1],
                    4 + upper_left_corner[0] + (i * 15) + 6,
                    12 + upper_left_corner[1],
                    color=Colors.RED_BKG,
                )
                self._digits.append(seg_g)

                seg_dp = Rect(
                    4 + upper_left_corner[0] + (i * 15) + 6 + 1,
                    18 + upper_left_corner[1],
                    2,
                    2,
                    fill=Colors.RED_BKG,
                )
                self._digits.append(seg_dp)

        self._cluster_group.append(self._cluster)
        self._cluster_group.append(self._digits)
        return

    @property
    def display_group(self):
        """Displayio cluster group."""
        return self._cluster_group

    @property
    def units(self):
        """Number of units."""
        return self._units

    @property
    def value(self):
        """Currently displayed value."""
        return self._value

    @value.setter
    def value(self, value=None, mode='Normal'):
        self._show_value(value, mode)

    @property
    def text(self):
        """Currently displayed text."""
        return self._text

    @text.setter
    def text(self, text=''):
        self._show_text(text)

    # @property
    # def center(self, cluster=0):
    #    """Normalized display coordinates of the object center."""
    #    determine center of cluster specified by the cluster parameter
    #    SHOULD THIS BE A FUNCTION?
    #    return

    # @centersetter
    # def center(self, cluster=0, x, y):
    #    """Set the normalized display coordinates of the object center."""
    #    procedure for setting all coordinates for a cluster
    #    as specified by the cluster parameter
    #    SHOULD THIS BE A FUNCTION?
    #    return

    def _show_text(self, text=''):
        text = text[0 : self._units * 4]  # truncate to left-most digits
        text = (' ' * ((self._units * 4) - len(text))) + text

        for _digit in range(0, self._units * 4):
            if text[_digit] in NUMBERS:
                _decode = NUMBERS[text[_digit]]
            else:
                _decode = NUMBERS[' ']
            for _segment in range(0, 8):
                if _decode & pow(2, _segment):
                    self._digits[(_digit * 8) + _segment].color = Colors.RED
                    self._digits[(_digit * 8) + _segment].fill = Colors.RED
                else:
                    self._digits[(_digit * 8) + _segment].color = Colors.RED_BKG
                    self._digits[(_digit * 8) + _segment].fill = Colors.RED_BKG

    def _show_value(self, value=None, mode='Normal'):
        """ use mode='HP-35' for decimal point between digits """
        self._mode = mode
        if value == None:
            _display = ''
        else:
            _display = str(value)

        # if value string is larger than can be displayed, show dashes
        if len(_display) > self._units * 4:
            _display = '-' * self._units * 4
        else:
            _display = (' ' * ((self._units * 4) - len(_display))) + _display

        # locate decimal point and remove from display string
        dp_digit = _display.find(".")
        if dp_digit > -1 and self._mode != 'HP-35':
            _display = ' ' + _display[0 : dp_digit] + _display[dp_digit + 1 :]

        self._show_text(_display)

        # clear all decimal points and plot the current point
        for digit in range(0, self._units * 4):
            self._digits[(digit * 8) + 7].fill = Colors.RED_BKG
        if dp_digit > -1:
            self._digits[(dp_digit * 8) + 7].fill = Colors.RED
        return

    def display_to_pixel(self, width_factor=0, height_factor=0, size=1.0):
        """Convert normalized display position input (0.0 to 1.0) to display
        pixel position."""
        return int(round(size * self.WIDTH * width_factor, 0)), int(
            round(size * self.HEIGHT * height_factor, 0)
        )

    def dial_to_pixel(self, dial_factor, center=(0, 0), radius=0):
        """Convert normalized dial_factor input (-1.0 to 1.0) to display pixel
        position on the circumference of the dial's circle with center
        (x,y pixels) and radius (pixels)."""
        rads = (-2 * pi) * (dial_factor)  # convert scale_factor to radians
        rads = rads + (pi / 2)  # rotate axis counterclockwise
        x = center[0] + int(cos(rads) * radius)
        y = center[1] - int(sin(rads) * radius)
        return x, y

    def cart_to_pixel(self, x, y, size=1.0):
        """Convert normalized cartesian position value (-0.5, to + 0.5) to display
        pixels."""
        min_axis = min(self.WIDTH, self.HEIGHT)
        x1 = int(round(min_axis * size * x, 0)) + self._center[0]
        y1 = self._center[1] - int(round(min_axis * size * y, 0))
        return x1, y1

    def cart_dist_to_pixel(self, distance=0, size=1.0):
        """Convert normalized cartesian distance value to display pixels."""
        min_axis = min(self.WIDTH, self.HEIGHT)
        return int(round(min_axis * size * distance, 0))
