from os import path
from json import loads, load

def load_config():
    _path = path.dirname(__file__)
    with open(_path + '/app-det.json') as f:
        return load(f)
