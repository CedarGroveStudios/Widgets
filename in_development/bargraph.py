# LED cluster widget
# based on the HP QDSP-6064 4-Digit Micro 7 Segment Numeric Indicator
# 2021-11-13 v1.0

import displayio
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect

class Palette:
    # Define a few colors (https://en.wikipedia.org/wiki/Web_colors)
    BLACK = 0x000000
    RED = 0xFF0000
    RED_PKG = 0x801010
    RED_BKG = 0x601010
    RED_LENS = 0xa01010

class LEDCluster:
    def __init__(self, units=0, center=(0, 0), size=1, display_size=(None,None)):
        self._size = size
        self._cluster_group = displayio.Group(scale=self._size)
        self._cluster = displayio.Group(scale=size)
        self._digits = displayio.Group(scale=size)

        self._units = units
        self._origin = center

        for chip in range(0, self._units):
            self._upper_left_corner = (self._origin[0] + (60 * chip), self._origin[1])
            self._dip_package = Rect(self._upper_left_corner[0], self._upper_left_corner[1], 60, 25, fill=Palette.RED_PKG)
            self._cluster.append(self._dip_package)
            self._dip_index = Rect(2 + self._upper_left_corner[0], 24 + self._upper_left_corner[1], 2, 2,
                fill=Palette.BLACK)
            self._cluster.append(self._dip_index)
            for i in range(0, 4):
                self._lens = RoundRect(self._upper_left_corner[0] + (i * 15), 0 + self._upper_left_corner[1],
                    15, 25, 7, fill=Palette.RED_BKG, outline=Palette.RED_LENS)
                self._cluster.append(self._lens)

                self._a = Line(4 + self._upper_left_corner[0] + (i * 15) + 1, 6 + self._upper_left_corner[1],
                    4 + self._upper_left_corner[0] + (i * 15) + 6 + 1, 6 + self._upper_left_corner[1],
                    color=Palette.RED)
                self._digits.append(self._a)

                self._g = Line(4 + self._upper_left_corner[0] + (i * 15), 12 + self._upper_left_corner[1],
                    4 + self._upper_left_corner[0] + (i * 15) + 6, 12 + self._upper_left_corner[1],
                    color=Palette.RED)
                self._digits.append(self._g)

                self._d = Line(4 + self._upper_left_corner[0] + (i * 15) - 1, 18 + self._upper_left_corner[1],
                    4 + self._upper_left_corner[0] + (i * 15) + 6 - 1, 18 + self._upper_left_corner[1],
                    color=Palette.RED)
                self._digits.append(self._d)

                self._b = Line(4 + self._upper_left_corner[0] + (i * 15) + 6 + 1, 6 + self._upper_left_corner[1],
                    4 + self._upper_left_corner[0] + (i * 15) + 6, 12 + self._upper_left_corner[1],
                    color=Palette.RED)
                self._digits.append(self._b)

                self._c = Line(4 + self._upper_left_corner[0] + (i * 15) + 6, 12 + self._upper_left_corner[1],
                    4 + self._upper_left_corner[0] + (i * 15) + 6 - 1, 18 + self._upper_left_corner[1],
                    color=Palette.RED)
                self._digits.append(self._c)

                self._f = Line(4 + self._upper_left_corner[0] + (i * 15) + 1, 6 + self._upper_left_corner[1],
                    4 + self._upper_left_corner[0] + (i * 15), 12 + self._upper_left_corner[1],
                    color=Palette.RED)
                self._digits.append(self._f)

                self._e = Line(4 + self._upper_left_corner[0] + (i * 15), 12 + self._upper_left_corner[1],
                    4 + self._upper_left_corner[0] + (i * 15) - 1, 18 + self._upper_left_corner[1],
                    color=Palette.RED)
                self._digits.append(self._e)

                self._dp = Rect(4 + self._upper_left_corner[0] + (i * 15) + 6 + 1, 18 + self._upper_left_corner[1],
                    2, 2, fill=Palette.RED)
                self._digits.append(self._dp)

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

    #@property
    #def center(self, cluster=0):
    #    """Normalized display coordinates of the object center."""
    #    determine center of cluster specified by the cluster parameter
    #    SHOULD THIS BE A FUNCTION?
    #    return

    #@centersetter
    #def center(self, cluster=0, x, y):
    #    """Set the normalized display coordinates of the object center."""
    #    procedure for setting all coordinates for a cluster
    #    as specified by the cluster parameter
    #    SHOULD THIS BE A FUNCTION?
    #    return


    def display_to_pixel(self, width_factor=0, height_factor=0, size=1.0):
        """Convert normalized display position input (0.0 to 1.0) to display
        pixel position."""
        return int(round(size * self.WIDTH * width_factor, 0)), int(
            round(size * self.HEIGHT * height_factor, 0))

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
