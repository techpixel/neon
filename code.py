# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import random
import time
from datetime import datetime
import math

import board
import displayio
import framebufferio
import rgbmatrix

import terminalio
from adafruit_display_text import label

import requests

TEXT_URL = "https://wakatime.com/api/v1/users/current/status_bar/today" # "https://waka.hackclub.com/api/users/current/statusbar/today" # 
KEY = "INSERT_KEY_HERE"

headers = {
    "accept": "application/json",
    "Authorization": f"Basic {KEY}"
}

def fetchMinutes():
    print("Querying Wakatime")
    with requests.get(TEXT_URL, headers=headers) as response:
        json_data = response.json()
        return json_data["data"]["grand_total"]["minutes"]

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

# Create a bitmap
bitmap = displayio.Bitmap(display.width, display.height, 8)

# Create a palette
palette = displayio.Palette(8)

UNFILLED = 1
palette[1] = 0x222034

palette[2] = 0xec3750
palette[3] = 0xec364f
palette[4] = 0xf15242
palette[5] = 0xf26b35 
palette[6] = 0xf08228

FILLED = range(2, 7)

WHITE = 7
palette[7] = 0xffffff

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

# Create a Label
# Set text, font, and color
text = "0m"

# Create the text label
wakaMinutes = label.Label(font=terminalio.FONT, text=text, color=palette[2], scale=1)
wakaMinutes.x = 1
wakaMinutes.y = 26

# Create a Group
group = displayio.Group(scale=1)

# Add the TileGrid to the Group
group.append(tile_grid)
group.append(wakaMinutes)

# Add the Group to the Display
display.root_group = group

# Fill area on screen
def fill(x1, y1, x2, y2, color):
#    print("Filling from (" + str(x1) + "," + str(y1) + ") to (" + str(x2) + "," + str(y2) + ")")
    for x in range(x1, x2):
       for y in range(y1, y2):
           bitmap[x, y] = color
    display.refresh()

# Fill bar on screen
def bar(x1, y1, x2, y2):
    segment = x2-x1
    colors = len(FILLED)
    for x in range(x1, x2):
       color = math.floor(colors*((x-x1)/segment))
        
       for y in range(y1, y2):
           bitmap[x, y] = FILLED[color]
    display.refresh()    

# Clock Digits
clockBitmap = displayio.OnDiskBitmap("clock3_small.bmp")
clockBitmap.pixel_shader.make_transparent(0x000000) #make the bg transparent

d1 = displayio.TileGrid(clockBitmap, pixel_shader=clockBitmap.pixel_shader,
                            width = 1,
                            height = 1,
                            tile_width = 8,
                            tile_height = 16)

d1.x = 24

d2 = displayio.TileGrid(clockBitmap, pixel_shader=clockBitmap.pixel_shader,
                            width = 1,
                            height = 1,
                            tile_width = 8,
                            tile_height = 16)
d2.x = 32

dc = displayio.TileGrid(clockBitmap, pixel_shader=clockBitmap.pixel_shader,
                            width = 1,
                            height = 1,
                            tile_width = 8,
                            tile_height = 16)
dc.x = 40

d3 = displayio.TileGrid(clockBitmap, pixel_shader=clockBitmap.pixel_shader,
                            width = 1,
                            height = 1,
                            tile_width = 8,
                            tile_height = 16)
d3.x = 48

d4 = displayio.TileGrid(clockBitmap, pixel_shader=clockBitmap.pixel_shader,
                            width = 1,
                            height = 1,
                            tile_width = 8,
                            tile_height = 16)
d4.x = 56

d1.y = d2.y = dc.y = d3.y = d4.y = 16

d1[0] = 1
d2[0] = 1
dc[0] = 10
d3[0] = 1
d4[0] = 1

group.append(d1)
group.append(d2)
group.append(dc)
group.append(d3)
group.append(d4)

fill(1,1,63,15,1)

now = datetime.now()
lastMinute = -1
totalMinutes = fetchMinutes()
i = 0
while True:
    now = datetime.now()
    i += 1

    if (now.minute != lastMinute):
        lastMinute = now.minute
        totalMinutes = fetchMinutes()

        renderMin = 30 if (totalMinutes > 30) else totalMinutes
        
        wakaMinutes.text = f"{totalMinutes}m"
        
        fill(1,1,63,15,UNFILLED)
        bar(1,1,math.floor((renderMin/30)*63),15)
    
        # Update the time
    
        if (now.hour > 9):
            d1[0] = int(str(now.hour)[0])
            d2[0] = int(str(now.hour)[1])
        else:
            d1[0] = 0
            d2[0] = now.hour
    
        if (now.minute > 9):
            d3[0] = int(str(now.minute)[0])
            d4[0] = int(str(now.minute)[1])
        else:
            d3[0] = 0
            d4[0] = now.minute
    
    display.refresh()

#    time.sleep(0.1)
    if (i == 10):
        dc.hidden = not dc.hidden
        i = 0

    next = palette[6]
    palette[6] = palette[5]
    palette[5] = palette[4]
    palette[4] = palette[3]
    palette[3] = palette[2]
    palette[2] = next

# -------------------