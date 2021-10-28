# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# 6E5_tuning_eye.py
# 2021-10-26 v0.1

import time
import board
import random
from analogio import AnalogIn
from simpleio import tone

from cedargrove_widgets.magic_eye import MagicEye

tone(board.A0, 440, 0.1)

display = board.DISPLAY
display.brightness = 0.75

magic_eye_1 = MagicEye(
    radius=0.25,
    bezel_color=0x000000,
)
magic_eye_1.plot_eye(0)

magic_eye_2 = MagicEye((0.25, 0.25), radius=0.10)
magic_eye_1.display_group.append(magic_eye_2.display_group)
magic_eye_2.plot_eye(0)

magic_eye_3 = MagicEye((0.75, 0.25), radius=0.10)
magic_eye_1.display_group.append(magic_eye_3.display_group)
magic_eye_3.plot_eye(0)

magic_eye_4 = MagicEye((0.75, 0.75), radius=0.10)
magic_eye_1.display_group.append(magic_eye_4.display_group)
magic_eye_4.plot_eye(0)

magic_eye_5 = MagicEye((0.25, 0.75), radius=0.10)
magic_eye_1.display_group.append(magic_eye_5.display_group)
magic_eye_5.plot_eye(0)

magic_eye_6 = MagicEye((0.50, 0.10), radius=0.10)
magic_eye_1.display_group.append(magic_eye_6.display_group)
magic_eye_6.plot_eye(0)

magic_eye_7 = MagicEye((0.50, 0.90), radius=0.10)
magic_eye_1.display_group.append(magic_eye_7.display_group)
magic_eye_7.plot_eye(0)

magic_eye_8 = MagicEye((0.0, 0.0), radius=0.20)
magic_eye_1.display_group.append(magic_eye_8.display_group)
magic_eye_8.plot_eye(0)

magic_eye_9 = MagicEye((0.12, 0.50), radius=0.14)
magic_eye_1.display_group.append(magic_eye_9.display_group)
magic_eye_9.plot_eye(0)

magic_eye_A = MagicEye((0.88, 0.50), radius=0.14)
magic_eye_1.display_group.append(magic_eye_A.display_group)
magic_eye_A.plot_eye(0)

display.show(magic_eye_1.display_group)
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
        magic_eye_3.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_4.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_5.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_6.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_7.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_8.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_9.plot_eye(random.randrange(0, 120) / 100)
        magic_eye_A.plot_eye(random.randrange(0, 120) / 100)
