# pip install "fastapi[standard]"
# pip install "uvicorn[standard]"
# pip install jinja2

from   lib.util   import lg
from   lib.util   import prof



import time
import json
import os
from   pathlib  import Path
from   pprint   import pformat


import asyncio


from contextlib import asynccontextmanager
from typing import Any, Dict, List



from fastapi import FastAPI
from fastapi import Header, Request, Depends, HTTPException, Form, File, UploadFile


from fastapi.responses   import Response, HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.responses   import RedirectResponse

from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware


from sqlalchemy.orm import Session





import lib.config as cfg
import lib.util   as util

from   lib.markdown_ext import renderToRevealHTML

from   lib.uploaded2samples import uploadedToSamples
from   lib.ecb2samples      import ecbSpeechesCSV2Json


from models.jinja import templates

# import  models.db1_embeds      as db1embeds
from models.db1_embeds import Embedding, dummyRecordEmbedding

# import  models.db1_completions as db1compls
from models.db1_completions import Completion, dummyRecordCompletion

import  models.db5 as db5




# modules with model
import models.contexts     as contexts
import models.benchmarks   as benchmarks
import models.samples      as samples
import models.pipelines    as pipelines
import models.embeds       as embeds


import  models.embeds_endpoints      as embeds_endpoints
import  models.completions_endpoints as completions_endpoints












@prof
def loadAll(args, db):

    if "ecb" in args and  len(args.ecb) > 0:
        default =  [1, 2, 4, 8, 500]
        numStcs = default
        try:
            numStcs = json.loads(args.ecb)
            if not type(numStcs) is list:
                print(f" cannot parse into a list: '{args.ecb}'")
                numStcs = default
        except Exception as exc:
            numStcs = default
            print(f" {exc} - \n\t cannot parse {args.ecb}")
            print(f" assuming default {numStcs} \n")


        smplsNew = ecbSpeechesCSV2Json(numStcs, earlyBreakAt=3, filterBy="Asset purchase" )
        samples.update(smplsNew)
        samples.save()
        quit()


    if "upl" in args and args.upl:
        smplsNew = uploadedToSamples()
        samples.update(smplsNew)
        samples.save()
        quit()



    embeds.load(db)
    contexts.load()
    benchmarks.load()
    samples.load()
    pipelines.load()






@prof
def saveAll(db, force=False):

    if force:
        embeds.cacheDirty = True
        contexts.cacheDirty = True
        benchmarks.cacheDirty = True
        samples.cacheDirty = True


    embeds.save(db)
    contexts.save()
    benchmarks.save()
    samples.save()
    pipelines.save()





@asynccontextmanager
async def lifespan(app: FastAPI):

    cfg.load(app, isFlaskApp=False)
    await db5.init_db()
    print("\tdb init stop")

    db = db5.SessionLocal()
    loadAll({}, db )



    # database access outside an endpoint
    # even with fastapi - we still need this  d------g complexity
    from contextlib import contextmanager
    @contextmanager
    def db_session():
        db = db5.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    with db_session() as db:
        db5.ifNotExistTable('embeddings')
        db5.ifNotExistTable('completions')

        for idx in range(3):
            pass
            # dummyRecordEmbedding(db, idx)
            # dummyRecordCompletion(db, idx)


    # application runs
    yield

    await db5.dispose_db()
    print("\tdb connection disposed")

    saveAll(db)
    cfg.save()




app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.static_dir = Path("static")
if False:
    app.root_path
    app.options
app.debug = True
app.dir_img_slides = Path("./doc/img")
app.dir_uploads = "uploaded-files"
app.dir_data    = "data"


os.makedirs(  os.path.join(app.root_path, app.dir_data), exist_ok=True )
os.makedirs(  os.path.join(app.root_path, app.dir_data,   "set1" ), exist_ok=True )
os.makedirs(  os.path.join(app.root_path, app.static_dir ), exist_ok=True )
os.makedirs(  os.path.join(app.root_path, app.static_dir, "img"), exist_ok=True )
os.makedirs(  os.path.join(app.root_path, app.static_dir, "img", "dynamic"), exist_ok=True )


app.include_router(contexts.router)
app.include_router(embeds_endpoints.router)
app.include_router(completions_endpoints.router)
app.add_middleware(SessionMiddleware, secret_key="32168")







# if False:
if True:
    @app.middleware("http")
    async def log_requests(request: Request, nextReq):

        # print(f"Incoming request: {request.method} {request.url}")
        # print(f"Headers: {dict(request.headers)}")

        tStart = time.time()
        response: Response = await nextReq(request)
        delta = time.time() - tStart

        print(f"\t\t{request.url.path}  {delta:.2f}"  )

        return response


    @app.middleware("http")
    async def cors_middleware(request: Request, nextReq):
        response: Response = await nextReq(request)
        # response = addActualCORS(response)
        return response











@app.get("/static-explicit/{fName:path}", response_class=FileResponse)
async def serve_file(fName: str):
    loc = app.static_dir / fName
    # print(f"{fName=} {loc=}")
    if not loc.exists() or not loc.is_file():
        raise HTTPException(status_code=404, detail=f"File not found {loc}")
    return FileResponse(loc)



