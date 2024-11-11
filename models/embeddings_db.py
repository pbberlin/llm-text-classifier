from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.sqlite import JSON

import  lib.config          as config


db = SQLAlchemy()

class Embedding(db.Model):
    __tablename__ = 'embeddings'
    id         = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    datetime   = db.Column(db.DateTime, default=datetime.utcnow)
    hash       = db.Column(db.String,   unique=True, nullable=False, index=True)
    text       = db.Column(db.Text,     nullable=False)
    embeddings = db.Column(JSON)  # SQLite > 3.9.

    modelmajor = db.Column(db.String,    nullable=False)
    modelminor = db.Column(db.String,    nullable=False)
    # promptversion = db.Column(db.String, nullable=False, default="1.0")
    # role       = db.Column(db.String,    nullable=False, default="")

    def __repr__(self):
        return f"<Embedding {self.id} - {self.hash}>"



def ifNotExistTable(tableName):
    inspector = inspect(db.engine)
    if tableName not in inspector.get_table_names():
        print(f"Table '{tableName}' does not exist. Creating tables...")
        db.create_all()
    else:
        print(f"Table '{tableName}' already exists. Skipping creation.")


def dummyRecordEmbedding(idx):

    from lib.util import strHash

    tNow = datetime.now()
    myText = f"For the {idx+0}th time. How strong is inflation? - \nAsked at {tNow}."

    strJson = '''{  "prompt": "Alice", "response": 30 }'''
    oJson = json.loads(strJson)

    embd0 = Embedding(
        modelmajor = "GPT-4o",
        modelminor = "-2024-08-06",
        role =  config.get("role"),
        text = myText,
        hash = strHash(myText),
        embeddings = oJson,
    )
    return embd0





