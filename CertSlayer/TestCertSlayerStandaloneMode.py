import os

from StandaloneServer import StandaloneServer
import StandaloneTestSuite
from Configuration import Configuration


class TestCertSlayerStandaloneMode(object):

    def __init__(self):
        self.cleanup()

    @staticmethod
    def cleanup():
        temp_cert_dir = os.path.abspath(Configuration().get_temp_certificate_folder())
        for _ in os.listdir(temp_cert_dir):
            os.remove(os.path.join(temp_cert_dir, _))

    def main(self):
        Configuration().fake_server_address = ("0.0.0.0", 4444)
        Configuration().verbose_mode = False
        Configuration().testcase_list = [
            StandaloneTestSuite.CertificateInvalidCASignature,
            StandaloneTestSuite.CertificateUnknownCA,
            StandaloneTestSuite.CertificateSignedWithCA,
            StandaloneTestSuite.CertificateSelfSigned,
            StandaloneTestSuite.CertificateWrongCN,
            StandaloneTestSuite.CertificateSignWithMD5,
            StandaloneTestSuite.CertificateSignWithMD4,
            StandaloneTestSuite.CertificateExpired,
            StandaloneTestSuite.CertificateNotYetValid
        ]
        StandaloneServer().start("j42d1i.ipq.co")

if __name__ == "__main__":
    certslayer = TestCertSlayerStandaloneMode()
    certslayer.main()
