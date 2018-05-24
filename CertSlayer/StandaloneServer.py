import time
import sys
from Logger import Logger
from StandaloneModeTestController import TestStandaloneModeController
from Configuration import Configuration

class StandaloneServer(object):

    def __init__(self):
        # We need the web server running on all the interfaces
        #Configuration().fake_server_address = ("0.0.0.0", 0)
        pass

    def start(self, hostname):
        # The hostname can be an IP
        test_controller = TestStandaloneModeController(
            hostname=hostname,
            testcase_list=Configuration().testcase_list
        )
        for i in xrange(len(Configuration().testcase_list)):
            server_address = test_controller.configure_web_server()
            address, port = server_address
            if Configuration().verbose_mode:
                print "+ Web Server for host listening at %s on port %d" % (address, port)
            try:
                raw_input(">> Hit enter for setting the next TestCase")
            except KeyboardInterrupt:
                print "" # make sure prompt is on new line
                test_controller.cleanup()
                sys.exit(0)
            print "+ Killing previous server"
            test_controller.cleanup()
