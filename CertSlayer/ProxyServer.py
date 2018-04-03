__author__ = 'n3k'

import SocketServer
import time
import socket
from select import select
from HttpData import HttpRequest, HttpResponse, HttpDataException
from Logger import Logger
from ProxyModeTestController import TestProxyModeController
from TestController import TestControllerException
from Configuration import Configuration


class ProxyThreadedServer(SocketServer.ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)
        self.allow_reuse_address = True

class Destination(object):
    """
    This is used because some browsers (like Firefox) use a single socket
    to send data to different hosts
    """
    def __init__(self, socket_connection, host, port, address):
        self.socket_connection = socket_connection
        self.host = host
        self.port = port
        self.address = address

class ProxyHandler(SocketServer.BaseRequestHandler):
    """
    This is an asynchronous handler
    """
    timeout = None

    # Disable nagle algorithm for this socket, if True.
    disable_nagle_algorithm = False

    def __init__(self, request, client_address, server):
        self.http_data = None
        self.current_socket = None
        self.keep_alive = False
        self.readable_sockets = []
        self.destination_list = []
        self.current_destination = None
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        self.connection = self.request
        if self.timeout is not None:
            self.connection.settimeout(self.timeout)
        if self.disable_nagle_algorithm:
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.readable_sockets.append(self.request)

    def handle(self):
        if self._read_initial_client_request() > 0:
            if self.http_data.request_method == "CONNECT":
                self.process_connect()
            else:
                self.process_generic_request()

    def finish(self):
        self.request.close()
        for destination in self.destination_list:
            try:
                destination.socket_connection.close()
            except:
                pass

    def _read_initial_client_request(self):
        """
        Reads the client socket and returns the len of bytes received
        """
        try:
            self.http_data = HttpRequest.parse(self._recv_timeout(self.request))
            return len(self.http_data)
        except HttpDataException:
            return 0

    def get_destination_from_data(self):
        host, port = self._get_host_and_port()
        #print host, port
        address = socket.gethostbyname(host)
        for destination in self.destination_list:
            if destination.host == host and destination.port == port and destination.address == address:
                return destination
        # If we don't find it, create a new Destination object
        connection = self.create_connection(address, port)
        new_destination = Destination(connection, host, port, address)
        self.destination_list.append(new_destination)
        return new_destination

    def process_generic_request(self):
        # Set keep_alive if necessary
        if self.http_data.has_keepalive():
            self.keep_alive = True

        self.current_destination = self.get_destination_from_data()
        # Set up the forward channel
        self.forward_http_channel()

    def create_connection(self, address, port):
        """
        Creates connection with the destination and adds the socket to the readable list
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            self.readable_sockets.append(s)
            return s
        except Exception as e:
            Logger().log_error("## {0} - While trying to connect to {1} at port {2}".format(e.message, address, port))
            return None

    def forward_http_channel(self):
        # Send the already parsed data (the first request)
        self.send_data(socket_to=self.current_destination.socket_connection, data=repr(self.http_data))
        # Channel loop
        if self.keep_alive:
            while self.keep_alive:
                self._forward_remaining_data()
        else:
            # Send and receive the data and finish the thing
            self.send_data(socket_to=self.request, data=self._recv_timeout(self.current_destination.socket_connection))

    def _forward_remaining_data(self):
        """
        Reads data from the socket list and forwards properly
        """
        timeout = 10
        readable, writable, exceptional = select(self.readable_sockets, [], [], timeout)
        for self.current_socket in readable:
            data = self._recv_timeout(self.current_socket)
            if self.current_socket is self.request:
                # We know is an HTTP Request
                try:
                    self.http_data = HttpRequest.parse(data)
                    # Some clients re-use the socket established with the proxy to send
                    # data to several hosts
                    self.current_destination = self.get_destination_from_data()
                    if not self.http_data.has_keepalive():
                        self.keep_alive = False
                except HttpDataException:
                    #self.readable_sockets.remove(self.request)
                    continue
            else:
                # We know is an HTTP Response or Response data
                try:
                    self.http_data = HttpResponse.parse(data)
                except HttpDataException:
                    # It could be something else like a chunked response or who knows xD
                    if len(data) > 0:
                        # In this particular case, send data directly
                        self.send_data(socket_to=self.request, data=data)
                    else:
                        self.readable_sockets.remove(self.current_destination.socket_connection)
                        self.destination_list.remove(self.current_destination)
                        self.keep_alive = False
                    continue

            self.send_data(socket_to=self.__get_peer_socket(), data=repr(self.http_data))

    def send_data(self, socket_to, data):
        #().log_http(self.http_data)
        #print self.http_data
        try:
            socket_to.sendall(data)
        except Exception as e:
            print e.message
            self.keep_alive = False

    def __get_peer_socket(self):
        if self.current_socket is self.request:
            return self.current_destination.socket_connection
        return self.request

    def process_connect(self):
        # Set keep_alive if necessary
        if self.http_data.has_keepalive():
            self.keep_alive = True

        self.current_destination = self.get_destination_from_data()
        # Else Reply 200 Connection Established and forward data
        self.send_data(socket_to=self.request, data="HTTP/1.0 200 Connection established\r\n\r\n")
        # Forward data
        self.forward_https_channel()

    def forward_https_channel(self):
        timeout = 10
        if self.keep_alive:
            while self.keep_alive:
                readable, writable, exceptional = select(self.readable_sockets, [], [], timeout)
                for self.current_socket in readable:
                    try:
                        data = self._recv_timeout(self.current_socket)
                        self.send_data(socket_to=self.__get_peer_socket(), data=data)
                    except:
                        return
                if len(readable) == 0:
                    return


    def _recv_timeout(self, s, timeout=0.5):
        #make socket non blocking
        s.setblocking(0)

        total_data = []
        data = ''

        #beginning time
        begin = time.time()
        while True:
            #if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break

            #if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break

            #recv chunks of 0x2000
            try:
                data = s.recv(0x2000)
                if data:
                    total_data.append(data)
                    #change the beginning time for measurement
                    begin = time.time()
                else:
                    #sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass

        return ''.join(total_data)

    def _get_host_and_port(self):
        if ":" in self.http_data.host:
            host, port = self.http_data.host.split(":")

            port = int(port)
            # just in case a whitespace is there
            host = host.strip()
        else:
            host = self.http_data.host.strip()
            if self.http_data.request_method == "CONNECT":
                port = 443
            else:
                port = 80
        return host, port

class ProxyHandlerCertificateTest(ProxyHandler):

    def setup(self):
        ProxyHandler.setup(self)
        self.client_address = self.request.getsockname()[0]

    def finish(self):
        """Overwrite the finish() to include the killing of the web_server"""
        if self.current_destination:
            TestProxyModeController.instance(self.client_address,
                                    self.current_destination.host,
                                    self.current_destination.port).cleanup()
        ProxyHandler.finish(self)

    def redirect_destination(self):
        #try:
        server_address = TestProxyModeController.instance(self.client_address,
                                                     self.current_destination.host,
                                                     self.current_destination.port).configure_web_server()
        if server_address == None:
            return

        if Configuration().verbose_mode:
            print "Web Server for host %s listening at %s on port %d" % (self.current_destination.host, server_address[0], server_address[1])
        #except TestControllerException:
            # This means the TestSuite finished, do not redirect anymore
            #return

        address, port = server_address
        # Remove the created connection to the original destination
        self.readable_sockets.remove(self.current_destination.socket_connection)
        # Create the new connection to our fake server
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(server_address)
            self.readable_sockets.append(s)
            self.current_destination.socket_connection = s
        except Exception as e:
            Logger().log_error("## FakeServer connection error - While trying to connect to {1} at port {2}".format(address, port))

    def process_connect(self):
        # Set keep_alive if necessary
        if self.http_data.has_keepalive():
            self.keep_alive = True

        self.current_destination = self.get_destination_from_data()

        if TestProxyModeController.match_monitored_domains(self.current_destination.host):
            self.redirect_destination()

        # Else Reply 200 Connection Established and forward data
        self.send_data(socket_to=self.request, data="HTTP/1.0 200 Connection established\r\n\r\n")
        # Forward data
        self.forward_https_channel()


class ProxyServer(object):

    def __init__(self, server_address=("0.0.0.0", 8080), proxy_handler=ProxyHandler):
        self.server_address = server_address
        self.proxy_handler = proxy_handler

    def start(self):
        server = ProxyThreadedServer(self.server_address, self.proxy_handler)
        server.serve_forever()
        #proxy = threading.Thread(target=server.serve_forever)
        #proxy.setDaemon(True)
        #proxy.start()


if __name__ == "__main__":
    proxy = ProxyServer()
    proxy.start()
