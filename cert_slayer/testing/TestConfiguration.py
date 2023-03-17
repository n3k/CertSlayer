import unittest
import os

from cert_slayer.Configuration import Configuration

"""
Run with nosetests:
> nosetests TestConfiguration.py
"""

class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.config_filename = "temp.ini"

    def test_config_file_creation(self):
        Configuration(config_filename=self.config_filename)
        self.assertEquals(True, os.path.isfile(self.config_filename))
        os.unlink(self.config_filename)

    def test_create_new_configuration(self):
        Configuration().create_new_configuration(config_filename="test.ini")
        Configuration().set_ca_certificate_filename("test.crt")
        self.assertEquals("test.crt", Configuration().get_ca_certificate_filename())
        Configuration().set_ca_certificate_filename("certslayer.net.crt")
        self.assertEquals("certslayer.net.crt", Configuration().get_ca_certificate_filename())
        os.unlink("test.ini")

    def test_set_ca_certificate_settings(self):
        Configuration().create_new_configuration(self.config_filename)
        Configuration().set_ca_key_filename("examplefilename.key")
        Configuration().set_ca_certificate_filename("examplefilename.crt")
        assert Configuration().get_ca_certificate_filename() == "examplefilename.crt"
        assert Configuration().get_ca_key_filename() == "examplefilename.key"
        os.unlink(self.config_filename)

    def test_set_temp_certificate_folder(self):
        Configuration().create_new_configuration(self.config_filename)
        Configuration().set_temp_certificate_folder("tempfolder")
        self.assertEquals("tempfolder", Configuration().get_temp_certificate_folder())
        os.unlink(self.config_filename)

    def test_set_ca_certificate_folder(self):
        Configuration().create_new_configuration(self.config_filename)
        Configuration().set_ca_certificate_folder("tempfolder")
        self.assertEquals("tempfolder", Configuration().get_ca_certificate_folder())
        os.unlink(self.config_filename)

    def test_defaults(self):
        """
        self.set_ca_certificate_filename("certslayer.net.crt")
        self.set_ca_key_filename("certslayer.net.key")
        self.set_ca_certificate_folder("ca_cert")
        self.set_temp_certificate_folder("certificates")
        """
        Configuration().create_new_configuration(self.config_filename)
        self.assertEquals("certslayer.net.crt", Configuration().get_ca_certificate_filename())
        self.assertEquals("certslayer.net.key", Configuration().get_ca_key_filename())
        self.assertEquals("ca_cert", Configuration().get_ca_certificate_folder())
        self.assertEquals("certificates", Configuration().get_temp_certificate_folder())
        os.unlink(self.config_filename)

    def test_fake_server_address(self):
        Configuration().create_new_configuration(self.config_filename)
        Configuration().fake_server_address = ("127.0.0.1", 0)
        self.assertEquals(("127.0.0.1", 0), Configuration().fake_server_address)
        os.unlink(self.config_filename)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestConfiguration)
    unittest.TextTestRunner().run(suite)