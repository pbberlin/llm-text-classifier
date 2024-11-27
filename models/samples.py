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


from lib.uploaded2samples import uploadedToSamples
from lib.ecb2samples      import ecbSpeechesCSV2Json

import json

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
    c_samples = loadJson("samples", subset=cfg.get("dataset"))
    if len(c_samples)== 0:
        c_samples = loadJson("samples", "init")
    # pprint(c_samples)

def save():
    if not cacheDirty:
        print(f"\tsamples    are unchanged ({len(c_samples):3} entries). ")
        return
    saveJson(c_samples, "samples", subset=cfg.get("dataset"))






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

    smplID = cfg.get("sample_id", len(c_samples)-1) # defaulting to last
    if "action" in kvPst and kvPst["action"] == "select_sample":
        smplID = int(kvPst["smplID"]) - 0 # jinja indexes are one-based
        cfg.set("sample_id", smplID)


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



async def PartialUI_Import(request: Request):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    print(kvPst)

    filterBy = ""
    if "filter" in kvPst:
        filterBy = kvPst["filter"]

    maxRecords = 10
    if "maxrecs" in kvPst:
        try:
            maxRecords = int(kvPst["maxrecs"])
        except Exception as exc:
            pass
        


    s  = f'''
    <div id='partial-ui-wrapper'>
    <form id='frmPartial2' class='frmPartial'  method=post>
        
        <label for='import-distinct'>  import distinct </label> 
        <input name='import-distinct'  type='checkbox'  /> <br>  

        <!--    
        <label for='import-all'>       import all      </label> 
        <input name='import-all'       type='checkbox'  /> <br>  
        -->


        <label for='filter'>          filter          </label> 
        <input name='filter'        type='text' value="{filterBy}"  
            size=30 maxlength=30  placeholder='i.e. Asset purchase'  /> <br>  
    
        <label for='maxrecs'>          max records          </label> 
        <input name='maxrecs'       type='text' value="{maxRecords}" 
            size=5 maxlength=5  placeholder='10'  /> <br>  

        <button
            name='action'
            value='import_samples'
            accesskey='i'
        >
            <u>I</u>mport 
        </button>
    </form>
    </div id='partial-ui-wrapper'>
    '''

    return s



async def samplesImportH(request: Request, db: Session):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    smpls = update([])
    impSmpls = []
    modeX = "none"
    filterBy = ""

    msgs = []


    if  "action" in kvPst and kvPst["action"] == "import_samples":

        if  "import-distinct" in kvPst:       # stupid checkbox submits no value if unchecked
            modeX = kvPst["import-distinct"]
        
        msgs.append(f"post request => import samples, mode {modeX}")
        
        maxRecords = int(kvPst["maxrecs"])

        filterBy = kvPst["filter"]


        if False:
            tmp = uploadedToSamples()
            impSmpls.extend(tmp)
            msgs.append(f"samples newly imported: {len(impSmpls) } (not filterd yet) ")
        else:
            numStcs = [1, 2, 4, 8, 500]
            tmp = ecbSpeechesCSV2Json(
                numStcs, 
                # filterBy="Asset purchase",
                filterBy=filterBy,
                # earlyBreakAt=3, 
                earlyBreakAt=maxRecords, 
            )
            impSmpls.extend(tmp)
            msgs.append(f"samples newly imported: {len(impSmpls) } ")



    if len(impSmpls)>0:

        existingKeys = {}
        for smpl in smpls:
            existingKeys[smpl["descr"]] = True

        importedDistinctAndFiltered = []
        for idx, smpl in enumerate(impSmpls):
            if smpl["descr"] in existingKeys:
                msgs.append(f"  smpl {idx:2} already exists - {smpl['descr']}  ")
                continue

            flat = json.dumps(smpl)
            if filterBy != "":
                contains1 = (filterBy         in flat)
                contains2 = (filterBy.title() in flat)
                contains3 = (filterBy.lower() in flat)
            if contains1 or contains2 or contains3:
                pass
            else:
                msgs.append(f"  smpl {idx:2} not contains '{filterBy}' - {smpl['descr']}  ")
                continue
            importedDistinctAndFiltered.append(smpl)
        msgs.append(f"distinct new samples: {len(importedDistinctAndFiltered) } ")


        smpls.extend(importedDistinctAndFiltered)
        smpls = update(smpls)
        msgs.append(f"overall number of samples:    {len(smpls) } ")

        # for i,v in enumerate(bmrks):
        #     msgs.append(f"   {i} - {v['descr'][0:15]} {v['statements'][0][0:15]}..." )

        msgs.append(f"{len(importedDistinctAndFiltered)} samples imported - {len(smpls) } total")


    importUI  = await PartialUI_Import(request)

    # msgsJ = f""
    # if len(msgs) > 0:
    msgsJ = f"<pre>{"\n".join(msgs)}</pre>"


    return templates.TemplateResponse(
        "main.html",
        {
            "request":      request,
            "HTMLTitle":    "Import samples",
            "contentTpl":   "samples",
            "cntBefore":    f'''
                            {msgsJ}
                            <br>
                            {importUI}
                            ''',
            "listSamples":  smpls,
        },
    )



