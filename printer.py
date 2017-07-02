import usb
import sys
from escpos import printer
import escpos.exceptions
import handlers

def setup_printer(maincfg, debugcfg, logging):
    # Connects to the printer (unless test mode is enabled, in which case starts a dummy instance)
    if debugcfg['TestMode'] == "1":
        logging.warning('Headlights is in test mode. Nothing will actually be printed - you\'ll just see the output to the printer on the screen.')
        p = printer.Dummy()
        logging.debug("Initialized dummy printer")
    else:
        try:
            p = printer.Usb(int(maincfg['Vendor'],16),int(maincfg['Product'],16))
        except (usb.core.NoBackendError, escpos.exceptions.USBNotFoundError) as e:
            logging.debug(e)
            handlers.criterr("Could not initialize printer. Check a printer matching the vendor and product in the config file is actually connected, and relaunch Headlights.")
        logging.debug("Initialized USB printer")
    return p