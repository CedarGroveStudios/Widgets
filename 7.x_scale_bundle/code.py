# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# scale_example.py
# 2021-12-11 v1.3

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

scale_1 = Scale(num_hands=2, max_scale=100, center=(0.85, 0.30), size=.25)
scale_1.alarm2 = 0.33
display_group.append(scale_1)

scale_2 = Scale(num_hands=2, center=(0.5, 0.5), size=0.5)
scale_2.alarm1 = 0.25
scale_2.alarm2 = 0.45
display_group.append(scale_2)

scale_1.hand1 = scale_1.hand2 = 0
scale_1.hand2 = scale_2.hand2 = 0

display.show(display_group)
tone(board.A0, 880, 0.1)

while True:
    t0 = time.monotonic()
    gc.collect()

    scale_2.hand2 = 0
    for i in range(0, 125, 1):
        m = i / 100
        scale_2.hand1 = m

    scale_2.hand_1 = 0
    for i in range(125, 0, -4):
        m = i / 100
        scale_2.hand2 = m

    free_memory = gc.mem_free()
    frame = time.monotonic() - t0
    print(
        f'frame: {frame:5.2f} sec   free memory: {free_memory} bytes'
    )
    print(
        (frame, (free_memory/1000))
    )

    m0 = 0
    for i in range(0, 100):
        scale_1.hand1 = random.randrange(10, 50) / 100
        scale_1.hand2 = random.randrange(60, 90) / 100
        scale_2.hand1 = random.randrange(0, 25) / 100
        scale_2.hand2 = random.randrange(25, 50) / 100
