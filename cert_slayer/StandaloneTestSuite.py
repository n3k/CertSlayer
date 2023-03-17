from cert_slayer.ProxyTestSuite import CertificateTC
import cert_slayer.Utils as Utils

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
        # Create the subject x509Name
        x509_details = {"CN": self.hostname}
        x509name = self.cert_manager.create_X509Name(x509_details)

        # Return a valid certificate signed with the CA
        attributes = {"subject": x509name}
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Signed with CertSlayer CA"

    def expected(self):
        return "Certificate Accepted"

class CertificateUnknownCA(CertificateTC):

    def create_testing_certificate(self):
        # Create the subject x509Name
        x509_details = {"CN": self.hostname}
        x509name = self.cert_manager.create_X509Name(x509_details)

        # Create the rogue CA
        ca_certificate_details = {
            "subject": {
                "C": "ES",
                "ST": Utils.get_random_name(10),
                "L": Utils.get_random_name(10),
                "O": Utils.get_random_name(10),
                "OU": Utils.get_random_name(10),
                "CN": Utils.get_random_name(10)
            }
        }
        ca_x509, ca_key = self.cert_manager.create_ca_certificate(ca_certificate_details)

        # Return a valid certificate signed with the CA
        attributes = {
            "subject": x509name,
            "issuer": ca_x509.get_issuer(),
            "ca_key": ca_key
        }
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Signed with Unknown CA"

    def expected(self):
        return "Certificate Rejected"

class CertificateInvalidCASignature(CertificateTC):
    """
    This is almost the same as CertificateUnknownCA but uses all the same attributes
    except for the signature
    """

    def create_testing_certificate(self):
        # Create the subject x509Name
        x509_details = {"CN": self.hostname}
        x509name = self.cert_manager.create_X509Name(x509_details)

        ca_x509, ca_key = self.cert_manager.create_ca_certificate()
        attributes = {
            "subject": x509name,
            "issuer": ca_x509.get_issuer(),
            "ca_key": ca_key
        }
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Trusted CA Invalid Signature"

    def expected(self):
        return "Certificate Rejected"

class CertificateWrongCN(CertificateTC):

    def create_testing_certificate(self):
        # Create the subject x509Name
        x509_details = {"CN": ".".join(["www", Utils.get_random_name(5), "com"])}
        x509name = self.cert_manager.create_X509Name(x509_details)
        attributes = {
            "subject": x509name
        }
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Wrong CNAME"

    def expected(self):
        return "Certificate Rejected"

class CertificateSignWithMD5(CertificateTC):

    def create_testing_certificate(self):
        # Create the subject x509Name
        x509_details = {"CN": self.hostname}
        x509name = self.cert_manager.create_X509Name(x509_details)
        attributes = {
            "subject": x509name,
            "signing_hash": "md5"
        }
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Signed with MD5"

    def expected(self):
        return "Certificate Rejected"


class CertificateSignWithMD4(CertificateTC):

    def create_testing_certificate(self):
        # Create the subject x509Name
        x509_details = {"CN": self.hostname}
        x509name = self.cert_manager.create_X509Name(x509_details)
        attributes = {
            "subject": x509name,
            "signing_hash": "md4"
        }
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Signed with MD4"

    def expected(self):
        return "Certificate Rejected"

class CertificateExpired(CertificateTC):

    def create_testing_certificate(self):
        # Create the subject x509Name
        x509_details = {"CN": self.hostname}
        x509name = self.cert_manager.create_X509Name(x509_details)
        attributes = {
            "subject": x509name,
            "notAfter": -1
        }
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Expired Certificate"

    def expected(self):
        return "Certificate Rejected"

class CertificateNotYetValid(CertificateTC):

    def create_testing_certificate(self):
        # Create the subject x509Name
        x509_details = {"CN": self.hostname}
        x509name = self.cert_manager.create_X509Name(x509_details)
        attributes = {
            "subject": x509name,
            "notBefore": 315360000 # not valid yet :)
        }
        return self.cert_manager.generate_certificate(attributes)

    def __str__(self):
        return "Not Yet Valid Certificate"

    def expected(self):
        return "Certificate Rejected"