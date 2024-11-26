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


from lib.uploaded2samples import uploadedToSamples
from lib.ecb2samples      import ecbSpeechesCSV2Json


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















@app.route('/samples-import', methods=['GET','POST'])
def samplesImportH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()

    # extract and process POST params
    importedSmpls = []
    if len(kvPst) > 0:

        if  "action" in kvPst and kvPst["action"] == "import_samples":

            modeX = "none"
            if  "import-distinct" in kvPst:       # stupid checkbox submits no value if unchecked
                modeX = kvPst["import-distinct"]
            print(f"post request => import samples, mode {modeX}")

            filterBy = kvPst["filter"]

            tmp = uploadedToSamples()
            importedSmpls.extend(tmp)

            print(f"samples imported new samples: {len(importedSmpls) } (not filterd yet) ")


    else:
        pass
        # print("post request is empty")


    existingSmpls = samples.update([])
    existingKeys = {}
    for smpl in existingSmpls:
        existingKeys[smpl["descr"]] = True


    importedDistinctAndFiltered = []
    for idx, smpl in enumerate(importedSmpls):
        if smpl["descr"] in existingKeys:
            print(f"  smpl {idx:2} already exists - {smpl['descr']}  ")
            continue
        if filterBy not in smpl["descr"]:
            print(f"  smpl {idx:2} not contains '{filterBy}' - {smpl['descr']}  ")
            continue
        importedDistinctAndFiltered.append(smpl)
    print(f"samples distinct new samples: {len(importedDistinctAndFiltered) } ")


    existingSmpls.extend(importedDistinctAndFiltered)
    effectiveSmpls = samples.update(existingSmpls)
    print(f"overall number of samples:    {len(effectiveSmpls) } ")

    # for i,v in enumerate(bmrks):
    #     print(f"   {i} - {v['descr'][0:15]} {v['statements'][0][0:15]}..." )


    importUI  = samples.PartialUI_Import(request, session)

    msg = ""
    if len(importedSmpls)>0:
        msg = f"{len(importedSmpls)} samples imported"


    return render_template(
        'main.html',
        HTMLTitle="Import samples",
        cntBefore=f'''
            {msg}
            <br>
            {importUI}
            ''',
        contentTpl="samples",
        listSamples=effectiveSmpls,
    )









@app.route('/contexts-edit', methods=['GET','POST'])
def contextsEditH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()

    # extract and process POST params
    reqCtxs = []
    if len(kvPst) > 0:
        # for i,k in enumerate(kvPost):
        #     print(f"  req key #{i:2d}  '{k}' - {openai.ell(kvPost[k][:20],x=12)}")

        for i in range(0,100):
            sh = f"ctx{i+1:d}sh"  # starts with 1
            lg = f"ctx{i+1:d}lg"
            dl = f"ctx{i+1:d}_del"
            if lg not in kvPst:
                # print(f"input '{lg}' is unknown - breaking")
                break
            if dl in kvPst and  kvPst[dl] != "":
                print(f"  input '{lg}' to be deleted")
                continue
            if kvPst[lg].strip() == "":
                print(f"  input '{lg}' is empty")
                continue
            reqCtxs.append( {  "short": kvPst[sh], "long": kvPst[lg]  } )
            print(f"  input '{lg}' - {kvPst[lg][0:15]}")
        print(f"post request contained {len(reqCtxs)} contexts")
    else:
        print("post request is empty")


    ctxs = contexts.update(reqCtxs)

    if len(ctxs)>0 and ctxs[-1]["long"].strip() != "":
        ctxs.append( contexts.dummy() )

    print(f" overall number of contexts {len(ctxs) } ")
    for i,v in enumerate(ctxs):
        print(f"   {i} - {v['short'][0:15]} {v['long'][0:15]}..." )


    return render_template(
        'main.html',
        HTMLTitle="Edit Contexts",
        cntBefore=f"{len(ctxs)} contexts found",
        contentTpl="contexts",
        listContexts=ctxs,
    )



