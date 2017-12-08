import os

from ProxyModeTestController import TestProxyModeController
import ProxyTestSuite
from ProxyServer import ProxyServer, ProxyHandlerCertificateTest
from Configuration import Configuration


class TestCertSlayerProxyMode(object):

    def __init__(self):
        self.cleanup()

    @staticmethod
    def cleanup():
        temp_cert_dir = os.path.abspath(Configuration().get_temp_certificate_folder())
        for _ in os.listdir(temp_cert_dir):
            os.remove(os.path.join(temp_cert_dir, _))

    def main(self):
        Configuration().fake_server_address = ("127.0.0.1", 0)
        Configuration().verbose_mode = True
        Configuration().testcase_list = [
            ProxyTestSuite.CertificateInvalidCASignature,
            ProxyTestSuite.CertificateUnknownCA,
            ProxyTestSuite.CertificateSignedWithCA,
            ProxyTestSuite.CertificateSelfSigned,
            ProxyTestSuite.CertificateWrongCN,
            ProxyTestSuite.CertificateSignWithMD5,
            ProxyTestSuite.CertificateSignWithMD4,
            ProxyTestSuite.CertificateExpired,
            ProxyTestSuite.CertificateNotYetValid
        ]
        TestProxyModeController.set_monitored_domains(["www.facebook.com"])
        ProxyAddress = ("127.0.0.1", 4444)
        proxy = ProxyServer(server_address=ProxyAddress, proxy_handler=ProxyHandlerCertificateTest)
        proxy.start()

if __name__ == "__main__":
    certslayer = TestCertSlayerProxyMode()
    certslayer.main()
