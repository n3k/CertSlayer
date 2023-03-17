from cert_slayer.TestController import TestController
from cert_slayer.Configuration import Configuration
from cert_slayer.CertManager import CertManager
import os

class TestStandaloneModeController(TestController):

    def __init__(self, hostname, testcase_list):
        # We don't need the port in this case, as we're creating all the certificates ourselves
        # The port is used by the ProxiedTestSuite for getting the actual certificate from the service
        super(TestStandaloneModeController, self).__init__(hostname, port=0, testcase_list=testcase_list)
        self.result_filename = "result.csv"
        self._create_test_result_file()

    def _create_test_result_file(self):
        if os.path.isfile(self.result_filename):
            return
        else:
            with open(self.result_filename, "wt") as f:
                f.write("Hostname,Current TestCase,Expected,Actual\n")

    def _log_test_result_file(self, logline):
        with open(self.result_filename, "at") as f:
            f.write(logline)

    def get_next_testcase(self):
        try:
            test_case = next(self.testcase_iterator)
            self.test_case_completed = False
            return test_case
        except StopIteration:
            # TestSuite has finished
            return None

    def register_test_result(self, actual_status):
        logline = "%s,%s,%s,%s\n" % (
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
        self.test_case_completed = True
       