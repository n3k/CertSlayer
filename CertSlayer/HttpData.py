from abc import ABCMeta
import urlparse

from Utils import get_request_path_from_urlparse


class HttpDataException(Exception):
    pass

class HttpData(object):

    __metaclass__ = ABCMeta

    def __init__(self, headers={}, body=""):
        self.headers = headers
        self.body = body

    def __len__(self):
        return len(repr(self))

    def has_keepalive(self):
        for k, v in self.headers.items():
            if k.lower() == "connection" or k.lower() == "proxy-connection":
                if "keep-alive" in v.lower():
                    return True
        return False


class HttpRequest(HttpData):

    def __init__(self, headers={}, body=""):
        super(HttpRequest, self).__init__(headers={}, body="")
        self.request_method = ""
        self.http_version = ""
        self.resource = ""
        self.host = ""

    def __repr__(self):
        data = "{0} {1} {2}".format(self.request_method, self.resource, self.http_version)
        data += "".join(["\r\n{0}:{1}".format(k, v) for k, v in self.headers.items()])
        data += "\r\n\r\n"
        data += self.body
        return data

    def __str__(self):
        return repr(self)

    @classmethod
    def parse(cls, stream):
        try:
            headers, body = stream.split("\r\n\r\n", 1)
        except:
            # In this case we're not dealing with HTTP data
            raise HttpDataException("This is not HTTP Data")
        headers = headers.split("\r\n")

        # Get the request line
        req = headers.pop(0)

        # Create a new HTTPData instance, fill it, and return it
        instance = cls()
        instance.request_method, instance.resource, instance.http_version = req.split()
        instance.request_method = instance.request_method.upper()
        instance.resource = get_request_path_from_urlparse(urlparse.urlparse(instance.resource))
        for k, v in [header_line.split(":", 1) for header_line in headers]:
            # No gzipped or cached content
            #if k.lower() != "if-modified-since" and k.lower() != "accept-encoding":
            # if k.lower() == "accept-encoding":
            #     v = " *;q=0"
            instance.headers[k] = v

        instance.body = body
        try:
            instance.host = next(v for k, v in instance.headers.items() if k.lower() == "host")
        except StopIteration:
            instance.host = ""

        return instance

class HttpResponse(HttpData):

    def __init__(self, headers={}, body=""):
        super(HttpResponse, self).__init__(headers={}, body="")
        self.http_version = ""
        self.http_code = ""
        self.http_status = ""

    def __repr__(self):
        data = "{0} {1} {2}".format(self.http_version, self.http_code, self.http_status)
        data += "".join(["\r\n{0}:{1}".format(k, v) for k, v in self.headers.items()])
        data += "\r\n\r\n"
        data += self.body
        return data

    def __str__(self):
        return repr(self)

    @classmethod
    def parse(cls, stream):
        try:
            headers, body = stream.split("\r\n\r\n", 1)
        except:
            # In this case we're not dealing with HTTP data
            raise HttpDataException("This is not HTTP Data")
        headers = headers.split("\r\n")

        # Get the response line
        req = headers.pop(0)

        # Create a new HTTPData instance, fill it, and return it
        instance = cls()

        req = req.split() # i.e: HTTP/1.1 304 Not Modified
        instance.http_version = req.pop(0)
        instance.http_code = req.pop(0)
        instance.http_status = " ".join(req)

        for k, v in [header_line.split(":", 1) for header_line in headers]:
            instance.headers[k] = v
        instance.body = body

        return instance
