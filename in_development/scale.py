# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# scale.py
# 2021-11-04 v0.3

import displayio
from math import pi, pow, sin, cos, sqrt
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_text.label import Label


class Palette:
    # Define a few colors (https://en.wikipedia.org/wiki/Web_colors)
    BLACK = 0x000000
    CYAN = 0x00FFFF
    BLUE = 0x0000FF
    BLUE_DK = 0x000080
    GRAY = 0x508080
    GREEN = 0x00FF00
    MAROON = 0x800000
    ORANGE = 0xFFA500
    PURPLE = 0x800080
    RED = 0xFF0000
    RED_DK = 0xA00000
    YELLOW = 0xFFFF00
    YELLOW_DK = 0x202000
    WHITE = 0xFFFFFF


class Scale:
    def __init__(self, max_scale=100, center=(0.50, 0.50), size=1.0, display_size=(None, None)):
        """Instantiate the scale graphic. Builds a displayio case group."""
        """Instantiate the dial graphic for PyPortal devices. Defaults to center
        at 0.5, 0.5 with a radius of 0.25 (normalized display units). Builds a
        displayio dial group.

        :param center: The dial center x,y tuple in normalized display units.
        :param radius: The dial radius in normalized display units."""

        # Determine default display size in pixels
        if None in display_size:
            import board
            if 'DISPLAY' in dir(board):
                self.WIDTH = board.DISPLAY.width
                self.HEIGHT = board.DISPLAY.height
            else:
                raise ValueError("No integral display. Specify display size.")
        else:
            self.WIDTH = display_size[0]
            self.HEIGHT = display_size[1]

        self._max_scale = max_scale

        self._size = size
        self._center_norm = center
        self._center = self.cartesian_to_pixel(0,0, self._size)

        self.FONT_0 = bitmap_font.load_font('/fonts/OpenSans-9.bdf')

        self._scale_group = displayio.Group()
        self._hands_group = displayio.Group()
        self._pivot_group = displayio.Group()

        self._sx0, self._sy0 = self._center
        self._sx1, self._sy1 = self.cartesian_to_pixel(-0.24, -0.33, self._size)
        self._sx2, self._sy2 = self.cartesian_to_pixel(0.24, -0.33, self._size)
        self._base = Triangle(
            self._sx0,
            self._sy0,
            self._sx1,
            self._sy1,
            self._sx2,
            self._sy2,
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._scale_group.append(self._base)

        self._sx, self._sy = self.cartesian_to_pixel(-0.25, -0.32, self._size)
        self._sw, self._sh = self.display_to_pixel(0.50, 0.08, self._size)
        self._foot = RoundRect(
            self._sx,
            self._sy,
            width=self._sw,
            height=self._sh,
            r=int(5 * self._size),
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._scale_group.append(self._foot)

        # Define moveable plate graphic
        self._sx, self._sy = self.cartesian_to_pixel(-0.05, 0.40, self._size)
        self._sw, self._sh = self.display_to_pixel(0.10, 0.40, self._size)
        self.riser = RoundRect(
            self._sx,
            self._sy,
            width=self._sw,
            height=self._sh,
            r=0,
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._scale_group.append(self.riser)

        self._sx, self._sy = self.cartesian_to_pixel(-0.25, 0.40, self._size)
        self._sw, self._sh = self.display_to_pixel(0.50, 0.08, self._size)
        self.plate = RoundRect(
            self._sx,
            self._sy,
            width=self._sw,
            height=self._sh,
            r=int(5 * self._size),
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._scale_group.append(self.plate)

        # Define primary dial graphic
        self._sx, self._sy = self._center
        self._outside_radius, self._ry = self.display_to_pixel(0.21, 0.21, self._size)
        self._major_radius = int(round(self._outside_radius * 0.88, 0))
        self._minor_radius = int(round(self._outside_radius * 0.93, 0))
        self._label_radius = int(round(self._outside_radius * 0.70, 0))
        self._dial = Circle(
            self._sx,
            self._sy,
            self._outside_radius,
            fill=Palette.BLUE_DK,
            outline=Palette.WHITE,
            stroke=1,
        )
        self._scale_group.append(self._dial)

        # Define hash marks
        self._point_radius = -5
        for i in range(0, self._max_scale, self._max_scale // 10):
            self._hash_value = Label(self.FONT_0, text=str(i), color=Palette.CYAN)
            self._hash_value.anchor_point = (0.5, 0.5)
            self._hash_value.anchored_position = self.dial_to_pixel(i / self._max_scale, center=self._center, radius=self._label_radius)
            self._scale_group.append(self._hash_value)

            # major hash marks
            self._x0, self._y0 = self.dial_to_pixel(i / self._max_scale, center=self._center, radius=self._major_radius)
            self._x1, self._y1 = self.dial_to_pixel(i / self._max_scale, center=self._center, radius=self._outside_radius)
            self._hash_mark_a = Line(self._x0, self._y0, self._x1, self._y1, Palette.CYAN)
            self._scale_group.append(self._hash_mark_a)

            # minor hash marks
            self._x0, self._y0 = self.dial_to_pixel((i + self._max_scale / 20) / self._max_scale, center=self._center, radius=self._minor_radius)
            self._x1, self._y1 = self.dial_to_pixel((i + self._max_scale / 20) / self._max_scale, center=self._center, radius=self._outside_radius)
            self._hash_mark_b = Line(self._x0, self._y0, self._x1, self._y1, Palette.CYAN)
            self._scale_group.append(self._hash_mark_b)

        # Define dial bezel graphic
        self._sx, self._sy = self.cartesian_to_pixel(0, 0, self._size)
        self._bezel = Circle(
            self._sx,
            self._sy,
            self._outside_radius + 1,
            fill=None,
            outline=Palette.BLACK,
            stroke=1,
        )
        self._scale_group.append(self._bezel)

        """self.hand_1_alarm = Circle(
            -50,
            -50,
            self._point_radius,
            fill=Palette.ORANGE,
            outline=Palette.ORANGE,
            stroke=self._point_stroke,
        )
        self._scale_group.append(self.hand_1_alarm)

        self.hand_2_alarm = Circle(
            -50,
            -50,
            self._point_radius,
            fill=Palette.GREEN,
            outline=Palette.GREEN,
            stroke=self._point_stroke,
        )
        self._scale_group.append(self.hand_2_alarm)"""

        self._x0, self._y0 = self.cartesian_to_pixel(0, 0, self._size)
        self._pivot = Circle(self._x0, self._y0, self._outside_radius // 14, fill=Palette.WHITE)
        self._pivot_group.append(self._pivot)

        self._scale_group.append(self._hands_group)
        self._scale_group.append(self._pivot_group)
        return


    @property
    def display_group(self):
        """Displayio scale group."""
        return self._scale_group

    @property
    def center(self):
        """Dial center normalized screen coordinates."""
        return self._center_norm

    def display_to_pixel(self, width_factor=0, height_factor=0, size=1.0):
        """Convert normalized display position input (0.0 to 1.0) to display
        pixel position."""
        return int(round(size * self.WIDTH * width_factor,0)), int(round(size * self.HEIGHT * height_factor, 0))

    def dial_to_pixel(self, dial_factor, center=(0, 0), radius=0):
        """Convert normalized dial_factor input (-1.0 to 1.0) to display pixel
        position on the circumference of the dial's circle with center
        (x,y pixels) and radius (pixels)."""
        self._rads = (-2 * pi) * (dial_factor)  # convert scale_factor to radians
        self._rads = self._rads + (pi / 2)  # rotate axis counterclockwise
        x = int(center[0] + (cos(self._rads) * radius))
        y = int(center[1] - (sin(self._rads) * radius))
        return x, y

    def cartesian_to_pixel(self, x, y, size=1.0):
        """Convert normalized cartesian value (-0.5, to + 0.5) to display
        pixel position."""
        x1 = (size * x) + self._center_norm[0]
        y1 = self._center_norm[1] - (size * y)
        return self.display_to_pixel(x1, y1, 1.0)


class Dial:
    def __init__(self, center=(0.50, 0.50), radius=0.25, display_size=(None, None)):
        """Instantiate the dial graphic for PyPortal devices. Defaults to center
        at 0.5, 0.5 with a radius of 0.25 (normalized display units).
        Display size in pixels is specified as an integer tuple. If the
        display_size tuple is not specified and an integral display is listed
        in the board class, the display_size tuple will be equal to the
        integral display width and height.
        Builds a displayio dial group.

        :param center: The dial center x,y tuple in normalized display units.
        :param radius: The dial radius in normalized display units.
        :param display_size: The host display's integer width and height tuple
        expressed in pixels. If (None, None) and the host includes an integral
        display, the value is (board.DISPLAY.width, board.DISPLAY.height)."""


        self._point_stroke = 2
        self._point_diameter = int((Screen.HEIGHT * 0.03) + (2 * self._point_stroke))
        self._point_radius = self._point_diameter // 2

        return


    def plot_needles(self, pointer_1=0, pointer_2=0):
        """Display channel 1 and 2 indicator needles and move scale plate
        proportionally. Input is normalized for 0.0 to 1.0 (minimum and maximum
        range), but accepts any floating point value.

        :param pointer_1: The normalized first needle position on the dial circumference.
        :param pointer_1: The normalized second needle position on the dial circumference."""

        if pointer_1 != min(1.0, max(pointer_1, 0.0)):
            self._hand_1_outline = Palette.RED
        else:
            self._hand_1_outline = Palette.ORANGE

        if pointer_2 != min(1.0, max(pointer_2, 0.0)):
            self._hand_2_outline = Palette.RED
        else:
            self._hand_2_outline = Palette.GREEN

        self._base = self.RADIUS // 10
        self._sx0, self._sy0 = display_to_pixel(0.00, 0.16)
        self._sx1, self._sy1 = display_to_pixel(0.00, 0.03)
        self.plate.y = int(
            self._sy0 + (self._sy1 * min(2, max(-2, (pointer_1 + pointer_2))))
        )
        self.riser.y = self.plate.y

        self._x0, self._y0 = dial_to_pixel(pointer_2, radius=self.RADIUS)
        self._x1, self._y1 = dial_to_pixel(pointer_2 - 0.25, radius=self._base // 2)
        self._x2, self._y2 = dial_to_pixel(pointer_2 + 0.25, radius=self._base // 2)
        self.hand_2 = Triangle(
            self._x0,
            self._y0,
            self._x1,
            self._y1,
            self._x2,
            self._y2,
            fill=Palette.GREEN,
            outline=self._hand_2_outline,
        )
        self._needles_group.append(self.hand_2)

        self._x0, self._y0 = dial_to_pixel(pointer_1, radius=self.RADIUS)
        self._x1, self._y1 = dial_to_pixel(pointer_1 - 0.25, radius=self._base // 2)
        self._x2, self._y2 = dial_to_pixel(pointer_1 + 0.25, radius=self._base // 2)
        self.hand_1 = Triangle(
            self._x0,
            self._y0,
            self._x1,
            self._y1,
            self._x2,
            self._y2,
            fill=Palette.ORANGE,
            outline=self._hand_1_outline,
        )
        self._needles_group.append(self.hand_1)

        return

    def erase_needles(self):
        self._needles_group.remove(self._needles_group[len(self._needles_group) - 1])
        self._needles_group.remove(self._needles_group[len(self._needles_group) - 1])
        self._needles_group.remove(self._needles_group[len(self._needles_group) - 1])
        return
