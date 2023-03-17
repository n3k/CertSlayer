from cert_slayer.StandaloneModeTestController import TestStandaloneModeController
from cert_slayer.Configuration import Configuration
from cert_slayer.Utils import recv_timeout
import socket
from select import select

class StandaloneServer(object):

    def __init__(self):
        # We need the web server running on all the interfaces
        pass

    def start(self, hostname, port):
        # Setup the hostname for the Cert generation (can be an IP)
        test_controller = TestStandaloneModeController(
            hostname=hostname,
            testcase_list=Configuration().testcase_list
        )

        # Create Proxy TCP Server
        # This will simply binds to specified port and connect to the target 
        # webserver that hosts the testing certificate

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", port))
        s.listen(1)

        for i in range(len(Configuration().testcase_list)):

            server_address = test_controller.configure_web_server()
            address, port = server_address
            if Configuration().verbose_mode:                
                print(f"+ Web Server:[{i}] for host listening at {address}:{port}")

            ## Accept the incoming connection
            csock, _ = s.accept()

            ## Create a new connection to our target sever
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.connect(server_address)           

            readable_sockets = [csock, temp_sock]

            keep_alive = True
            timeout    = 10
            while keep_alive and test_controller.test_case_completed is False:
                readable, writable, exceptional = select(readable_sockets, [], [], timeout)
                #print("looping")
                for current_socket in readable:                    
                    try:
                        data = recv_timeout(current_socket)
                        if data == b'':
                            keep_alive = False

                        target_sock = csock
                        if (target_sock == current_socket):
                            target_sock = temp_sock
                        try:                            
                            target_sock.sendall(data)
                        except Exception as e:                            
                            print("sendall err: ", e)
                            keep_alive = False
                    except:
                        break
                if len(readable) == 0:
                    break

            temp_sock.close()
            csock.close()
            
            input(">> Hit enter for setting the next TestCase\n")
            print("+ Killing previous server")
            test_controller.cleanup()


        s = socket.socket()
        s.bind(("0.0.0.0", port))

        ###########################
        #############################


        # for i in range(len(Configuration().testcase_list)):

        #     server_address = test_controller.configure_web_server()
        #     address, port = server_address
        #     if Configuration().verbose_mode:                
        #         print("+ Web Server for host listening at %s on port %d" % (address, port))
                       
        #     # csock = s.accept()
                
        #     input(">> Hit enter for setting the next TestCase\n")
        #     print("+ Killing previous server")
        #     test_controller.cleanup()
                