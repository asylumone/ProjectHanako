import logging
import core.config as config
import os
import traceback

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


logger = Log('Lib')

try:
    import yaml
except ImportError:
    logger.error("Install PyYAML to use YAMLProvider")


class YAMLProvider:
    def __init__(self, path, type={}):
        self.logger = Log(name='YAML Driver')
        self._path = path
        self.data = type
        self.load()

    def load(self):
        """Loading data from self.data"""
        try:
            self.data = yaml.load(open(self._path, 'r'))
            self.logger.debug("Loaded load()")
        except FileNotFoundError:
            self.logger.error("File not found. Creating...")
            self.save([])
        except Exception as e:
            self.logger.error(f"Exception in load(), calling save(). Exception: {e}")
            self.logger.error(traceback.format_exc())
            self.save([])
        self.logger.debug("Return data")
        return self.data

    def save(self, data=None):
        """Save data to file from data"""
        if data:
            self.data = data
        yaml.dump(self.data, open(self._path, 'w'))
        self.logger.debug("Data saved!")


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
