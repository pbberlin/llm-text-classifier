import models.embeds as embeds
import pickle
from   pprint import pprint, pformat

from   copy     import deepcopy

from lib.util   import saveJson, loadJson 
from lib.config import get, set


c_samples = []
cacheDirty = False

# new statement - part of new sample
def newSt(lg=""):
    st = {
        "short":"",
        "long": lg,
    }
    return st


def new():
    st = newSt()
    nw = {  "descr": "",
        "statements": [
            st,
        ]
    }
    return nw


def dummy():
    st1 = newSt("dummy sample 1")
    st2 = newSt("dummy sample 2")

    dmmy = {
        "descr": "",
        "statements": [
            st1,
            st2,
        ]
    }
    return dmmy


def toHTMLShort(smpl):
    s  = ""
    s += f"<div>\n"
    s += f"    <p>  {smpl['descr']} </p>\n"
    smtsFlat = f"{smpl['statements']}"
    s += f"    <p style='font-size: 85%; '>{embeds.ell(smtsFlat,x=72)}</p>\n"
    s += f"</div>\n"
    return s


def toHTML(smpl):
    s = ""
    s += f"<div class='item-row'>"
    s += f"<p style='width: 99%;'>{smpl['descr']}</p>"
    for stmt in smpl["statements"]:
        s += f'''   <p class='item-shrt' > {stmt["short"]} </p>'''
        s += f'''   <p class='item-long' > {stmt["long"]}  </p>'''
    s += f"</div>"
    return s






def load():
    global c_samples  # in order to _write_ to module variable
    c_samples = loadJson("samples", subset=get("dataset"))
    if len(c_samples)== 0:
        c_samples = loadJson("samples", "init")
    # pprint(c_samples)

def save():
    if not cacheDirty:
        print(f"\tsamples    are unchanged ({len(c_samples):3} entries). ")
        return
    saveJson(c_samples, "samples", subset=get("dataset"))






# extension to handler
def update(updated):

    global c_samples  # in order to _write_ to module variable

    if len(updated) > 0:
        c_samples = updated
        global cacheDirty  
        cacheDirty = True

    # only the built in deepcopy function really isolates
    return deepcopy(c_samples)


def getLast():
    for item in reversed(c_samples):
        if item["descr"].strip() == "":
            continue
        return item

    nw = new()
    nw["descr"] = "not found"
    return  nw


def getByID(smplID):
    smplID = int(smplID)
    for idx, item in enumerate(c_samples):
        if (idx+0) == smplID:
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
    #       <button  name='action'  value='select_sample' ...
    s += f"<select  name='smplID'   >\n"

    for idx, item in enumerate(c_samples):
        if item["descr"].strip() == "":
            continue
        sel = ""
        if (idx+0) == selected:
            sel = "selected"
        s += f"\t<option {sel} value='{idx+0}' >{item['descr'].strip()}</option>\n"

    s += f"</select>\n"
    return s



async def PartialUI(request, showSelected=True):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    smplID = get("sample_id", len(c_samples)-1) # defaulting to last
    if "action" in kvPst and kvPst["action"] == "select_sample":
        smplID = int(kvPst["smplID"]) - 0 # jinja indexes are one-based
        set("sample_id", smplID)


    s  = ""
    s += "<div id='partial-ui-wrapper'>"

    s += "<form id='frmPartial1' class='frmPartial'  method=post>"
    s += f"<div style='display: inline-block: 20rem'>  {selectSingle(smplID)} </div>"
    s += '''<button
                name='action'
                value='select_sample'
                accesskey='s'
            >
                <u>S</u>witch text sample 
            </button>'''
    s += "</form>"


    smpl = getByID(smplID)
    if showSelected:
        s += toHTMLShort(smpl)


    s += "</div id='partial-ui-wrapper'>"


    return (s, smpl)



def PartialUI_Import(req, session):

    s  = ""
    s += "<div id='partial-ui-wrapper'>"
    s += "<form id='frmPartial2' class='frmPartial'  method=post>"
    s += '''    
            <label for='import-distinct'> import distinct </label> 
            <input name='import-distinct'  type='checkbox'  /> <br>  
         '''
    s += '''    
            <label for='import-all'>      import all      </label> 
            <input name='import-all'       type='checkbox'  /> <br>  
         '''
    s += '''    
            <label for='filter'>          filter          </label> 
            <input name='filter'       type='text' size=30 maxlength=30  /> <br>  
         '''
    s += '''
            <button
                name='action'
                value='import_samples'
                accesskey='i'
            >
                <u>I</u>mport 
            </button>
         '''
    s += "</form>"
    s += "</div id='partial-ui-wrapper'>"

    return s