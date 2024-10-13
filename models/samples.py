import models.embeddings as embeddings
import pickle
from   pprint import pprint, pformat

from   copy     import deepcopy


defaults = [

    {
         "descr": "EU agriculture",
         "statements": [
            {
                "short": "CAP adjustment",
                "long":  "The common agricultural policy (CAP) should be readjusted from a compensation for cheap imports towards a green subsidy.",
            },
            {
                "short": "contradiction + nonsensical robustness",
                "long":  "If you sugar rhubarb, it gets sour. Pollution has vitamins.",
            },
        ],
    },



    {
         "descr": "EU foreign policy - border",
         "statements": [
            {
                "short": "joint borders pro",
                "long":  "Germany should give bilateral help to Greece for border security and humanitarian relief.",
            },
            {
                "short": "joint borders con",
                "long":  "Countries should enforce their national borders even in breach of EU agreements.",
            },
        ],
    },


    {
         "descr": "EU foreign policy - economic sanctions",
         "statements": [
            {
                "short": "joint sanctions pro",
                "long":  "Violation of economic sanctions should be penalized by withholding EU subsidies",
            },
            {
                "short": "joint sanctions con",
                "long":  "EU countries should not be subjected to a common regime of economic sanctiions.",
            },
        ],
    },


    {
         "descr": "EU foreign policy - joint military",
         "statements": [
            {
                "short": "joint military pro",
                "long":  "Germany and France should revive their joint maneuvers.",
            },
            {
                "short": "joint military con",
                "long":  "All military operations should exclusively supervised by NATO. No role for the EU policy makers.",
            },
        ],
    },



    {
         "descr": "EU fiscal policy - taxation",
         "statements": [
            {
                "short": "taxation authority pro",
                "long":  "Import taxes and custom duties should be collected directly and retained by the EU.",
            },
            {
                "short": "taxation authority pro ultra",
                "long":  "The EU should be authorized to collect taxes. A surplus charge to national income taxes.",
            },
            {
                "short": "taxation authority con",
                "long":  "EU contributions by member states are too large. They are unfairly redistributed.",
            },
        ],
    },


    {
         "descr": "EU monetary policy - bond",
         "statements": [
            {
                "short": "bond issuance pro",
                "long":  "The EU should issue bonds. All member states should be liable.",
            },
            {
                "short": "bond issuance pro ultra",
                "long":  "The issuance of bonds, jointly underwritten by all EU member countries, would unleash growth, quickly amortizing.",
            },
            {
                "short": "bond issuance neutral",
                "long":  "The issuance of bonds, jointly underwritten by all EU member countries, would result in fiscal expansion.",
            },
            {
                "short": "bond issuance detail - pro",
                "long":  "Tranches of high, medium and low risk should be issued and auctioned separately.",
            },
            {
                "short": "bond issuance - implicit - con",
                "long":  "Once an euro bond facility is established, the political economy of Europe will inevitably lead to excessive use of it. The price of money will fall. Supply of money will outstrip demand.",
            },
            {
                "short": "bond issuance explicit - con",
                "long":  "EU debt will be ruinous. It will destroy the currency. Making imports impossible. Impoverish wage earners. Benefitting asset owners. Decline and fall of Rome will ensue.",
            },

        ],
    },



]


c_samples = []

# new statement - part of new sample
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
                "long":"dummy sample 1",
            },
            {
                "short":"",
                "long":"dummy sample 2",
            },
        ]
    }
    return dmmy


# unused
def toHTMLShort(smpl):
    s  = ""
    s += f"<div>\n"
    s += f"    <p>  {smpl['descr']} </p>\n"
    smtsFlat = f"{smpl['statements']}"
    s += f"    <p style='font-size: 85%; '>{embeddings.ell(smtsFlat,x=72)}</p>\n"
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



# load from disk
def load():
    global c_samples  # in order to _write_ to module variable

    try:
        with open(r"./data/samples.pickle", "rb") as inpFile:
            c_samples = pickle.load(inpFile)
        print(f"loading pickle file 'samples'     - size {len(c_samples):2} - type {type(c_samples)}   ")
    except Exception as error:
        print(f"loading pickle file 'samples' caused error: {str(error)}")
        c_samples = []



def loadAndAppendImported():
    global c_samples  # in order to _write_ to module variable
    try:
        with open(r"./data/samples-newly-imported.pickle", "rb") as inpFile:
            uploaded = pickle.load(inpFile)
            c_samples.extend(uploaded) # not append
        print(f"loading pickle file 'samples upl' - size {len(c_samples):2} - type {type(c_samples)}   ")
    except Exception as error:
        print(f"loading pickle file 'samples uploaded' caused error: {str(error)}")



def save():
    with open(r"./data/samples.pickle", "wb+") as outFile:
        pickle.dump(c_samples, outFile)
        print(f"saving pickle file 'samples'    {len(c_samples):3} entries")
        # print(f"  last entry is' {samples.c_samples[-1]}")



# extension to handler
def update(updated):

    global c_samples  # in order to _write_ to module variable

    if len(updated) > 0:
        c_samples = updated
        # saving to disk is done on stop-application
    else:
        if len(c_samples)<1:
            c_samples = defaults

    if False:
        # avoiding to expose c_samples as global variable
        ret1 = c_samples[:]
        # and doing copy of level one key "statments"
        #   but statements can still be changed by caller funcs :-(
        for idx, bm in enumerate(ret1):
            ret1[idx]["statements"] = ret1[idx]["statements"][:]

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
        if (idx+1) == smplID:
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


    smplID = f"{len(c_samples)-0}" # defaulting to last - jinja indexes are one-based
    if "action" in reqArgs and reqArgs["action"] == "select_sample":
        smplID = reqArgs["smplID"]
        # print(f"new sample ID is {smplID}")
        session["smplID"] = smplID
    else:
        if "smplID" in session:
            smplID = session["smplID"]
            print(f"sample ID from session is {smplID}")



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