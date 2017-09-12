# Scheduling and web server and all sorts of fancy things!
from six.moves import configparser
import web.serv
import schedule
import time
import six
import main
import handlers
import os
import threading
import eink
import pluginloader

global headlightsjob
global configfile


def start():
    global headlightsjob
    global configfile
    if os.path.isfile('config/headlights.cfg'):
        configfile = configparser.ConfigParser()
        try:
            configfile.read('config/headlights.cfg')
        except Exception as e:
            handlers.criterr("Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
    else:
        print("Please configure Headlights!")
        exit()
    print("Headlights started at " + time.strftime("%d/%m/%y %H:%M:%S"))
    main.start()
    refresh_eink(configfile)
    print("Headlights completed!")


def refresh_eink(configfile):
    if configfile['Output'].getboolean('eink', False):
        handlers.debug("headlights.py importing papirus")
        from papirus import PapirusComposite
        screen = PapirusComposite(False)
        eink.push(screen, configfile['General']['HelloMyNameIs'])
        pluginlist = configfile['Plugins']['toload'].split(',')
        for plugin in pluginlist:
            pluginloader.init(plugin)
        pluginloader.updateAllPlugins()
        eink.push_plugins(screen)
    else:
        handlers.debug("Skipping e-ink due to it being disabled in the config file")


def runapp():
    global headlightsjob
    global configfile
    refresh_eink(configfile)
    headlightsjob = schedule.every().day.at(configfile['Schedule']['runat']).do(start)
    web.serv.updateScheduledRun(headlightsjob.next_run.strftime("%d/%m/%y %H:%M:%S"))
    print("Headlights service running, next scheduled launch is at " + headlightsjob.next_run.strftime("%d/%m/%y %H:%M:%S"))
    while True:
        schedule.run_pending()
        time.sleep(1)


def reload():
    global headlightsjob
    global configfile
    if os.path.isfile('config/headlights.cfg'):
        configfile = configparser.ConfigParser()
        try:
            configfile.read('config/headlights.cfg')
        except Exception as e:
            handlers.criterr("Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
    else:
        print("Please configure Headlights!")
        exit()
    schedule.clear()
    refresh_eink(configfile)
    headlightsjob = schedule.every().day.at(configfile['Schedule']['runat']).do(start)
    web.serv.updateScheduledRun(headlightsjob.next_run.strftime("%d/%m/%y %H:%M:%S"))


if __name__ == "__main__":
    global configfile
    # Load the configuration file
    # noinspection PyPackageRequirements
    if os.path.isfile('config/headlights.cfg'):
        configfile = configparser.ConfigParser()
        try:
            configfile.read('config/headlights.cfg')
        except Exception as e:
            handlers.criterr("Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        
        web.serv.init()
        # Run the web server
        thr = threading.Thread(target=web.serv.run)
        thr.start()

        # Runs the API
        thr = threading.Thread(target=web.serv.run_api)
        thr.start()

        # Runs the scheduler and all that jazz
        thr = threading.Thread(target=runapp)
        thr.start()
    else:
        print("Please configure Headlights! Visit http://localhost:9375/ to start the setup.")
        web.serv.init(True)
        # Run the web server
        thr = threading.Thread(target=web.serv.run)
        thr.start()
