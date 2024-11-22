# pip install "fastapi[standard]"
# pip install "uvicorn[standard]"
# pip install jinja2

from fastapi import FastAPI
from fastapi import Header, Request, Depends, HTTPException, Form, File, UploadFile


from fastapi.responses   import Response, HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.responses   import RedirectResponse

from fastapi.templating  import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from typing import List


import asyncio

from contextlib import asynccontextmanager




import markdown
import time
import os
from pathlib import Path



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






async def addCorsHeaders(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response



if False:
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
        response = await addCorsHeaders(response)
        return response


# convenience upload files
@app.post("/upload-file")
async def upload_file(files: List[UploadFile] = File(...)):
    responses = []
    for file in files:
        fPath = os.path.join(app.dir_uploads, file.filename)
        with open(fPath, "wb") as bufWrite:
            bufWrite.write(await file.read())
        responses.append(f"{file.filename} uploaded successfully!")
    return {"messages": responses}



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