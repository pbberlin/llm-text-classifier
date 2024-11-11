

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from .embeddings_db import Embedding
# db = SQLAlchemy()
from .embeddings_db import db

from lib.util import strHash, strHashes
from lib.config import get, set






def getEmbeddingsDB(stmts):

    hashes = strHashes(stmts)

    existingEmbeds = Embedding.query.filter(Embedding.hash.in_(hashes)).all()
    existingHashes = {}
    for embd in existingEmbeds:
        existingHashes[embd.hash] = embd

    missingStmts = []
    for txt, hsh in zip(stmts, hashes):
        if hsh not in existingHashes:
            missingStmts.append(txt)


    newEmbeds = []
    if missingStmts:
        from .embeddings import embedsFromOpenAI

        openAIResults = embedsFromOpenAI(missingStmts)
        for k in openAIResults:
            txt  = k
            embd = openAIResults[k]

            newEmbedding = Embedding(
                modelmajor=get("modelNameEmbeddings"),
                modelminor="v1",
                role=get("role"),
                hash=strHash(txt),
                text=txt,
                embeddings=embd
            )
            newEmbeds.append(newEmbedding)

        try:
            db.session.bulk_save_objects(newEmbeds)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Exception("Error inserting embeds into database")


    # Combine existing and new
    allEmbeddings = {}
    for embedding in existingEmbeds + newEmbeds:
        allEmbeddings[embedding.hash] = embedding    


    results = []
    for text, hash in zip(stmts, hashes):
        embd = {
            "text":      text, 
            "embedding": allEmbeddings[hash].embeddings,
        }
        results.append(embd)

    return results



