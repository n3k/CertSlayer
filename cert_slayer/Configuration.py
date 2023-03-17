__author__ = 'n3k'

import configparser
import os
#from OpenSSL import crypto

from cert_slayer.Utils import Singleton


class ConfigurationException(Exception):
    pass

class Configuration(metaclass=Singleton):
    """
    This class exposes methods to retrieve the filenames and saves dynamic server settings
    """
    #SAVED_x509_GetExtension = None

    SECTION_CA_CERTIFICATE_SETTINGS = "CA_CERTIFICATE_SETTINGS"
    SECTION_TEMPORAL_CERTIFICATES = "TEMPORAL_CERTIFICATES"

    CA_CERTIFICATE_FILENAME = "CACertificateFilename"
    CA_KEY_FILENAME = "CAKeyFilename"

    CA_CERTIFICATE_FOLDER = "CACertificateFolder"
    TEMP_CERTIFICATE_FOLDER = "TempCertificateFolder"

    @property
    def verbose_mode(self):
        return self._verbose_mode
    @verbose_mode.setter
    def verbose_mode(self, value):
        self._verbose_mode = value

    def __init__(self, config_filename="config.ini"):
        #self._hook_GetExtension_x509()
        self.verbose_mode = False
        self.config_filename = config_filename
        if self._check_file_existence():
            self._config = configparser.ConfigParser()
            self._config.read(self.config_filename)

    #@staticmethod
    #def _x509_custom_GetExtension(instance, index):
    #    extension = Configuration.SAVED_x509_GetExtension(instance, index)
    #    print(extension.get_short_name())
    #    return extension

    #def _hook_GetExtension_x509(self):
    #    Configuration.SAVED_x509_GetExtension = crypto.X509.get_extension
    #    crypto.X509.get_extension = self._x509_custom_GetExtension

    def create_new_configuration(self, config_filename):
        self.config_filename = config_filename
        if self._check_file_existence():
            self._config = configparser.ConfigParser()
            self._config.read(self.config_filename)

    def _check_file_existence(self):
        if not os.path.isfile(self.config_filename):
            self._set_defaults()
            return False
        return True

    def _set_defaults(self):
        self._config = configparser.ConfigParser()
        self._config.read(self.config_filename)
        self._create_required_sections()
        self.set_ca_certificate_filename("certslayer.net.crt")
        self.set_ca_key_filename("certslayer.net.key")
        self.set_ca_certificate_folder("ca_cert")
        self.set_temp_certificate_folder("certificates")
        try:
            os.makedirs(self.get_ca_certificate_folder())
        except WindowsError:
            pass
        try:
            os.makedirs(self.get_temp_certificate_folder())
        except WindowsError:
            pass


    def _create_required_sections(self):
        """
        This method creates the required sections if they do not exist
        """
        if not self._check_for_section(self.SECTION_CA_CERTIFICATE_SETTINGS):
            self._config.add_section(self.SECTION_CA_CERTIFICATE_SETTINGS)
        if not self._check_for_section(self.SECTION_TEMPORAL_CERTIFICATES):
            self._config.add_section(self.SECTION_TEMPORAL_CERTIFICATES)

    ### SECTION CA_CERTIFICATE_SETTINGS

    def _check_for_section(self, section_name):
        return self._config.has_section(section_name)

    def set_ca_certificate_folder(self, value):
        self._config.set(self.SECTION_CA_CERTIFICATE_SETTINGS, self.CA_CERTIFICATE_FOLDER, value)
        self._flush_configuration()

    def set_ca_certificate_filename(self, value):
        self._config.set(self.SECTION_CA_CERTIFICATE_SETTINGS, self.CA_CERTIFICATE_FILENAME, value)
        self._flush_configuration()

    def set_ca_key_filename(self, value):
        self._config.set(self.SECTION_CA_CERTIFICATE_SETTINGS, self.CA_KEY_FILENAME, value)
        self._flush_configuration()

    def get_ca_certificate_folder(self):
        try:
            value = self._config.get(self.SECTION_CA_CERTIFICATE_SETTINGS, self.CA_CERTIFICATE_FOLDER)
        except configparser.NoOptionError:
            raise ConfigurationException("The option %s doesn't exists in %s" % (self.CA_CERTIFICATE_FOLDER, self.SECTION_CA_CERTIFICATE_SETTINGS))
        return value

    def get_ca_certificate_filename(self):
        try:
            value = self._config.get(self.SECTION_CA_CERTIFICATE_SETTINGS, self.CA_CERTIFICATE_FILENAME)
        except configparser.NoOptionError:
            raise ConfigurationException("The option %s doesn't exists in %s" % (self.CA_CERTIFICATE_FILENAME, self.SECTION_CA_CERTIFICATE_SETTINGS))
        return value

    def get_ca_certificate_file(self):
        return os.path.abspath(os.path.join(self.get_ca_certificate_folder(), self.get_ca_certificate_filename()))

    def get_ca_key_filename(self):
        try:
            value = self._config.get(self.SECTION_CA_CERTIFICATE_SETTINGS, self.CA_KEY_FILENAME)
        except configparser.NoOptionError:
            raise ConfigurationException("The option %s doesn't exists in %s" % (self.CA_KEY_FILENAME, self.SECTION_CA_CERTIFICATE_SETTINGS))
        return value

    def get_ca_key_file(self):
        return os.path.abspath(os.path.join(self.get_ca_certificate_folder(), self.get_ca_key_filename()))

    def set_temp_certificate_folder(self, value):
        self._config.set(self.SECTION_TEMPORAL_CERTIFICATES, self.TEMP_CERTIFICATE_FOLDER, value)
        self._flush_configuration()

    def get_temp_certificate_folder(self):
        try:
            value = self._config.get(self.SECTION_TEMPORAL_CERTIFICATES, self.TEMP_CERTIFICATE_FOLDER)
        except configparser.NoOptionError:
            raise ConfigurationException("The option %s doesn't exists in %s" % (self.TEMP_CERTIFICATE_FOLDER, self.SECTION_TEMPORAL_CERTIFICATES))
        return value

    def get_temp_certificate_fullpath_folder(self):
        return os.path.abspath(self.get_temp_certificate_folder())

    def _flush_configuration(self):
        with open(self.config_filename, "w") as f:
            self._config.write(f)

    @property
    def fake_server_address(self):
        return self._server_address
    @fake_server_address.setter
    def fake_server_address(self, value):
        self._server_address = value

    @property
    def testcase_list(self):
        return self._testcase_list
    @testcase_list.setter
    def testcase_list(self, value):
        self._testcase_list = value
