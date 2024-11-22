'''
we have several options

Pydantic vs Dataclasses
https://medium.com/@danielwume/exploring-pydantic-and-dataclasses-in-python-a-comprehensive-comparison-c3269eb606af
=> Pydantic is slightly better

Pydantic models vs. sqlalchemy models:
We would need *both*. And we would need a mapper back and forth for each entity.
And the mapping is not even trivial. Especially for composite objects.
And the Pydantic classes need to be two-pronged -  Embeddings(EmbeddingsBase),
  where the outer class contains the database cols (id, lastchanged..)
  and the inner contains the idiosyncratic entity fields.
  We would have four classes for each entity to content with.
  There is some mapper lib "SQLObjects" - but this does not reduce complexity.
  Even if we would go with pydantic classes close to FastAPI endpoints,
  there is a lot of syntactic complexity and logic even for minimal REST stuff.
  Pydantic only offer some comfort in validation. We reject Pydantic.

Use sqlalchemy models only.
No support for JSON serializaton. No support for validation.

=> Decision: use dataclasses and  [dataclasses-json](https://pypi.org/project/dataclasses-json/)


'''

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.inspection import inspect


from datetime import datetime as datetimeFunc

import  lib.config          as cfg

# database setup

# aiosqlite caused trouble
DATABASE_URL = "sqlite+aiosqlite:..."

DATABASE_URL = "sqlite:///./data/db-fastapi.db"

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    # echo=True,
    connect_args={"check_same_thread": False},
)
print(f"\tdb engine created")
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    # class_=AsyncSession,
    # expire_on_commit=False,
)
print(f"\tdb session local created")



if False:
    # pure sqlalchemy data class
    class Embedding(Base):
        __tablename__ = 'embeddings'

        id:         int        = Column(Integer,  primary_key=True, autoincrement=True)
        datetime:   datetimeFunc = Column(DateTime, default=datetimeFunc.utcnow)
        dataset:    str        = Column(String,   nullable=False, default="")
        hash:       str        = Column(String,   unique=True, nullable=False, index=True)
        text:       str        = Column(Text,     nullable=False)
        embeddings: dict       = Column(JSON)   # SQLite > 3.9.
        modelmajor: str        = Column(String, nullable=False)
        modelminor: str        = Column(String, nullable=False)
        # role       = db.Column(db.String,    nullable=False, default="")

        def __repr__(self):
            return f"<Embedding {self.id} - {self.hash}>"

        # explicit
        def asDictInner0(self):
            return {
                "id":         self.id,
                "dataset":    self.dataset,
                "hash":       self.hash,
                "text":       self.text,
                "embeddings": self.embeddings,  # this will be expensive
                "modelmajor": self.modelmajor,
                "modelminor": self.modelminor,
            }

    # generic serialization
        def asDictInner1(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}



from dataclasses      import dataclass, asdict
from dataclasses_json import dataclass_json
from dataclasses_json import Undefined


