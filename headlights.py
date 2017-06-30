# Scheduling and web server and all sorts of fancy things!
import configparser
import web.serv
import schedule
import time
import main
import handlers
import os
import threading
import eink

global headlightsjob
global configfile


def start():
    global headlightsjob
    print("Headlights started at " + time.strftime("%d/%m/%y %H:%M:%S"))
    main.start()
    web.serv.updateScheduledRun(headlightsjob.next_run.strftime("%d/%m/%y %H:%M:%S"))
    print("Headlights completed, next scheduled launch is at " + headlightsjob.next_run.strftime("%d/%m/%y %H:%M:%S"))


def runapp():
    global headlightsjob
    global configfile
    eink.main(configfile)
    headlightsjob = schedule.every().day.at(configfile['Schedule']['runat']).do(start)
    web.serv.updateScheduledRun(headlightsjob.next_run.strftime("%d/%m/%y %H:%M:%S"))
    print("Headlights service running, next scheduled launch is at " + headlightsjob.next_run.strftime("%d/%m/%y %H:%M:%S"))
    while True:
        schedule.run_pending()
        time.sleep(1)


def reload():
    global headlightsjob
    global configfile
    schedule.clear()
    if os.path.isfile('config/headlights.cfg') == True:
        configfile = configparser.ConfigParser()
        try:
            configfile.read('config/headlights.cfg')
        except PermissionError:
            handlers.criterr("Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
    else:
        print("No configuration file found. Please configure Headlights.")
        exit()
    headlightsjob = schedule.every().day.at(configfile['Schedule']['runat']).do(start)
    web.serv.updateScheduledRun(headlightsjob.next_run.strftime("%d/%m/%y %H:%M:%S"))


if __name__ == "__main__":
    # Load the configuration file
    if os.path.isfile('config/headlights.cfg') == True:
        configfile = configparser.ConfigParser()
        try:
            configfile.read('config/headlights.cfg')
        except Exception as e:
            handlers.criterr("Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        web.serv.init()
        # Run the web server
        thr = threading.Thread(target=web.serv.run)
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