@app.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    loc = app.static_dir / "favicon.svg"
    if not loc.exists() or not loc.is_file():
        raise HTTPException(status_code=404, detail=f"File not found {loc}")

    # following mimetypes made it worse:
    #  ...', mimetype='image/vnd.microsoft.icon')
    #  ...', mimetype='image/x-icon')
    return FileResponse(
        loc,
        headers={
            "Cache-Control": "public, max-age=31536000",    # Cache 1 year
            "Content-Type": "image/svg+xml"                 # Ensure correct MIME type
        },
    )



# special image handler for slides, doc
@app.get("/doc/img/{fName:path}", response_class=FileResponse)
def docImages(fName):
    loc = app.dir_img_slides / fName
    if not loc.exists() or not loc.is_file():
        raise HTTPException(status_code=404, detail=f"doc img file not found {loc}")
    return FileResponse(
        loc,
        headers={
            "Cache-Control": "public, max-age=31536000",    # Cache 1 year
        },
    )





@app.get("/slides/{fName:path}", response_class=HTMLResponse)
async def serveSlides(fName:str ="doc1" ):

    if fName == "":
        fName = "doc1"

    loc = Path(".") / "doc" / "slides" / fName

    if not loc.suffix:
        loc = loc.with_suffix(".md")

    print(f"\t{loc=}  {fName=}")

    try:
        with open(loc, encoding="utf-8") as inFile:
            mdContent = inFile.read()
            print(f"\tloaded markdown '{loc}' - {len(mdContent)} bytes")

        html = renderToRevealHTML(mdContent)

        # dump file for debug
        locOut = Path(".") / "doc" / "slides" / f"tmp-{fName}-rendered.html"
        with open( locOut, "w", encoding='utf-8') as outFile:
            outFile.write(html)


        return templates.TemplateResponse(
            "reveal-js-adapter.html",
            {
                "request": {},
                "revealHTML": html,
            },
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found {loc}")




# home, index
@app.get("/", response_class=HTMLResponse)
async def readRoot(request: Request):

    apiKey = cfg.get('OpenAIKey')

    successMsg, invalidMsg = "", ""
    referrer = request.headers.get("referer", None)
    if referrer is None:
        apiKeyValid, successMsg, invalidMsg = embeds.checkAPIKeyOuter(apiKey)
        if not apiKeyValid:
            url1 = request.url_for("serveSlides", fName="doc2")
            return RedirectResponse( url=url1 )


    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "HTMLTitle": "Main page",
            "contentTpl": "main-body",
            "cntBefore": f"<p>{successMsg}  {invalidMsg}</p>",
            # "cntAfter":  "<p> after   </p>",
        },
    )




'''
two endpoint for same URL - GET and POST

curl -X POST "http://127.0.0.1:8000/upload-file" \
  -F "uploaded_files=@2014-15.PNG" \
  -F "uploaded_files=@berenberg-2015.pdf"


'''
@app.get('/upload-file')
async def uploadFileGetH(request: Request, msg1: str | None = None):

    content = ""
    content += "<br>\n"

    if msg1:
        content += f"{msg1}<br>\n"
    else:
        content += "No multi files<br>\n"


    msgs   = request.session.pop("fileUploadMsgs",   None)
    if msgs:
        content += f"{msgs}<br>\n"
    else:
        content += "No multi files<br>\n"


    content += "<br>\n"

    return templates.TemplateResponse(
        "main.html",
        {
            "request":    request,
            "HTMLTitle":  "Upload file",
            "contentTpl": "upload-file",
            "cntAfter":   content,
        },
    )



@app.post("/upload-file")
async def uploadFilePostH(request: Request, uploaded_files: List[UploadFile] = File(...)):

    dir = Path(app.dir_data, cfg.get("dataset"), app.dir_uploads)
    os.makedirs(dir, exist_ok=True)

    msgs = []
    for idx, f in enumerate(uploaded_files):
        if f and f.filename:
            msgs.append( f"processing file {idx+1} of {len(uploaded_files)}. {f.size/1024:.2f} kB  ")
            # cnt.append( f" -{pformat(f.size)}- ")
            fn = util.cleanFileName(f.filename)
            filepath = dir / fn

            checkExisting = Path(filepath)
            if checkExisting.is_file():
                msgs.append( f"  {idx+1:3} - '{f.filename}' => '{fn}' already exists. Will overwrite. ")

            with open(filepath, "wb") as bufWrite:
                bufWrite.write(await f.read())

            msgs.append( f"  {idx+1:3} - '{f.filename}' => '{fn}' uploaded successfully ")
        else:
            msgs.append( f"  {idx+1:3} - no file contents in multiple   input  {pformat(f)} ")


    request.session["fileUploadMsgs"] = msgs


    msg = "<br>\n".join(msgs)
    url1 = request.url_for("uploadFileGetH")
    url1 = str(request.url_for("uploadFileGetH")) + f"?msg={msg}"
    '''
        By default, RedirectResponse uses a 307 Temporary Redirect, which preserves the original HTTP method (in this case, POST).
        To force the redirection to use GET, you can set the status code to 303 'See Other'
    '''
    return RedirectResponse( url=url1, status_code=303 )



