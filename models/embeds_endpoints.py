from sqlalchemy.orm import Session
from models.db5 import get_db

from models.db1_embeds import Embedding, embeddingsTop3, embeddingsWhereHash




# in ..[app].py
#    app.include_router(db.router)
from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.responses   import Response, HTMLResponse, JSONResponse

router = APIRouter()




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







import routes.embeddings_basics     as embeddings_basics
import routes.embeddings_similarity as embeddings_similarity

from models.jinja import templates


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



import models.contexts     as contexts
import models.benchmarks   as benchmarks
import models.samples      as samples


@router.get('/embeddings/similarity')
async def embeddingsSimilarityH(request: Request, db: Session = Depends(get_db)):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    ctxUI,  ctxs     = await contexts.PartialUI(request)
    bmrkUI, bmSel    = await benchmarks.PartialUI(request, showSelected=False)
    smplUI, smplSel  = await samples.PartialUI(request, showSelected=False)

    print(f"{ctxs=}" )
    print(f"{bmSel=}" )
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
            "smplUI":      smplUI,
            "cnt1":        benchmarks.toHTML(bmSel),
            "cnt2":        samples.toHTML(smplSel),
            "cntTable":    sTable,
        },
    )

