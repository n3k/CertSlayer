__author__ = 'n3k'

import os
import optparse

from ProxyModeTestController import TestProxyModeController
from ProxyTestSuite import *
from ProxyServer import ProxyServer, ProxyHandlerCertificateTest
from Configuration import Configuration


class CertSlayer(object):

    def __init__(self):
        self.cleanup()

    @staticmethod
    def cleanup():
        temp_cert_dir = os.path.abspath(Configuration().get_temp_certificate_folder())
        for _ in os.listdir(temp_cert_dir):
            os.remove(os.path.join(temp_cert_dir, _))

    def main(self):
        parser = optparse.OptionParser()
        parser.add_option("-d", "--domain", dest="domains_arg", action="append",
                          help="Domain to be monitored, might be used multiple times and supports regular expressions")
        parser.add_option("-v", "--verbose", dest="verbose_arg", default=False,
                          action="store_true", help="Verbose mode")
        (options, args) = parser.parse_args()
        if not options.domains_arg or len(options.domains_arg) <1:   # if domains_arg is not given
            parser.error('Domain not given')

        Configuration().fake_server_address = ("127.0.0.1", 0)
        Configuration().verbose_mode = options.verbose_arg

        # Define the test cases
        Configuration().testcase_list = [CertificateInvalidCASignature,
                                         CertificateUnknownCA,
                                         CertificateSignedWithCA,
                                         CertificateSelfSigned,
                                         CertificateWrongCN,
                                         CertificateSignWithMD5,
                                         CertificateSignWithMD4,
                                         CertificateExpired,
                                         CertificateNotYetValid
                                         ]

        # Set the domains that will be tracked
        TestProxyModeController.set_monitored_domains(options.domains_arg)

        # Start the Proxy to Trap Connections to targeted domains
        proxy = ProxyServer(proxy_handler=ProxyHandlerCertificateTest)
        proxy.start()

if __name__ == "__main__":
    certslayer = CertSlayer()
    certslayer.main()
