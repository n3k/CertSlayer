__author__ = 'n3k'

from Configuration import Configuration
from Logger import Logger
from OpenSSL import crypto
import httplib
import os
import random
import Utils

class CertManager(object):

    CA_CERT = None

    def __init__(self, ca_certificate_details={}):
        self._read_ca_certificate(ca_certificate_details)

    def _read_ca_certificate(self, ca_certificate_details):
        CertManager.CA_CERT = self.load_certificate(filename=Configuration().get_ca_certificate_file())
        if CertManager.CA_CERT is None:
            Logger().log_error("## The Root CA certificate wasn't found, generating a new one...")
            crt, key = self.create_trusted_ca_certificate(ca_certificate_details)
            CertManager.CA_CERT = self.load_certificate(crt)
            Logger().log_error("## Certificate %s and key %s were generated successfully,"
                               " don't forget to add the certificate to your Tusted CA" % (crt, key))

    @classmethod
    def load_certificate(cls, filename):
        """
        Reads .PEM Certificates from disk
        """
        try:
            with open(filename, "rt") as f:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
                return cert
        except IOError:
            return None

    @classmethod
    def load_key(cls, filename):
        """
        Reads .PEM Key files from disk
        """
        try:
            with open(filename, "rt") as pkey_buffer:
                key = crypto.load_privatekey(crypto.FILETYPE_PEM, pkey_buffer.read())
                return key
        except IOError:
            return None

    @classmethod
    def describe_certificate(cls, x509):
        data = "Subject CN: %s\n" % x509.get_subject().CN
        data += "Subject Country: %s\n" % x509.get_subject().C
        data += "Subject State: %s\n" % x509.get_subject().ST
        data += "Subject City: %s\n" % x509.get_subject().L
        data += "Subject Organization: %s\n" % x509.get_subject().O
        data += "Subject Organizational Unit: %s\n" % x509.get_subject().OU
        data += "Serial Number: %s\n" % x509.get_serial_number()
        #data += "Valid from: %s\n" % x509.get_notBefore().strftime("%Y-%m-%dT%H:%M:%S%Z")
        data += crypto.dump_privatekey(crypto.FILETYPE_TEXT, x509.get_pubkey())

        data += "Issuer CN: %s\n" % x509.get_issuer().CN
        data += "Issuer Country: %s\n" % x509.get_issuer().C
        data += "Issuer State: %s\n" % x509.get_issuer().ST
        data += "Issuer City: %s\n" % x509.get_issuer().L
        data += "Issuer Organization: %s\n" % x509.get_issuer().O
        data += "Issuer Organizational Unit: %s\n" % x509.get_issuer().OU

        for i in xrange(0, x509.get_extension_count()):
            extension = x509.get_extension(i)
            try:
                data += "Extension - " + extension.get_short_name() + " " + extension.get_data() + "\n"
            except UnicodeDecodeError:
                data += "Extension - " + extension.get_short_name() + " " + "".join(["\\x{0:2x}".format(ord(_)) for _ in extension.get_data()]) + "\n"

        return data

    @classmethod
    def generate_key(cls, bits=2048):
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, bits)
        return k

    @classmethod
    def create_ca_certificate(cls, ca_certificate_details={}):
        # Create the key
        k = cls.generate_key()

        subject = ca_certificate_details.get("subject", {})

        ca_cert = crypto.X509()
        ca_cert.set_version(2) # Version 3 - we need extensions
        ca_cert.set_serial_number(1)
        ca_cert.get_subject().C = subject.get("C", "US") #Country
        ca_cert.get_subject().ST = subject.get("ST", "EarthRealm") #State
        ca_cert.get_subject().L = subject.get("L", "Racoon") #City
        ca_cert.get_subject().O = subject.get("O", "Black Mesa") #Organization
        ca_cert.get_subject().OU = subject.get("OU", "Lambda") #Organizational Unit
        ca_cert.get_subject().CN = subject.get("CN", "certslayer.net")

        ca_cert.gmtime_adj_notBefore(0)
        ca_cert.gmtime_adj_notAfter(157680000) # Five years
        # This is a Root CA, we're our own issuer ;)
        ca_cert.set_issuer(ca_cert.get_subject())
        ca_cert.set_pubkey(k)

        # Add x509 required extensions for a CA Cert
        ca_cert.add_extensions([crypto.X509Extension("basicConstraints", True, "CA:TRUE, pathlen:0"),
                                crypto.X509Extension("keyUsage", True, "keyCertSign, cRLSign")
                               ])

        # Self Signed here :)
        ca_cert.sign(k, 'sha256')

        return ca_cert, k

    @classmethod
    def duplicate_certificate_without_extensions_or_signature(cls, x509):
        cert = crypto.X509()
        cert.set_version(x509.get_version())
        cert.set_serial_number(x509.get_serial_number())
        cert.set_subject(x509.get_subject())
        cert.set_issuer(x509.get_issuer())
        cert.set_notAfter(x509.get_notAfter())
        cert.set_notBefore(x509.get_notBefore())
        return cert

    @classmethod
    def create_trusted_ca_certificate(cls, ca_certificate_details={}):
        """
        This method creates a CA Certificate that will be used to signed further certificates
        The resulting certificate should be manually installed in the system
        """
        ca_cert, k = cls.create_ca_certificate(ca_certificate_details)
        crt_filename, key_filename = cls._write_ca_cert_and_key_to_disk(ca_cert, k)
        return crt_filename, key_filename

    @classmethod
    def _write_ca_cert_and_key_to_disk(cls, cert, key):
        # Write the cert and key to disk
        # We take the names set in the configuration
        # If this wasn't set it will be the defaults
        crt_filename = Configuration().get_ca_certificate_file()
        key_filename = Configuration().get_ca_key_file()
        with open(crt_filename, "wt") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(key_filename, "wt") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        return crt_filename, key_filename

    def create_X509Name(self, x509_details={}):
        cert = crypto.X509()
        cert.get_subject().C = x509_details.get("C", "AR") #Country
        cert.get_subject().ST = x509_details.get("ST", "Argentina") #State
        cert.get_subject().L = x509_details.get("L", "CABA") #City
        cert.get_subject().O = x509_details.get("O", "CORE Security") #Organization
        cert.get_subject().OU = x509_details.get("OU", "SCS") #Organizational Unit
        cert.get_subject().CN = x509_details.get("CN", "127.0.0.1")
        return cert.get_subject()

    def sign_with_root_ca(self, x509, signing_hash="sha256"):
        k = self.generate_key()
        x509.set_pubkey(k)
        self._set_random_serial(x509)
        x509.set_issuer(CertManager.CA_CERT.get_subject())
        ca_key = self.load_key(filename=Configuration().get_ca_key_file())
        x509.sign(ca_key, signing_hash)
        return self._write_cert_and_key_to_disk(x509, k)

    def sign_with_rouge_ca(self, x509, ca_cert, ca_key, signing_hash="sha256"):
        k = self.generate_key()
        x509.set_pubkey(k)
        self._set_random_serial(x509)
        x509.set_issuer(ca_cert.get_subject())
        x509.sign(ca_key, signing_hash)
        return self._write_cert_and_key_to_disk(x509, k)

    def _set_random_serial(self, x509):
        x509.set_serial_number(random.randint(2, 12157665459056928801))

    def generate_certificate(self, attributes={}):
        """
        This method creates a certificate signed with our CA Certificate
        """
        # generate the key
        k = attributes.get("public_key", self.generate_key(bits=1024))

        # create the cert
        cert = crypto.X509()
        cert.set_subject(attributes.get("subject", self.create_X509Name()))

        self._set_random_serial(cert)
        cert.gmtime_adj_notBefore(attributes.get("notBefore", 0))
        cert.gmtime_adj_notAfter(attributes.get("notAfter", 315360000))
        cert.set_pubkey(k)

        if attributes.get("self-signed", False):
             cert.set_issuer(cert.get_subject())
        else:
            # Set the CA Cert as the Issuer if nothing is specified in attributes
            cert.set_issuer(attributes.get("issuer", CertManager.CA_CERT.get_subject()))

        # Get the hash function that will be used to sign the cert
        signing_hash = attributes.get("signing_hash", "sha256")

        if attributes.get("self-signed", False):
            key = attributes.get("signing_key", k)
            cert.sign(key, signing_hash)
        else:
        #     Sign this cert with our CA Cert
            ca_key = self.load_key(filename=Configuration().get_ca_key_file())
            cert.sign(ca_key, signing_hash)

        return self._write_cert_and_key_to_disk(cert, k)

    @classmethod
    def _write_cert_and_key_to_disk(cls, cert, key):
        # Write the cert and key to disk
        temp_folder = Configuration().get_temp_certificate_folder()
        rname = Utils.get_random_name(5)
        crt_filename = "".join([rname, ".crt"])
        key_filename = "".join([rname, ".key"])
        crt_filename = os.path.abspath(os.path.join(temp_folder, crt_filename))
        key_filename = os.path.abspath(os.path.join(temp_folder, key_filename))
        with open(crt_filename, "wt") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(key_filename, "wt") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        return crt_filename, key_filename

    @classmethod
    def get_domain_certificate(cls, hostname, port):
        c = httplib.HTTPSConnection(hostname, port)
        c.connect()
        x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, c.sock.getpeercert(True))
        return x509

if __name__ == "__main__":
    cert_manager = CertManager()
    x509 = cert_manager.get_domain_certificate("www.facebook.com", 443)
    print x509.get_subject()