# dataclass with SQLAlchemy table mapping and enhanced JSON support
# similar to above - but we get better 
# https://pypi.org/project/dataclasses-json/
@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Embedding(Base):
    __tablename__ = 'embeddings'

    id:         int        = Column(Integer,  primary_key=True, autoincrement=True)
    datetime:   datetimeFunc = Column(DateTime, default=datetimeFunc.utcnow)
    dataset:    str        = Column(String,   nullable=False, default="")
    hash:       str        = Column(String,   unique=True, nullable=False, index=True)
    text:       str        = Column(Text,     nullable=False)
    embeddings: dict       = Column(JSON)   # SQLite > 3.9.
    modelmajor: str        = Column(String, nullable=False)
    modelminor: str        = Column(String, nullable=False)
    # role       = db.Column(db.String,    nullable=False, default="")

    def __repr__(self):
        return f"<Embedding {self.id} - {self.hash}>"

    # explicit
    def asDictInner0(self):
        return {
            "id":         self.id,
            "dataset":    self.dataset,
            "hash":       self.hash,
            "text":       self.text,
            "embeddings": self.embeddings,  # this will be expensive
            "modelmajor": self.modelmajor,
            "modelminor": self.modelminor,
        }

   # serialization generic 
    def asDictInner1(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

   # serialization using dataclasses.asdict
    def asDictInner2(self):
        return asdict(self)

   # serialization using dataclass_json.to_dict
    def asDictInner3(self):
        return self.to_dict()

   # serialization using dataclass_json.to_json
    def asDictInner4(self):
        return self.to_json()



    def createNoValidation(self):
        newEmbedding = Embedding.from_json( '{id:2, dataset: "ds"}' )
    def createWithValidation(self):
        newEmbedding = Embedding.schema().loads( '{id:2, dataset: "ds"}' )



if False:
    # moved into init_db()
    Base.metadata.create_all(bind=engine)
    print(f"\tdb create all stop")


# funcs to integrate db management with fastapi
#   @asynccontextmanager
#   async def lifespan(app: FastAPI):
#       ...
async def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"\tdb create all stop")


async def dispose_db():
    engine.dispose()


# get a DB session for endpoints
# 
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



from fastapi import HTTPException, Depends

# create all - if one does not exist
def ifNotExistTable(tableName, db: Session = Depends(get_db)):
    inspector = inspect(engine)
    # if Embedding.__tablename__ not in inspector.get_table_names():
    if tableName not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
        return {"message": f"Tables '{inspector.get_table_names()}' created"}
    return {"message": f"table '{tableName}' already exists"}



## -----------------------------------
# end of general db stuff






def embeddingsCount(db: Session = Depends(get_db)):
    count = db.query(func.count(Embedding.id)).scalar()
    return count

def embeddingsAll(db: Session = Depends(get_db)):
    embeds = db.query(Embedding).all()
    ret = []
    for e in embeds:
        ret.append( e.to_json() )
    print(f"\tfound {len(embeds)} embeddings total in the DB")
    return ret


def embeddingsWhereDataset(dataset: str = "", db: Session = Depends(get_db)):
    datasets = [dataset, ""]  # include legacy records
    embeds = db.query(Embedding).filter(Embedding.dataset.in_(datasets)).all()
    ret = []
    for e in embeds:
        ret.append( e.to_json() )
    print(f"\tfound {len(embeds)} embeddings for dataset '{dataset}' ")
    return ret


def embeddingsWhereHash(hashes: list[str], db: Session = Depends(get_db)):
    embeds = db.query(Embedding).filter(Embedding.hash.in_(hashes)).all()
    ret = []
    for e in embeds:
        ret.append( e.to_json() )
    print(f"\tfound {len(embeds)} embeddings for hashes '{hashes}' ")
    return ret


# Depend is only for endpoints
#  "standalone code requires... see usage of dummyRecordEmbedding in main module "
from lib.util import strHash
# def dummyRecordEmbedding(idx: int, db: Session = Depends(get_db)):
def dummyRecordEmbedding(idx: int, db: Session):
    txt = f"For the {idx}th time. How strong is inflation? - Asked at {datetimeFunc.now()}."
    strJson = {"prompt": "Alice", "response": 30}
    e = Embedding(
        dataset   =cfg.get("dataset"),
        text      =txt,
        hash      =strHash(txt) ,
        embeddings=strJson,
        modelmajor="GPT-4o",
        modelminor="-2024-08-06",
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e.to_json()




# in ..[app].py
#    app.include_router(db.router)
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi.responses   import Response, HTMLResponse, JSONResponse

router = APIRouter()


# example for an endpoint using the database
@router.post("/embeddings/hashes", response_model=list[dict])
def embeddingsWhereHashH(hashes: list[str], db: Session = Depends(get_db)):
    # we dont use db here
    return embeddingsWhereHash(hashes)


