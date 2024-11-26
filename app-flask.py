from lib.init import logTimeSince
logTimeSince(f"python script - imports start", startNew=True)


import os
from   pathlib import Path

import json

import sys

from   datetime import datetime, timedelta
import   time

from   pprint   import pprint, pformat

import re
import signal

import argparse
import markdown

from   flask import Flask, request, Response
from   flask import redirect, url_for
from   flask import session
from   flask import jsonify
from   flask import render_template
from   flask import send_from_directory
from   flask import make_response


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import inspect


from models.tmp_embeddings_db import db, Embedding, dummyRecordEmbedding, ifNotExistTable


# modules with model
import models.contexts     as contexts
import models.benchmarks   as benchmarks
import models.samples      as samples
import models.pipelines    as pipelines
import routes.embeddings_basics     as embeddings_basics
import routes.embeddings_similarity as embeddings_similarity

# modules generic logic
from lib.util import loadEnglishStopwords
from lib.util import loadDomainSpecificWords
from lib.util import cleanFileName
from lib.util import stackTrace
from lib.util import mainTemplateHeadForChunking, templateSuffix

from lib.markdown_ext import renderToRevealHTML

import  lib.config          as cfg




import models.embeds as embeds


logTimeSince(f"python script - imports stop")







def signalHandler(signal, frame):
    print(f'flask server immediate shutdown - sig {signal}')
    sys.exit(0)

# signal.signal(signal.SIGINT,  signalHandler) # CTRL+C
# signal.signal(signal.SIGTSTP, signalHandler) # CTRL+Q


# we need this two at the top
app = Flask(__name__)



# global error handler for any exception
@app.errorhandler(Exception)
def handle_error(e):
    print( stackTrace(e) )
    code = 500  # orig error code is not preserved
    return jsonify(error=str(e)), code





































def loadAll(args):

    logTimeSince(f"loading data start", startNew=True)

    if "ecb" in args and  len(args.ecb) > 0:
        default =  [1, 2, 4, 8, 500]
        numStcs = default
        try:
            numStcs = json.loads(args.ecb)
            if not type(numStcs) is list:
                print(f" cannot parse into a list: '{args.ecb}'")
                numStcs = default
        except Exception as exc:
            numStcs = default
            print(f" {exc} - \n\t cannot parse {args.ecb}")
            print(f" assuming default {numStcs} \n")


        # smplsNew = ecbSpeechesCSV2Json(earlyBreakAt=10, filterBy="Asset purchase")
        smplsNew = ecbSpeechesCSV2Json(numStcs, earlyBreakAt=3, filterBy="Asset purchase" )
        samples.update(smplsNew)
        samples.save()
        quit()

    if "upl" in args and args.upl:
        smplsNew = uploadedToSamples()
        samples.update(smplsNew)
        samples.save()
        quit()


    loadEnglishStopwords()
    loadDomainSpecificWords()

    embeds.load()
    contexts.load()
    benchmarks.load()
    samples.load()
    pipelines.load()

    logTimeSince(f"loading data stop")







def saveAll(force=False):

    logTimeSince(f"saving  data start", startNew=True)

    if force:
        embeds.cacheDirty = True
        contexts.cacheDirty = True
        benchmarks.cacheDirty = True
        samples.cacheDirty = True


    embeds.save()
    contexts.save()
    benchmarks.save()
    samples.save()
    pipelines.save()

    logTimeSince(f"saving  data stop")








# https://dev.to/fullstackstorm/working-with-sessions-in-flask-a-comprehensive-guide-525k
def createAndRun(app2):

    parser = argparse.ArgumentParser("LLM classifier args")
    parser.add_argument(
        "-cntr", "--counter",
        help="help for command line arg",
        default=0      , type=int,
    )
    parser.add_argument(
        "-ecb" , "--ecb",
        help="import ECB - num sentences - [1, 2, 4, 500]",
        default=""    , type=str,
    )
    parser.add_argument(
        "-upl" , "--upl",
        help="import uploaded files",
        default=False  , type=bool,
    )

    args = parser.parse_args()

    dummy = args.counter + 1

    # app must be created at the start of the file
    # before any routes are registered
    # app2 = Flask(__name__)

    app2.secret_key = b'32168'
    app2.permanent_session_lifetime = timedelta(minutes=30)
    app2.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=230)
    app2.static_folder='static'  # only source for static files in templates?
    app2.instance_path='data'    # default is "instance" - sqlite file go here
    app2.debug=True

    cfg.load(app2)


    UPLOAD_FOLDER = os.path.join(app2.root_path, 'uploaded-files')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(  os.path.join(app2.root_path, "data"), exist_ok=True )
    os.makedirs(  os.path.join(app2.root_path, "data",   "set1" ), exist_ok=True )
    os.makedirs(  os.path.join(app2.root_path, "static" ), exist_ok=True )
    os.makedirs(  os.path.join(app2.root_path, "static", "img"), exist_ok=True )
    os.makedirs(  os.path.join(app2.root_path, "static", "img", "dynamic"), exist_ok=True )

    app2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///embeddings-mostly.db'
    app2.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app2)

    with app2.app_context():
        # db.create_all()
        ifNotExistTable('embeddings')

    # insert dummy records
    with app2.app_context():
        for idx in [1,2,3]:
            pass
            # db.session.add( dummyRecordEmbedding(idx) )
        db.session.commit()


    with app2.app_context():
        loadAll(args)

    app2.run(
        host='0.0.0.0',
        debug=True,
        port=8001,
        use_reloader=False,
    )

    cfg.save()

    with app2.app_context():
        saveAll()

    return app2



UPLOAD_FOLDER = ""

if __name__ == '__main__':
    app = createAndRun(app)


