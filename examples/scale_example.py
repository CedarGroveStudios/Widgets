# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# scale_example.py
# 2021-11-04 v0.0

# For host board with integral display

import time
import board
import displayio
import random
from analogio import AnalogIn
from simpleio import tone

from cedargrove_widgets.magic_eye import MagicEye
from cedargrove_widgets.scale import Scale

tone(board.A0, 440, 0.1)

display = board.DISPLAY
display.brightness = 0.75

display_group = displayio.Group()

scale_1 = Scale(max_scale=10, center=(0.75, 0.30), size=.50)
display_group.append(scale_1.display_group)

magic_eye_1 = MagicEye()
display_group.append(magic_eye_1.display_group)

magic_eye_2 = MagicEye((0.35, 0.15), radius=0.10)
display_group.append(magic_eye_2.display_group)

scale_2 = Scale(center=(0.25, 0.65), size=.75)
display_group.append(scale_2.display_group)

display.show(display_group)
tone(board.A0, 880, 0.1)

while True:
    t0 = time.monotonic()
    for i in range(0, 200, 5):
        m = i / 100
        magic_eye_1.plot_eye(m)
    for i in range(200, 0, -5):
        m = i / 100
        magic_eye_1.plot_eye(m)
    print(f'frame: {(time.monotonic() - t0):5.2f} sec')
    m0 = 0
    for i in range(0, 100):
        magic_eye_1.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_2.plot_eye(random.randrange(0, 120) / 100)
