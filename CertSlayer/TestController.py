__author__ = 'n3k'

from Configuration import Configuration
from CertManager import CertManager
from FakeTLSServer import WebServerSetup
import threading
import os
import re


class TestControllerException(Exception):
    pass

class TestController(object):
    """
    This class is holds a dictionary with singletons per "client_address:hostname"
    that holds the tracking for all the testcases for domains under evaluation
    """

    __singleton_lock = threading.Lock()
    __singleton_dict = {}

    __domain_monitor_lock = threading.Lock()

    """A class variable to keep tracking of domains under test"""
    __monitored_domains = []

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
                    return True
            except re.error:
                if domain == monitored_domain:
                    return True
        return False

    def __init__(self, client_address, hostname, port, testcase_list):
        self.client_address = client_address
        self.hostname = hostname
        self.port = port
        self.testcase_iterator = iter(testcase_list)
        self.fake_server = None
        self.current_testcase = None
        self.remove_filename_list = []
        self.crt_filename = None
        self.key_filename = None
        self.result_filename = "".join([self.client_address, ".csv"])
        self._create_test_result_file()

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

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
            test_case = self.testcase_iterator.next()
            return test_case
        except StopIteration:
            TestController.remove_monitored_domain(self.hostname)
            raise TestControllerException("TestSuite has finished for domain: %s" % self.hostname)

    def create_certificate(self):
        self.current_testcase = self.get_next_testcase()
        self.current_testcase = self.current_testcase(self.hostname, self.port)
        cert_folder = Configuration().get_temp_certificate_folder()
        crt, key = self.current_testcase.create_testing_certificate()
        crt_filename = os.path.join(cert_folder, crt)
        key_filename = os.path.join(cert_folder, key)
        self.remove_filename_list.append(crt_filename)
        self.remove_filename_list.append(key_filename)
        return crt_filename, key_filename

    def configure_fake_server(self):
        # First check for current_testcase, if is not None we know
        # the client did not connect to our fakeserver
        if self.current_testcase is not None:
            self.register_test_result("Certificate Rejected")

        self.crt_filename, self.key_filename = self.create_certificate()
        server_address = Configuration().fake_server_address
        self.fake_server = WebServerSetup(keyfile=self.key_filename,
                                          certfile=self.crt_filename,
                                          server_address=server_address,
                                          callback=self.notification)
        # Return the actual address binded
        server_address = self.fake_server.start()
        return server_address

    def register_test_result(self, actual_status):
        logline = "%s,%s,%s,%s,%s\n" % (self.client_address,
                                              self.hostname,
                                              self.current_testcase,
                                              self.current_testcase.expected(),
                                              actual_status)
        print logline
        self._log_test_result_file(logline)
        if Configuration().verbose_mode and self.crt_filename is not None:
            x509 = CertManager.load_certificate(self.crt_filename)
            if x509:
                print CertManager.describe_certificate(x509)

    def notification(self):
        """This method is called when the client reached the web server successfully"""
        self.register_test_result("Certificate Accepted")
        self.current_testcase = None
        self.cleanup()

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