@app.route('/benchmarks-edit', methods=['GET','POST'])
def benchmarksEditH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()
    # for k in kvPost:
    #     print(f"{k}")

    # extract and process POST params
    reqBenchmarks = []
    if len(kvPst) > 0:
        for i1 in range(0,100):
            descr = f"benchmark{i1+1:d}_descr"  # starts with 1
            delet = f"benchmark{i1+1:d}_del"

            if descr not in kvPst:
                break

            if descr in kvPst and delet in kvPst and  kvPst[delet] != "":
                print(f"  input benchmark '{descr}' to be deleted")
                continue
            if kvPst[descr].strip() == "":
                print(f"  input benchmark '{descr}' is empty")
                continue

            sts = []
            for i2 in range(0,100):
                sh = f"benchmark{i1+1:d}_st{i2+1}_shrt"
                lg = f"benchmark{i1+1:d}_st{i2+1}_long"
                if lg not in kvPst:
                    break
                if kvPst[lg].strip() == "":
                    print(f"    bm {i1+1} stmt {i2+1} is empty")
                    # continue
                else:
                    sts.append(
                        {  "short": kvPst[sh], "long": kvPst[lg]  }
                    )

            reqBenchmarks.append(
                {
                    "descr": kvPst[descr],
                    "statements": sts,
                }
            )
            print(f"  input benchmark '{descr}' - {len(sts)} stmts - {kvPst[descr]}")

        print(f"post request contained {len(reqBenchmarks)} benchmarks")
    else:
        pass
        # print("post request is empty")


    bmrks = benchmarks.update(reqBenchmarks)

    print(f"overall number of benchmarks {len(bmrks) } ")
    # for i,v in enumerate(bmrks):
    #     print(f"   {i} - {v['descr'][0:15]} {v['statements'][0][0:15]}..." )


    for bm in bmrks:
        sts = bm["statements"]
        if len(sts) == 0  or  sts[-1]["long"].strip() != "":
            nwSt = benchmarks.newSt()
            sts.append( nwSt )


    if len(bmrks)>0 and bmrks[-1]["descr"].strip() != "" :
        bmrks.append( benchmarks.dummy() )



    bmrkUI, bmSel  = benchmarks.PartialUI(request, session)

    # benchmarks.toHTML(bmSel)

    return render_template(
        'main.html',
        HTMLTitle="Edit benchmarks",
        cntBefore=f'''
            {len(bmrks)} benchmarks found
            <br>
            {bmrkUI}
            ''',
        contentTpl="benchmarks",
        listBenchmarks=bmrks,
    )






@app.route('/samples-edit', methods=['GET','POST'])
def samplesEditH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()
    # for k in kvPost:
    #     print(f"{k}")

    # extract and process POST params
    reqSamples = []
    if len(kvPst) > 0:

        for i1 in range(0,100):
            descr = f"sample{i1+1:d}_descr"  # starts with 1
            delet = f"sample{i1+1:d}_del"

            if descr not in kvPst:
                break

            if descr in kvPst and delet in kvPst and  kvPst[delet] != "":
                print(f"  input sample '{descr}' to be deleted")
                continue
            if kvPst[descr].strip() == "":
                print(f"  input sample '{descr}' is empty")
                continue

            sts = []
            for i2 in range(0,100):
                sh = f"sample{i1+1:d}_st{i2+1}_shrt"
                lg = f"sample{i1+1:d}_st{i2+1}_long"
                if lg not in kvPst:
                    break
                if kvPst[lg].strip() == "":
                    print(f"    bm {i1+1} stmt {i2+1} is empty")
                    # continue
                else:
                    sts.append(
                        {  "short": kvPst[sh], "long": kvPst[lg]  }
                    )

            reqSamples.append(
                {
                    "descr": kvPst[descr],
                    "statements": sts,
                }
            )
            print(f"  input sample '{descr}' - {len(sts)} stmts - {kvPst[descr]}")

        print(f"post request contained {len(reqSamples)} samples")


    else:
        pass
        # print("post request is empty")


    newSmpls = samples.update(reqSamples)

    print(f"overall number of samples {len(newSmpls) } ")
    # for i,v in enumerate(bmrks):
    #     print(f"   {i} - {v['descr'][0:15]} {v['statements'][0][0:15]}..." )


    for smpl in newSmpls:
        sts = smpl["statements"]
        if len(sts) == 0  or  sts[-1]["long"].strip() != "":
            nwSt = samples.newSt()
            sts.append( nwSt )


    if len(newSmpls)>0 and newSmpls[-1]["descr"].strip() != "" :
        newSmpls.append( samples.dummy() )



    smplUI, bmSel  = samples.PartialUI(request, session)

    # samples.toHTML(bmSel)

    return render_template(
        'main.html',
        HTMLTitle="Edit samples",
        cntBefore=f'''
            {len(newSmpls)} samples found
            <br>
            {smplUI}
            ''',
        contentTpl="samples",
        listSamples=newSmpls,
    )



