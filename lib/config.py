

from lib.util import loadJson
from lib.util import saveJson

from   copy     import deepcopy

from pprint import pprint, pformat


cfg = {}


def load():
    global cfg  # in order to _write_ to module variable
    cfg = loadJson("config", "cfg", onEmpty="dict")
    if len(cfg)== 0:
        cfg = loadJson("config", "init", onEmpty="dict")
    pprint(cfg)

def save():
    saveJson(cfg, "config", "cfg")

def get(key):
    if key in cfg:
        return cfg[key]
    return None

def set(key, val):
    global cfg
    cfg[key] = val


