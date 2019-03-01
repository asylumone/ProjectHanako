import core.lib as lib
import yaml
import traceback


class YAMLProvider:
    def __init__(self, path):
        self.logger = lib.Log(name='YAML Driver')
        self._path = path
        self.data = []
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
