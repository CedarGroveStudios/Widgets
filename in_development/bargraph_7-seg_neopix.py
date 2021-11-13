# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# bargraph_7-seg_neopix.py
# 2021-11-13 v1.0

# For host board with integral display

import displayio
import gc
import time
import board
import random
from analogio import AnalogIn
from simpleio import tone
import neopixel as boardneo

from cedargrove_widgets.magic_eye import MagicEye
from cedargrove_widgets.scale import Scale
from cedargrove_widgets.neopixel import NeoPixel

from cedargrove_sdcard import SDCard

from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle

sdcard = SDCard()
pixel = boardneo.NeoPixel(board.NEOPIXEL, 1)
pixel[0] = 0x020102

# HP QDSP-6064 4-Digit Micro 7 Segment Numeric Indicator
size=2
cluster = displayio.Group(scale=size)
digits = displayio.Group(scale=size)


units = 2
origin = (10, 100)

for chip in range(0, units):
    upper_left_corner = (origin[0] + (60 * chip), origin[1])
    dip_package = Rect(upper_left_corner[0], upper_left_corner[1], 60, 25, fill=0x801010)
    cluster.append(dip_package)
    dip_index = Rect(2 + upper_left_corner[0], 24 + upper_left_corner[1], 2, 2,
        fill=0x000000)
    cluster.append(dip_index)
    for i in range(0, 4):
        lens = RoundRect(upper_left_corner[0] + (i * 15), 0 + upper_left_corner[1],
            15, 25, 7, fill=0x601010, outline=0xa01010)
        cluster.append(lens)

        a = Line(4 + upper_left_corner[0] + (i * 15) + 1, 6 + upper_left_corner[1],
            4 + upper_left_corner[0] + (i * 15) + 6 + 1, 6 + upper_left_corner[1],
            color=0xff1010)
        digits.append(a)

        g = Line(4 + upper_left_corner[0] + (i * 15), 12 + upper_left_corner[1],
            4 + upper_left_corner[0] + (i * 15) + 6, 12 + upper_left_corner[1],
            color=0xff1010)
        digits.append(g)

        d = Line(4 + upper_left_corner[0] + (i * 15) - 1, 18 + upper_left_corner[1],
            4 + upper_left_corner[0] + (i * 15) + 6 - 1, 18 + upper_left_corner[1],
            color=0xff1010)
        digits.append(d)

        b = Line(4 + upper_left_corner[0] + (i * 15) + 6 + 1, 6 + upper_left_corner[1],
            4 + upper_left_corner[0] + (i * 15) + 6, 12 + upper_left_corner[1],
            color=0xff1010)
        digits.append(b)

        c = Line(4 + upper_left_corner[0] + (i * 15) + 6, 12 + upper_left_corner[1],
            4 + upper_left_corner[0] + (i * 15) + 6 - 1, 18 + upper_left_corner[1],
            color=0xff1010)
        digits.append(c)

        f = Line(4 + upper_left_corner[0] + (i * 15) + 1, 6 + upper_left_corner[1],
            4 + upper_left_corner[0] + (i * 15), 12 + upper_left_corner[1],
            color=0xff1010)
        digits.append(f)

        e = Line(4 + upper_left_corner[0] + (i * 15), 12 + upper_left_corner[1],
            4 + upper_left_corner[0] + (i * 15) - 1, 18 + upper_left_corner[1],
            color=0xff1010)
        digits.append(e)

        dp = Rect(4 + upper_left_corner[0] + (i * 15) + 6 + 1, 18 + upper_left_corner[1],
            2, 2, fill=0xff1010)
        digits.append(dp)



# LM3914 Dot/Bar Display Driver (volts; 1.2v full-scale/10 bars)
# LM3915 (dB; 3dB per step, 30dB range/10 bars)
# LM3916 (VU; 10v full-scale; -20, -10, -7, -5, -3, -1, 0, +1, +2, +3dB)
#        ( -40, -37, -34, -31, -28, -25, -22, -19, -16, -13, -10, -7, -5, -3, -1, 0, +1, +2, +3dB)
# dot or bar mode; slight glow of surrounding dots in dot mode
size=2
bars=displayio.Group(scale=size)
chips=displayio.Group(scale=size)

units = 1
origin = (10, 10)
for chip in range(0, units):
    upper_left_corner = (origin[0] + (100 * chip), origin[1])
    dip_package = Rect(upper_left_corner[0], upper_left_corner[1], 100, 40, fill=0xa0a0a0)
    chips.append(dip_package)
    dip_index = Triangle(upper_left_corner[0], 39 + upper_left_corner[1],
        upper_left_corner[0], 35 + upper_left_corner[1],
        4 + upper_left_corner[0], 39 + upper_left_corner[1],
        fill=0x000000)
    chips.append(dip_index)
    for i in range(0, 10):
        bar = Rect(upper_left_corner[0] + 2 + (i * 10), 10 + upper_left_corner[1],
            6, 20, fill=0x00a000, outline=None)
        bars.append(bar)
for i in range(0, units * 10):
    if (units == 1 and i > 6) or (units == 2 and i > 16):
        bars[i].fill=0xff0800

    if (units == 1 and i == 6) or (units == 2 and i == 16):
        bars[i].fill=0xffc000




tone(board.A0, 440, 0.1)

display = board.DISPLAY
display.brightness = 0.95
display.rotation = 0

magic_eye_1 = MagicEye((0.75, 0.75), size=0.3)
#magic_eye_2 = MagicEye((0.25, 0.25), size=0.20)
#magic_eye_1.display_group.append(magic_eye_2.display_group)

scale = Scale(max_scale=100, center=(0.75, 0.25), size=0.3)
magic_eye_1.display_group.append(scale.display_group)

magic_eye_1.display_group.append(chips)
magic_eye_1.display_group.append(bars)
magic_eye_1.display_group.append(cluster)
magic_eye_1.display_group.append(digits)

neopixel = NeoPixel(units=16, center=(20,140))
magic_eye_1.display_group.append(neopixel.display_group)

display.show(magic_eye_1.display_group)
tone(board.A0, 880, 0.1)

while True:
    t0 = time.monotonic()
    gc.collect()

    for i in range(0, 200, 5):
        m = i / 100
        magic_eye_1.plot_eye(m)
        scale.plot_hands(m, 0)
    for i in range(200, 0, -5):
        m = i / 100
        magic_eye_1.plot_eye(m)
        scale.plot_hands(0, m)
    print(f'frame: {(time.monotonic() - t0):5.2f} sec   free memory: {gc.mem_free()} bytes')

    neopixel.fill(color=0xffffff)
    time.sleep(0.5)
    neopixel.fill()
    time.sleep(0.5)

    m0 = 0
    for i in range(0, 100):
        magic_eye_1.plot_eye(random.randrange(0, 120) / 100)
        #magic_eye_2.plot_eye(random.randrange(0, 120) / 100)
        scale.plot_hands(random.randrange(0, 75) / 100, random.randrange(25, 50) / 100)
        neopixel.show(random.randrange(0, neopixel.units), random.randrange(0, 256, 16) +
            (256 * random.randrange(0, 256, 16)) + (256 * 256 * random.randrange(0, 256, 16)))

    sdcard.screenshot()
