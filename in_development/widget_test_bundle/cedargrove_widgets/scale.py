# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# scale.py
# 2021-11-20 v1.0

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
    BLUE = 0x0000FF
    BLUE_DK = 0x000080
    CYAN = 0x00FFFF
    GRAY = 0x508080
    GREEN = 0x00FF00
    ORANGE = 0xFFA500
    RED = 0xFF0000
    WHITE = 0xFFFFFF


class Scale:
    def __init__(
        self, max_scale=100, center=(0.50, 0.50), size=0.5, display_size=(None, None)
    ):
        """Instantiate the scale graphic object for DisplayIO devices.
        Builds a displayio group representing the scale widget.

        :param max_scale: The maximum scale integer value. Used to label the
        ten major dial hash marks.
        :param center: The dial center x,y tuple in normalized display units.
        :param size: The widget size factor relative to the display's
        shorter axis.
        :param display_size: The host display's integer width and height tuple
        expressed in pixels. If (None, None) and the host includes an integral
        display, the tuple value is set to (board.DISPLAY.width, board.DISPLAY.height)."""

        # Determine default display size in pixels
        if None in display_size:
            import board

            if "DISPLAY" in dir(board):
                self.WIDTH = board.DISPLAY.width
                self.HEIGHT = board.DISPLAY.height
            else:
                raise ValueError("No integral display. Specify display size.")
        else:
            self.WIDTH = display_size[0]
            self.HEIGHT = display_size[1]

        self._max_scale = max_scale

        self._size = size
        # Define object center relative to normalized display and pixel coordinates
        self._center_norm = center
        self._center = self.display_to_pixel(self._center_norm[0], self._center_norm[1])

        if self._size < 0.50:
            self.FONT_0 = bitmap_font.load_font("/fonts/brutalist-6.bdf")
        else:
            self.FONT_0 = bitmap_font.load_font("/fonts/OpenSans-9.bdf")

        self._scale_group = displayio.Group()
        self._hands_group = displayio.Group()
        self._pivot_group = displayio.Group()

        # Define dial radii layout
        self._outside_radius = self.ortho_dist_to_pixel(0.5, self._size)
        self._major_radius = int(round(self._outside_radius * 0.88, 0))
        self._minor_radius = int(round(self._outside_radius * 0.93, 0))
        self._label_radius = int(round(self._outside_radius * 0.70, 0))

        self._sx0, self._sy0 = self._center
        self._sx1, self._sy1 = self.ortho_to_pixel(-0.49, -0.51, self._size)
        self._sx2, self._sy2 = self.ortho_to_pixel(0.49, -0.51, self._size)
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

        self._sx, self._sy = self.ortho_to_pixel(-0.5, -0.5, self._size)
        self._foot = RoundRect(
            self._sx,
            self._sy,
            width=self.ortho_dist_to_pixel(1.0, self._size),
            height=self.ortho_dist_to_pixel(0.08, self._size),
            r=int(10 * self._size),
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._scale_group.append(self._foot)

        # Define moveable plate graphic
        self._plate_y = 0.65
        self._sx, self._sy = self.ortho_to_pixel(-0.05, self._plate_y, self._size)
        self.riser = RoundRect(
            self._sx,
            self._sy,
            width=self.ortho_dist_to_pixel(0.10, self._size),
            height=self.ortho_dist_to_pixel(0.20, self._size),
            r=0,
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._scale_group.append(self.riser)

        self._sx, self._sy = self.ortho_to_pixel(-0.5, self._plate_y, self._size)
        self.plate = RoundRect(
            self._sx,
            self._sy,
            width=self.ortho_dist_to_pixel(1.0, self._size),
            height=self.ortho_dist_to_pixel(0.08, self._size),
            r=int(10 * self._size),
            fill=Palette.GRAY,
            outline=Palette.BLACK,
        )
        self._scale_group.append(self.plate)

        # Define primary dial graphic
        self._sx, self._sy = self._center
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
            self._hash_value.anchored_position = self.dial_to_pixel(
                i / self._max_scale, center=self._center, radius=self._label_radius
            )
            self._scale_group.append(self._hash_value)

            # Major hash marks
            self._x0, self._y0 = self.dial_to_pixel(
                i / self._max_scale, center=self._center, radius=self._major_radius
            )
            self._x1, self._y1 = self.dial_to_pixel(
                i / self._max_scale, center=self._center, radius=self._outside_radius
            )
            self._hash_mark_a = Line(
                self._x0, self._y0, self._x1, self._y1, Palette.CYAN
            )
            self._scale_group.append(self._hash_mark_a)

            # Minor hash marks
            self._x0, self._y0 = self.dial_to_pixel(
                (i + self._max_scale / 20) / self._max_scale,
                center=self._center,
                radius=self._minor_radius,
            )
            self._x1, self._y1 = self.dial_to_pixel(
                (i + self._max_scale / 20) / self._max_scale,
                center=self._center,
                radius=self._outside_radius,
            )
            self._hash_mark_b = Line(
                self._x0, self._y0, self._x1, self._y1, Palette.CYAN
            )
            self._scale_group.append(self._hash_mark_b)

        # Define dial bezel graphic
        self._sx, self._sy = self.ortho_to_pixel(0, 0, self._size)
        self._bezel = Circle(
            self._sx,
            self._sy,
            self._outside_radius + 1,
            fill=None,
            outline=Palette.BLACK,
            stroke=1,
        )
        self._scale_group.append(self._bezel)

        """# Define alarm points
        self._point_stroke = 2
        self._point_diameter = int((Screen.HEIGHT * 0.03) + (2 * self._point_stroke))
        self._point_radius = self._point_diameter // 2

        self.hand_1_alarm = Circle(
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

        # Define dial center piviot
        self._x0, self._y0 = self.ortho_to_pixel(0, 0, self._size)
        self._pivot = Circle(
            self._x0, self._y0, self._outside_radius // 14, fill=Palette.WHITE
        )
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
        """Normalized display coordinates of object center."""
        return self._center_norm

    @property
    def value(self):
        """Currently displayed value."""
        return self._hand_1, self._hand_2

    @value.setter
    def value(self, hands=(0,0)):
        self._show_hands(hands[0], hands[1])

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
        self._rads = (-2 * pi) * (dial_factor)  # convert scale_factor to radians
        self._rads = self._rads + (pi / 2)  # rotate axis counterclockwise
        x = int(center[0] + (cos(self._rads) * radius))
        y = int(center[1] - (sin(self._rads) * radius))
        return x, y

    def ortho_to_pixel(self, x, y, size=1.0):
        """Convert normalized cartesian position value (-0.5, to + 0.5) to display
        pixels."""
        self._min_axis = min(self.WIDTH, self.HEIGHT)
        x1 = int(round(self._min_axis * size * x, 0)) + self._center[0]
        y1 = self._center[1] - int(round(self._min_axis * size * y, 0))
        return x1, y1

    def ortho_dist_to_pixel(self, distance=0, size=1.0):
        """Convert normalized cartesian distance value to display pixels."""
        self._min_axis = min(self.WIDTH, self.HEIGHT)
        return int(round(self._min_axis * size * distance, 0))

    def _show_hands(self, hand_1=0, hand_2=0):
        """Display indicator plot_handes and move scale plate
        proportionally. Input is normalized for 0.0 to 1.0 (minimum and maximum
        range), but accepts any floating point value.

        :param hand_1: The normalized first hand position on the dial circumference.
        :param hand_1: The normalized second hand position on the dial circumference."""

        self._hand_1 = hand_1
        self._hand_2 = hand_2

        if self._hand_1 != min(1.0, max(self._hand_1, 0.0)):
            self._hand_1_outline = Palette.RED
        else:
            self._hand_1_outline = Palette.ORANGE

        if self._hand_2 != min(1.0, max(self._hand_2, 0.0)):
            self._hand_2_outline = Palette.RED
        else:
            self._hand_2_outline = Palette.GREEN

        # Move plate/riser
        self._plate_disp = self._plate_y - (
            min(2, max(-2, (self._hand_1 + self._hand_2))) * 0.10 / 2
        )
        self._x0, self.plate.y = self.ortho_to_pixel(
            0.00, self._plate_disp, size=self._size
        )
        self.riser.y = self.plate.y

        # Draw hands
        self._base = self._outside_radius // 16
        self._x0, self._y0 = self.dial_to_pixel(
            self._hand_2, center=self._center, radius=self._outside_radius
        )
        self._x1, self._y1 = self.dial_to_pixel(
            self._hand_2 - 0.25, center=self._center, radius=self._base
        )
        self._x2, self._y2 = self.dial_to_pixel(
            self._hand_2 + 0.25, center=self._center, radius=self._base
        )
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
        self._hands_group.append(self.hand_2)
        if len(self._hands_group) > 2:
            self._hands_group.remove(self._hands_group[0])

        self._x0, self._y0 = self.dial_to_pixel(
            self._hand_1, center=self._center, radius=self._outside_radius
        )
        self._x1, self._y1 = self.dial_to_pixel(
            self._hand_1 - 0.25, center=self._center, radius=self._base
        )
        self._x2, self._y2 = self.dial_to_pixel(
            self._hand_1 + 0.25, center=self._center, radius=self._base
        )
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
        self._hands_group.append(self.hand_1)
        if len(self._hands_group) > 2:
            self._hands_group.remove(self._hands_group[0])

        return
