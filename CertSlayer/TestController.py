__author__ = 'n3k'

import os
from FakeTLSServer import WebServerSetup
from Configuration import Configuration

class TestControllerException(Exception):
    pass

class TestController(object):
    """
    This class is holds a dictionary with singletons per "client_address:hostname"
    that holds the tracking for all the testcases for domains under evaluation
    """

    def __init__(self, hostname, port, testcase_list):
        self.hostname = hostname
        self.port = port
        self.testcase_iterator = iter(testcase_list)
        self.fake_server = None
        self.current_testcase = None
        self.remove_filename_list = []
        self.crt_filename = None
        self.key_filename = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def notification(self):
        """
        A callback defining the action to perform after a client connects to our web server
        :return:
        """
        pass

    def create_certificate(self):
        # Get the next TC of the List
        self.current_testcase = self.get_next_testcase()
        if self.current_testcase == None:
            return (None,), False
        # Make an instance
        self.current_testcase = self.current_testcase(self.hostname, self.port)
        cert_folder = Configuration().get_temp_certificate_folder()
        # Generate the Certificate
        crt, key = self.current_testcase.create_testing_certificate()
        crt_filename = os.path.join(cert_folder, crt)
        key_filename = os.path.join(cert_folder, key)
        self.remove_filename_list.append(crt_filename)
        self.remove_filename_list.append(key_filename)
        return (crt_filename, key_filename), True

    def get_next_testcase(self):
        pass

    def register_test_result(self, actual_status):
        pass

    def configure_web_server(self):
        """
        Setup the internal web server that will get the request instead of the target domain
        """

        # First check for current_testcase, if is not None we know
        # the client did not connect to our fakeserver
        if self.current_testcase is not None:
            self.register_test_result("Certificate Rejected")

        certificate, status = self.create_certificate()
        if not status:
            return None

        self.crt_filename, self.key_filename = certificate
        server_address = Configuration().fake_server_address
        print "+ Setting up WebServer with Test: %s" % self.current_testcase
        self.fake_server = WebServerSetup(keyfile=self.key_filename,
                                          certfile=self.crt_filename,
                                          server_address=server_address,
                                          callback=self.notification)
        # Return the actual address binded
        server_address = self.fake_server.start()
        return server_address


    def cleanup(self):
        """Kill web server and erase cert,key pair"""
        self.kill_web_server()
        for filename in self.remove_filename_list:
            try:
                os.unlink(filename)
            except:
                pass

    def kill_web_server(self):
        if self.fake_server:
            self.fake_server.kill()
            self.fake_server = None # Don't call this twice!