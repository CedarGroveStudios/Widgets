# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# scale_example.py
# 2021-11-08 v1.0

# For host board with integral display

import gc
import time
import board
import displayio
import random
from analogio import AnalogIn
from simpleio import tone

from cedargrove_widgets.scale import Scale

tone(board.A0, 440, 0.1)

display = board.DISPLAY
display.brightness = 0.75
display.rotation = 0

display_group = displayio.Group()

scale_1 = Scale(max_scale=100, center=(0.85, 0.30), size=0.15)
display_group.append(scale_1.display_group)

scale_2 = Scale(center=(0.5, 0.5), size=0.5)
display_group.append(scale_2.display_group)

scale_1.plot_hands()
scale_2.plot_hands()

display.show(display_group)
tone(board.A0, 880, 0.1)

while True:
    t0 = time.monotonic()
    gc.collect()

    for i in range(0, 125, 1):
        m = i / 100
        scale_2.plot_hands(m, 0)
    for i in range(125, 0, -4):
        m = i / 100
        scale_2.plot_hands(0, m)
    print(f'frame: {(time.monotonic() - t0):5.2f} sec    free memory: {gc.mem_free()} bytes')

    m0 = 0
    for i in range(0, 100):
        scale_1.plot_hands(random.randrange(10, 50) / 100, random.randrange(60, 90) / 100)
        scale_2.plot_hands(random.randrange(0, 25) / 100, random.randrange(25, 50) / 100)
