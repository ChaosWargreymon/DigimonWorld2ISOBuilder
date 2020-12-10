from datetime import datetime

class Logging:
    def __init__(self, log_level=1, console_print=False):
        self.debug_level = log_level
        self.console_print = console_print

    def debug(self, message):
        if self.debug_level >= 5:
            self._log(message, "DEBUG")

    def warn(self, message):
        if self.debug_level >= 4:
            self._log(message, "INFO")

    def info(self, message):
        if self.debug_level >= 3:
            self._log(message, "WARN")

    def error(self, message):
        if self.debug_level >= 2:
            self._log(message, "ERROR")

    def critical(self, message):
        if self.debug_level >= 1:
            self._log(message, "CRITICAL")

    def _log(self, message, debug_string):
        message = "{0} [{1}] - {2}".format(str(datetime.now()), debug_string, message)
        with open("ProcessFile.log", "a") as f:
            f.writelines("{0}\r\n".format(message))
        if self.console_print:
            print(message)