import os

from lib.util import loadJson, saveJson

from   copy     import deepcopy



cfg = {}




def load():
    global cfg  # in order to _write_ to module variable
    cfg = loadJson("config", "cfg", onEmpty="dict")
    if len(cfg)== 0:
        cfg = loadJson("config", "init", onEmpty="dict")

    envOpenAIKey = os.getenv('OPENAI_API_KEY')
    if envOpenAIKey is None or  len(envOpenAIKey) < 2:
        pass
    else:
        set("OpenAIKey", envOpenAIKey)

    for idx, k in enumerate(cfg):
        if not k.endswith("_help") and not k.endswith("last-item")  :
            print(f"\t  {k:24} {cfg[k]}")




def save():
    saveJson(cfg, "config", "cfg")

def get(key):
    if key in cfg:
        return cfg[key]
    return None

def set(key, val):
    global cfg
    cfg[key] = val


