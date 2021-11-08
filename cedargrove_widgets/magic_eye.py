# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# magic_eye.py
# 2021-11-02 v0.4

#import board
import displayio
from math import pi, pow, sin, cos, sqrt
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle


class Palette:
    # Define a few colors
    BLACK = 0x000000
    CYAN = 0x00FFFF
    GREEN_DK = 0x006000
    GREEN_LT = 0x40A060


class MagicEye:
    def __init__(
        self,
        center=(0.50, 0.50),
        radius=0.25,
        display_size=(None, None),
        bezel_color=Palette.BLACK,
    ):
        """Instantiate the 6E5 magic eye display widget. This class creates a
        hierarchical DisplayIO group consisting of sub-groups for the target
        anode, eye, and bezel/cathode. Defaults to an object with
        display center (0.5, 0.5) and radius of 0.25, both in normalized
        display units.
        Display size in pixels is specified as an integer tuple. If the
        display_size tuple is not specified and an integral display is listed
        in the board class, the display_size tuple will be equal to the
        integral display width and height. The default RGB bezel color is
        0x000000 (black).

        :param center: The floating point width and height tuple value
        representing the center of the target anode in relative display units.
        Defaults to (0.5, 0.5).
        :param radius: The floating point radius value of the target anode in
        relative display units. Defaults to 0.25.
        :param display_size: The host display's integer width and height tuple
        expressed in pixels. If (None, None) and the host includes an integral
        display, the value is (board.DISPLAY.width, board.DISPLAY.height).
        :param bezel_color: The integer RGB color value for the outer bezel.
        Defaults to 0x000000 (black)."""

        # Normalized screen values for the dial
        self._center_norm = center
        self._radius_norm = radius

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

        # Dial pixel screen values
        self.CENTER = int(center[0] * self.WIDTH), int(center[1] * self.HEIGHT)
        self.RADIUS = int(radius * min(self.WIDTH, self.HEIGHT))

        self._outside_radius = self.RADIUS
        self._inside_radius = int(0.90 * self._outside_radius)
        self._shield_radius = int(0.40 * self._outside_radius)

        # Create displayio groups
        self._image_group = displayio.Group()  # Primary group for MagicEye class
        self._anode_group = displayio.Group()  # Target anode and wire shadows
        self._eye_group = displayio.Group()  # Dynamic eye and tarsus shadow wedge
        self._bezel_group = displayio.Group()  # Bezel wedges/doughnut and light shield

        self._bezel_color = bezel_color  # Set to match background color

        # Define phosphor target anode
        self._sx, self._sy = self.screen_to_rect(
            self._center_norm[0], self._center_norm[1]
        )
        self._rx, self._ry = self.screen_to_rect(0.00, self._radius_norm)
        self.target_anode = Circle(
            self._sx,
            self._sy,
            self._ry,
            fill=Palette.GREEN_LT,
            outline=None,
            stroke=0,
        )
        self._anode_group.append(self.target_anode)

        # Define wire shadows
        self._rx, self._ry = self.dial_to_rect(
            0.25, center=self.CENTER, radius=self._inside_radius
        )
        self.shadow_a = Line(self._sx, self._sy, self._rx, self._ry, Palette.BLACK)
        self._anode_group.append(self.shadow_a)

        self._rx, self._ry = self.dial_to_rect(
            0.75, center=self.CENTER, radius=self._inside_radius
        )
        self.shadow_b = Line(self._sx, self._sy, self._rx, self._ry, Palette.BLACK)
        self._anode_group.append(self.shadow_b)

        # Define bezel: corner wedges
        self._corner_side = int(
            sqrt(2 * pow(self._outside_radius, 2)) - self._outside_radius
        )
        self._corner_hyp = int(sqrt(2 * pow(self._corner_side, 2)))
        self._corner_x = self.CENTER[0] - self._outside_radius
        self._corner_y = self.CENTER[1] + self._outside_radius

        self._wedge_a = Triangle(
            self._corner_x,
            self._corner_y,
            self._corner_x + self._corner_hyp,
            self._corner_y,
            self._corner_x,
            self._corner_y - self._corner_hyp,
            fill=self._bezel_color,
        )
        self._bezel_group.append(self._wedge_a)

        self._corner_x = self.CENTER[0] + self._outside_radius
        self._wedge_b = Triangle(
            self._corner_x,
            self._corner_y,
            self._corner_x - self._corner_hyp,
            self._corner_y,
            self._corner_x,
            self._corner_y - self._corner_hyp,
            fill=self._bezel_color,
        )
        self._bezel_group.append(self._wedge_b)

        # Define bezel: doughnut
        # Future: REPAIR displayio circle FUNCTION FOR LARGER STROKE VALUES
        self._doughnut_gap = (
            sqrt(pow(self._outside_radius, 2) + pow(1 - self._corner_hyp, 2))
        ) - self._outside_radius

        for i in range(1, self._doughnut_gap):
            self._color = self._bezel_color
            if i == 1:
                self._color = Palette.GREEN_DK

            self._rx, self._ry = self.screen_to_rect(0.00, self._radius_norm)
            self._doughnut_mask = Circle(
                self._sx,
                self._sy,
                self._outside_radius + i,
                fill=None,
                outline=self._color,
                stroke=2,
            )
            self._bezel_group.append(self._doughnut_mask)

        # Define cathode light shield
        self._cathode_shield_group = displayio.Group()
        self._rx, self._ry = self.screen_to_rect(0.00, self._radius_norm)
        self._cathode_shield = Circle(
            self._sx,
            self._sy,
            self._shield_radius,
            fill=Palette.BLACK,
            outline=None,
            stroke=1,
        )
        self._bezel_group.append(self._cathode_shield)

        # Arrange image group layers
        self._image_group.append(self._anode_group)
        self._image_group.append(self._eye_group)
        self._image_group.append(self._bezel_group)

        self.plot_eye()  # Plot no signal shadow wedge
        return

    @property
    def display_group(self):
        """Displayio dial group."""
        return self._image_group

    @property
    def display_size(self):
        """Size of display."""
        return (self.WIDTH, self.HEIGHT)

    def plot_eye(self, signal=0):
        """Plot the MagicEye shadow wedge. Input is a positive floating point
        value normalized for 0.0 to 1.0 (no signal to full signal) within the
        100-degree shadow wedge, but accepts a signal value up to and including
        2.0 (signal overlap).

        :param eye_normal: The normalized floating point signal  value for the
        shadow wedge. Defaults to 0 (no signal)."""

        self._eye_value = signal
        self._eye_value = min(max(0, self._eye_value), 2.0)
        if self._eye_value > 1.0:
            self._eye_color = Palette.CYAN
        else:
            self._eye_color = Palette.GREEN_DK

        self._x0, self._y0 = self.screen_to_rect(
            self._center_norm[0], self._center_norm[1]
        )
        self._x1, self._y1 = self.dial_to_rect(
            0.35 + (self._eye_value * 0.15), center=self.CENTER, radius=self._outside_radius
        )
        self._x2, self._y2 = self.dial_to_rect(
            0.65 - (self._eye_value * 0.15), center=self.CENTER, radius=self._outside_radius
        )

        self.eye = Triangle(
            self._x0,
            self._y0,
            self._x1,
            self._y1,
            self._x2,
            self._y2,
            fill=self._eye_color,
            outline=Palette.CYAN,
        )
        self._eye_group.append(self.eye)

        self._x = min(self._x1, self._x2)
        self._y = min(self._y1, self._y2)
        self._w = max(self._x1, self._x2) - self._x
        self._h = abs(self.CENTER[1] + self._outside_radius - self._y) + 1

        self.tarsus = Rect(self._x, self._y, self._w, self._h, fill=self._eye_color)
        self._eye_group.append(self.tarsus)

        if len(self._eye_group) > 2:
            self._eye_group.remove(self._eye_group[0])
            self._eye_group.remove(self._eye_group[0])
        return

    def screen_to_rect(self, width_factor=0, height_factor=0):
        """Convert normalized screen position input (0.0 to 1.0) to the display's
        rectangular pixel position."""
        return int(self.WIDTH * width_factor), int(self.HEIGHT * height_factor)

    def dial_to_rect(self, scale_factor, center=(0, 0), radius=0):
        """Convert normalized scale_factor input (-1.0 to 1.0) to a rectangular pixel
        position on the circumference of a circle with center (x,y pixels) and
        radius (pixels)."""
        self._rads = (-2 * pi) * (scale_factor)  # convert scale_factor to radians
        self._rads = self._rads + (pi / 2)  # rotate axis counterclockwise
        x = int(center[0] + (cos(self._rads) * radius))
        y = int(center[1] - (sin(self._rads) * radius))
        return x, y
