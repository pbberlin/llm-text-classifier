import models.embeddings as embeddings
import pickle
from   pprint import pprint, pformat

from   copy     import deepcopy

from lib.util import saveJson
from lib.util import loadJson


c_benchmarks = []

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
    s += f"    <p style='font-size: 85%; '>{embeddings.ell(smtsFlat,x=72)}</p>\n"
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



# load from disk
def load():
    global c_benchmarks  # in order to _write_ to module variable
    try:
        with open(r"./data/benchmarks.pickle", "rb") as inpFile:
            c_benchmarks = pickle.load(inpFile)
        print(f"loading pickle file 'benchmarks'  - size {len(c_benchmarks):2} - type {type(c_benchmarks)}   ")
    except Exception as error:
        print(f"loading pickle file 'benchmarks' caused error: {str(error)}")
        c_benchmarks = []


def save():

    if len(c_benchmarks) < 1:
        return


    saveJson(c_benchmarks, "benchmarks", tsGran=1)

    with open(r"./data/benchmarks.pickle", "wb+") as outFile:
        pickle.dump(c_benchmarks, outFile)
        print(f"saving pickle file 'benchmarks' {len(c_benchmarks):3} entries")
        # print(f"  last entry is' {benchmarks.c_benchmarks[-1]}")



# extension to handler
def update(updated):

    global c_benchmarks  # in order to _write_ to module variable

    if len(updated) > 0:
        c_benchmarks = updated
        # saving to disk is done on stop-application
    else:
        if len(c_benchmarks)<1:
            initBenchmarks    = loadJson("benchmarks", "init")
            c_benchmarks = initBenchmarks

    if False:
        # avoiding to expose c_benchmarks as global variable
        ret1 = c_benchmarks[:]
        # and doing copy of level one key "statments"
        #   but statements can still be changed by caller funcs :-(
        for idx, bm in enumerate(ret1):
            ret1[idx]["statements"] = ret1[idx]["statements"][:]

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
        if (idx+1) == bmID:
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
        if (idx+1) == selected:
            sel = "selected"
        s += f"\t<option {sel} value='{idx+1}' >{item['descr'].strip()}</option>\n"

    s += f"</select>\n"
    return s



def PartialUI(req, session, showSelected=True):

    # GET params
    args = req.args
    kvGet = args.to_dict()

    # POST params
    reqArgs = req.form.to_dict()


    bmrkID = f"{len(c_benchmarks)-0}" # defaulting to last - jinja indexes are one-based
    if "action" in reqArgs and reqArgs["action"] == "select_benchmark":
        bmrkID = reqArgs["bmrkID"]
        # print(f"new benchmark ID is {bmrkID}")
        session["bmrkID"] = bmrkID
    else:
        if "bmrkID" in session:
            bmrkID = session["bmrkID"]
            print(f"benchmark ID from session is {bmrkID}")



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

    if showSelected:
        s += toHTMLShort(bmrk)


    s += "</div id='partial-ui-wrapper'>"


    return (s, bmrk)



