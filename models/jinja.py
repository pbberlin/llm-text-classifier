from fastapi.templating  import Jinja2Templates
import  lib.config as cfg


templates = Jinja2Templates(directory="templates")

# custom template functions
def templateFunc01(value: str) -> str:
    return f"<p>templateFunc01 says: -{value}-</p>\n"
def exampleFunc(amount, currency="€"):
    return f"{amount:.2f}{currency}"
def datasetDyn():
    return cfg.get('dataset')

# register custom function to Jinja environment
templates.env.globals["templateFunc01"] = templateFunc01
templates.env.globals["exampleFunc"]    = exampleFunc
templates.env.globals["datasetDyn"]     = datasetDyn
