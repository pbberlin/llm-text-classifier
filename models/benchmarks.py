from   copy     import deepcopy

from fastapi import APIRouter, Request, Depends
from fastapi.responses   import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter()

from    lib.util   import saveJson, loadJson 
import  lib.config as cfg

from    models.jinja import templates
from    models.db5 import get_db
import  models.embeds as embeds


c_benchmarks = []
cacheDirty = False

# new statement - part of new benchmark
def newSt():
    st = {
        "short":"",
        "long": "",
    }
    return st


def new():
    nw = {  "descr": "",
        "statements": [
            {
                "short":"",
                "long":"",
            },
        ]
    }
    return nw


def dummy():
    dmmy = {
        "descr": "",
        "statements": [
            {
                "short":"",
                "long":"dummy statement 1",
            },
            {
                "short":"",
                "long":"dummy statement 2",
            },
        ]
    }
    return dmmy


def toHTMLShort(bmrk):
    s  = ""
    s += f"<div>\n"
    s += f"    <p>  {bmrk['descr']} </p>\n"
    smtsFlat = f"{bmrk['statements']}"
    s += f"    <p style='font-size: 85%; '>{embeds.ell(smtsFlat,x=72)}</p>\n"
    s += f"</div>\n"
    return s


def toHTML(bmrk):
    s = ""
    s += f"<div class='item-row'>"
    s += f"<p style='width: 99%;'>{bmrk['descr']}</p>"
    for stmt in bmrk["statements"]:
        s += f'''   <p class='item-shrt' > {stmt["short"]} </p>'''
        s += f'''   <p class='item-long' > {stmt["long"]}  </p>'''
    s += f"</div>"
    return s



def load():
    global c_benchmarks  # in order to _write_ to module variable
    c_benchmarks = loadJson("benchmarks", subset=cfg.get("dataset"))
    if len(c_benchmarks)== 0:
        c_benchmarks = loadJson("benchmarks", "init")
    # pprint(c_benchmarks)

def save():
    if not cacheDirty:
        print(f"\tbenchmarks are unchanged ({len(c_benchmarks):3} entries). ")
        return
    saveJson(c_benchmarks, "benchmarks", subset=cfg.get("dataset"))




# extension to handler
def update(updated):

    global c_benchmarks  # in order to _write_ to module variable

    if len(updated) > 0:
        c_benchmarks = updated
        global cacheDirty  
        cacheDirty = True
        # saving to disk is done on stop-application

    # only the built in deepcopy function really isolates
    return deepcopy(c_benchmarks)


def getLast():
    for item in reversed(c_benchmarks):
        if item["descr"].strip() == "":
            continue
        return item

    nw = new()
    nw["descr"] = "not found"
    return  nw


def getByID(bmID):
    bmID = int(bmID)
    for idx, item in enumerate(c_benchmarks):
        if (idx+0) == bmID:
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
    #       <button  name='action'  value='select_benchmark' ...
    s += f"<select  name='bmrkID'   >\n"

    for idx, item in enumerate(c_benchmarks):
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


    bmrkID = cfg.get("benchmark_id", len(c_benchmarks)-1) # defaulting to last
    if "action" in kvPst and kvPst["action"] == "select_benchmark":
        bmrkID = int(kvPst["bmrkID"]) - 0
        cfg.set("benchmark_id", bmrkID)

    # print(f"benchmark PartialUI id {bmrkID=}")


    s  = ""
    s += "<div id='partial-ui-wrapper'>"

    s += "<form id='frmPartial' class='frmPartial'  method=post>"
    s += f"<div style='display: inline-block: 20rem'>  {selectSingle(bmrkID)} </div>"
    s += '''<button
                name='action'
                value='select_benchmark'
                accesskey='s'
            >
                <u>S</u>witch benchmark
            </button>'''
    s += "</form>"



    bmrk = getByID(bmrkID)

    # print(f"benchmark PartialUI bm {bmrk=}")

    if showSelected:
        s += toHTMLShort(bmrk)


    s += "</div id='partial-ui-wrapper'>"


    return (s, bmrk)




async def benchmarksEditH(request: Request, db: Session):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete


    # extract and process POST params
    reqBenchmarks = []
    if len(kvPst) > 0:
        for i1 in range(0,100):
            descr = f"benchmark{i1+1:d}_descr"  # starts with 1
            delet = f"benchmark{i1+1:d}_del"

            if descr not in kvPst:
                break

            if descr in kvPst and delet in kvPst and  kvPst[delet] != "":
                print(f"  input benchmark '{descr}' to be deleted")
                continue
            if kvPst[descr].strip() == "":
                print(f"  input benchmark '{descr}' is empty")
                continue

            sts = []
            for i2 in range(0,100):
                sh = f"benchmark{i1+1:d}_st{i2+1}_shrt"
                lg = f"benchmark{i1+1:d}_st{i2+1}_long"
                if lg not in kvPst:
                    break
                if kvPst[lg].strip() == "":
                    print(f"    bm {i1+1} stmt {i2+1} is empty")
                    # continue
                else:
                    sts.append(
                        {  "short": kvPst[sh], "long": kvPst[lg]  }
                    )

            reqBenchmarks.append(
                {
                    "descr": kvPst[descr],
                    "statements": sts,
                }
            )
            print(f"  input benchmark '{descr}' - {len(sts)} stmts - {kvPst[descr]}")

        print(f"post request contained {len(reqBenchmarks)} benchmarks")
    else:
        pass
        # print("post request is empty")


    bmrks = update(reqBenchmarks)

    print(f"overall number of benchmarks {len(bmrks) } ")
    # for i,v in enumerate(bmrks):
    #     print(f"   {i} - {v['descr'][0:15]} {v['statements'][0][0:15]}..." )


    for bm in bmrks:
        sts = bm["statements"]
        if len(sts) == 0  or  sts[-1]["long"].strip() != "":
            nwSt = newSt()
            sts.append( nwSt )


    if len(bmrks)>0 and bmrks[-1]["descr"].strip() != "" :
        bmrks.append( dummy() )



    bmrkUI, bmSel  = await PartialUI(request)

    # benchmarks.toHTML(bmSel)

    return templates.TemplateResponse(
        "main.html",
        {
            "request":      request,
            "HTMLTitle":    "Edit Benchmarks",
            "contentTpl":   "benchmarks",
            "cntBefore":    f'''
                            {len(bmrks)} benchmarks found
                            <br>
                            {bmrkUI}
                            ''',
            "listBenchmarks": bmrks,
        },
    )


@router.get('/benchmarks/edit')
async def benchmarksEditHGet(request: Request, db: Session = Depends(get_db)):
    return await benchmarksEditH(request, db)

@router.post('/benchmarks/edit')
async def benchmarksEditHPost(request: Request, db: Session = Depends(get_db)):
    return await benchmarksEditH(request, db)