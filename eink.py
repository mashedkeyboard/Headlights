#!/usr/bin/env python

from papirus import Papirus
from PIL import ImageFont, ImageDraw, Image
import sys
import os
import time

# Check EPD_SIZE is defined
EPD_SIZE=0.0
if os.path.exists('/etc/default/epd-fuse'):
    execfile('/etc/default/epd-fuse')
if EPD_SIZE == 0.0:
    print("Please select your screen size by running 'papirus-config'.")
    sys.exit()

# Running as root only needed for older Raspbians without /dev/gpiomem
if not (os.path.exists('/dev/gpiomem') and os.access('/dev/gpiomem', os.R_OK | os.W_OK)):
    user = os.getuid()
    if user != 0:
        print("Please run script as root")
        sys.exit()

WHITE = 1
BLACK = 0


def getFontSize(my_papirus, printstring):
    #returns (ideal fontsize, (length of text, height of text)) that maximally
    #fills a papirus object for a given string
    fontsize = 0
    stringlength = 0
    stringwidth = 0

    maxLength = my_papirus.width
    maxHeight = my_papirus.height

    while (stringlength <= maxLength and stringwidth <= maxHeight):

        fontsize += 1
        font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', fontsize)
        size = font.getsize(printstring)
        stringlength = size[0]
        stringwidth = size[1]

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', fontsize-1)
    return fontsize-1, font.getsize(printstring)


def drawWords(papirus, printstring, fontsize, dims):

    #initially set all white background
    image = Image.new('1', papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', fontsize)

    draw.text(((papirus.width - dims[0]) / 2, (papirus.height / 2) - (dims[1] / 2)), printstring, font=font, fill=BLACK)

    papirus.display(image)
    papirus.update()


def full_write(string):
    rot = '0'
    papirus = Papirus(rotation=int(rot))
    fontsize, dims = getFontSize(papirus, string)
    drawWords(papirus, string, fontsize, dims)

