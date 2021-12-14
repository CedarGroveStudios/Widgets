# SPDX-FileCopyrightText: 2021 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# bubble_display_example.py
# 2021-12-14 v1.0

# For host board with integral display (PyPortal, Clue, FunHouse, etc.)

import board
import random
import time

from cedargrove_widgets.bubble_display import BubbleDisplay

display = board.DISPLAY

# Instantiate the BubbleDisplay widget, 4 digits in a single unit
# Locate at display center (0.5, 0.5) with size = 2, "Normal" mode

bubble_display = BubbleDisplay(size=2)

display.show(bubble_display)

while True:
    # Count up and down
    for i in range(0, 100, 1):
        m = i / 100
        bubble_display.value = m
        time.sleep(0.01)
    for i in range(100, 0, -1):
        m = i / 100
        bubble_display.value = m
        time.sleep(0.01)
    time.sleep(2)

    # Display some text
    bubble_display.text = "face"
    time.sleep(2)

    # Count in hexadecimal
    for i in range(0, 256):
        bubble_display.text = hex(i)
        time.sleep(0.01)
    time.sleep(2)
