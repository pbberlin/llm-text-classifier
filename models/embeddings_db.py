from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.sqlite import JSON

from sqlalchemy import select, func

import json
from   datetime import datetime

import  lib.config          as cfg


db = SQLAlchemy()

# models
class Embedding(db.Model):
    __tablename__ = 'embeddings'
    id         = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    datetime   = db.Column(db.DateTime, default=datetime.utcnow)
    dataset    = db.Column(db.String,   nullable=False, default="")
    hash       = db.Column(db.String,   unique=True, nullable=False, index=True)
    text       = db.Column(db.Text,     nullable=False)
    embeddings = db.Column(JSON)  # SQLite > 3.9.

    modelmajor = db.Column(db.String,    nullable=False)
    modelminor = db.Column(db.String,    nullable=False)
    # role       = db.Column(db.String,    nullable=False, default="")

    def __repr__(self):
        return f"<Embedding {self.id} - {self.hash}>"


# following funcs
# must be called inside app context; either @app.route or
#     with app.app_context():
#       funcBelow()
def embeddingsCount(tableName="embeddings"):
    if False:
        stmt = select(func.count()).select_from(Embedding)
        result = db.session.execute(stmt).scalar_one()
    result = Embedding.query.count()
    return result

def embeddingsAll(tableName="embeddings"):
    if False:
        embdsAsList = Embedding.query.filter(Embedding.hash.in_(["hash01", "hash02"])).all()
    embdsAsList = Embedding.query.all()
    print(f"\tfound {len(embdsAsList)} embeddings total in the DB")
    return embdsAsList


def embeddingsWhereDataset(   tableName="embeddings"):
    ds = cfg.get("dataset")
    datasets = [ds, ""] # legcacy - dataset == ""
    embdsAsList = Embedding.query.filter(Embedding.dataset.in_(datasets)).all()
    print(f"\tfound {len(embdsAsList)} embeddings for dataset '{ds}' ")
    return embdsAsList


# stmtsHshs is a list of hashes
def embeddingsWhereHash( stmtsHshs,  tableName="embeddings"):
    embdsAsList = Embedding.query.filter(Embedding.hash.in_(stmtsHshs)).all()
    print(f"\tfound {len(embdsAsList)} embeddings for given {len(stmtsHshs)} hashes")
    return embdsAsList

    if False:
        embdsByStmt = {}
        for embd in embdsAsList:
            embdsByStmt[embd.text] = embd.embeddings
        embdsByHash = {}
        for embd in embdsAsList:
            embdsByHash[embd.hash] = embd.embeddings


def ifNotExistTable(tableName):
    inspector = inspect(db.engine)
    if tableName not in inspector.get_table_names():
        print(f"    table '{tableName}' does not exist. Creating tables...")
        db.create_all()
    else:
        pass
        # print(f"    table '{tableName}' already exists. Skipping creation.")


def dummyRecordEmbedding(idx):

    from lib.util import strHash

    tNow = datetime.now()
    myText = f"For the {idx+0}th time. How strong is inflation? - \nAsked at {tNow}."

    strJson = '''{  "prompt": "Alice", "response": 30 }'''
    oJson = json.loads(strJson)

    embd0 = Embedding(
        dataset =  cfg.get("dataset"),
        text = myText,
        hash = strHash(myText),
        embeddings = oJson,
        modelmajor = "GPT-4o",
        modelminor = "-2024-08-06",
    )
    return embd0





