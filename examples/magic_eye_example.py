# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# magic_eye_example.py
# 2021-12-09 v1.1

# For host board with integral display

import gc
import time
import board
import random
from analogio import AnalogIn
from simpleio import tone

from cedargrove_widgets.magic_eye import MagicEye

tone(board.A0, 440, 0.1)

display = board.DISPLAY
display.brightness = 0.75
display.rotation = 0

magic_eye_1 = MagicEye(size=0.55)
magic_eye_2 = MagicEye((0.25, 0.25), size=0.20)
magic_eye_1.append(magic_eye_2)

display.show(magic_eye_1)
tone(board.A0, 880, 0.1)

while True:
    t0 = time.monotonic()
    gc.collect()

    for i in range(0, 200, 5):
        m = i / 100
        magic_eye_1.value = m
    for i in range(200, 0, -5):
        m = i / 100
        magic_eye_1.value = m
    print(f'frame: {(time.monotonic() - t0):5.2f} sec   free memory: {gc.mem_free()} bytes')

    m0 = 0
    for i in range(0, 100):
        magic_eye_1.value = (random.randrange(0, 120) / 100)
        magic_eye_2.value = (random.randrange(0, 120) / 100)