@app.get('/config/edit')
async def configH(request: Request, db: Session = Depends(db5.get_db)):


    apiKey = cfg.get("OpenAIKey", "")
    apiCheckSuccessMsg   = request.session.pop("config-edit-key-success-msg",   None)
    apiCheckInvalidMsg   = request.session.pop("config-edit-key-invalid-msg-ext",   None)
    
    switchDatasetMsg = cfg.get("config-edit-ds-switch-msg", "")

    content = f'''

    <form action="" method="post">

        {apiCheckInvalidMsg}
        {apiCheckSuccessMsg}

        <label for="dataset">Open AI API Key</label>
        <input    name="api_key" type="input" size="64" value="{apiKey}"  >
        <br>

        
        {switchDatasetMsg}

        {cfg.datasetsAsHTMLSelect(app)}
        <br>

        <button accesskey="s" ><u>S</u>ubmit</button>
    </form>

    '''


    return templates.TemplateResponse(
        "main.html",
        {
            "request":    request,
            "HTMLTitle":  "Config, api key",
            "cntBefore":  content,
        },
    )





@app.post('/config/edit')
async def configHPost(request: Request, db: Session = Depends(db5.get_db)):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    apiKey = cfg.get("OpenAIKey", None)
    if "api_key" in kvPst:
        cfg.set("OpenAIKey", kvPst["api_key"])
        apiKey = kvPst["api_key"]

    apiKeyValid, successMsg, invalidMsg = embeds.checkAPIKeyOuter(apiKey)
    invalidMsgExt = ""
    if not apiKeyValid:
        invalidMsgExt = f'''
            {invalidMsg}
            <br>
            API key looks like <span style='font-size:85%'>sk-iliEnLtScLqauJejcpuDT4BlbkFJNTOc16c7E8R0NYVfODh5</span> <br>
            <br>
        '''

    request.session["config-edit-key-valid"]   = apiKeyValid
    request.session["config-edit-key-success-msg"] = successMsg
    request.session["config-edit-key-invalid-msg"] = invalidMsg
    request.session["config-edit-key-invalid-msg-ext"] = invalidMsgExt


    dsOld = cfg.get("dataset")
    dsNew = None
    if "dataset" in kvPst:
        dsNew = kvPst["dataset"]

        if dsNew != dsOld:

            request.session["config-edit-ds-switch-msg"] = f"switching from dataset '{dsOld}' to '{dsNew}' ..."

            # before switching
            saveAll(db, force=True) 

            # now switch
            cfg.set("dataset", dsNew)
            
            cfg.set("context_id",   [0])
            cfg.set("benchmark_id",  0)
            cfg.set("sample_id",     0)
            cfg.set("pipeline_id",   0)

            cfg.save()

            loadAll(db, {} )

            request.session["config-edit-ds-switch-msg"] += f"<br>\n success"

    url1 = request.url_for("configHGet")
    return RedirectResponse( url=url1, status_code=303 )





@app.get('/data/save-all')
async def saveAllH(request: Request, db: Session = Depends(db5.get_db)):
    saveAll(db, force=True)
    return "OK"






@app.get("/generate-stream-example", response_class=StreamingResponse)
async def generate_stream_example():
    async def generateChunks():
        yield "Starting stream...\n"
        yield f"{ " " * 2000 }\n"
        for i in range(20):
            yield f"chunk {i}\n"
            await asyncio.sleep(0.5)
        yield "Stream complete!"
    return StreamingResponse(generateChunks(), media_type="text/plain")






@app.get("/form01", response_class=HTMLResponse)
async def renderForm01(request: Request):

    msg   = request.session.pop("frm01Msg",   None)
    data1 = request.session.pop("frm01Data1", None)
    data2 = request.session.pop("frm01Data2", None)

    return templates.TemplateResponse(
        "main.html",
        {
            "request":    request,
            "HTMLTitle":  "form 01",
            "contentTpl": "form01",
            "msg":   msg,
            "data1": data1,
            "data2": data2,
        },
    )



@app.post("/form01")
async def processForm01(request: Request):
# async def processForm(field1: str = Form(...), field1: int = Form(...),  ):

    # key-values, dict() to make it json serializable for session storage
    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    request.session["frm01Msg"]   = "processing success"
    request.session["frm01Data1"] = kvPst
    request.session["frm01Data2"] = kvGet

    url1 = request.url_for("renderForm01")
    return RedirectResponse( url=url1, status_code=303 )

    # return {"received_form_data": dict(formData)}








if __name__ == "__main__":

    '''
taskkill /im  Python.exe  /F
cls && fastapi dev  app-fa.py

cls && fastapi run  app-fa.py

reload or workers can only be used from the command line:
        uvicorn [module-filename]:[instance-name-of-app]
        uvicorn app-fa:app
        uvicorn app-fa:app --reload   --port 8200
    '''

    if False:
        # run without reload
        # cls && python app-fa.py
        import uvicorn
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8200,
            # workers=1,
            # reload=True,
        )