import unittest

from CertSlayer.HttpData import HttpResponse, HttpRequest

"""
Run with nosetests:
> nosetests TestHttpData.py
"""

class TestHttpData(unittest.TestCase):

    def test_httprequest_simple_parse(self):
        # Arrange
        r = "GET / HTTP/1.1\r\n"
        r += "HOST: asd.com\r\n"
        r += "Cookie: asdasd\r\n"
        r += "Connection: keep-alive\r\n"
        r += "\r\n"
        r += "data"
        # Act
        httpdata = HttpRequest.parse(r)
        # Assert
        self.assertEquals("GET", httpdata.request_method)
        self.assertEquals("/", httpdata.resource)
        self.assertEquals("asd.com", httpdata.host.strip())
        self.assertEquals("HTTP/1.1", httpdata.http_version)
        self.assertEquals(True, httpdata.has_keepalive())

    def test_httprequest_multiplenewlines(self):
        # Arrange
        r = "GET / HTTP/1.1\r\n"
        r += "\r\n"
        r += "data\r\n\r\n\r\ndata"
        # Act
        httpdata = HttpRequest.parse(r)
        # Assert
        self.assertEquals("data\r\n\r\n\r\ndata", httpdata.body)

    def test_httprequest_simple_repr(self):
        # Arrange
        r = "GET / HTTP/1.1\r\n"
        r += "\r\n"
        r += "data\r\n\r\n\r\ndata"
        # Act
        httpdata = HttpRequest.parse(r)
        # Assert
        self.assertEquals(r, repr(httpdata))

    def test_httprequest_headers_repr(self):
        # Arrange
        r = "GET / HTTP/1.1\r\n"
        r += "HOST: asd.com\r\n"
        r += "Cookie: asdasd\r\n"
        r += "Connection: keep-alive\r\n"
        r += "\r\n"
        r += "data\r\n\r\n\r\ndata"
        # Act
        httpdata = HttpRequest.parse(r)
        # Assert
        self.assertEquals(r, repr(httpdata))

    def test_httpresponse_simple_parse(self):
        # Arrange
        r = "HTTP/1.1 200 OK\r\n"
        r += "Date: Sun, 08 Feb xxxx 01:11:12 GMT\r\n"
        r += "Server: Apache/1.3.29 (Win32)\r\n"
        r += "Last-Modified: Sat, 07 Feb xxxx\r\n"
        r += "ETag: '0-23-4024c3a5'\r\n"
        r += "Accept-Ranges: bytes\r\n"
        r += "Content-Length: 35\r\n"
        r += "Connection: close\r\n"
        r += "Content-Type: text/html\r\n"
        r += "\r\n"
        r += "<h1> Hi mom! </h1>"
        # Act
        httpdata = HttpResponse.parse(r)
        # Assert
        self.assertEquals("HTTP/1.1", httpdata.http_version)
        self.assertEquals("200", httpdata.http_code)
        self.assertEquals("OK", httpdata.http_status)
        self.assertEquals("<h1> Hi mom! </h1>", httpdata.body)

    def test_httpresponse_multiplenewlines(self):
        # Arrange
        r = "HTTP/1.1 200 OK\r\n"
        r += "Date: Sun, 08 Feb xxxx 01:11:12 GMT\r\n"
        r += "Server: Apache/1.3.29 (Win32)\r\n"
        r += "Last-Modified: Sat, 07 Feb xxxx\r\n"
        r += "ETag: '0-23-4024c3a5'\r\n"
        r += "Accept-Ranges: bytes\r\n"
        r += "Content-Length: 35\r\n"
        r += "Connection: close\r\n"
        r += "Content-Type: text/html\r\n"
        r += "\r\n"
        r += "<h1> Hi\r\n\r\n\r\nmom! </h1>"
        # Act
        httpdata = HttpResponse.parse(r)
        # Assert
        self.assertEquals("<h1> Hi\r\n\r\n\r\nmom! </h1>", httpdata.body)

    def test_httpresponse_repr(self):
        # Arrange
        r = "HTTP/1.1 200 OK\r\n"
        r += "Server: Apache/1.3.29 (Win32)\r\n"
        r += "\r\n"
        r += "<h1> Hi mom! </h1>"
        # Act
        httpdata = HttpResponse.parse(r)
        # Assert
        self.assertEquals(r, repr(httpdata))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestHttpData)
    unittest.TextTestRunner().run(suite)