# NeoPixel widget
# 2021-11-20 v0.6

import displayio
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect


class Palette:
    # Define a few colors (https://en.wikipedia.org/wiki/Web_colors)
    BLACK = 0x000000
    GRAY = 0x508080
    GRAY_DK = 0x101010


class NeoPixel:
    def __init__(self, units=0, center=(0, 0), size=1, display_size=(None, None)):
        self._size = size
        self._neopixel_group = displayio.Group(scale=self._size)
        self._neo_pkg = displayio.Group()
        self._reflector = displayio.Group()

        self._neopixel_units = units
        self._origin = center

        for chip in range(0, self._neopixel_units):
            self._upper_left_corner = (self._origin[0] + (15 * chip), self._origin[1])

            self._pkg = Rect(
                self._upper_left_corner[0],
                self._upper_left_corner[1],
                15,
                15,
                fill=Palette.GRAY_DK,
            )
            self._neo_pkg.append(self._pkg)

            self._pkg_index = Rect(
                self._upper_left_corner[0],
                14 + self._upper_left_corner[1],
                1,
                1,
                fill=Palette.GRAY,
            )
            self._neo_pkg.append(self._pkg_index)

            self._reflect_base = Circle(
                self._upper_left_corner[0] + 7,
                self._upper_left_corner[1] + 7,
                6,
                fill=Palette.BLACK,
                outline=None,
            )
            self._reflector.append(self._reflect_base)

        self._neopixel_group.append(self._neo_pkg)
        self._neopixel_group.append(self._reflector)
        return

    @property
    def display_group(self):
        """Displayio neopixel group."""
        return self._neopixel_group

    @property
    def neo_group(self):
        return self._reflector

    @property
    def units(self):
        """Number of NeoPixel units."""
        return self._neopixel_units

    # @property
    # def center(self, n=0):
    #    """Normalized display coordinates of neopixel object center."""
    #    determine center of neopixel specified by the n parameter
    #    SHOULD THIS BE A FUNCTION?
    #    return

    # @centersetter
    # def center(self, unit, x, y):
    #    """Set the normalized display coordinates of neopixel object center."""
    #    procedure for setting all coordinates for a pixel's display elements
    #    as specified by the n parameter
    #    SHOULD THIS BE A FUNCTION?
    #    return

    def show(self, n=None, color=Palette.BLACK):
        """Set the color of the nth neopixel."""
        if n != None:
            self._reflector[n].fill = color
        return

    def fill(self, color=Palette.BLACK):
        """Fill all neopixels with color."""
        for i in range(0, self._neopixel_units):
            self.show(i, color)
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
