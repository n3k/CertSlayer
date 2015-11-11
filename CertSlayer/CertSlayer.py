__author__ = 'n3k'

import os
import optparse

from TestController import TestController
from TestSuite import *
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
        parser.add_option("-d", "--domains", dest="domains_arg",
                          help="Set a list of comma-separated domains")
        parser.add_option("-v", "--verbose", dest="verbose_arg", default=False,
                          action="store_true", help="Verbose mode")
        (options, args) = parser.parse_args()
        if not options.domains_arg:   # if domains_arg is not given
            parser.error('Domain not given')

        domain_list = options.domains_arg.split(",")

        Configuration().fake_server_address = ("127.0.0.1", 0)
        Configuration().verbose_mode = options.verbose_arg
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
        TestController.set_monitored_domains(domain_list)
        proxy = ProxyServer(proxy_handler=ProxyHandlerCertificateTest)
        proxy.start()

if __name__ == "__main__":
    certslayer = CertSlayer()
    certslayer.main()
