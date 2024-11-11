import os

from lib.util import loadJson, saveJson

from   copy     import deepcopy

# from your_application import app
from flask import current_app


cfg = {}


def copyToAppState(appInstance):

    '''
        intricate: we have to import current_app from flask
        we have *also* need the app instance
            either per import or as function parameter
        => then we can do following
            config settings being stored in app context
            possible only once - "staticValue" can never be changed
            => dynamic stuff needs to be written as function: exampleFunc(...)

        see documentation, esp. the examples that *dont work*
        https://flask.palletsprojects.com/en/stable/templating/#context-processors
    '''
    with appInstance.app_context():
        @current_app.context_processor
        def setTemplateVars():
            def exampleFunc(amount, currency="€"):
                return f"{amount:.2f}{currency}"
            def datasetDyn():
                return get('dataset')
            return dict(
                staticValue="alpha",
                exampleFunc=exampleFunc,
                datasetDyn =datasetDyn,
            )

    if False:
        sessLifeTime = appInstance.config.get("PERMANENT_SESSION_LIFETIME")
        print(f" sessLifeTime {sessLifeTime} ")
        argApp.template_global()
        argApp.before_first_request()




def load(argApp):

    global cfg, appInstance  # in order to _write_ to module variable

    cfg = loadJson("config", "cfg", onEmpty="dict")
    if len(cfg)== 0:
        cfg = loadJson("config", "init", onEmpty="dict")

    envOpenAIKey = os.getenv('OPENAI_API_KEY')
    if envOpenAIKey is None or  len(envOpenAIKey) < 2:
        pass
    else:
        set("OpenAIKey", envOpenAIKey)


    printKeys = ["OpenAIKey", "dataset", "tokens_max"]

    for idx, k in enumerate(cfg):
        if not k.endswith("_help") and not k.endswith("last-item")  :
            if k in printKeys:
                print(f"\t  {k:24} {cfg[k]}")


    copyToAppState(argApp)


def save():
    saveJson(cfg, "config", "cfg")




def get(key):
    if len(cfg) < 1:
        raise ValueError('config not initialized yet')

    if key in cfg:
        return cfg[key]
    return None

def set(key, val):
    global cfg
    cfg[key] = val


