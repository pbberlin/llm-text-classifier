import models.embeds as embeds

from   copy     import deepcopy

from lib.util   import saveJson, loadJson 
from lib.config import get, set


c_pipelines = []
cacheDirty = False

# new stage - part of new pipeline
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
    st1 = newStage("dummy pipeline 1")
    st2 = newStage("dummy pipeline 2")
    dmmy = {
        "descr": "",
        "role":  "",
        "stages": [
            st1,
            st2,
        ]
    }
    return dmmy


def toHTMLShort(pipeL):
    s  = ""
    s += f"<div>\n"
    s += f"    <p>  {pipeL['descr']} </p>\n"
    smtsFlat = f"{pipeL['stages']}"
    s += f"    <p style='font-size: 85%; '>{embeds.ell(smtsFlat,x=72)}</p>\n"
    s += f"</div>\n"
    return s


def toHTML(pipeL):
    s = ""
    s += f"<div class='item-row'>"
    s += f"<p style='width: 99%;'>{pipeL['descr']}</p>"
    s += f"<p style='width: 99%;'>{pipeL['role']}</p>"
    for stage in pipeL["stages"]:
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


def getByID(pipeID):
    pipeID = int(pipeID)
    for idx, item in enumerate(c_pipelines):
        if (idx) == pipeID:
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
    #       <button  name='action'  value='select_pipeline' ...
    s += f"<select  name='pipeID'   >\n"

    for idx, item in enumerate(c_pipelines):
        if item["descr"].strip() == "":
            continue
        sel = ""
        if (idx+0) == selected:
            sel = "selected"
        s += f"\t<option {sel} value='{idx+0}' >{item['descr'].strip()}</option>\n"

    s += f"</select>\n"
    return s



# async def PartialUI(request, session, showSelected=True):
async def PartialUI(request, showSelected=True):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    pipeID = get("pipeline_id", len(c_pipelines)-1) # defaulting to last
    if "action" in kvPst and kvPst["action"] == "select_pipeline":
        pipeID = int(kvPst["pipeID"]) - 0 
        set("pipeline_id", pipeID)

    s  = ""
    s += "<div id='partial-ui-wrapper'>"

    s += "<form id='frmPartial5' class='frmPartial'  method=post>"
    s += f"<div style='display: inline-block: 20rem'>  {selectSingle(pipeID)} </div>"
    s += '''<button
                name='action'
                value='select_pipeline'
                accesskey='s'
            >
                <u>S</u>witch pipeline 
            </button>'''
    s += "</form>"


    pipe = getByID(pipeID)
    if showSelected:
        s += toHTMLShort(pipe)


    s += "</div id='partial-ui-wrapper'>"


    return (s, pipe)



