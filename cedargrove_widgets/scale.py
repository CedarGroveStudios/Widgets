# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# dial.py
# 2021-10-28 v0.2

import board
import displayio
from math import pi, pow, sin, cos, sqrt
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle

if 'DISPLAY' in dir(board):
    WIDTH = board.DISPLAY.width
    HEIGHT = board.DISPLAY.height
else:
    WIDTH = 320
    HEIGHT = 240


class Palette:
    # Define a few colors
    BLACK = 0x000000
    CYAN = 0x00FFFF
    GREEN_DK = 0x006000
    GREEN_LT = 0x40A060


class Dial:
    def __init__(self, center=(0.50, 0.50), radius=0.25):
        """Instantiate the dial graphic for PyPortal devices. Defaults to center
        at 0.5, 0.5 with a radius of 0.25 (normalized display units). Builds a
        displayio dial group.

        :param center: The dial center x,y tuple in normalized display units.
        :param radius: The dial radius in normalized display units."""

        # Dial normalized screen values
        self._center_norm = center
        self._radius_norm = radius

        # Dial pixel screen values
        self.CENTER = int(center[0] * Screen.WIDTH), int(center[1] * Screen.HEIGHT)
        self.RADIUS = int(radius * min(Screen.WIDTH, Screen.HEIGHT))

        self._point_stroke = 2
        self._point_diameter = int((Screen.HEIGHT * 0.03) + (2 * self._point_stroke))
        self._point_radius = self._point_diameter // 2
        self._outside_radius = self.RADIUS - self._point_diameter
        self._inside_radius = self.RADIUS - (2 * self._point_diameter)

        self._plate_group = displayio.Group()
        self._dial_group = displayio.Group()
        self._needles_group = displayio.Group()

        # Define moveable plate graphic
        self._sx, self._sy = screen_to_rect(0.46, 0.16)
        self._sw, self._sh = screen_to_rect(0.08, 0.25)
        self.riser = Rect(
            self._sx,
            self._sy,
            width=self._sw,
            height=self._sh,
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._plate_group.append(self.riser)

        self._sx, self._sy = screen_to_rect(0.34, 0.16)
        self._sw, self._sh = screen_to_rect(0.32, 0.06)
        self.plate = RoundRect(
            self._sx,
            self._sy,
            width=self._sw,
            height=self._sh,
            r=5,
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._plate_group.append(self.plate)

        # Define primary dial graphic
        self._sx, self._sy = screen_to_rect(self._center_norm[0], self._center_norm[1])
        self._ry, self._ry = screen_to_rect(0.00, self._radius_norm)
        self.scale_dial = Circle(
            self._sx,
            self._sy,
            self._ry,
            fill=Palette.BLUE_DK,
            outline=Palette.WHITE,
            stroke=1,
        )
        self._dial_group.append(self.scale_dial)

        # Define hash marks
        for i in range(0, Defaults.MAX_GR, Defaults.MAX_GR // 10):
            self._hash_value = Label(FONT_2, text=str(i), color=Palette.CYAN)
            self._hash_value.anchor_point = (0.5, 0.5)
            self._hash_value.anchored_position = dial_to_rect(
                i / Defaults.MAX_GR, radius=self._inside_radius
            )
            self._dial_group.append(self._hash_value)

            self._x0, self._y0 = dial_to_rect(
                i / Defaults.MAX_GR, radius=self._outside_radius
            )
            self._x1, self._y1 = dial_to_rect(i / Defaults.MAX_GR, radius=self.RADIUS)
            self._hash_mark_a = Line(
                self._x0, self._y0, self._x1, self._y1, Palette.CYAN
            )
            self._dial_group.append(self._hash_mark_a)

            self._x0, self._y0 = dial_to_rect(
                (i + Defaults.MAX_GR / 20) / Defaults.MAX_GR,
                radius=self._outside_radius + self._point_radius,
            )
            self._x1, self._y1 = dial_to_rect(
                (i + Defaults.MAX_GR / 20) / Defaults.MAX_GR, radius=self.RADIUS
            )
            self._hash_mark_b = Line(
                self._x0, self._y0, self._x1, self._y1, Palette.CYAN
            )
            self._dial_group.append(self._hash_mark_b)

        # Define dial bezel graphic
        self._sx, self._sy = screen_to_rect(self._center_norm[0], self._center_norm[1])
        self._ry, self._ry = screen_to_rect(0.00, self._radius_norm)
        self._ry = self._ry + 1
        self.scale_bezel = Circle(
            self._sx,
            self._sy,
            self._ry,
            fill=None,
            outline=Palette.BLACK,
            stroke=1,
        )
        self._dial_group.append(self.scale_bezel)

        self.chan_1_alarm = Circle(
            -50,
            -50,
            self._point_radius,
            fill=Palette.ORANGE,
            outline=Palette.ORANGE,
            stroke=self._point_stroke,
        )
        self._dial_group.append(self.chan_1_alarm)

        self.chan_2_alarm = Circle(
            -50,
            -50,
            self._point_radius,
            fill=Palette.GREEN,
            outline=Palette.GREEN,
            stroke=self._point_stroke,
        )
        self._dial_group.append(self.chan_2_alarm)
        return

    @property
    def display_group(self):
        """Displayio dial group."""
        return self._dial_group

    @property
    def needles_group(self):
        """Displayio needles group."""
        return self._needles_group

    @property
    def plate_group(self):
        """Displayio plate group."""
        return self._plate_group

    @property
    def center(self):
        """Dial center normalized screen coordinates."""
        return self._center_norm

    @property
    def radius(self):
        """Dial radius normalized screen value."""
        return self._radius_norm

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
        self._sx0, self._sy0 = screen_to_rect(0.00, 0.16)
        self._sx1, self._sy1 = screen_to_rect(0.00, 0.03)
        self.plate.y = int(
            self._sy0 + (self._sy1 * min(2, max(-2, (pointer_1 + pointer_2))))
        )
        self.riser.y = self.plate.y

        self._x0, self._y0 = dial_to_rect(pointer_2, radius=self.RADIUS)
        self._x1, self._y1 = dial_to_rect(pointer_2 - 0.25, radius=self._base // 2)
        self._x2, self._y2 = dial_to_rect(pointer_2 + 0.25, radius=self._base // 2)
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

        self._x0, self._y0 = dial_to_rect(pointer_1, radius=self.RADIUS)
        self._x1, self._y1 = dial_to_rect(pointer_1 - 0.25, radius=self._base // 2)
        self._x2, self._y2 = dial_to_rect(pointer_1 + 0.25, radius=self._base // 2)
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

        self._x0, self._y0 = screen_to_rect(self.center[0], self.center[1])
        self.pivot = Circle(self._x0, self._y0, self._base // 2, fill=Palette.WHITE)
        self._needles_group.append(self.pivot)

        return

    def erase_needles(self):
        self._needles_group.remove(self._needles_group[len(self._needles_group) - 1])
        self._needles_group.remove(self._needles_group[len(self._needles_group) - 1])
        self._needles_group.remove(self._needles_group[len(self._needles_group) - 1])
        return




    def screen_to_rect(self, width_factor=0, height_factor=0):
        """Convert normalized screen position input (0.0 to 1.0) to the display's
        rectangular pixel position."""
        return int(self.WIDTH * width_factor), int(self.HEIGHT * height_factor)

    def dial_to_rect(self, scale_factor, center=(0.50, 0.50), radius=0.25):
        """Convert normalized scale_factor input (-1.0 to 1.0) to a rectangular pixel
        position on the circumference of a circle with center (x,y pixels) and
        radius (pixels)."""
        self._rads = (-2 * pi) * (scale_factor)  # convert scale_factor to radians
        self._rads = self._rads + (pi / 2)  # rotate axis counterclockwise
        x = int(center[0] + (cos(self._rads) * radius))
        y = int(center[1] - (sin(self._rads) * radius))
        return x, y
