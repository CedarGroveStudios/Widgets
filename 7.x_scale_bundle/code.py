# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# scale_example.py
# 2021-12-09 v1.2

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

scale_1 = Scale(max_scale=100, alarm_2=0.33, center=(0.85, 0.30), size=.25)
display_group.append(scale_1)

scale_2 = Scale(alarm_1=0.25, alarm_2=0.45, center=(0.5, 0.5), size=0.5)
display_group.append(scale_2)

scale_1.value = (0, 0)
scale_2.value = (0, 0)

display.show(display_group)
tone(board.A0, 880, 0.1)

while True:
    t0 = time.monotonic()
    gc.collect()

    for i in range(0, 125, 1):
        m = i / 100
        scale_2.value = (m, 0)
    for i in range(125, 0, -4):
        m = i / 100
        scale_2.value = (0, m)

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
        scale_1.value = (random.randrange(10, 50) / 100, random.randrange(60, 90) / 100)
        scale_2.value = (random.randrange(0, 25) / 100, random.randrange(25, 50) / 100)
