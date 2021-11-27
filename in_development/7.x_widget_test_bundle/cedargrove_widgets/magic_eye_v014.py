# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# magic_eye.py
# 2021-11-26 v1.4

"""OUTSIDE RADIUS LENGTH CREATES MINOR ARTIFACTS WHEN USING VECTORIO POLYGON FOR
SHADOW WEDGE + ARC """

import displayio
import vectorio
from math import pi, pow, sin, cos, sqrt
from adafruit_display_shapes.circle import Circle


class Colors:
    # Define a few default colors
    BLACK = 0x000000
    CYAN = 0x00FFFF
    GREEN_DK = 0x005000
    GREEN_LT = 0x00A060


class MagicEye:
    def __init__(
        self,
        center=(0.50, 0.50),
        size=0.5,
        display_size=(None, None),
    ):
        """Instantiate the 6E5 magic eye graphic object for DisplayIO devices.
        Builds a hierarchical DisplayIO group consisting of sub-groups for the
        anode target, eye, and cathode.
        Display size in pixels is specified as an integer tuple. If the
        display_size tuple is not specified and an integral display is listed
        in the board class, the display_size tuple will be equal to the
        integral display width and height.

        :param center: The target anode center x,y tuple in normalized display
        units. Defaults to (0.5, 0.5).
        :param size: The normalized diameter value of the target anode relative
        to the display's shorter axis. Defaults to 0.5.
        :param display_size: The host display's integer width and height tuple
        expressed in pixels. If (None, None) and the host includes an integral
        display, the tuple value is set to (board.DISPLAY.width, board.DISPLAY.height).
        """

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

        # Define object center in normalized display and pixel coordinates
        self._center_norm = center
        self._center = self.display_to_pixel(self._center_norm[0], self._center_norm[1])
        self._radius_norm = size / 2

        # Target anode pixel screen values
        self._outside_radius = int(round(self._radius_norm * min(self.WIDTH, self.HEIGHT), 0))
        self._inside_radius = int(round(0.90 * self._outside_radius, 0))
        self._shield_radius = int(round(0.40 * self._outside_radius, 0))

        # Create displayio group layers
        self._image_group = displayio.Group()  # Primary group for MagicEye class
        self._anode_group = displayio.Group()  # Target anode and wire shadows
        self._eye_group = displayio.Group()  # Dynamic eye + tarsus shadow wedge
        self._bezel_group = displayio.Group()  # Bezel wedges/doughnut and light shield

        self._anode_palette = displayio.Palette(1)
        self._anode_palette[0] = Colors.GREEN_LT

        self._shadow_palette = displayio.Palette(1)
        self._shadow_palette[0] = Colors.GREEN_DK

        self._overlap_palette = displayio.Palette(1)
        self._overlap_palette[0] = Colors.CYAN

        self._cathode_palette = displayio.Palette(1)
        self._cathode_palette[0] = Colors.BLACK

        # Define green phosphor target anode
        self.target_anode = vectorio.Circle(
            pixel_shader=self._anode_palette,
            radius=self._outside_radius,
            x=self._center[0],
            y=self._center[1],
        )
        self._anode_group.append(self.target_anode)

        # Define wire shadow
        self._rx0, self._ry0 = self.dial_to_pixel(
            0.75, center=self._center, radius=self._inside_radius
        )
        self._rx1, self._ry1 = self.dial_to_pixel(
            0.25, center=self._center, radius=self._inside_radius
        )
        self.shadow = vectorio.Rectangle(
            pixel_shader=self._cathode_palette,
            x=self._rx0,
            y=self._ry0,
            width=self._rx1 - self._rx0,
            height=1,
        )
        self._anode_group.append(self.shadow)

        # Combined shadow wedge and tarsus polygon points
        self._x1, self._y1 = self.dial_to_pixel(
            0.35 + (0 * 0.15),
            center=self._center,
            radius=self._outside_radius,
        )
        self._x2, self._y2 = self.dial_to_pixel(
            0.65 - (0 * 0.15),
            center=self._center,
            radius=self._outside_radius,
        )
        self._points = [
            (self._x2, self._y2),
            self._center,
            (self._x1, self._y1),
        ]

        for i in range(0.35 * 100, 0.65 * 100):
            self._points.append(self.dial_to_pixel(i/100, center=self._center, radius=self._outside_radius))

        self.eye = vectorio.Polygon(
            pixel_shader=self._shadow_palette,
            points=self._points,
        )
        self._eye_group.append(self.eye)

        # Define cathode light shield
        self._cathode_shield_group = displayio.Group()
        self._rx, self._ry = self.display_to_pixel(0.00, self._radius_norm)
        self._cathode_shield = vectorio.Circle(
            pixel_shader=self._cathode_palette,
            radius=self._shield_radius,
            x=self._center[0],
            y=self._center[1],
        )
        self._bezel_group.append(self._cathode_shield)

        # Define surrounding bezel
        self._bezel = Circle(
            x0=self._center[0],
            y0=self._center[1],
            r=self._outside_radius,
            fill=None,
            outline=Colors.BLACK,
            stroke=1,
        )
        self._bezel_group.append(self._bezel)

        # Arrange image group layers
        self._image_group.append(self._anode_group)
        self._image_group.append(self._eye_group)
        self._image_group.append(self._bezel_group)

        self._eye_value = 0
        self._show_signal(self._eye_value)  # Plot no signal shadow wedge
        return

    @property
    def display_group(self):
        """Displayio dial group."""
        return self._image_group

    @property
    def display_size(self):
        """Size of display."""
        return (self.WIDTH, self.HEIGHT)

    @property
    def value(self):
        """Currently displayed value."""
        return self._eye_value

    @value.setter
    def value(self, signal=0):
        self._eye_value = min(max(0, signal), 2.0)
        self._show_signal(self._eye_value)

    def _show_signal(self, signal=0):
        """Plot the MagicEye shadow wedge. Input is a positive floating point
        value normalized for 0.0 to 1.0 (no signal to full signal) within the
        100-degree shadow wedge, but accepts a signal value up to and including
        2.0 (signal overlap).

        :param eye_normal: The normalized floating point signal  value for the
        shadow wedge. Defaults to 0 (no signal)."""

        # Combined shadow wedge and tarsus polygon points
        self._x1, self._y1 = self.dial_to_pixel(
            0.35 + (signal * 0.15),
            center=self._center,
            radius=self._outside_radius,
        )
        self._x2, self._y2 = self.dial_to_pixel(
            0.65 - (signal * 0.15),
            center=self._center,
            radius=self._outside_radius,
        )

        if signal > 1.0:
            self.eye.pixel_shader = self._overlap_palette
            self._points = [
                (self._x1, self._y1),
                self._center,
                (self._x2, self._y2),
            ]

        else:
            self.eye.pixel_shader = self._shadow_palette
            self._points = [
                (self._x2, self._y2),
                self._center,
                (self._x1, self._y1),
            ]

        rez = 100  # SHOULD CALC BASED ON DIAMETER PIXEL COUNT

        range_min = min((0.35 + (signal * 0.15)) * rez, (0.65 - (signal * 0.15)) * rez)
        range_max = 1+max((0.35 + (signal * 0.15)) * rez, (0.65 - (signal * 0.15)) * rez)

        for i in range(range_min, range_max):
            self._points.append(self.dial_to_pixel(i/rez, center=self._center, radius=self._outside_radius))
            #print(i, self.dial_to_pixel(i/rez, center=self._center, radius=self._outside_radius),range_min, range_max)

        self.eye.points = self._points
        """while True:
            pass"""
        return

    def display_to_pixel(self, x_norm=0, y_norm=0, size=1.0):
        """Convert normalized display position input (0.0 to 1.0) to display
        pixel position."""
        return int(round(size * self.WIDTH * x_norm, 0)), int(
            round(size * self.HEIGHT * y_norm, 0)
        )

    def dial_to_pixel(self, dial_norm, center=(0, 0), radius=0):
        """Convert normalized dial_norm input (-1.0 to 1.0) to display pixel
        position on the circumference of the dial's circle with center
        (x,y pixels) and radius (pixels)."""
        self._rads = (-2 * pi) * (dial_norm)  # convert dial_norm to radians
        self._rads = self._rads + (pi / 2)  # rotate axis counterclockwise
        x = center[0] + int(round(cos(self._rads) * radius, 0))
        y = center[1] - int(round(sin(self._rads) * radius, 0))
        return x, y

    def cart_to_pixel(self, x_cart, y_cart, size=1.0):
        """Convert normalized cartesian position value (-0.5, to + 0.5) to display
        pixels."""
        self._min_axis = min(self.WIDTH, self.HEIGHT)
        x1 = int(round(self._min_axis * size * x_cart, 0)) + self._center[0]
        y1 = self._center[1] - int(round(self._min_axis * size * y_cart, 0))
        return x1, y1

    def cart_dist_to_pixel(self, dist_cart_norm=0, size=1.0):
        """Convert normalized cartesian distance value to display pixels."""
        self._min_axis = min(self.WIDTH, self.HEIGHT)
        return int(round(self._min_axis * size * dist_cart_norm, 0))
