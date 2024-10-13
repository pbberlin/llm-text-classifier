import models.embeddings as embeddings
import pickle
from pprint import pprint, pformat

from   copy     import deepcopy


# https://scholar.google.com/citations?view_op=view_citation&hl=de&user=21uCJ-IAAAAJ&sortby=pubdate&citation_for_view=21uCJ-IAAAAJ:TesyEGJKHF4C
entry1 = {
    "short": "EU policy evals",
    "long": '''Independent and high-quality evaluations of government policies are an important input for designing evidence-based policy. 
Lack of incentives and institutions to write such evaluations, on the other hand, carry the risk of turning the system into a costly beauty contest. 
We study one of the most advanced markets of policy evaluations in the world, the evaluations of EU Cohesion Policies by its Member States (MS). 
We use large language models quantify the findings of about 2,300 evaluations, and complement this data with our own survey of the authors. 
We show that the findings of evaluations are inconsistent with those of the academic literature on the output impacts of Cohesion Policy. 
Using further variation across MS, our analysis suggests that the market of evaluations is rather oligopolistic within MS, that it is very fragmented across the EU, and that there is often a strong involvement of managing authorities in the work of formally independent evaluators. 
These factors contribute to making the findings of the evaluations overly optimistic (beautiful) risking their overall usefulness (evidence-based policy). 
We conclude by discussing reform options to make the evaluations of EU Cohesion Policies more unbiased and effective.
''',
}

entry2 = {
    "short": "balcony flowers and herbs",
    "long": '''Gardening on the balcony can transform a small outdoor space into a lush oasis. With the right selection of plants, even a modest balcony can bloom vibrantly. Suitable flowers for balcony gardening include petunias, marigolds, and geraniums. These flowers thrive in containers and offer a burst of color throughout the growing season. For a fragrant touch, consider adding lavender or jasmine.

Herbs and spices are perfect companions to these floral beauties. Basil, mint, and parsley are well-suited for balcony gardens and can enhance your culinary creations. Rosemary and thyme are also excellent choices, providing robust flavors and aromatic foliage. These herbs are relatively low-maintenance and thrive in sunny spots.

Watering is crucial for container plants. Due to limited soil volume, containers dry out faster than garden beds. Water your balcony plants regularly, ensuring the soil stays moist but not waterlogged. Early morning or late evening is the best time to water, reducing evaporation and preventing fungal diseases.

Fertilization is vital for the health and growth of balcony plants. Use a balanced, water-soluble fertilizer every two weeks during the growing season. Organic options, like compost tea or fish emulsion, can provide essential nutrients while being environmentally friendly. Regular feeding ensures your plants remain vigorous and productive, turning your balcony into a green haven.
''',
}


entry3 = {
    "short": "Oncology",
    "long": '''Cancer growth is a negative thing. Cancer research wants to prevent or limit the growth of cancers.
''',
}


default = [
    entry1,
    entry2,
    entry3,
]

c_contexts = []

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


# load from disk
def load():
    global c_contexts  # in order to _write_ to module variable
    try:
        with open(r"./data/contexts.pickle", "rb") as inpFile:
            c_contexts = pickle.load(inpFile)
        print(f"loading pickle file 'contexts'    - size {len(c_contexts):2} - type {type(c_contexts)}   ")

    except Exception as error:
        print(f"loading pickle file 'contexts' caused error: {str(error)}")
        c_contexts = []


def save():
    # global c_contexts
    with open(r"./data/contexts.pickle", "wb+") as outFile:
        pickle.dump(c_contexts, outFile)
        print(f"saving pickle file 'contexts'   {len(c_contexts):3} entries")


# extension to handler
def update(updated):

    global c_contexts  # in order to _write_ to module variable

    if len(updated) > 0:
        c_contexts = updated 
        # saving to disk is done on stop-application
    else: 
        if len(c_contexts)<1:
            c_contexts = default

    if False:
        ret=c_contexts[:]  # a shallow copy, avoiding to expose c_contexts as global variable

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
            s += f"     <span style='font-size: 85%'>{embeddings.ell(ctxObj['long'],x=64)}</span>\n"
            s += f"</li>\n"
        s += f"</ul>\n"

    # s += f"<hr>\n"

    s += "</div id='partial-ui-wrapper'>"


    return (s, ctxs)



