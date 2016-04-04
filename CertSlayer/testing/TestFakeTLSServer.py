import unittest
import os

from CertSlayer.FakeTLSServer import WebServerSetup
from CertSlayer.CertManager import CertManager
from CertSlayer.Configuration import Configuration

"""
Run with nosetests:
> nosetests TestFakeTLSServer.py
"""


class callbackTest(object):

    def __init__(self):
        self.track = 0

    def increment(self):
        self.track += 1
        return self.track

class AuxiliarHTTPSClient(object):

    @classmethod
    def request(cls, url, method="GET"):
        import urllib3
        ca_certs = os.path.join(Configuration().get_ca_certificate_folder(), Configuration().get_ca_certificate_filename())

        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                   ca_certs=ca_certs)
        try:
            r = http.request(method, url)
        except urllib3.exceptions.SSLError as e:
            pass

class TestFakeTLSServer(unittest.TestCase):
    """
    Yeah.. these are not "unit" tests,, but whatever...
    """

    def setUp(self):
        self.cert_manager = CertManager()
        self.callback_test = callbackTest()

    def test_local_server_up_ca_signed(self):
        crt_file, key_file = self.cert_manager.generate_certificate()
        crt_file = os.path.join(Configuration().get_temp_certificate_folder(), crt_file)
        key_file = os.path.join(Configuration().get_temp_certificate_folder(), key_file)
        worker1 = WebServerSetup(keyfile=key_file,
                                 certfile=crt_file,
                                 server_address=("127.0.0.1", 4444),
                                 callback=self.callback_test.increment)
        worker1.start()
        AuxiliarHTTPSClient.request("https://127.0.0.1:4444/")
        # import time
        # time.sleep(200)
        worker1.kill()
        self.assertEquals(1, self.callback_test.track)

    def test_local_server_up_self_signed(self):
        attribs = {"self-signed": True}
        crt_file, key_file = self.cert_manager.generate_certificate(attribs)
        crt_file = os.path.join(Configuration().get_temp_certificate_folder(), crt_file)
        key_file = os.path.join(Configuration().get_temp_certificate_folder(), key_file)
        worker1 = WebServerSetup(keyfile=key_file,
                                 certfile=crt_file,
                                 server_address=("127.0.0.1", 4444),
                                 callback=self.callback_test.increment)
        worker1.start()
        AuxiliarHTTPSClient.request("https://127.0.0.1:4444/")
        worker1.kill()
        self.assertEquals(0, self.callback_test.track)

    def tearDown(self):
        target_folder = Configuration().get_temp_certificate_folder()
        for f in os.listdir(target_folder):
            os.remove(os.path.join(target_folder, f))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFakeTLSServer)
    unittest.TextTestRunner().run(suite)