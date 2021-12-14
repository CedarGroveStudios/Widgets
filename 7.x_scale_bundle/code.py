# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# scale_example.py
# 2021-12-14 v1.1

# For host board with integral display (PyPortal, Clue, FunHouse, etc.)

import board
import random

from cedargrove_widgets.scale import Scale

display = board.DISPLAY

# Instantiate the Scale widget with a single pointer hand
# Locate at display center (0.5, 0.5) with size = 0.5 and scale maximum = 100
scale = Scale()

display.show(scale)

while True:
    # Move the hand
    for i in range(0, 100, 1):
        m = i / 100
        scale.hand1 = m
    for i in range(100, 0, -1):
        m = i / 100
        scale.hand1 = m

    # Toss the pointer hand around randomly
    for i in range(0, 100):
        scale.hand1 = random.randrange(0, 100) / 100
