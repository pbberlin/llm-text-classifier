# in ..[app].py
#    app.include_router(db.router)
from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.responses   import Response, HTMLResponse, JSONResponse

from sqlalchemy.orm import Session


router = APIRouter()


from models.jinja import templates
from models.db1_embeds import Embedding, embeddingsTop3, embeddingsWhereHash
from models.db5 import get_db


import models.contexts     as contexts
import models.benchmarks   as benchmarks
import models.samples      as samples
import models.pipelines    as pipelines


import routes.embeddings_basics     as embeddings_basics
import routes.embeddings_similarity as embeddings_similarity



# endpoints using database

@router.post("/embeddings/hashes", response_model=list[Embedding])
def embeddingsWhereHashH(hashes: list[str], db: Session = Depends(get_db)):
    return embeddingsWhereHash(db,hashes)


@router.get("/embeddings/top3/json", response_class=JSONResponse)
def embeddingsTop3H(db: Session = Depends(get_db)):
    embeds =  embeddingsTop3(db)
    ret = []
    for e in embeds:
        ret.append( e.to_json() )
    return ret
    # raise HTTPException(status_code=404, detail="xxx")


@router.get("/embeddings/top3/obj", response_model=list[Embedding])
def embeddingsTop3ObjH(db: Session = Depends(get_db)):
    embeds =  embeddingsTop3(db)
    return embeds


# list[dict] - needs to be list[Embedding]
#  => response validation error - 
@router.get("/embeddings/top3/dict", response_model=list[dict])
def embeddingsTop3ObjDictH(db: Session = Depends(get_db)):
    embeds =  embeddingsTop3(db)
    return embeds








async def embeddingsBasicsH(request: Request, db: Session = Depends(get_db)):

    content = await embeddings_basics.model(db, request)

    return templates.TemplateResponse(
        "main.html",
        {
            "request":    request,
            "HTMLTitle":  "Basic Embedding",
            "cntBefore":  content,
        },
    )


@router.get('/embeddings/basics')
async def embeddingsBasicsHGet(request: Request, db: Session = Depends(get_db)):
    return await embeddingsBasicsH(request, db)


@router.post('/embeddings/basics')
async def embeddingsBasicsHPost(request: Request, db: Session = Depends(get_db)):
    return await embeddingsBasicsH(request, db)





async def embeddingsSimilarityH(request: Request, db: Session = Depends(get_db)):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    ctxUI,  ctxs     = await contexts.PartialUI(request)
    bmrkUI, bmSel    = await benchmarks.PartialUI(request, showSelected=False)
    smplUI, smplSel  = await samples.PartialUI(request, showSelected=False)
    pipeUI, pipeSel  = await pipelines.PartialUI(request, showSelected=False)

    # print(f"{ctxs=}" )
    # print(f"{bmSel=}" )
    # print(f"{smplSel=}" )

    sTable = embeddings_similarity.model(request, db, ctxs, bmSel, smplSel)


    return templates.TemplateResponse(
        "main.html",
        {
            "request":     request,
            "HTMLTitle":   "Embeddings - Similarity",
            "contentTpl":  "embeddings-similarity",
            "ctxUI":       ctxUI,
            
            "bmrkUI":      bmrkUI,
            "bmSel":       benchmarks.toHTML(bmSel),

            "smplUI":      smplUI,
            "smplSel":     samples.toHTML(smplSel),

            "pipeUI":      pipeUI,
            "pipeSel":     pipelines.toHTML(pipeSel),
            
            "cntTable":    sTable,
        },
    )



@router.get('/embeddings/similarity')
async def embeddingsSimilarityHGet(request: Request, db: Session = Depends(get_db)):
    return await embeddingsSimilarityH(request, db)


@router.post('/embeddings/similarity')
async def embeddingsSimilarityHPost(request: Request, db: Session = Depends(get_db)):
    return await embeddingsSimilarityH(request, db)
