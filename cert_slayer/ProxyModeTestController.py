__author__ = 'n3k'

from cert_slayer.Configuration import Configuration
from cert_slayer.CertManager import CertManager

import threading
from cert_slayer.TestController import TestController, TestControllerException
import os
import re

class TestProxyModeController(TestController):
    """
    This class is holds a dictionary with singletons per "client_address:hostname"
    that holds the tracking for all the testcases for domains under evaluation
    """

    __singleton_lock = threading.Lock()
    __singleton_dict = {}

    __domain_monitor_lock = threading.Lock()

    """A class variable to keep tracking of domains under test"""
    __monitored_domains = []

    # A lock for the webserver
    __webserver_lock = threading.Lock()

    @classmethod
    def remove_monitored_domain(cls, domain):
        cls.__domain_monitor_lock.acquire()
        cls.__monitored_domains.remove(domain)
        cls.__domain_monitor_lock.release()

    @classmethod
    def add_monitored_domain(cls, domain):
        cls.__domain_monitor_lock.acquire()
        cls.__monitored_domains.append(domain)
        cls.__domain_monitor_lock.release()

    @classmethod
    def set_monitored_domains(cls, monitored_domains):
        cls.__domain_monitor_lock.acquire()
        cls.__monitored_domains = monitored_domains
        cls.__domain_monitor_lock.release()

    @classmethod
    def get_monitored_domains(cls):
        return cls.__monitored_domains

    @classmethod
    def match_monitored_domains(cls, domain):
        for monitored_domain in cls.__monitored_domains:
            try:
                if re.match(monitored_domain, domain):
                    #print("Monitored Domain: %s - Domain: %s" % (monitored_domain, domain))
                    return True
            except re.error:
                if domain == monitored_domain:
                    return True
        return False

    def __init__(self, client_address, hostname, port, testcase_list):
        super(TestProxyModeController, self).__init__(hostname, port, testcase_list)
        self.client_address = client_address
        self.result_filename = "".join([self.client_address, ".csv"])
        self._create_test_result_file()

    def _create_test_result_file(self):
        if os.path.isfile(self.result_filename):
            return
        else:
            with open(self.result_filename, "wt") as f:
                f.write("Client Address,Hostname,Current TestCase,Expected,Actual\n")

    def _log_test_result_file(self, logline):
        with open(self.result_filename, "at") as f:
            f.write(logline)

    @classmethod
    def instance(cls, client_address, hostname, port):
        key = "%s:%s:%d" % (client_address, hostname, port)
        if not key in cls.__singleton_dict:
            with cls.__singleton_lock:
                if not key in cls.__singleton_dict:
                    cls.__singleton_dict[key] = cls(client_address, hostname, port, Configuration().testcase_list)
        return cls.__singleton_dict[key]

    def get_next_testcase(self):
        try:
            test_case = next(self.testcase_iterator)
            return test_case
        except StopIteration:
            self.remove_monitored_domain(self.hostname)
            #raise TestControllerException("TestSuite has finished for domain: %s" % self.hostname)
            return None

    def cleanup(self):
        #print("+] trying to aqcuire lock for cleanup")
        #self.__webserver_lock.acquire()
        #print("+] aquired lock for cleanup")
        super(TestProxyModeController, self).cleanup()
        #print("+] trying to release lock for cleanup")
        #self.__webserver_lock.release()
        #print("+] released lock for cleanup")


    def configure_web_server(self):
        #print("+] trying to aqcuire lock for creating web server")
        self.__webserver_lock.acquire()
        #print("+] aquired lock for creating web server")
        server_address = super(TestProxyModeController, self).configure_web_server()
        #print("+] trying to release lock for creating web server")
        self.__webserver_lock.release()
        #print("+] released lock for creating web server")
        return server_address

    def register_test_result(self, actual_status):
        logline = "%s,%s,%s,%s,%s\n" % (self.client_address,
                                              self.hostname,
                                              self.current_testcase,
                                              self.current_testcase.expected(),
                                              actual_status)
        print(logline)
        self._log_test_result_file(logline)
        if Configuration().verbose_mode and self.crt_filename is not None:
            x509 = CertManager.load_certificate(self.crt_filename)
            if x509:
                print(CertManager.describe_certificate(x509))

    def notification(self):
        """This method is called when the client reached the web server successfully"""
        self.register_test_result("Certificate Accepted")
        self.current_testcase = None
        self.cleanup()