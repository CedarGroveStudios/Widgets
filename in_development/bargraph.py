# 10-Segment Bargraph widget
# based on the Lucky Light LED 10-Segment LED Gauge Bar and LML391x controllers
# 2021-11-14 v1.0

import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle


class Palette:
    # Define a few colors (https://en.wikipedia.org/wiki/Web_colors)
    BLACK = 0x000000
    GRAY = 0x508080
    GRAY_DK = 0x404040
    GREEN_DK = 0x00A000
    RED = 0xFF0000
    YELLOW = 0xFFFF00


class Bargraph:
    def __init__(
        self,
        units=0,
        center=(0, 0),
        size=1,
        range="VU",
        mode="BAR",
        display_size=(None, None),
    ):
        """LM3914 Dot/Bar Display Driver (volts; 1.2v full-scale/10 bars)
        LM3915 (dB; 3dB per step, 30dB range/10 bars)
        LM3916 (VU; 10v full-scale; -20, -10, -7, -5, -3, -1, 0, +1, +2, +3dB)
            ( -40, -37, -34, -31, -28, -25, -22, -19, -16, -13, -10, -7, -5, -3, -1, 0, +1, +2, +3dB)
        dot or bar mode; slight glow of surrounding dots in dot mode"""

        self._units = units
        self._origin = center
        self._size = size
        self._range = range
        self._mode = mode

        self._bargraph_group = displayio.Group(scale=self._size)
        self._chips = displayio.Group()
        self._bars = displayio.Group()

        for chip in range(0, self._units):
            self._upper_left_corner = (self._origin[0] + (100 * chip), self._origin[1])
            self._dip_package = Rect(
                self._upper_left_corner[0],
                self._upper_left_corner[1],
                100,
                40,
                fill=Palette.GRAY_DK,
            )
            self._chips.append(self._dip_package)
            self._dip_index = Triangle(
                self._upper_left_corner[0],
                39 + self._upper_left_corner[1],
                self._upper_left_corner[0],
                35 + self._upper_left_corner[1],
                4 + self._upper_left_corner[0],
                39 + self._upper_left_corner[1],
                fill=Palette.BLACK,
            )
            self._chips.append(self._dip_index)
            for i in range(0, 10):
                self._bar = Rect(
                    self._upper_left_corner[0] + 2 + (i * 10),
                    10 + self._upper_left_corner[1],
                    6,
                    20,
                    fill=Palette.BLACK,
                    outline=None,
                )
                self._bars.append(self._bar)
        self._bargraph_group.append(self._chips)
        self._bargraph_group.append(self._bars)
        return

    @property
    def display_group(self):
        """Displayio bargraph group."""
        return self._bargraph_group

    @property
    def units(self):
        """Number of units."""
        return self._units

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

    def show(self, signal=None):
        self._signal = signal
        self._bar = int(round(self._signal * (self._units * 10), 0))
        for i in range(0, self._units * 10):
            if i <= self._bar and self._range == "VU":
                if i > ((self._units - 1) * 10) + 6:
                    self._bars[i].fill = Palette.RED
                elif i == ((self._units - 1) * 10) + 6:
                    self._bars[i].fill = Palette.YELLOW
                else:
                    self._bars[i].fill = Palette.GREEN_DK
            else:
                self._bars[i].fill = Palette.BLACK
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
