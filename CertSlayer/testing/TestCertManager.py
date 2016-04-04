import unittest
import os

import OpenSSL

from CertSlayer.CertManager import CertManager
from CertSlayer.Configuration import Configuration

"""
Run with nosetests:
> nosetests TestCertManager.py
"""


class TestCertManager(unittest.TestCase):

    def setUp(self):
        pass

    def test_generate_key(self):
        key = CertManager.generate_key(bits=1024)
        self.assertEquals(OpenSSL.crypto.PKey, key.__class__)
        self.assertEquals(1024, key.bits())
        key = CertManager.generate_key()
        self.assertEquals(2048, key.bits())

    def test_read_ca_certificate_existent_default(self):
        Configuration()
        # create a manager
        manager = CertManager()
        self.assertEquals("certslayer.net.crt", Configuration().get_ca_certificate_filename())
        self.assertEquals("certslayer.net.key", Configuration().get_ca_key_filename())
        self.assertEquals("certslayer.net", manager.CA_CERT.get_issuer().CN)

    def test_read_ca_certificate_non_existent(self):
        Configuration().create_new_configuration("temp.ini")
        Configuration().set_ca_certificate_filename("trav.crt")
        Configuration().set_ca_key_filename("trav.key")
        manager = CertManager()
        self.assertEquals("trav.crt", Configuration().get_ca_certificate_filename())
        self.assertEquals("trav.key", Configuration().get_ca_key_filename())
        self.assertEquals("certslayer.net", manager.CA_CERT.get_issuer().CN)
        os.unlink(Configuration().get_ca_key_file())
        os.unlink(Configuration().get_ca_certificate_file())
        os.unlink("temp.ini")

    def test_create_X509Name_default(self):
        manager = CertManager()
        x509 = manager.create_X509Name()
        self.assertEquals(OpenSSL.crypto.X509Name, x509.__class__)
        self.assertEquals("AR", x509.C)
        self.assertEquals("Argentina", x509.ST)
        self.assertEquals("CABA", x509.L)
        self.assertEquals("CORE Security", x509.O)
        self.assertEquals("SCS", x509.OU)
        self.assertEquals("127.0.0.1", x509.CN)

    def test_get_domain_certificate(self):
        cert_manager = CertManager()
        x509 = cert_manager.get_domain_certificate("www.microsoft.com", 443)
        self.assertEquals("www.microsoft.com", x509.get_subject().CN)

    def test_sign_with_root_ca(self):
        Configuration().create_new_configuration("config.ini")
        manager = CertManager()
        crt, key = manager.sign_with_root_ca(x509=manager.get_domain_certificate("www.google.com", 443))
        x509 = manager.load_certificate(filename=crt)
        self.assertEquals("certslayer.net", x509.get_issuer().CN)
        os.unlink(crt)
        os.unlink(key)

    def test_generate_certificate_self_signed(self):
        manager = CertManager()
        attribs = {"self-signed": True}
        cert, key = manager.generate_certificate(attributes=attribs)
        x509 = manager.load_certificate(filename=cert)
        self.assertEquals(x509.get_issuer(), x509.get_subject())
        os.unlink(cert)
        os.unlink(key)

    def test_generate_certificate_self_signed_with_subject(self):
        manager = CertManager()
        x509_details = {"C": "US", "ST": "Boston",
                        "L": "Boston", "O": "CORE Security",
                        "OU": "SCS", "CN": "itsevart.com"}
        attribs = {
            "self-signed": True,
            "subject": manager.create_X509Name(x509_details)
        }
        cert, key = manager.generate_certificate(attribs)
        x509 = manager.load_certificate(filename=cert)
        self.assertEquals(x509.get_issuer(), x509.get_subject())
        self.assertEquals("itsevart.com", x509.get_subject().CN)
        self.assertEquals("Boston", x509.get_subject().ST)
        os.unlink(cert)
        os.unlink(key)

    def test_generate_certificate_signed_with_ca(self):
        manager = CertManager()
        cert, key = manager.generate_certificate()
        x509 = manager.load_certificate(filename=cert)
        self.assertEquals(x509.get_issuer(), manager.CA_CERT.get_subject())
        os.unlink(cert)
        os.unlink(key)

    def test_generate_certificate_signed_with_ca_with_subject(self):
        manager = CertManager()
        x509_details = {"C": "US", "ST": "Boston",
                        "L": "Boston", "O": "CORE Security",
                        "OU": "SCS", "CN": "itsevart.com"}
        attribs = {
            "subject": manager.create_X509Name(x509_details)
        }
        cert, key = manager.generate_certificate(attribs)
        x509 = manager.load_certificate(filename=cert)
        self.assertEquals(x509.get_issuer(), manager.CA_CERT.get_subject())
        self.assertEquals("itsevart.com", x509.get_subject().CN)
        self.assertEquals("Boston", x509.get_subject().ST)
        os.unlink(cert)
        os.unlink(key)

    def test_expired_certificate(self):
        manager = CertManager()
        x509 = manager.get_domain_certificate("www.google.com", 443)
        x509.gmtime_adj_notAfter(-1)
        self.assertEquals(True, x509.has_expired())

    def test_describe_certificate(self):
        manager = CertManager()
        x509 = manager.load_certificate(filename=Configuration().get_ca_certificate_file())
        description = manager.describe_certificate(x509)
        description = description.split("\n")[0]
        self.assertEquals("Subject CN: certslayer.net", description)

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCertManager)
    unittest.TextTestRunner().run(suite)