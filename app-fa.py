# pip install "fastapi[standard]"
# pip install "uvicorn[standard]"
# pip install jinja2

from fastapi import FastAPI
from fastapi import Request, Depends, HTTPException, Form, File, UploadFile

from fastapi.responses   import Response, HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.templating  import Jinja2Templates
from fastapi.staticfiles import StaticFiles



import asyncio

from contextlib import asynccontextmanager


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select


import markdown
import time
import os
from pathlib import Path
import logging

from pydantic import BaseModel
from typing import List, Dict

from lib.markdown_ext import renderToRevealHTML


logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s - %(levelname)s - %(message)s",
    format="%(levelname)s: - %(message)s",
)
lg = logging.getLogger(__name__)



# database setup
DATABASE_URL = "sqlite+aiosqlite:///./data/embeddings-mostly-fastapi.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
)

# models
class EmbeddingX(BaseModel):
    id: int
    data: Dict

async def init_db():
    async with engine.begin() as conn:
        # from models import Base  
        # Ensure models have shared base class
        if False:
            await conn.run_sync(EmbeddingX.metadata.create_all)


async def get_db():
    async with async_session() as session:
        yield session






@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()
    print("\tdb init")

    yield  # application runs here


    await engine.dispose()
    print("\tdb connection disposed")


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# custom template functions
def templateFunc01(value: str) -> str:
    return f"<p>templateFunc01 says: -{value}-</p>\n"

# register custom function to Jinja environment
templates.env.globals["templateFunc01"] = templateFunc01



@app.middleware("http")
async def log_requests(request: Request, nextReq):

    # print(f"Incoming request: {request.method} {request.url}")
    # print(f"Headers: {dict(request.headers)}")
    
    tStart = time.time()

    response: Response = await nextReq(request)
    
    delta = time.time() - tStart

    print(f"\t\t{request.url.path}  {delta:.2f}"  )

    return response




if False:
    async def addCorsHeaders(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        return response


    @app.middleware("http")
    async def cors_middleware(request: Request, call_next):
        response = await call_next(request)
        return await addCorsHeaders(response)


DIR_STATIC = Path("./static")


@app.get("/static-explicit/{fName:path}", response_class=FileResponse)
async def serve_file(fName: str):
    loc = DIR_STATIC / fName
    # print(f"{fName=} {loc=}")
    if not loc.exists() or not loc.is_file():
        raise HTTPException(status_code=404, detail=f"File not found {loc}")
    return FileResponse(loc)



@app.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    loc = DIR_STATIC / "favicon.svg"
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


DIR_IMG_SLIDES = Path("./doc/img")


# special image handler for slides, doc
@app.get("/doc/img/{fName:path}", response_class=FileResponse)
def docImages(fName):
    loc = DIR_IMG_SLIDES / fName
    if not loc.exists() or not loc.is_file():
        raise HTTPException(status_code=404, detail=f"doc img file not found {loc}")
    return FileResponse(
        loc,
        headers={
            "Cache-Control": "public, max-age=31536000",    # Cache 1 year
        },   
    )     





'''
    Page break for every header 1-3
        # Heading 1
        ## Heading 2...

    In addition: Explicit page break can be set using
        <!--pagebreak-->

'''
@app.get("/slides/{fName:path}", response_class=HTMLResponse)
async def serve_slides(fName:str ="doc1" ):

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





@app.get("/", response_class=HTMLResponse)
async def readRoot(request: Request):
  return templates.TemplateResponse(
        "tmp-main-fa.html", 
        {
            "request": request, 
            "HTMLTitle": "HTMLTitle ",
            "cntBefore": "<p> before  </p> ",
            "cntAfter":  "<p> after   </p>",
        },
    )



@app.get("/generate-stream-example")
async def generate_stream_example():
    async def generator():
        yield "Starting stream...\n"
        for i in range(20):
            yield f"chunk {i}\n"
            await asyncio.sleep(0.5)
        yield "Stream complete!"
    return StreamingResponse(generator(), media_type="text/plain")






@app.post("/upload-file")
async def upload_file(files: List[UploadFile] = File(...)):

    UPLOAD_FOLDER = "uploaded-files"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    responses = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        responses.append(f"{file.filename} uploaded successfully!")

    return {"messages": responses}








if __name__ == "__main__":
    # command line:
    #       uvicorn app-fa:app --reload
    #       uvicorn app-fa:app --reload   --port 8200
    if True:
        import uvicorn
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8200,
            # workers=1, 
            # reload=True,
        )