import os

from CertSlayer.TestController import TestController
from CertSlayer.TestSuite import *
from CertSlayer.ProxyServer import ProxyServer, ProxyHandlerCertificateTest
from CertSlayer.Configuration import Configuration


class TestCertSlayer(object):

    def __init__(self):
        self.cleanup()

    @staticmethod
    def cleanup():
        temp_cert_dir = os.path.abspath(Configuration().get_temp_certificate_folder())
        for _ in os.listdir(temp_cert_dir):
            os.remove(os.path.join(temp_cert_dir, _))

    def main(self):
        Configuration().fake_server_address = ("127.0.0.1", 0)
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
        TestController.set_monitored_domains(["www.facebook.com"])
        proxy = ProxyServer(proxy_handler=ProxyHandlerCertificateTest)
        proxy.start()

if __name__ == "__main__":
    certslayer = TestCertSlayer()
    certslayer.main()
