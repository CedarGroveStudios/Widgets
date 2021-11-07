# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# magic_eye_example.py
# 2021-10-29 v1.0

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

magic_eye_1 = MagicEye()
magic_eye_2 = MagicEye((0.25, 0.25), radius=0.10)
magic_eye_1.display_group.append(magic_eye_2.display_group)

display.show(magic_eye_1.display_group)
tone(board.A0, 880, 0.1)

while True:
    t0 = time.monotonic()
    gc.collect()

    for i in range(0, 200, 5):
        m = i / 100
        magic_eye_1.plot_eye(m)
    for i in range(200, 0, -5):
        m = i / 100
        magic_eye_1.plot_eye(m)
    print(f'frame: {(time.monotonic() - t0):5.2f} sec')
    print(f'free memory: {gc.free_mem()} bytes')
    
    m0 = 0
    for i in range(0, 100):
        magic_eye_1.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_2.plot_eye(random.randrange(0, 120) / 100)
