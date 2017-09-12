# Tests that the configparser works and that the included configuration files are all working fine

from six.moves import configparser

def weatherConfTest():
    configfile = configparser.ConfigParser()
    configfile.read("config/weather.cfg.sample")
    if not configfile:
        raise configparser.Error("Could not read and parse weather.cfg.sample successfully")

def webConfTest():
    configfile = configparser.ConfigParser()
    configfile.read("config/web.cfg")
    if not configfile:
        raise configparser.Error("Could not read and parse web.cfg successfully")

def headlightsConfTest():
    configfile = configparser.ConfigParser()
    configfile.read("config/headlights.cfg.sample")
    if not configfile:
        raise configparser.Error("Could not read and parse headlights.cfg.sample successfully")

def headlightsSaveCfgTest():
    configfile = configparser.ConfigParser()
    configfile['testsect'] = {}
    configfile['testsect']['test'] = 'true'
    with open('config/test.cfg', 'w') as fileman:
        configfile.write(fileman)
        configfile = configparser.ConfigParser()
    configfile.read("config/test.cfg")
    if configfile['testsect']['test'] != 'true':
        raise configparser.Error("Could not write to test.cfg successfully")