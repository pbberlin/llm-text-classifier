from lib.init import logTimeSince
logTimeSince(f"python script - imports start", startNew=True)


import os
from   pathlib import Path

import json
import pickle

import sys

from   datetime import datetime, timedelta

from   pprint   import pprint, pformat

import re
import signal

import argparse

import flask
from   flask import Flask, request
from   flask import redirect, url_for
from   flask import session
from   flask import jsonify
from   flask import render_template



# modules with model
import models.contexts   as contexts
import models.benchmarks as benchmarks
import models.samples    as samples
import routes.embeddings_basics as embeddings_basics
import routes.embeddings_similarity as embeddings_similarity

# modules generic logic
from lib.util import loadEnglishStopwords
from lib.util import loadDomainSpecificWords
from lib.util import cleanFileName
from lib.util import stackTrace

import  lib.config          as config


from lib.uploaded2samples import uploadedToSamples
from lib.ecb2samples      import ecbSpeechesCSV2Json


import models.embeddings as embeddings


logTimeSince(f"python script - imports stop")


# https://dev.to/fullstackstorm/working-with-sessions-in-flask-a-comprehensive-guide-525k
app = Flask(__name__)
app.secret_key = b'32168'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=230)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploaded-files')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(  os.path.join(app.root_path, "data"), exist_ok=True )
os.makedirs(  os.path.join(app.root_path, "static" ), exist_ok=True )
os.makedirs(  os.path.join(app.root_path, "static", "img"), exist_ok=True )
os.makedirs(  os.path.join(app.root_path, "static", "img", "dynamic"), exist_ok=True )



def signalHandler(signal, frame):
    print(f'flask server immediate shutdown - sig {signal}')
    sys.exit(0)

# signal.signal(signal.SIGINT,  signalHandler) # CTRL+C
# signal.signal(signal.SIGTSTP, signalHandler) # CTRL+Q

# global error handler for any exception
@app.errorhandler(Exception)
def handle_error(e):
    print( stackTrace(e) )
    code = 500  # orig error code is not preserved
    return jsonify(error=str(e)), code


# hone
@app.route('/')
def indexH():

    session.permanent = True

    apiKey = None
    if 'api_key' in session:
        apiKey = session['api_key']
    else:
        apiKey = config.get('OpenAIKey')

    referrer = request.referrer
    # print(f"referrer {referrer}")
    successMsg = ""
    if referrer is None:
        apiKeyValid, successMsg, invalidMsg = embeddings.checkAPIKeyOuter(apiKey)
        if not apiKeyValid:
            return redirect( url_for("configH") )


    try:
        return render_template(
            'main.html',
            HTMLTitle="Main page",
            contentTpl="main-body",
            cntBefore=f"<p>{successMsg}</p>",
        )

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')



@app.route('/upload-file',methods=['post','get'])
def uploadFileH():

    content = ""
    content += "<br>\n"


    if 'uploaded-files' in request.files:

        fs = request.files.getlist('uploaded-files')
        if (not fs) or len(fs) < 1:
            content += "No file contents in multiple input  <br>\n"
        else:
            # content += f"{len(fs)} multi file(s)<br>\n"
            for idx, f in enumerate(fs):
                if f and f.filename:
                    content += f"Processing multiple file {idx+1}. -{pformat(f)}- <br>\n"
                    fn = cleanFileName(f.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, fn)

                    # print(f" fn {f.filename} ")
                    # print(f" fn {fn} ")
                    # print(f" fp {filepath} ")

                    checkExisting = Path(filepath)
                    if checkExisting.is_file():
                        content += f" &nbsp; {idx+1:3} - '{f.filename}' ('{fn}') already exists. Will overwrite. <br>\n"

                    f.save(filepath)
                    content += f" &nbsp; {idx+1:3} - '{f.filename}' ('{fn}') uploaded successfully <br>\n"

                else:
                    content += f" &nbsp; {idx+1:3} - no file contents in multiple   input  {pformat(f)} <br>\n"

    else:
        content += "No multi files<br>\n"


    content += "<br>\n"


    if 'uploaded-file-1' in request.files:

        f = request.files['uploaded-file-1']
        if f.filename == '':
            content += "No file contents in single input  <br>\n"
        else:
            if f and f.filename:
                fn = cleanFileName(f.filename)
                filepath = os.path.join(UPLOAD_FOLDER, fn)

                checkExisting = Path(filepath)
                if checkExisting.is_file():
                    content += f"'{f.filename}' ('{fn}') already exists. Will overwrite. <br>\n"

                f.save(filepath)
                content += f"single file '{f.filename}' ('{fn}') uploaded successfully <br>\n"

    else:
        pass
        # content += "No single file<br>\n"


    try:
        return render_template(
            'main.html',
            HTMLTitle="Upload file",
            contentTpl="upload-file",
            cntAfter=content,
        )

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')