@app.route('/templates-edit', methods=['GET','POST'])
def templatesEditH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()

    # extract and process POST params
    reqTemplates = []
    if len(kvPst) > 0:

        for i1 in range(0,100):
            descK = f"template{i1+1:d}_descr"  # starts with 1
            roleK = f"template{i1+1:d}_role" 
            deleK = f"template{i1+1:d}_del"

            if descK not in kvPst:
                break

            if descK in kvPst and deleK in kvPst and  kvPst[deleK] != "":
                print(f"  input template '{descK}' to be deleted")
                continue
            if kvPst[descK].strip() == "":
                print(f"  input template '{descK}' is empty")
                continue

            stages = []
            for i2 in range(0,100):
                sh = f"stage{i1+1:d}_st{i2+1}_shrt"
                lg = f"stage{i1+1:d}_st{i2+1}_long"
                rm = f"stage{i1+1:d}_st{i2+1}_rem"
                if lg not in kvPst:
                    break
                if kvPst[lg].strip() == "":
                    print(f"    bm {i1+1} stage {i2+1} is empty")
                else:
                    stages.append(
                        {  
                            "short": kvPst[sh], 
                            "long":  kvPst[lg],
                            "remark":  kvPst[rm],
                        }
                    )

            reqTemplates.append(
                {
                    "descr":  kvPst[descK],
                    "role":   kvPst[roleK],
                    "stages": stages,
                }
            )
            print(f"  input template '{descK}' - {len(stages)} stages - {kvPst[descK]}")

        print(f"post request contained {len(reqTemplates)} templates")


    else:
        pass
        # print("post request is empty")


    newTemplates = pipelines.update(reqTemplates)

    print(f"overall number of templates {len(newTemplates) } ")


    for tpl in newTemplates:
        stages = tpl["stages"]
        if len(stages) == 0  or  stages[-1]["long"].strip() != "":
            nwSt = pipelines.newStage()
            stages.append( nwSt )


    if len(newTemplates)>0 and newTemplates[-1]["descr"].strip() != "" :
        newTemplates.append( samples.dummy() )

    tplUI, _  = pipelines.PartialUI(request, session)


    return render_template(
        'main.html',
        HTMLTitle="Edit templates",
        cntBefore=f'''
            {len(newTemplates)} templates found
            <br>
            {tplUI}
            ''',
        contentTpl="templates",
        listTemplates=newTemplates,
    )




@app.route('/embeddings-basics', methods=['GET','POST'])
def embeddingsBasicsH():
    try:

        content = embeddings_basics.model(request,session)

        return render_template(
            'main.html',
            HTMLTitle="Basic Embedding",
            cntBefore=content,
        )


    except Exception as exc:
        print( stackTrace(exc) )
        return app.response_class(response=json.dumps( str(exc) ), status=500, mimetype='application/json')





# single caveat
#   we receive a *stream* of responses from OpenAI
#   we collect all responses and render them at onece
@app.route('/chat-completion-synchroneous', methods=['GET','POST'])
def chatCompletionSynchroneousH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()

    beliefStatement =  ""
    if "belief-statement" in kvPst:
        beliefStatement =  kvPst["belief-statement"]

    speech          =  ""
    if "speech" in kvPst:
        speech =  kvPst["speech"]


    # requestChatCompletion is now a generator
    # returning various types of returns in a protracted way
    # we collect all chunks - and then render them in one go
    prompt = ""
    results = []
    idx1 = -1
    for res in embeds.generateChatCompletionChunks( beliefStatement, speech):
        idx1 += 1
        if idx1 == 0:
            prompt = res
        elif res == "end-of-func":
            pass
        else:
            results.append(res)



    return render_template(
        'main.html',
        HTMLTitle="Ask ChatGPT",
        contentTpl="llm-answer-sync",
        # cnt1=cnt1,
        # cnt2=cnt2,
        beliefStatement=beliefStatement,
        speech=speech,
        prompt=prompt,
        results=results,
    )




def generateStreamExample(modeES=False):

    pfx = ""
    if modeES:
        pfx = "data: "

    if not modeES:
        yield mainTemplateHeadForChunking("main", "streaming example")
        yield f"{pfx}<p><a href=/generate-stream-example?event-stream=1>Switch to event stream</a></p>\n" + " " * 1024

    # force early flush with padding
    yield f"{pfx}<p>Starting streaming...</p>" + " " * 1024  + "\n\n"

    # force early flush with padding
    yield f"{pfx}<div style='height: 2px; background-color: grey'> { ' ' * 1024}  &nbsp;</div>\n\n"

    # sending content chunks to client
    for i in range(12):
        print(f"\t  yielding chunk {i:2}")
        yield f"{pfx}<p>Chunk {(i + 1):2}  { ' '  * 512} &nbsp;</p>\n\n"
        time.sleep(0.15)
        time.sleep(0.05)
    yield f"{pfx}<p>response finished</p>\n\n"

    if not modeES:
        yield templateSuffix()



