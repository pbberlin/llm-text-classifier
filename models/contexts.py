from    copy   import deepcopy

from fastapi import APIRouter, Request, Depends
from fastapi.responses   import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter()

from    lib.util   import saveJson, loadJson 
import  lib.config as cfg

from    models.jinja import templates
from    models.db5 import get_db
import  models.embeds as embeds






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
    c_contexts = loadJson("contexts", subset=cfg.get("dataset"))
    if len(c_contexts)== 0:
        c_contexts = loadJson("contexts", "init")
    # pprint(c_contexts)

def save():
    if not cacheDirty:
        print(f"\tcontexts   are unchanged ({len(c_contexts):3} entries). ")
        return
    saveJson(c_contexts, "contexts", subset=cfg.get("dataset"))




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

    if id < 0:
        nw = new()
        nw["short"] = "not found"
        return  nw

    for idx, item in enumerate(c_contexts):
        if (idx+0) == id:
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



async def PartialUI(request):

    kvGet = dict(request.query_params)
    kvPstObj = await request.form()    # keep kvPstObj - to call "getlist()" on it
    kvPst = dict(kvPstObj) # after async complete

    # read multi
    ctxIds = cfg.get("context_id", [0])
    if "action" in kvPst and kvPst["action"] == "select_context":
        ctxIds = kvPstObj.getlist('ctxMulti')
        cfg.set("context_id", ctxIds)


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



@router.get('/contexts/edit')
async def contextsEditHGet(request: Request, db: Session = Depends(get_db)):

    ctxs = update([])

    msgs   = request.session.pop("context-edit-msg",  [])

    if len(msgs) == 0:
        msgs.append(f"{len(ctxs)} contexts found")


    if len(ctxs)>0 and ctxs[-1]["long"].strip() != "":
        ctxs.append( dummy() )


    return templates.TemplateResponse(
        "main.html",
        {
            "request":      request,
            "HTMLTitle":    "Edit Contexts",
            "contentTpl":   "contexts",
            "cntBefore":    "<pre>" +  "\n".join(msgs) + "</pre>",
            "listContexts": ctxs,
        },
    )




@router.post('/contexts/edit')
async def contextsEditHPost(request: Request, db: Session = Depends(get_db)):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    request.session["context-edit-msg"] = []
    request.session["context-edit-msg"].append(f"context edit start")


    # extract and process POST params
    reqCtxs = []
    if len(kvPst) > 0:
        # for i,k in enumerate(kvPost):
        #     request.session["context-edit-msg"].appendf"  req key #{i:2d}  '{k}' - {openai.ell(kvPost[k][:20],x=12)}")

        for i in range(0,100):
            sh = f"ctx{i+1:d}sh"  # starts with 1
            lg = f"ctx{i+1:d}lg"
            dl = f"ctx{i+1:d}_del"
            if lg not in kvPst:
                # print(f"input '{lg}' is unknown - breaking")
                break
            if dl in kvPst and  kvPst[dl] != "":
                request.session["context-edit-msg"].append(f"   {i} - input '{lg}' to be deleted")
                continue
            if kvPst[lg].strip() == "":
                request.session["context-edit-msg"].append(f"   {i} - input '{lg}' is empty")
                continue
            v = {  "short": kvPst[sh], "long": kvPst[lg]  }
            reqCtxs.append(v)
            request.session["context-edit-msg"].append(f"   {i} - {v['short'][0:15]} - {v['long'][0:15]}..." )
            
        request.session["context-edit-msg"].append(f"post request contained {len(reqCtxs)} contexts")
    else:
        request.session["context-edit-msg"].append("post request is empty")


    ctxs = update(reqCtxs)

    request.session["context-edit-msg"].append(f"overall number of contexts {len(ctxs) } ")

    # if len(ctxs) != len(reqCtxs):
    #     for i,v in enumerate(ctxs):
    #         request.session["context-edit-msg"].append(f"   {i} - {v['short'][0:15]} {v['long'][0:15]}..." )
    # request.session["context-edit-msg"].append(f"context edit success")

    url1 = request.url_for("contextsEditHGet")
    return RedirectResponse( url=url1, status_code=303 )


