__author__ = 'n3k'

from Logger import Logger
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import ssl
import threading
from StringIO import StringIO
from ssl import SSLError


class FakeHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, callback=None):
        self.callback = callback
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)


class SecureHTTPServer(threading.Thread):
    """
    This class will set up an HTTPS Server with a given certificate
    """
    def __init__(self, keyfile, certfile, server_address):
        threading.Thread.__init__(self)
        self.keyfile = keyfile
        self.certfile = certfile
        self.server_address = server_address
        self.httpd = None

    def setup(self, callback):
        self.httpd = FakeHTTPServer(self.server_address, FakeRequestHandler, callback=callback)
        self.httpd.socket = ssl.wrap_socket(self.httpd.socket, keyfile=self.keyfile, certfile=self.certfile, server_side=True)
        return self.httpd.socket.getsockname()

    def run(self):
        self.httpd.serve_forever()

class FakeRequestHandler(SimpleHTTPRequestHandler):

    def handle_one_request(self):
        """
        This is a wrapper on handle_on_request of BaseHTTPRequestHandler
        to handle an SSLError smoothly
        """
        try:
            SimpleHTTPRequestHandler.handle_one_request(self)
        except SSLError as e:
            Logger().log_error("## SSL exception: %s" % e.message)
            return

    def do_GET(self):
        """
        If we ever reach this method means that the SSL connection was accepted
        """
        # Perform the response
        f = StringIO()
        f.write("<html>\n")
        f.write("<title>CertSlayer</title>\n")
        f.write("<h1>Client connected</h1>")
        f.write("</html>\n")
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()

        # Perform a callback to notify the TestController about the client connection
        self.server.callback()

    def do_POST(self):
        return self.do_GET()

    def do_PUT(self):
        return self.do_GET()

    def do_HEAD(self):
        return self.do_GET()

    def do_DELETE(self):
        return self.do_GET()

class WebServerSetup(object):

    def __init__(self, keyfile=None, certfile=None, server_address=("0.0.0.0", 4444), callback=lambda x: x):
        self.keyfile = keyfile
        self.certfile = certfile
        self.server_address = server_address
        self.http_worker = None
        self.callback = callback

    def start(self):
        self.http_worker = SecureHTTPServer(self.keyfile, self.certfile, self.server_address)
        self.http_worker.setDaemon(False)
        server_address = self.http_worker.setup(self.callback)
        self.http_worker.start()
        return server_address

    def kill(self):
        """
        This is likely ending in deadlock, as the thread never returns after the call to server_close
        For now just 'pass' -> do not kill the web server created

        if self.http_worker.isAlive():
            self.http_worker.httpd.server_close()
        """
        pass







if __name__ == '__main__':
    from CertManager import CertManager

    class test(object):
        def __init__(self):
            print "CALLBACK"

    cert_manager = CertManager()
    crt_file, key_file = cert_manager.generate_certificate()
    worker1 = WebServerSetup(keyfile=key_file, certfile=crt_file, callback=test)
    print worker1.start()
    #worker1.kill()




