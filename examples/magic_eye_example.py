# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# magic_eye_example.py
# 2021-12-14 v1.1

# For host board with integral display (PyPortal, Clue, FunHouse, etc.)

import board
import random
import time

from cedargrove_widgets.magic_eye import MagicEye

display = board.DISPLAY

# Instantiate the MagicEye widget
# Locate at display center (0.5, 0.5) with size = 0.5
magic_eye = MagicEye()

display.show(magic_eye)

while True:

    # Close and open the wedge
    for i in range(0, 200, 1):
        m = i / 100
        magic_eye.value = m
        time.sleep(0.01)
    for i in range(200, 0, -1):
        m = i / 100
        magic_eye.value = m
        time.sleep(0.01)

    # Randomly control the wedge
    for i in range(0, 100):
        magic_eye.value = (random.randrange(0, 200) / 100)
        time.sleep(0.01)
