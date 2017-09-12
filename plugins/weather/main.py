# coding=utf-8
## PLUGIN NAME: weather
## PLUGIN AUTHOR: mashedkeyboard
## PLUGIN DESCRIPTION: Prints an icon and weather text report to the headlights printout based on the Met Office's DataPoint
## PLUGIN CONFIGURATION FILES: weather.cfg

import os
import handlers
from six.moves import configparser
import pluginloader
import eink
from plugins.weather import datapoint


def init():
    global config
    global wtypes
    global weathercfg

    # Load configuration and all that jazz
    config = configparser.ConfigParser()
    if os.path.isfile('config/weather.cfg'):
        config.read('config/weather.cfg')
        weathercfg = config['Info']
    else:
        if "HEADLIGHTS_TESTMODE" in os.environ and os.environ['HEADLIGHTS_TESTMODE'] == '1':
            try:
                weathercfg = {'TextRegionCode': '514', 'ForecastLocation': '3672', 'DataPointKey': os.environ['HEADLIGHTS_DPKEY']}
            except KeyError:
                handlers.criterr("Incorrectly set test environment variables. Please set up Headlights correctly for testing.")
        else:
            handlers.err('Cannot find weather.cfg. weather has not been loaded.')
            pluginloader.unload('weather')

    # Convert the weather types returned from the Met Office API into something vaguely sensible
    wtypes = {'NA' : ['questionmark.png', ')', 'Unknown'],
           '1' : ['sunny.png', 'B', 'Sunny'],
           '3' : ['ptlycloudy.png', 'H', 'Partly cloudy'],
           '5' : ['mist.png', 'E', 'Misty'],
           '6' : ['fog.png', 'F', 'Foggy'],
           '7' : ['cloudy.png', 'Y', 'Cloudy'],
           '8' : ['overcast.png', '%', 'Overcast'],
           '11' : ['drizzle.png', 'Q', 'Drizzly'],
           '12' : ['lightrain.png', 'T', 'Light rain'],
           '15' : ['heavyrain.png', 'R', 'Heavy rain'],
           '18' : ['sleet.png', 'M', 'Sleet'],
           '21' : ['hail.png', 'X', 'Hail'],
           '24' : ['lightsnow.png', 'V', 'Light snow'],
           '27' : ['heavysnow.png', 'W', 'Heavy snow'],
           '30' : ['thunder.png', '0', 'Thunder']
    }


def update(local_forecast=None):
    handlers.debug("Weather registering with E-ink controller")
    if local_forecast is None:
        local_forecast = datapoint.fetchLocalFrc(weathercfg['ForecastLocation'], weathercfg['DataPointKey'])
    weather_now = wtypes[local_forecast['W']]
    short_weather = weather_now[2] + ', ' + local_forecast['FDm'] + u'°' + 'C'
    eink.register('weather', short_weather, icon=weather_now[1], ifpath='resources/plugins/weather/fonts/meteocons.ttf')
    handlers.debug("Weather registered with E-ink controller")


def run(p):

    # Fetch current weather from DataPoint
    local_forecast = datapoint.fetchLocalFrc(weathercfg['ForecastLocation'], weathercfg['DataPointKey'])
    weather_now = wtypes[local_forecast['W']]

    # Now let's fetch the more localized and up-to-date but raw data - with an accurate 'real' OS path?
    p.image(os.path.join(os.path.realpath('resources/plugins/weather/images') + os.path.sep +
                         weather_now[0]), impl="bitImageColumn")
    handlers.debug("Weather printed the localized weather data image")

    update(local_forecast)

    # And now we can find the text forecast from the Met Office's DataPoint API
    p.text(datapoint.fetchRegionFrcAsText(weathercfg['TextRegionCode'], weathercfg['DataPointKey']))
    handlers.debug("Weather printed the regional weather text")
