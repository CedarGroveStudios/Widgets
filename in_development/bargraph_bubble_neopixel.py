# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# bargraph_bubble_neopix.py
# 2021-11-14 v1.0

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
from cedargrove_widgets.bubble_display import BubbleDisplay
from cedargrove_widgets.bargraph import Bargraph

from cedargrove_sdcard import SDCard

sdcard = SDCard()
pixel = boardneo.NeoPixel(board.NEOPIXEL, 1)
pixel[0] = 0x020102

tone(board.A0, 440, 0.1)

test_display_group = displayio.Group()

display = board.DISPLAY
display.brightness = 0.75
display.rotation = 0

magic_eye_1 = MagicEye((0.80, 0.75), size=0.3)
test_display_group.append(magic_eye_1.display_group)

# magic_eye_2 = MagicEye((0.25, 0.25), size=0.20)
# test_display_group.display_group.append(magic_eye_2.display_group)

scale = Scale(max_scale=100, center=(0.80, 0.25), size=0.3)
test_display_group.append(scale.display_group)

bargraph_1 = Bargraph(units=2, center=(10, 10), mode="VU")
test_display_group.append(bargraph_1.display_group)

bargraph_2 = Bargraph(units=2, center=(10, 55), mode="VU")
test_display_group.append(bargraph_2.display_group)

bubble_display = BubbleDisplay(units=3, center=(10, 200))
test_display_group.append(bubble_display.display_group)

neopixel = NeoPixel(units=12, center=(10, 140))
test_display_group.append(neopixel.display_group)

display.show(test_display_group)
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
    print(
        f"frame: {(time.monotonic() - t0):5.2f} sec   free memory: {gc.mem_free()} bytes"
    )

    neopixel.fill(color=0xFFFFFF)
    time.sleep(0.5)
    neopixel.fill()
    time.sleep(0.5)

    m0 = 0
    for i in range(0, 100):
        magic_eye_1.plot_eye(random.randrange(0, 120) / 100)
        # magic_eye_2.plot_eye(random.randrange(0, 120) / 100)
        scale.plot_hands(random.randrange(0, 75) / 100, random.randrange(25, 50) / 100)
        neopixel.show(
            random.randrange(0, neopixel.units),
            random.randrange(0, 256, 16)
            + (256 * random.randrange(0, 256, 16))
            + (256 * 256 * random.randrange(0, 256, 16)),
        )

        left_level = random.randrange(50, 100) / 100
        right_level = min(left_level + (random.randrange(-25, 25) / 100), 1.0)
        bargraph_1.show(left_level)
        bargraph_2.show(right_level)

    gc.collect()
    sdcard.screenshot()
