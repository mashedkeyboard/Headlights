#!/usr/bin/env python
# coding=utf-8

from PIL import ImageFont, ImageDraw, Image
from configparser import ConfigParser
import sys
import os
import time
import random

global lfsize
lfsize = 0

global plugins
plugins = {}

# Create a new configuration file instance
configfile = ConfigParser()
try:
    configfile.read('config/headlights.cfg')
except PermissionError:
    handlers.criterr("Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")

if configfile['Output'].getboolean('eink', False):
    handlers.debug("eink.py importing papirus")
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


def drawWords(screen, printstring, text_id, fontsize, icon, icon_id, ifpath, line, last_font_size, spacing):
    vpos = (line * last_font_size) + 3

    # prepare for drawing
    screen.AddText(icon, 3, vpos, fontsize, icon_id, font_path=ifpath)
    screen.AddText(printstring, fontsize + (6 if spacing else 3), vpos, fontsize, text_id)

    screen.WriteAll()


def push(screen, string, text_id=None, icon=u'', icon_id=None, ifpath='web/public/fonts/headlights.ttf', spacing=False, line=0):
    ident = str(random.randint(1024, 2048))
    if text_id is None:
        text_id = 'text_' + ident
    if icon_id is None:
        icon_id = 'icon_'+str(random.randint(1024, 2048))
    global lfsize
    rot = '0'
    papirus = Papirus(rotation=int(rot))
    if line == 0:
        fontsize, dims = getFontSize(papirus, 'mm ' + string)
    else:
        fontsize = 20
    drawWords(screen, string, text_id, fontsize, icon, icon_id, ifpath, line, lfsize, spacing)
    lfsize = fontsize
    return ident


def register(plugin, string, text_id=None, icon=u'', icon_id=None, ifpath='web/public/fonts/headlights.ttf',
             spacing=True):
    handlers.debug("eInk registering plugin " + plugin)
    global plugins
    plugins[plugin] = {'string': string, 'text_id': text_id, 'icon': icon, 'icon_id': icon_id, 'ifpath': ifpath, 'spacing': spacing}


def push_plugins(screen):
    global plugins
    i = 1  # start at line 1
    for name, plugin in plugins.iteritems():
        push(screen, plugin['string'], plugin['text_id'], plugin['icon'], plugin['icon_id'], plugin['ifpath'], plugin['spacing'], i)
        i += 1
