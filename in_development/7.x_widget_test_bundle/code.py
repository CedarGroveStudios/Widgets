# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# bar_bubble_neo_code.py
# 2021-11-27 v1.1

# For host board with integral display

lone_eye = False

import displayio
import gc
import time
import board
import math
import random
from analogio import AnalogIn
from simpleio import tone
import neopixel as boardneo

from cedargrove_widgets.magic_eye import MagicEye
if not lone_eye:
    from cedargrove_widgets.scale import Scale
    from cedargrove_widgets.neopixel import NeoPixel
    from cedargrove_widgets.bubble_display import BubbleDisplay
    from cedargrove_widgets.bargraph import Bargraph
    from cedargrove_sdcard import SDCard
    sdcard = SDCard()

pixel = boardneo.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.5
pixel[0] = 0x020102

tone(board.A0, 440, 0.1)

test_display_group = displayio.Group()

display = board.DISPLAY
display.brightness = 0.75
display.rotation = 0

gc.collect()

magic_eye_1 = MagicEye((0.85, 0.75), size=0.3, bezel_color=0x000000)
#magic_eye_1 = MagicEye()
test_display_group.append(magic_eye_1.display_group)

# magic_eye_2 = MagicEye((0.25, 0.25), size=0.20)
# test_display_group.display_group.append(magic_eye_2.display_group)

if not lone_eye:
    scale = Scale(max_scale=100, center=(0.85, 0.30), size=0.3)
    test_display_group.append(scale.display_group)

    bargraph_1 = Bargraph(units=2, center=(10, 10), mode="VU")
    test_display_group.append(bargraph_1.display_group)

    bargraph_2 = Bargraph(units=2, center=(10, 75), mode="VU")
    test_display_group.append(bargraph_2.display_group)

    bubble_display_1 = BubbleDisplay(units=1, center=(5, 40))
    test_display_group.append(bubble_display_1.display_group)

    bubble_display_2 = BubbleDisplay(units=1, center=(5, 105))
    test_display_group.append(bubble_display_2.display_group)

    neo_units = 10
    neopixel_1 = NeoPixel(units=neo_units, center=(10, 160))
    test_display_group.append(neopixel_1.display_group)

    neopixel_2 = NeoPixel(units=neo_units, center=(10, 175))
    test_display_group.append(neopixel_2.display_group)

    neopixel_3 = NeoPixel(units=neo_units, center=(10, 190))
    test_display_group.append(neopixel_3.display_group)

    neopixel_4 = NeoPixel(units=neo_units, center=(10, 205))
    test_display_group.append(neopixel_4.display_group)

    neo = neopixel_1.neo_group

    neo[0].fill = 0xf040f0

display.show(test_display_group)
tone(board.A0, 880, 0.1)

while True:
    t0 = time.monotonic()
    gc.collect()

    for i in range(0, 200, 5):
        m = i / 100
        magic_eye_1.value = m
        if not lone_eye:
            scale.value = (m, 0)
            bubble_display_1.value = i
        """else:
            time.sleep(0.050)"""
    for i in range(200, 0, -5):
        m = i / 100
        magic_eye_1.value = m
        if not lone_eye:
            scale.value = (0, m)
            bubble_display_2.value = i
        """else:
            time.sleep(0.050)"""

    free_memory = gc.mem_free()
    frame = time.monotonic() - t0
    print(
        f'frame: {frame:5.2f} sec   free memory: {free_memory} bytes'
    )
    print(
        (frame, (free_memory/1000))
    )

    if not lone_eye:
        bubble_display_1.value = round(frame, 1)
        bubble_display_2.value = round(free_memory/1000, 1)
        time.sleep(3)

        neopixel_1.fill(color=0xFF0000)
        neopixel_2.fill(color=0x00FF00)
        neopixel_3.fill(color=0x0000FF)
        neopixel_4.fill(color=0xFFFFFF)
        time.sleep(0.5)
        neopixel_1.fill()
        neopixel_2.fill()
        neopixel_3.fill()
        neopixel_4.fill()
        time.sleep(0.5)

    m0 = 0
    for i in range(0, 100):
        magic_eye_1.value = random.randrange(0, 120) / 100
        # magic_eye_2.value = random.randrange(0, 120) / 100

        if not lone_eye:
            scale.value = (random.randrange(0, 75) / 100, random.randrange(25, 50) / 100)
            neopixel_1.show(
                random.randrange(0, neopixel_1.units),
                random.randrange(0, 256, 16)
                + (256 * random.randrange(0, 256, 16))
                + (256 * 256 * random.randrange(0, 256, 16)),
            )
            neopixel_2.show(
                random.randrange(0, neopixel_2.units),
                random.randrange(0, 256, 16)
                + (256 * random.randrange(0, 256, 16))
                + (256 * 256 * random.randrange(0, 256, 16)),
            )
            neopixel_3.show(
                random.randrange(0, neopixel_3.units),
                random.randrange(0, 256, 16)
                + (256 * random.randrange(0, 256, 16))
                + (256 * 256 * random.randrange(0, 256, 16)),
            )
            neopixel_4.show(
                random.randrange(0, neopixel_4.units),
                random.randrange(0, 256, 16)
                + (256 * random.randrange(0, 256, 16))
                + (256 * 256 * random.randrange(0, 256, 16)),
            )

            left_level = random.randrange(50, 100) / 100
            right_level = min(left_level + (random.randrange(-25, 25) / 100), 1.0)
            bargraph_1.value = bubble_display_1.value = left_level
            bargraph_2.value = bubble_display_2.value = right_level

        """else:
            time.sleep(0.050)"""

    gc.collect()

    if not lone_eye:
        sdcard.screenshot()

    pass
