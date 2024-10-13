import models.embeddings as embeddings
import pickle
from   pprint import pprint, pformat

from   copy     import deepcopy


defaults = [
    {
        "descr": "Embeddings for concepts - multilingual - sentence structure",
        "statements": [
            {"long": "employment"},
            {"long": "inflation"},
            {"long": "stocks"},
            {"long": "bubbles"},
        ],
    },


    {
         "descr": "Multi-Lingual - different tokens, similar vector scope",
         "statements": [
            {"long": "Price"},
            {"long": "price"},
            {"long": "prezzo"},
            {"long": "Preis"},
        ],
    },

    {
         "descr": "Weights are dynamically derived by the LLM using the context and using 'attention'",
         "statements": [
            {"long": "I am giving up  drinking until this is over."},
            {"long": "I am giving up. Drinking until this is over."},
        ],
    },

    {
         "descr": "Domain specific statements",
         "statements": [
            {
                "short": "falling inflation 1",
                "long":  "Deflationary trends are setting in",
            },
            {
                "short": "falling inflation 2",
                "long":  "Inflation rates are moderating",
            },
            {
                "short": "rising inflation 1",
                "long":  "Unexpected inflation is an ongoing concern",
            },
            {
                "short": "rising inflation 2",
                "long":  "Price stability is uncertain",
            },
            {
                "short": "falling inflation 3",
                "long":  "Inflationary pressures are easing",
            },
            {
                "short": "rising inflation 3",
                "long":  "Price levels surged unexpectedly",
            },
        ],
    },

    {
         "descr": "Dimensions of EU cohesion policy - border",
         "statements": [
            # "The EU should get a stronger role in immigration policy (e.g. decisions over admission standards or allocation of refugees).",
            {
                "short": "immigration",
                "long":  "The EU should get a stronger role in immigration policy.",
            },

            {
                "short": "defence",
                "long":  "A European army under the command of the EU and financed from its budget should take over duties from national armies regarding international conflict deployments.",
            },
        ],
    },

    {
         "descr": "Dimensions of EU cohesion policy - industry",
         "statements": [
            {
                "short": "industrial policy",
                "long":  "For higher economic growth of the EMU it is essential that its member states increase their investment expenditures.",
            },
            {
                "short": "agricultural policy",
                "long":  "The common agricultural policy remains the central cohesive instrument.",
            },


        ],
    },


    {
         "descr": "EU fiscal rules",
         "statements": [
            {
                "short": "fiscal rules 1",
                "long":  "The EU Stability and Growth Pact (SGP) defines deficit and debt limits for EU member states. The SGP inappropriately constrains fiscal policy in member states, and should be relaxed.",
            },
            {
                "short": "fiscal rules 2",
                "long":  "Fical rules are essential to maintain long term economic stability.",
            },
        ],
    },

    {
         "descr": "EU monetary policy - nat. bond purchases",
         "statements": [
            {
                "short": "gvt bond purchases pro",
                "long":  "The European Central Bank (ECB) did take a strongly active position in recent years by purchasing sovereign bonds of euro countries. This strongly active position of the ECB should continue.",
            },
            {
                "short": "gvt bond purchases con",
                "long":  "The European Central Bank (ECB) purchase programmes for sovereign bonds of euro countries will increase money supply and eventually increase expectations of the price level.",
            },

        ],
    },


    {
         "descr": "EU monetary policy - euro bonds",
         "statements": [
            {
                "short": "Eurobonds pro",
                "long":  "All euro countries are jointly liable for Eurobonds and all euro countries pay the same interest. The EMU should issue Eurobonds.",
            },
            {
                "short": "Eurobonds con",
                "long":  "EU political unity is too weak. EU political institutions are not developed enough to restrain debt expansion.",
            },
        ],
    },





]


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
            c_benchmarks = defaults

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



