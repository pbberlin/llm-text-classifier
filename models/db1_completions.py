from datetime import datetime as datetimeFunc


from sqlalchemy     import Column, Integer, String, Text, DateTime, func, desc, Index

from sqlalchemy.orm import Session

from sqlalchemy.dialects.sqlite import JSON



from models.db0_base import Base

from sqlalchemy.exc import IntegrityError


from dataclasses      import dataclass, asdict
from dataclasses_json import dataclass_json
from dataclasses_json import Undefined


# dataclass with SQLAlchemy table mapping and enhanced JSON support
# similar to above - but we get better
# https://pypi.org/project/dataclasses-json/
@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Completion(Base):
    __tablename__ = 'completions'

    id:         int        = Column(Integer,  primary_key=True, autoincrement=True)
    datetime:   datetimeFunc = Column(DateTime, default=datetimeFunc.utcnow)
    dataset:    str        = Column(String,   nullable=False, default="")
    hash:       str        = Column(String,   unique=False, nullable=False, index=True)
    ident:      str        = Column(Text,     nullable=False)
    prompt:     str        = Column(Text,     nullable=False)
    # result:     dict       = Column(JSON)   # SQLite > 3.9.
    result:     str        = Column(Text,     nullable=False)
    error:      str        = Column(Text,     nullable=True)
    modelmajor: str        = Column(String, nullable=False)
    modelminor: str        = Column(String, nullable=False)

    __table_args__ = (Index('unique_set_model_hash', "hash", "dataset", "modelmajor", unique=True), )

    def __repr__(self):
        return f"<Completion {self.id} - {self.hash}>"


    def __repr__(self):
        return f"<Completion {self.id} - {self.hash}>"

    # explicit
    def asDictInner0(self):
        return {
            "id":         self.id,
            "dataset":    self.dataset,
            "hash":       self.hash,
            # ...
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

    # json SCHEMA - to generate edit forms - input for JSONForms
    def schema(self):
        return self.json_schema()




    def createNoValidation(self):
        newCompletion = Completion.from_json( '{id:2, dataset: "ds"}' )
    def createWithValidation(self):
        newCompletion = Completion.schema().loads( '{id:2, dataset: "ds"}' )



#### utility funcs





def completionsCount(db: Session) -> int:
    count = db.query(func.count(Completion.id)).scalar()
    return count


def completionsAll(db: Session) -> list[Completion]:
    completes = db.query(Completion).all()
    print(f"\tfound {len(completes)} completions total in the DB")
    return completes
    ret = []
    for e in completes:
        ret.append( e.to_json() )
    return ret


def completionsTop3(db: Session) -> list[Completion]:
    completes = db.query(Completion).order_by(desc(Completion.datetime)).limit(3).all()
    print(f"\tfound {len(completes)} top3 completions")
    return completes



def completionsWhereDataset(db: Session, dataset: str = "") -> list[Completion]:
    datasets = [dataset, ""]  # include legacy records
    completes = db.query(Completion).filter(Completion.dataset.in_(datasets)).all()
    print(f"\tfound {len(completes)} completions for dataset '{dataset}' ")
    return completes


def completionsWhereHash(db: Session, hashes: list[str], ) -> list[Completion]:
    completes = db.query(Completion).filter(Completion.hash.in_(hashes)).all()
    print(f"\tfound {len(completes)} out of {len(hashes)} completions for hashes '{hashes[:2]}' ")
    return completes




# we dont save the role yet
def saveCompletionDB(
    db:      Session,
    hsh     :str,
    ident   :str,
    prompt  :str,
    result  :str,
    model   :str,
):

    dataset = cfg.get("dataset")
    recsUpsert = []

    for idx in range(1):
        rec = Completion(
            dataset=dataset,
            hash=hsh,
            ident=ident,
            prompt=prompt,
            result=result,
            modelmajor=model,
            modelminor="v1",
        )
        recsUpsert.append(rec)
    try:
        db.bulk_save_objects(recsUpsert)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        print(f"\terror upserting completions into database")
        print(f"\t{exc}")
        # raise Exception(f"error upserting completions into database\n{exc}")


# Depend is only possible for endpoints
#  "standalone code requires... see usage of dummyRecordCompletion in main module "
from    lib.util import strHash
import  lib.config          as cfg
# def dummyRecordCompletion(idx: int, db: Session = Depends(get_db)):
def dummyRecordCompletion(db: Session, idx: int):
    prompt = f"For the {idx}th time. How strong is inflation? - Asked at {datetimeFunc.now()}."
    strJson = {"prompt": "Alice", "response": 30}
    strJson = f"My respone is {datetimeFunc.now()}"
    e = Completion(
        # dataset   =cfg.get("dataset"),
        dataset   ="ds-dummy",
        prompt    =prompt,
        hash      =strHash(prompt) ,
        ident     ="GPT-4o-2200tokens",
        result    =strJson,
        modelmajor="GPT-4o",
        modelminor="-2024-08-06",
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e.to_json()

