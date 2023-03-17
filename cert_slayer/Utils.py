__author__ = 'n3k'

import random
import time
import string

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def get_random_name(size):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

def get_domain_from_urlparse(parsed_url):
    """
    This method receives the netloc member of the result from urlparse.urlparse("url_here")
    """
    netloc = parsed_url.netloc
    at_index = netloc.find("@")
    if at_index != -1:
        netloc = netloc[at_index+1:]
    colon_index = netloc.find(":")
    if colon_index != -1:
        netloc = netloc[0:colon_index]
    return netloc

def get_request_path_from_urlparse(parsed_url):
    if parsed_url.query != "":
        return parsed_url.path + "?" + parsed_url.query
    return parsed_url.path


def recv_timeout(s, timeout=0.5):
    #make socket non blocking
    s.setblocking(0)

    total_data = []
    data = b''

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

    return b''.join(total_data)

if __name__ == "__main__":
    from urllib.parse import urlparse
    urls = ["http://asdad.com/resource?b=1",
            "https://eni@asdas.com/asdasd/xxx.php?foo",
            "https://en:passwordi@asdas.com/asdasd/asd.html?user=1&asd=1",
            "https://adsasd.com:8000/asdsad",
            "https://user@adsasd.com:8000/asdsad",
            "https://user:password@padsasd.com:8000/asdsad"]

    for i in urls:
        parsed_url = urlparse(i)
        print(get_domain_from_urlparse(parsed_url), get_request_path_from_urlparse(parsed_url))