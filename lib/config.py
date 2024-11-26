import os

from lib.util import loadJson, saveJson

from   copy     import deepcopy

# from your_application import app
from flask import current_app


_cfg = {}


# list of subdirectories in ./data as HTMLselect
def datasetsAsHTMLSelect(app):

    base_path = app.dir_data
    dirs = []

    exclude = {
        "cfg": True,
        "init":True,
        "old-obsolete":True,
     }

    for item in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, item)) and item not in exclude and not item.startswith("tmp-"):
            dirs.append(item)

    selected = get("dataset")

    s  = '<label for="dataset">Choose a dataset:</label> '
    s += '<select name="dataset" id="dataset">'

    for dir in dirs:
        sel = ""
        if dir == selected:
            sel = ' selected'
        s += f'<option value="{dir}" {sel} >{dir}  </option>'
    s += '</select>'
    return s





def load(argApp, isFlaskApp=True):

    global _cfg, appInstance  # in order to _write_ to module variable

    _cfg = loadJson("config", "cfg", onEmpty="dict")
    if len(_cfg)== 0:
        _cfg = loadJson("config", "init", onEmpty="dict")

    envOpenAIKey = os.getenv('OPENAI_API_KEY')
    if envOpenAIKey is None or  len(envOpenAIKey) < 2:
        pass
    else:
        set("OpenAIKey", envOpenAIKey)


    printKeys = ["OpenAIKey", "dataset", "tokens_max"]

    for idx, k in enumerate(_cfg):
        if not k.endswith("_help") and not k.endswith("last-item")  :
            if k in printKeys:
                print(f"\t  {k:24} {_cfg[k]}")



def save():
    saveJson(_cfg, "config", "cfg")




def get(key, default=None):
    if len(_cfg) < 1:
        raise ValueError('config not initialized yet')

    if key in _cfg:
        return _cfg[key]
    return default


def set(key, val):
    global _cfg
    _cfg[key] = val


