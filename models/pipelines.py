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
    c_pipelines = loadJson("pipelines", subset=cfg.get("dataset"))
    if len(c_pipelines)== 0:
        c_pipelines = loadJson("pipelines", "init")

def save():
    if not cacheDirty:
        print(f"\tpipelines  are unchanged ({len(c_pipelines):3} entries). ")
        return
    saveJson(c_pipelines, "pipelines", subset=cfg.get("dataset"))






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

    pipeID = cfg.get("pipeline_id", len(c_pipelines)-1) # defaulting to last
    if "action" in kvPst and kvPst["action"] == "select_pipeline":
        pipeID = int(kvPst["pipeID"]) - 0 
        cfg.set("pipeline_id", pipeID)

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



async def pipelinesEditH(request: Request, db: Session):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete


    # extract and process POST params
    reqPipes = []
    if len(kvPst) > 0:

        for i1 in range(0,100):
            descK = f"pipeline{i1+1:d}_descr"  # starts with 1
            roleK = f"pipeline{i1+1:d}_role" 
            deleK = f"pipeline{i1+1:d}_del"

            if descK not in kvPst:
                break

            if descK in kvPst and deleK in kvPst and  kvPst[deleK] != "":
                print(f"  input pipeline '{descK}' to be deleted")
                continue
            if kvPst[descK].strip() == "":
                print(f"  input pipeline '{descK}' is empty")
                continue

            stages = []
            for i2 in range(0,100):
                sh = f"stage{i1+1:d}_st{i2+1}_shrt"
                lg = f"stage{i1+1:d}_st{i2+1}_long"
                rm = f"stage{i1+1:d}_st{i2+1}_rem"
                if lg not in kvPst:
                    break
                if kvPst[lg].strip() == "":
                    print(f"    bm {i1+1} stage {i2+1} is empty")
                else:
                    stages.append(
                        {  
                            "short": kvPst[sh], 
                            "long":  kvPst[lg],
                            "remark":  kvPst[rm],
                        }
                    )

            reqPipes.append(
                {
                    "descr":  kvPst[descK],
                    "role":   kvPst[roleK],
                    "stages": stages,
                }
            )
            print(f"  input pipeline '{descK}' - {len(stages)} stages - {kvPst[descK]}")

        print(f"post request contained {len(reqPipes)} pipelines")


    else:
        pass
        # print("post request is empty")


    pipes = update(reqPipes)

    print(f"overall number of pipeline {len(pipes) } ")


    for pl in pipes:
        stages = pl["stages"]
        if len(stages) == 0  or  stages[-1]["long"].strip() != "":
            nwSt = newStage()
            stages.append( nwSt )


    if len(pipes)>0 and pipes[-1]["descr"].strip() != "" :
        pipes.append( dummy() )

    pipeUI, _  = await PartialUI(request)



    return templates.TemplateResponse(
        "main.html",
        {
            "request":      request,
            "HTMLTitle":    "Edit Pipelines",
            "contentTpl":   "pipelines",
            "cntBefore":    f'''
                            {len(pipes)} pipelines found
                            <br>
                            {pipeUI}
                            ''',
            "listPipelines": pipes,
        },
    )




@router.get('/pipelines/edit')
async def pipelinesEditHGet(request: Request, db: Session = Depends(get_db)):
    return await pipelinesEditH(request, db)

@router.post('/pipelines/edit')
async def pipelinesEditHPost(request: Request, db: Session = Depends(get_db)):
    return await pipelinesEditH(request, db)