@app.route('/samples-import', methods=['post','get'])
def samplesImportH():



    # POST params
    kvPost = request.form.to_dict()
    # for k in kvPost:
    #     print(f"{k}")

    # extract and process POST params
    importedSmpls = []
    if len(kvPost) > 0:

        if  "action" in kvPost and kvPost["action"] == "import_samples":

            modeX = "none"
            if  "import-distinct" in kvPost:       # stupid checkbox submits no value if unchecked
                modeX = kvPost["import-distinct"]
            print(f"post request => import samples, mode {modeX}")

            filterBy = kvPost["filter"]

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

    try:
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

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')



# list of subdirectories in ./data as HTMLselect
def listBoxDataset():

    base_path = './data'
    dirs = []

    exclude = {
        "cfg": True,
        "init":True,
        "old-obsolete":True,
     }

    for item in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, item)) and item not in exclude and not item.startswith("tmp-"):
            dirs.append(item)

    selected = config.get("dataset")

    s  = '<label for="dataset">Choose a dataset:</label> '
    s += '<select name="dataset" id="dataset">'

    for dir in dirs:
        sel = ""
        if dir == selected:
            sel = ' selected'
        s += f'<option value="{dir}" {sel} >{dir}  </option>'
    s += '</select>'
    return s


@app.route('/save-all',methods=['post','get'])
def saveAllH():
    saveAll(force=True)
    return "OK"



@app.route('/config-edit',methods=['post','get'])
def configH():

    kvPost = request.form.to_dict()

    apiKey =  None
    if 'api_key' in kvPost:
        apiKey = kvPost['api_key']
    else:
        if 'api_key' in session:
            apiKey = session['api_key']
        else:
            apiKey = config.get("OpenAIKey")

    apiKeyValid, successMsg, invalidMsg = embeddings.checkAPIKeyOuter(apiKey)

    invalidMsgExt = ""
    if not apiKeyValid:
        invalidMsgExt = f'''
            {invalidMsg}
            <br>
            API key looks like <span style='font-size:85%'>sk-iliEnLtScLqauJejcpuDT4BlbkFJNTOc16c7E8R0NYVfODh5</span> <br>
            <br>
        '''


    datasetNew = None
    if 'dataset' in kvPost:
        datasetNew = kvPost['dataset']
        old = config.get("dataset")

        if datasetNew != old:
            config.set("dataset", datasetNew)
            saveAll(force=True)


    content = f'''

    <form action="" method="post">

        {invalidMsgExt}
        {successMsg}

        <label for="dataset">Open AI API Key</label>
        <input    name="api_key" type="input" size="64" value="{apiKey}"  >
        <br>

        {listBoxDataset()}
        <br>

        <button accesskey="s" ><u>S</u>ubmit</button>
    </form>

    <a href="/" {"autofocus" if apiKeyValid else ""}  >   Home        </a>

    '''

    try:
        return render_template(
            'main.html',
            HTMLTitle="API key",
            cntBefore=content,
        )

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')




@app.route('/contexts-edit', methods=['post','get'])
def contextsEditH():

    # POST params
    kvPost = request.form.to_dict()

    # extract and process POST params
    reqCtxs = []
    if len(kvPost) > 0:
        # for i,k in enumerate(kvPost):
        #     print(f"  req key #{i:2d}  '{k}' - {openai.ell(kvPost[k][:20],x=12)}")

        for i in range(0,100):
            sh = f"ctx{i+1:d}sh"  # starts with 1
            lg = f"ctx{i+1:d}lg"
            dl = f"ctx{i+1:d}_del"
            if lg not in kvPost:
                # print(f"input '{lg}' is unknown - breaking")
                break
            if dl in kvPost and  kvPost[dl] != "":
                print(f"  input '{lg}' to be deleted")
                continue
            if kvPost[lg].strip() == "":
                print(f"  input '{lg}' is empty")
                continue
            reqCtxs.append( {  "short": kvPost[sh], "long": kvPost[lg]  } )
            print(f"  input '{lg}' - {kvPost[lg][0:15]}")
        print(f"post request contained {len(reqCtxs)} contexts")
    else:
        print("post request is empty")


    ctxs = contexts.update(reqCtxs)

    if len(ctxs)>0 and ctxs[-1]["long"].strip() != "":
        ctxs.append( contexts.dummy() )

    print(f" overall number of contexts {len(ctxs) } ")
    for i,v in enumerate(ctxs):
        print(f"   {i} - {v['short'][0:15]} {v['long'][0:15]}..." )


    try:
        return render_template(
            'main.html',
            HTMLTitle="Edit Contexts",
            cntBefore=f"{len(ctxs)} contexts found",
            contentTpl="contexts",
            listContexts=ctxs,
        )

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')


