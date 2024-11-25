import models.embeds as embeds
import pickle
from pprint import pprint, pformat

from   copy     import deepcopy

from lib.util   import saveJson, loadJson 
from lib.config import get, set


c_contexts = []
cacheDirty = False

def new():
    nw = {
        "short":"",
        "long": "",
    }
    return nw


def dummy():
    dumm = {
        "short": "dummy",
        "long":  "",
    }
    return dumm


def load():
    global c_contexts  # in order to _write_ to module variable
    c_contexts = loadJson("contexts", subset=get("dataset"))
    if len(c_contexts)== 0:
        c_contexts = loadJson("contexts", "init")
    # pprint(c_contexts)

def save():
    if not cacheDirty:
        print(f"\tcontexts   are unchanged ({len(c_contexts):3} entries). ")
        return
    saveJson(c_contexts, "contexts", subset=get("dataset"))




# extension to handler
def update(updated):

    global c_contexts  # in order to _write_ to module variable

    if len(updated) > 0:
        c_contexts = updated 
        global cacheDirty  
        cacheDirty = True

    # only the built in deepcopy function really isolates 
    return deepcopy(c_contexts)


def getLast():
    for item in reversed(c_contexts):
        if item["long"].strip() == "":
            continue
        return item

    nw = new()
    nw["short"] = "not found"
    return  nw


def getByID(idstr):
    id = int(idstr)

    if id < 1:
        nw = new()
        nw["short"] = "not found"
        return  nw

    for idx, item in enumerate(c_contexts):
        if (idx+1) == id:
            return item

    nw = new()
    nw["short"] = "not found"
    return  nw


def selectMulti(selectedIds):
    
    s = ""
    attrChecked = ""

    # UI for none / empty 
    if "-1" in selectedIds:
        attrChecked = "checked" 
    s += f'''\t<label   for='ctxNone' >None</label>\n'''
    s += f'''\t<input  name='ctxMulti'
            type='checkbox'  value='-1' {attrChecked} /><br>\n'''


    for idx, item in enumerate(c_contexts):
        if item["long"].strip() == "":
            continue
        attrChecked = ""
        if f"{idx+1}" in selectedIds:
            attrChecked = "checked" 
        s += f'''\t<label  for='ctx{idx+1}' >{item['short'].strip()}</label>\n'''
        s += f'''\t<input name='ctxMulti' oldName='ctxMulti{idx+1}' 
                type='checkbox'   value='{idx+1}' {attrChecked} /> <br>\n'''
    
    return s   



def PartialUI(req, session):

    # GET params
    args = req.args
    kvGet = args.to_dict()

    # POST params
    reqArgs = req.form.to_dict()

    ctxIds = []
    if "action" in reqArgs and reqArgs["action"] == "select_context":
        ctxIds = req.form.getlist("ctxMulti") # flask specific - returns array of checkboxes
        session["ctxs"] = ctxIds
    else:
        if "ctxs" in session:
            ctxIds = session["ctxs"]


    s  = ""
    s += "<div id='partial-ui-wrapper'>"
    s += "<form id='frmPartial' class='frmPartial'  method=post>" # must be post get request.form.get_list("ctxMulti")
    s += f"<div style='display: inline-block: 20rem'>  {selectMulti(ctxIds)} </div>"
    s += '''<button 
                name='action' 
                value='select_context'
                accesskey='s' 
            >
                <u>S</u>witch context 
            </button>'''
    s += "</form>"


    # s += f"<p>effective context  -<span style='font-size: 85%'>{lib_openai.ell(ctx['long'],x=64)}</span>-</p>\n"



    ctxs = []
    if len(ctxIds) >= 0:
        s += f"<ul>\n"
        for ctxId in ctxIds:
            if ctxId == "-1":
                ctxObj = {"short": "", "long": ""}
            else:
                ctxObj = getByID(ctxId)
            ctxs.append( ctxObj )
            shrt = ctxObj['short']
            if shrt.strip() == "":
                shrt = "none"
            s += f"<li> {shrt} &nbsp;&nbsp;&nbsp; \n"
            s += f"     <span style='font-size: 85%'>{embeds.ell(ctxObj['long'],x=64)}</span>\n"
            s += f"</li>\n"
        s += f"</ul>\n"

    # s += f"<hr>\n"

    s += "</div id='partial-ui-wrapper'>"


    return (s, ctxs)



