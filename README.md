# Headlights
Information when it's needed, where it's needed.

## What is Headlights?
Headlights is a project that aims to deliver information across a variety of different and novel formats.
The main goal of Headlights is to create a product that delivers information in a new and useful way.
Headlights currently utilises ESCPOS receipt printing and e-ink PaPiRus displays to do this.

## What is Headlights written in?
Headlights is a Python application, currently running in Python 2.7 due to the need for PaPiRus support. It uses a very slightly modified version of the wonderful [Meteocons](http://www.alessioatzeni.com/meteocons/) icon set for weather icons in the output, and the [python-escpos](https://github.com/python-escpos/python-escpos) library for printer communication.

## What prerequisites are there?
* A USB ESC/POS compatible thermal or dot matrix printer
* An [e-ink PaPiRus display](https://www.pi-supply.com/product/PaPiRus-zero-epaper-screen-phat-pi-zero/)
* [Python](https://www.python.org/downloads/) - Headlights itself is compatible with Python 2.7 upwards and Python 3 (other than 3.4), although Python 2 is required to use e-Ink due to the PaPiRus Python library only being compatible with Python 2.
* [Pip, the Python package manager](https://pip.pypa.io/en/stable/installing/)
* Optionally, a [PaPiRus e-Ink display](https://www.pi-supply.com/product/papirus-epaper-eink-screen-hat-for-raspberry-pi/)

## How do I work this thing?
1. `git clone https://github.com/mashedkeyboard/Headlights.git`
2. `cd Headlights`
3. Run `sudo apt-get install libjpeg-dev` to install JPEG libraries, if not already there
3. `pip install -r requirements.txt`
4. Run headlights.py and browse to localhost:9375.
5. Complete the setup with your own values. To find your printer's vendor and product IDs, [use the python-escpos documentation](https://python-escpos.readthedocs.io/en/latest/user/usage.html#usb-printer). Note that at this time Headlights only supports USB printers.

NOTE: This setup is not 100% complete at the moment. If something breaks, manually copy headlights.cfg.sample in the config directory, and edit from there.

## What's all this about plugins?
All the individual sections of the report are put into plugins - you can enable or disable whatever you want within the app. Individual plugin configuration files live within the /config directory, and the plugins themselves live within the /plugins one. If you want to build a plugin, take a look at the weather plugin for an example to go on.

## What if something goes wrong?
1. Make sure you a) have headlights.cfg in your config directory, and b) it's syntactically valid (check the sample to make sure).
2. Check headlights.log - see if there's anything helpful in there, it should all be human readable.
3. [Create an issue on GitHub](https://github.com/mashedkeyboard/Headlights/issues) if you still can't get things working. Include your headlights.log file.
