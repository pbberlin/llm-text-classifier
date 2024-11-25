from sqlalchemy.orm import Session
from models.db5 import get_db

from models.db1_embeds import Embedding, embeddingsTop3, embeddingsWhereHash




# in ..[app].py
#    app.include_router(db.router)
from fastapi import APIRouter
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


# this leads to response validation error - because of list[dict] - needs to be list[Embedding]
@router.get("/embeddings/top3/dict", response_model=list[dict])
def embeddingsTop3ObjDictH(db: Session = Depends(get_db)):
    embeds =  embeddingsTop3(db)
    return embeds

