__author__ = 'n3k'

import os
import optparse

from cert_slayer.ProxyModeTestController import TestProxyModeController
import cert_slayer.ProxyTestSuite as ProxyTestSuite
import cert_slayer.StandaloneTestSuite as StandaloneTestSuite
from cert_slayer.ProxyServer import ProxyServer, ProxyHandlerCertificateTest
from cert_slayer.StandaloneServer import StandaloneServer
from cert_slayer.Configuration import Configuration


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
                          help="Domain to be monitored, might be used multiple times and supports regular expressions (Only valid for proxy mode)")
        parser.add_option("-p", "--port", dest="port_arg", action="store",
                          default="8080", help="port to listen")
        parser.add_option("-m", "--mode", dest="mode_arg", action="store",
                          default="proxy", help="Operation mode: proxy or standalone")
        parser.add_option("-i", "--hostname", dest="host_arg", action="store",
                          default="localhost",
                          help="Hostname: the IP address or Domain name that the certificate CN will stand for (Only valid for standalone mode)")
        parser.add_option("-v", "--verbose", dest="verbose_arg", default=False,
                          action="store_true", help="Verbose mode")
        (options, args) = parser.parse_args()

        if options.verbose_arg:
            print("-Info: verbose mode enabled")
        Configuration().verbose_mode = options.verbose_arg

        if not options.port_arg:
            print("-Info: port not specified, using 8080")
        port = int(options.port_arg,10)

        if options.mode_arg == "proxy":

            if not options.domains_arg or len(options.domains_arg) <1:   # if domains_arg is not given
                parser.error("-Error: target domain was not specified")

            Configuration().fake_server_address = ("127.0.0.1", 0)

            # Define the test cases
            Configuration().testcase_list = [
                ProxyTestSuite.CertificateInvalidCASignature,
                ProxyTestSuite.CertificateUnknownCA,
                ProxyTestSuite.CertificateSignedWithCA,
                ProxyTestSuite.CertificateSelfSigned,
                ProxyTestSuite.CertificateWrongCN,                
                ProxyTestSuite.CertificateExpired,
                ProxyTestSuite.CertificateNotYetValid,
                ProxyTestSuite.CertificateSignWithMD5,
                ProxyTestSuite.CertificateSignWithMD4
            ]

            # Set the domains that will be tracked
            TestProxyModeController.set_monitored_domains(options.domains_arg)

            # Start the Proxy to Trap Connections to targeted domains
            proxy = ProxyServer(server_address=("0.0.0.0", port),
                                proxy_handler=ProxyHandlerCertificateTest)
            proxy.start()

        elif options.mode_arg == "standalone":
            Configuration().fake_server_address = ("0.0.0.0", 0)
            Configuration().testcase_list = [
                StandaloneTestSuite.CertificateInvalidCASignature,
                StandaloneTestSuite.CertificateUnknownCA,
                StandaloneTestSuite.CertificateSignedWithCA,
                StandaloneTestSuite.CertificateSelfSigned,
                StandaloneTestSuite.CertificateWrongCN,                
                StandaloneTestSuite.CertificateExpired,
                StandaloneTestSuite.CertificateNotYetValid,
                StandaloneTestSuite.CertificateSignWithMD5,
                StandaloneTestSuite.CertificateSignWithMD4
            ]
            if not options.host_arg:
                print("-Warning: hostname not given, using 'localhost'")
            StandaloneServer().start(options.host_arg, port)

        else:
            parser.error('-Error: Unsupported mode')


if __name__ == "__main__":
    certslayer = CertSlayer()
    certslayer.main()
