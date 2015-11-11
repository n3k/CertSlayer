from Utils import Singleton

class Logger(object):
    """
    This will Log HTTPData requests as well as other events like exceptions
    """

    __metaclass__ = Singleton

    def __init__(self, logfile="logfile.txt"):
        self.logfile = logfile
        with open(self.logfile, "w") as f:
            f.write("Here is the logged information\n")
            f.write("---------------------------------------------------\n")

    def log_http(self, http_data, verbose=False):
        with open(self.logfile, "a") as f:
            f.write(str(http_data))

    def log_error(self, error):
        with open(self.logfile, "a") as f:
            line = "*** Error ocurred: {0}\n".format(error)
            f.write(line)
