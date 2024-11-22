from sqlalchemy import Column, Integer, String, Text, DateTime, func, desc

from sqlalchemy.orm import Session

from sqlalchemy.dialects.sqlite import JSON


from datetime import datetime as datetimeFunc

from models.db0_base import Base


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



#### utility funcs





def embeddingsCount(db: Session) -> int:
    count = db.query(func.count(Embedding.id)).scalar()
    return count


def embeddingsAll(db: Session) -> list[Embedding]:
    embeds = db.query(Embedding).all()
    print(f"\tfound {len(embeds)} embeddings total in the DB")
    return embeds
    ret = []
    for e in embeds:
        ret.append( e.to_json() )
    return ret


def embeddingsTop3(db: Session) -> list[Embedding]:
    embeds = db.query(Embedding).order_by(desc(Embedding.datetime)).limit(3).all()
    print(f"\tfound {len(embeds)} top3 embeddings")
    return embeds



def embeddingsWhereDataset(db: Session, dataset: str = "") -> list[Embedding]:
    datasets = [dataset, ""]  # include legacy records
    embeds = db.query(Embedding).filter(Embedding.dataset.in_(datasets)).all()
    print(f"\tfound {len(embeds)} embeddings for dataset '{dataset}' ")
    return embeds


def embeddingsWhereHash(db: Session, hashes: list[str], ) -> list[Embedding]:
    embeds = db.query(Embedding).filter(Embedding.hash.in_(hashes)).all()
    print(f"\tfound {len(embeds)} embeddings for hashes '{hashes}' ")
    return embeds




# Depend is only possible for endpoints
#  "standalone code requires... see usage of dummyRecordEmbedding in main module "
from    lib.util import strHash
import  lib.config          as cfg
# def dummyRecordEmbedding(idx: int, db: Session = Depends(get_db)):
def dummyRecordEmbedding(db: Session, idx: int):
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