@app.route('/benchmarks-edit', methods=['post','get'])
def benchmarksEditH():

    # POST params
    kvPost = request.form.to_dict()
    # for k in kvPost:
    #     print(f"{k}")

    # extract and process POST params
    reqBenchmarks = []
    if len(kvPost) > 0:
        for i1 in range(0,100):
            descr = f"benchmark{i1+1:d}_descr"  # starts with 1
            delet = f"benchmark{i1+1:d}_del"

            if descr not in kvPost:
                break

            if descr in kvPost and delet in kvPost and  kvPost[delet] != "":
                print(f"  input benchmark '{descr}' to be deleted")
                continue
            if kvPost[descr].strip() == "":
                print(f"  input benchmark '{descr}' is empty")
                continue

            sts = []
            for i2 in range(0,100):
                sh = f"benchmark{i1+1:d}_st{i2+1}_shrt"
                lg = f"benchmark{i1+1:d}_st{i2+1}_long"
                if lg not in kvPost:
                    break
                if kvPost[lg].strip() == "":
                    print(f"    bm {i1+1} stmt {i2+1} is empty")
                    # continue
                else:
                    sts.append(
                        {  "short": kvPost[sh], "long": kvPost[lg]  }
                    )

            reqBenchmarks.append(
                {
                    "descr": kvPost[descr],
                    "statements": sts,
                }
            )
            print(f"  input benchmark '{descr}' - {len(sts)} stmts - {kvPost[descr]}")

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

    try:
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

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')





@app.route('/samples-edit', methods=['post','get'])
def samplesEditH():

    # POST params
    kvPost = request.form.to_dict()
    # for k in kvPost:
    #     print(f"{k}")

    # extract and process POST params
    reqSamples = []
    if len(kvPost) > 0:

        for i1 in range(0,100):
            descr = f"sample{i1+1:d}_descr"  # starts with 1
            delet = f"sample{i1+1:d}_del"

            if descr not in kvPost:
                break

            if descr in kvPost and delet in kvPost and  kvPost[delet] != "":
                print(f"  input sample '{descr}' to be deleted")
                continue
            if kvPost[descr].strip() == "":
                print(f"  input sample '{descr}' is empty")
                continue

            sts = []
            for i2 in range(0,100):
                sh = f"sample{i1+1:d}_st{i2+1}_shrt"
                lg = f"sample{i1+1:d}_st{i2+1}_long"
                if lg not in kvPost:
                    break
                if kvPost[lg].strip() == "":
                    print(f"    bm {i1+1} stmt {i2+1} is empty")
                    # continue
                else:
                    sts.append(
                        {  "short": kvPost[sh], "long": kvPost[lg]  }
                    )

            reqSamples.append(
                {
                    "descr": kvPost[descr],
                    "statements": sts,
                }
            )
            print(f"  input sample '{descr}' - {len(sts)} stmts - {kvPost[descr]}")

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

    try:
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

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')






@app.route('/embeddings-basics', methods=['post','get'])
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




@app.route('/llm-chat', methods=['post','get'])
def llmChatH():

    args = request.args
    kvGet = args.to_dict()
    kvPost = request.form.to_dict()


    beliefStatement =  ""
    if "belief-statement" in kvPost:
        beliefStatement =  kvPost["belief-statement"]

    speech          =  ""
    if "speech" in kvPost:
        speech =  kvPost["speech"]


    inputs = {
        "beliefStatement" :  beliefStatement,
        "speech"          :  speech,
    }


    try:

        if len(beliefStatement.strip()) > 5 and len(speech.strip()) > 5:
            results = embeddings.requestChatCompletion(beliefStatement, speech)

        else:
            results = []
            results.append(
                {
                "prompt"    : "-",
                },
                {
                "ident":      "-",
                "jsonResult": "{}",
                "error"     : "no input given",
                }
            )


        return render_template(
            'main.html',
            HTMLTitle="Ask ChatGPT",
            contentTpl="llm-answer",
            # cnt1=cnt1,
            # cnt2=cnt2,
            vals=inputs,
            results=results,
        )

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')





@app.route('/embeddings-similarity', methods=['post','get'])
def embeddingsSimilarityH():


    # GET params
    args = request.args
    kvGet = args.to_dict()
    # pprint(kvGet)

    # POST params
    kvPost = request.form.to_dict()

    ctxUI, ctxs  = contexts.PartialUI(request, session)

    bmrkUI, bmSel  = benchmarks.PartialUI(request, session, showSelected=False)

    smplUI, smplSel  = samples.PartialUI(request, session, showSelected=False)



    try:
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

    except Exception as exc:
        # print(str(exc))
        print( stackTrace(exc) )
        return app.response_class(response=str(exc), status=500, mimetype='text/plain')





def loadAll(args):

    logTimeSince(f"loading data start", startNew=True)

    config.load()

    if len(args.ecb) > 0:
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

    if args.upl:
        smplsNew = uploadedToSamples()
        samples.update(smplsNew)
        samples.save()
        quit()


    loadEnglishStopwords()
    loadDomainSpecificWords()

    embeddings.load()
    contexts.load()
    benchmarks.load()
    samples.load()

    logTimeSince(f"loading data stop")



def saveAll(force=False):

    logTimeSince(f"saving  data start", startNew=True)

    if force:
        embeddings.cacheDirty = True
        contexts.cacheDirty = True
        benchmarks.cacheDirty = True
        samples.cacheDirty = True

    config.save()

    embeddings.save()
    contexts.save()
    benchmarks.save()
    samples.save()

    logTimeSince(f"saving  data stop")



if __name__ == '__main__':

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



    loadAll(args)

    app.run(
        host='0.0.0.0',
        debug=True,
        port=8001,
        use_reloader=False,
    )


    saveAll()

