#!/usr/bin/env python

import os
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import time
from papirus import Papirus

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

CLOCK_FONT_FILE = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
DATE_FONT_FILE  = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'


def main(config):

    """main program - draw and display time and date"""

    papirus = Papirus()

    papirus.clear()

    demo(papirus, config)


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


def demo(papirus, config):
    """simple partial update demo - draw a clock"""

    # initially set all white background
    image = Image.new('1', papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    font_size, dims = getFontSize(papirus, 'Hi, ' + config['General']['HelloMyNameIs'])
    font = ImageFont.truetype(CLOCK_FONT_FILE, font_size)

    # clear the display buffer
    draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)
    previous_second = 0
    previous_day = 0

    draw.rectangle((2, 2, width - 2, height - 2), fill=WHITE, outline=BLACK)

    draw.text(((papirus.width-dims[0])/2, (papirus.height/2) - (dims[1]/2)),
              'Hi, ' + config['General']['HelloMyNameIs'], fill=BLACK, font=font)

    # display image on the panel
    papirus.display(image)

# main
# if "__main__" == __name__:
#     if len(sys.argv) < 1:
#         sys.exit('usage: {p:s}'.format(p=sys.argv[0]))
#
#     try:
#         main(sys.argv[1:])
#     except KeyboardInterrupt:
#         sys.exit('interrupted')
#         pass
