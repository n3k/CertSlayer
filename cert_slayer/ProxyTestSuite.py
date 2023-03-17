from abc import ABCMeta, abstractmethod

from cert_slayer.CertManager import CertManager
import cert_slayer.Utils as Utils

class CertificateTC(metaclass=ABCMeta):
   
    def __init__(self, hostname, port):
        self.cert_manager = CertManager()
        self.hostname = hostname
        self.port = port

    @abstractmethod
    def create_testing_certificate(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def expected(self):
        pass

class CertificateSelfSigned(CertificateTC):

    def create_testing_certificate(self):
        # Create the subject x509Name
        x509_details = {"CN": self.hostname}
        x509name = self.cert_manager.create_X509Name(x509_details)

        # Fill the certificate attributes
        attributes = {}
        attributes["self-signed"] = True
        attributes["subject"] = x509name
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Self Signed Certificate"

    def expected(self):
        return "Certificate Rejected"

class CertificateSignedWithCA(CertificateTC):

    def create_testing_certificate(self):
        # Get the original certificate
        x509 = self.cert_manager.get_domain_certificate(self.hostname, self.port)
        return self.cert_manager.sign_with_root_ca(x509)

    def __str__(self):
        return "Signed with CertSlayer CA"

    def expected(self):
        return "Certificate Accepted"

class CertificateUnknownCA(CertificateTC):

    def create_testing_certificate(self):
        # Get the original certificate
        x509 = self.cert_manager.get_domain_certificate(self.hostname, self.port)
        ca_certificate_details = {
            "subject": {
                "C": "ES",
                "ST": Utils.get_random_name(10),
                "L": Utils.get_random_name(10),
                "O": Utils.get_random_name(10),
                "OU": Utils.get_random_name(10),
                "CN": Utils.get_random_name(10),
            }
        }
        ca_cert, k = self.cert_manager.create_ca_certificate(ca_certificate_details)
        return self.cert_manager.sign_with_rouge_ca(x509, ca_cert, k)

    def __str__(self):
        return "Signed with Unknown CA"

    def expected(self):
        return "Certificate Rejected"

class CertificateInvalidCASignature(CertificateTC):

    def create_testing_certificate(self):
        # Get the original certificate
        x509 = self.cert_manager.get_domain_certificate(self.hostname, self.port)
        ca_cert, k = self.cert_manager.create_ca_certificate()
        return self.cert_manager.sign_with_rouge_ca(x509, ca_cert, k)

    def __str__(self):
        return "Trusted CA Invalid Signature"

    def expected(self):
        return "Certificate Rejected"

class CertificateWrongCN(CertificateTC):

    def create_testing_certificate(self):
        # Get the original certificate
        x509 = self.cert_manager.get_domain_certificate(self.hostname, self.port)
        # Duplicate the basic fields
        new_x509 = self.cert_manager.duplicate_certificate_without_extensions_or_signature(x509)
        # Change the CN
        new_x509.get_subject().CN = ".".join(["www", Utils.get_random_name(5), "com"])
        # Add all the extensions except for the subjectAltName
        extensions = []
        for i in range(0, x509.get_extension_count()):
            extension = x509.get_extension(i)
            if extension.get_short_name() != "subjectAltName":
                extensions.append(extension)
        new_x509.add_extensions(extensions)
        return self.cert_manager.sign_with_root_ca(new_x509)

    def __str__(self):
        return "Wrong CNAME"

    def expected(self):
        return "Certificate Rejected"

class CertificateSignWithMD5(CertificateTC):

    def create_testing_certificate(self):
        # Get the original certificate
        x509 = self.cert_manager.get_domain_certificate(self.hostname, self.port)
        return self.cert_manager.sign_with_root_ca(x509,signing_hash="md5")

    def __str__(self):
        return "Signed with MD5"

    def expected(self):
        return "Certificate Rejected"


class CertificateSignWithMD4(CertificateTC):

    def create_testing_certificate(self):
        # Get the original certificate
        x509 = self.cert_manager.get_domain_certificate(self.hostname, self.port)
        return self.cert_manager.sign_with_root_ca(x509,signing_hash="md4")

    def __str__(self):
        return "Signed with MD4"

    def expected(self):
        return "Certificate Rejected"

class CertificateExpired(CertificateTC):

    def create_testing_certificate(self):
        # Get the original certificate
        x509 = self.cert_manager.get_domain_certificate(self.hostname, self.port)
        x509.gmtime_adj_notAfter(-1) # Expired
        return self.cert_manager.sign_with_root_ca(x509)

    def __str__(self):
        return "Expired Certificate"

    def expected(self):
        return "Certificate Rejected"

class CertificateNotYetValid(CertificateTC):

    def create_testing_certificate(self):
        # Get the original certificate
        x509 = self.cert_manager.get_domain_certificate(self.hostname, self.port)
        x509.gmtime_adj_notBefore(315360000) # not valid yet :)
        return self.cert_manager.sign_with_root_ca(x509)

    def __str__(self):
        return "Not Yet Valid Certificate"

    def expected(self):
        return "Certificate Rejected"