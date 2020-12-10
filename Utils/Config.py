import json
from pathlib import Path

class Config(object):
    def __init__(self, json_to_load):
        self._conf = self.read_config(json_to_load)

    def __getitem__(self, key):
        try:
            return self._conf[key]
        except:
            raise KeyError("The key: {} was not found in the "
                           "config.".format(key))

    def read_config(self, json_to_load):
        try:
            with open(json_to_load) as f:
                config = json.loads(f.read())
        except Exception as e:
            config = {}
        return config

    def get(self, key, default=None):
        return self._conf.get(key, default)

config = Config(Path(__file__).resolve().parent.parent.parent / "config.json")
settings = config.get("General", {})
files = config.get("Files", {})