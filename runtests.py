# Headlights testing
# Designed to be run by Travis CI. Should work for humans too, we suppose. But humans? Bleh.
# Remember to set the HEADLIGHTS_TESTMODE and HEADLIGHTS_DPKEY env-vars before testing.

import tests.configuration, tests.printer, tests.server, tests.plugins
import main

try:
    # Run the configuration tests
    tests.configuration.headlightsConfTest()
    print("Headlights.cfg.sample configuration test passed")
    tests.configuration.weatherConfTest()
    print("Weather.cfg.sample configuration test passed")
    tests.configuration.webConfTest()
    print("Web.cfg configuration test passed")
    tests.configuration.headlightsSaveCfgTest()
    print("Test.cfg configuration save test passed")

    # Run printer-related tests with dummy printers
    tests.printer.testSetFont()
    print("Dummy printer font set test passed")
    tests.printer.testPrintText()
    print("Dummy printer text print test passed")
    tests.printer.testPrintImage()
    print("Dummy printer image print test passed")
    tests.printer.testCutPaper()
    print("Dummy printer cut paper test passed")

    # Run the test for the web server
    tests.server.testWebServer()
    print("Internal web server test passed")

    # Run the plugin loader tests
    tests.plugins.testLoadPlugin()
    print("Plugin loader test passed")

    # Finally, run the actual Headlights script - this should be done with the testmode env-var
    main.start()
    print("Main script tests passed")

    # If this all works, congrats - you've managed to not screw something up, which is a miracle!
    print("All tests passed - headlights build tests successful")
except Exception as e:
    print("Tests failed with exception \"" + str(e) + "\" - headlights build tests failed.")
    raise