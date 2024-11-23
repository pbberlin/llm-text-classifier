# pip install "fastapi[standard]"
# pip install "uvicorn[standard]"
# pip install jinja2

from fastapi import FastAPI
from fastapi import Header, Request, Depends, HTTPException, Form, File, UploadFile


from fastapi.responses   import Response, HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.responses   import RedirectResponse

from starlette.middleware.sessions import SessionMiddleware


from fastapi.templating  import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from typing import Any, Dict, List


import asyncio

from contextlib import asynccontextmanager




import markdown
import time
import os
from pathlib import Path
from   pprint   import pformat

import lib.util as util

from    lib.markdown_ext import renderToRevealHTML

import  lib.config as cfg

import  models.db5 as db5
import  models.db1_embeddings as db1
import  models.db6_embeddings as db6





import logging
logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s - %(levelname)s - %(message)s",
    format="%(levelname)s: - %(message)s",
)
lg = logging.getLogger(__name__)




templates = Jinja2Templates(directory="templates")

# custom template functions
def templateFunc01(value: str) -> str:
    return f"<p>templateFunc01 says: -{value}-</p>\n"
def exampleFunc(amount, currency="€"):
    return f"{amount:.2f}{currency}"
def datasetDyn():
    return cfg.get('dataset')

# register custom function to Jinja environment
templates.env.globals["templateFunc01"] = templateFunc01
templates.env.globals["exampleFunc"] = exampleFunc
templates.env.globals["datasetDyn"] = datasetDyn





@asynccontextmanager
async def lifespan(app: FastAPI):

    cfg.load(app, isFlaskApp=False)


    await db5.init_db()
    print("\tdb init stop")


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
        for idx in range(3):
            db1.dummyRecordEmbedding(db, idx)


    # application runs
    yield

    await db5.dispose_db()
    print("\tdb connection disposed")



app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.static_dir = Path("static")
app.dir_img_slides = Path("./doc/img")
app.dir_uploads = Path("./uploaded-files")
app.include_router(db6.router)
app.add_middleware(SessionMiddleware, secret_key="32168")



def addPreflightCORS():
    rsp = Response()
    rsp.headers["Access-Control-Allow-Origin"]  = "*"
    rsp.headers["Access-Control-Allow-Headers"] = "*"
    rsp.headers["Access-Control-Allow-Methods"] = "*"
    return rsp

def addActualCORS(rsp):
    rsp.headers["Access-Control-Allow-Origin"]  = "*"
    return rsp




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
        # response = await addActualCORS(response)
        response = addActualCORS(response)
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


def mock_EmbeddingsCheckAPIKeyOuter(apiKey):
    return True, "mock verification success", ""


# home, index
@app.get("/", response_class=HTMLResponse)
async def readRoot(request: Request):

    apiKey = cfg.get('OpenAIKey')

    successMsg = ""
    referrer = request.headers.get("referer", None)
    if referrer is None:
        # apiKeyValid, successMsg, invalidMsg = embeddings.checkAPIKeyOuter(apiKey)
        apiKeyValid, successMsg, invalidMsg = mock_EmbeddingsCheckAPIKeyOuter(apiKey)
        if not apiKeyValid:
            url1 = request.url_for("serveSlides", fName="doc2")
            return RedirectResponse( url=url1 )


    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "HTMLTitle": "Main page",
            "contentTpl": "main-body",
            "cntBefore": f"<p>{successMsg}</p>",
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
async def uploadFileGetH(request: Request, msg: str | None = None):

    content = ""
    content += "<br>\n"

    if msg:
        content += f"{msg}<br>\n"
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

    cnt = ""
    for idx, f in enumerate(uploaded_files):
        if f and f.filename:
            cnt += f"processing file {idx+1} of {len(uploaded_files)}. {f.size/1024:.2f} kB  <br>\n"
            # cnt += f" -{pformat(f.size)}- <br>\n"
            fn = util.cleanFileName(f.filename)
            filepath = os.path.join(app.dir_uploads, fn)

            checkExisting = Path(filepath)
            if checkExisting.is_file():
                cnt += f"  {idx+1:3} - '{f.filename}' => '{fn}' already exists. Will overwrite. <br>\n"

            with open(filepath, "wb") as bufWrite:
                bufWrite.write(await f.read())

            cnt += f"  {idx+1:3} - '{f.filename}' => '{fn}' uploaded successfully <br>\n"
        else:
            cnt += f"  {idx+1:3} - no file contents in multiple   input  {pformat(f)} <br>\n"

    # print(f"{cnt}")

    url1 = request.url_for("uploadFileGetH")
    url1 = str(request.url_for("uploadFileGetH")) + f"?msg={cnt}"
    '''
        By default, RedirectResponse uses a 307 Temporary Redirect, which preserves the original HTTP method (in this case, POST).
        To force the redirection to use GET, you can set the status code to 303 'See Other'
    '''
    return RedirectResponse( url=url1, status_code=303 )



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

    msg   = request.session.pop("msg",   None)
    data1 = request.session.pop("data1", None)
    data2 = request.session.pop("data2", None)

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

    formData = await request.form()      # key-values

    queryData = request.query_params
    queryData = dict(queryData)

    request.session["msg"]   = "processing success"
    request.session["data1"] = dict(formData)  # to make it json serializable
    request.session["data2"] = queryData

    url1 = request.url_for("renderForm01")
    return RedirectResponse( url=url1, status_code=303 )

    # return {"received_form_data": dict(formData)}








if __name__ == "__main__":

    '''
taskkill /im  Python.exe  /F
cls && fastapi dev app-fa.py
fastapi run app-fa.py

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