@router.get('/samples/import')
async def samplesImportHGet(request: Request, db: Session = Depends(get_db)):
    return await samplesImportH(request, db)

@router.post('/samples/import')
async def samplesImportHPost(request: Request, db: Session = Depends(get_db)):
    return await samplesImportH(request, db)



async def samplesEditH(request: Request, db: Session):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete


    # extract and process POST params
    reqSamples = []
    if len(kvPst) > 0:

        for i1 in range(0,100):
            descr = f"sample{i1+1:d}_descr"  # starts with 1
            delet = f"sample{i1+1:d}_del"

            if descr not in kvPst:
                break

            if descr in kvPst and delet in kvPst and  kvPst[delet] != "":
                print(f"\t  input sample '{descr}' to be deleted")
                continue
            if kvPst[descr].strip() == "":
                print(f"\t  input sample '{descr}' is empty")
                continue

            sts = []
            for i2 in range(0,100):
                sh = f"sample{i1+1:d}_st{i2+1}_shrt"
                lg = f"sample{i1+1:d}_st{i2+1}_long"
                if lg not in kvPst:
                    break
                if kvPst[lg].strip() == "":
                    print(f"\t    bm {i1+1} stmt {i2+1} is empty")
                    # continue
                else:
                    sts.append(
                        {  "short": kvPst[sh], "long": kvPst[lg]  }
                    )

            reqSamples.append(
                {
                    "descr": kvPst[descr],
                    "statements": sts,
                }
            )
            print(f"\t  input sample '{descr}' - {len(sts)} stmts - {kvPst[descr]}")

        print(f"\tpost request contained {len(reqSamples)} samples")


    else:
        pass
        # print("post request is empty")


    smpls = update(reqSamples)

    print(f"\toverall number of samples {len(smpls) } ")
    # for i,v in enumerate(newSmpls):
    #     print(f"\t   {i} - {v['descr'][0:15]} {v['statements'][0][0:15]}..." )


    for smpl in smpls:
        sts = smpl["statements"]
        if len(sts) == 0  or  sts[-1]["long"].strip() != "":
            nwSt = newSt()
            sts.append( nwSt )


    if len(smpls)>0 and smpls[-1]["descr"].strip() != "" :
        smpls.append( dummy() )



    smplUI, _  = await PartialUI(request)

    # toHTML(bmSel)

    return templates.TemplateResponse(
        "main.html",
        {
            "request":      request,
            "HTMLTitle":    "Edit Samples",
            "contentTpl":   "samples",
            "cntBefore":    f'''
                            {len(smpls)} samples found
                            <br>
                            {smplUI}
                            ''',
            "listSamples": smpls,
        },
    )




@router.get('/samples/edit')
async def samplesEditHGet(request: Request, db: Session = Depends(get_db)):
    return await samplesEditH(request, db)

@router.post('/samples/edit')
async def samplesEditHPost(request: Request, db: Session = Depends(get_db)):
    return await samplesEditH(request, db)