@app.route('/generate-stream-example', methods=['GET','POST'])
def generateStreamExampleH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()
    # for k in kvPost:
    #     print(f"{k}")

    asEventStream = False
    # 'text/plain', 'text/html; charset=UTF-8'
    mType = 'text/html'

    if ("event-stream" in kvGet) or ("event-stream" in kvPst):
        asEventStream = True
        mType = 'text/event-stream'


    # content_type=mType if '...charset=UTF-8'
    rsp = Response( generateStreamExample(modeES=asEventStream), mimetype=mType)
    # if True:
    if False:
        # No need for 'Transfer-Encoding: chunked'; Flask handles it for you
        rsp.headers['Transfer-Encoding'] = 'chunked'
        rsp.status_code = 200  # Explicitly set status code (optional)
    return rsp





# returns JSON
@app.route('/chat-completion-json', methods=['GET','POST','OPTIONS'])
def chatCompletionJsonH():

    if request.method == "OPTIONS": # CORS preflight
        return addPreflightCORS()

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()

    role   =  ""
    model  =  ""
    prompt =  ""

    try:
        kvPst = request.json()

        if "role" in kvPst:
            role   =  kvPst["role"]

        if "prompt" in kvPst:
            prompt =  kvPst["prompt"]


    except Exception as exc:

        print(f"request body was not JSON - probably POST")

        if "model" in kvPst:
            model =  kvPst["model"].strip()

        beliefStatement  =  ""
        if "belief-statement" in kvPst:
            beliefStatement =  kvPst["belief-statement"]

        speech           =  ""
        if "speech" in kvPst:
            speech =  kvPst["speech"]

        prompt, _, _ = embeds.designPrompt(beliefStatement, speech)


    if model == "":
        models = cfg.get("modelNamesChatCompletion")
        model =  models[0]



    # if len(prompt) < 5:
    #     print(f"  too short")
    #     return app.response_class(
    #         response=f"{{ error: too short {prompt} }}   ",
    #         mimetype='application/json',
    #         status=500,
    #     )

    try:

        result = embeds.chatCompletion(model, prompt, role)
        resp = Response(
            json.dumps(result, indent=4),
            mimetype='application/json',
        )
        return addActualCORS(resp)


    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(
            response=f"{{ error: {str(exc)} }}   ",
            mimetype='application/json',
            status=500,
        )


# returns HTML - first part of the page
#   makes JS requests
#   renders JSON responses
@app.route('/chat-completion-js', methods=['GET','POST'])
def chatCompletionJSH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()

    beliefStatement =  ""
    if "belief-statement" in kvPst:
        beliefStatement =  kvPst["belief-statement"]

    speech          =  ""
    if "speech" in kvPst:
        speech =  kvPst["speech"]


    prompt, role , err = embeds.designPrompt(beliefStatement, speech)
    if err != "":
        prompt = f"Error designing prompt: {err}"

    return render_template(
        'main.html',
        HTMLTitle="chat completion",
        contentTpl="llm-answer-js",
        # cnt1=cnt1,
        # cnt2=cnt2,
        beliefStatement=beliefStatement,
        speech=speech,
        prompt=prompt,
        role=role,
    )






@app.route('/embeddings-similarity', methods=['GET','POST'])
def embeddingsSimilarityH():

    # GET + POST params
    kvGet = request.args.to_dict()
    kvPst = request.form.to_dict()

    ctxUI, ctxs  = contexts.PartialUI(request, session)

    bmrkUI, bmSel  = benchmarks.PartialUI(request, session, showSelected=False)

    smplUI, smplSel  = samples.PartialUI(request, session, showSelected=False)


    sTable = embeddings_similarity.model(ctxs, bmSel, smplSel )

    return render_template(
        'main.html',
        HTMLTitle="Embeddings - Similarity",
        contentTpl="embeddings-similarity",
        ctxUI=ctxUI,
        bmrkUI=bmrkUI,
        smplUI=smplUI,
        cnt1=benchmarks.toHTML(bmSel),
        cnt2=samples.toHTML(smplSel),
        cntTable=sTable,
    )


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


