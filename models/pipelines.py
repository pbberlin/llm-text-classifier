import models.embeds as embeds

from   copy     import deepcopy

from lib.util   import saveJson, loadJson 
from lib.config import get, set


c_pipelines = []
cacheDirty = False

# new statement - part of new template
def newStage(lg=""):
    st = {
        "short":  "",
        "long":   lg,
        "remark": "",
    }
    return st


def new():
    st1 = newStage()
    nw = {  
        "descr": "",
        "role":  "",
        "stages": [
            st1,
        ]
    }
    return nw


def dummy():
    st1 = newStage("dummy template 1")
    st2 = newStage("dummy template 2")
    dmmy = {
        "descr": "",
        "role":  "",
        "stages": [
            st1,
            st2,
        ]
    }
    return dmmy


def toHTMLShort(tpl):
    s  = ""
    s += f"<div>\n"
    s += f"    <p>  {tpl['descr']} </p>\n"
    smtsFlat = f"{tpl['stages']}"
    s += f"    <p style='font-size: 85%; '>{embeds.ell(smtsFlat,x=72)}</p>\n"
    s += f"</div>\n"
    return s


def toHTML(tpl):
    s = ""
    s += f"<div class='item-row'>"
    s += f"<p style='width: 99%;'>{tpl['descr']}</p>"
    s += f"<p style='width: 99%;'>{tpl['role']}</p>"
    for stage in tpl["stages"]:
        s += f'''   <p class='item-shrt' > {stage["short"]} </p>'''
        s += f'''   <p class='item-long' > {stage["long"]}  </p>'''
    s += f"</div>"
    return s






def load():
    global c_pipelines  # in order to _write_ to module variable
    c_pipelines = loadJson("pipelines", subset=get("dataset"))
    if len(c_pipelines)== 0:
        c_pipelines = loadJson("pipelines", "init")

def save():
    if not cacheDirty:
        print(f"\tpipelines  are unchanged ({len(c_pipelines):3} entries). ")
        return
    saveJson(c_pipelines, "pipelines", subset=get("dataset"))






# extension to handler
def update(updated):

    global c_pipelines  # in order to _write_ to module variable

    if len(updated) > 0:
        c_pipelines = updated
        global cacheDirty  
        cacheDirty = True

    # only the built in deepcopy function really isolates
    return deepcopy(c_pipelines)


def getLast():
    for item in reversed(c_pipelines):
        if item["descr"].strip() == "":
            continue
        return item

    nw = new()
    nw["descr"] = "not found"
    return  nw


def getByID(tplID):
    tplID = int(tplID)
    for idx, item in enumerate(c_pipelines):
        if (idx) == tplID:
            return item

    nw = new()
    nw["descr"] = "not found"
    return  nw


def selectSingle(selectedStr):

    selected = int(selectedStr)

    s = ""
    # we cannot use
    #        onchange='this.form.submit()'
    # since it does not convey the
    #       <button  name='action'  value='select_template' ...
    s += f"<select  name='tplID'   >\n"

    for idx, item in enumerate(c_pipelines):
        if item["descr"].strip() == "":
            continue
        sel = ""
        if (idx+0) == selected:
            sel = "selected"
        s += f"\t<option {sel} value='{idx+0}' >{item['descr'].strip()}</option>\n"

    s += f"</select>\n"
    return s



def PartialUI(req, session, showSelected=True):

    # GET params
    args = req.args
    kvGet = args.to_dict()

    # POST params
    reqArgs = req.form.to_dict()


    tplID = get("pipeline_id", len(c_pipelines)-1) # defaulting to last
    if "action" in reqArgs and reqArgs["action"] == "select_template":
        tplID = int(reqArgs["tplID"]) - 0  # jinja indexes are one-based
        set("pipeline_id", tplID)


    s  = ""
    s += "<div id='partial-ui-wrapper'>"

    s += "<form id='frmPartial5' class='frmPartial'  method=post>"
    s += f"<div style='display: inline-block: 20rem'>  {selectSingle(tplID)} </div>"
    s += '''<button
                name='action'
                value='select_template'
                accesskey='s'
            >
                <u>S</u>witch template 
            </button>'''
    s += "</form>"


    tpl = getByID(tplID)
    if showSelected:
        s += toHTMLShort(tpl)


    s += "</div id='partial-ui-wrapper'>"


    return (s, tpl)



