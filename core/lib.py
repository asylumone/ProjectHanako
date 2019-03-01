import logging
import core.config as config
import os


class Log:
    """Some logger for lib."""

    def __init__(self, name='bot', level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        Formatter = logging.Formatter(config.logformat)
        # Adding filehandler
        fh = logging.FileHandler(config.logfile, 'a')
        self.logger.addHandler(fh)
        fh.setFormatter(Formatter)
        # Adding Streamhandler
        sh = logging.StreamHandler()
        self.logger.addHandler(sh)
        sh.setFormatter(Formatter)

    def debug(self, *message):
        self.logger.debug(" ".join(map(str, message)))

    def info(self, *message):
        self.logger.info(" ".join(map(str, message)))

    def warning(self, *message):
        self.logger.warning(" ".join(map(str, message)))

    def error(self, *message):
        self.logger.error(" ".join(map(str, message)))


class Utils:
    @staticmethod
    def htmlescape(text, quote=True):
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if quote:
            text = text.replace('"', '&quot;').replace('\'', '&#x27;')
        return text
    
    @staticmethod
    def modulepath(modulename=None):
        if not modulename or modulename == '__main__':
            return os.path.abspath('.')
        return os.path.abspath(os.path.join(*modulename.split('.')[:-1]))
