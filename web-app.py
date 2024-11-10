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

import flask
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
from lib.util import mainTemplateHeadForChunking, templateSuffix
from lib.util import splitByMarkownHeaders
from lib.util import markdownLineWrap
from lib.util import splitByLineBreak

import  lib.config          as config


from lib.uploaded2samples import uploadedToSamples
from lib.ecb2samples      import ecbSpeechesCSV2Json


import models.embeddings as embeddings


logTimeSince(f"python script - imports stop")






def addPreflightCORS():
    rsp = make_response()
    rsp.headers.add("Access-Control-Allow-Origin",  "*")
    rsp.headers.add("Access-Control-Allow-Headers", "*")
    rsp.headers.add("Access-Control-Allow-Methods", "*")
    return rsp

def addActualCORS(rsp):
    rsp.headers.add("Access-Control-Allow-Origin", "*")
    return rsp

def signalHandler(signal, frame):
    print(f'flask server immediate shutdown - sig {signal}')
    sys.exit(0)

# signal.signal(signal.SIGINT,  signalHandler) # CTRL+C
# signal.signal(signal.SIGTSTP, signalHandler) # CTRL+Q


# we need this two at the top
app = Flask(__name__)
db  = SQLAlchemy()


# global error handler for any exception
@app.errorhandler(Exception)
def handle_error(e):
    print( stackTrace(e) )
    code = 500  # orig error code is not preserved
    return jsonify(error=str(e)), code


# home
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


    return render_template(
        'main.html',
        HTMLTitle="Main page",
        contentTpl="main-body",
        cntBefore=f"<p>{successMsg}</p>",
    )





# we set a different URL for favicon in main.html
# this is only for the 'rogue' routes, who generate streams etc.
@app.route('/favicon.ico')
def favicon():
    # following mimetypes made it worse:
    #  ...', mimetype='image/vnd.microsoft.icon')
    #  ...', mimetype='image/x-icon')
    return send_from_directory('static', 'favicon.svg')
    if False:
        return '', 204


# image handler for doc
@app.route('/doc/img/<path:fileName>')
def docImages(fileName):
    return send_from_directory('doc/img', fileName)



@app.route('/slides',  defaults={'fileName': "doc1.md"})
@app.route('/slides/', defaults={'fileName': "doc1.md"})
@app.route('/slides/<path:fileName>')
def serveSlides2(fileName):

    '''
        Page break for every header 1-3
          # Heading 1
          ## Heading 2...

        In addition: Explicit page break can be set using
            <!--pagebreak-->

    '''

    dr = os.path.join(".", "doc", "slides")
    fn = os.path.join(dr, f"{fileName}" )
    if not fn.lower().endswith(".md"):
        fn += ".md"
    with open(fn, encoding="utf-8") as inFile:
        mdContent = inFile.read()
        print(f"\tloaded markdown '{fileName}' - {len(mdContent)} bytes - from {dr}")


    pbInner = "<!--pagebreak-->"
    pbOuter = f"\r\n{pbInner}\r\n"

    # wrapping into <section> tags _after_ conversion to HTML proved impossible:
    # found no comfy document tree parser to wrap subtrees into <section>.
    # Instead we insert user-defined string <!--pagebreak--> before headings.
    # <!--pagebreak--> can be inserted in original markdown too.
    for hdrLvl in [2,3,4]:
        sections = splitByMarkownHeaders(mdContent, hdrLvl)
        mdContent = f"{pbOuter}{ '#'*hdrLvl } ".join(sections)


    if False:
        # auto split long text without headings
        splitThreshold = 12
        sections = mdContent.split(pbInner)
        for idx1, sect in enumerate(sections):
            lines = splitByLineBreak(sect)
            nonEmpty =  [ln for ln in lines if ln]

            if len(nonEmpty) > splitThreshold:
                linesNew = []
                lastInsert = 0
                for idx2, line in enumerate(lines):
                    if lastInsert > splitThreshold:
                        if not line.startswith(" "):
                            lastInsert = 0
                            linesNew.append("\r\n<!-- automatic pagebreak insertion -->")
                            linesNew.append(pbOuter)
                            print(f"\tsect{idx1} - pb before after {idx2}")
                    linesNew.append(line)
                    lastInsert += 1
                sections[idx1] = "\n".join(linesNew)

        mdContent = pbOuter.join(sections)

    mdContent = markdownLineWrap(mdContent)


    # https://python-markdown.github.io/extensions/
    # https://python-markdown.github.io/extensions/attr_list/
    # we can add CSS classes, element IDs and key-value attributes to markdown
    # using syntax   {: #myid .myclass   key='val' }
    from markdown.extensions.attr_list import AttrListExtension

    # note: dont use the mermaid extension
    #   instead write mermaid elements as <div class="mermaid">...
    #   and import the necessary javascript.
    #   examples in doc2.md

    htmlContent = markdown.markdown(
        mdContent,
        extensions=[AttrListExtension()],
        extension_configs="",
        tab_length=4,
    )


    # replacing  <!--pagebreak--> from above
    #  turning it into <section> nodes
    openSect = "\t<section>\n"
    closSect = "\n\t</section>"

    # replace inner
    htmlContent = htmlContent.replace( pbInner, f"{closSect}{openSect}")
    # enclose outer
    htmlContent = f"{openSect}<!--outer-->\n{htmlContent}\n<!--outer-->{closSect}"

    '''
     negative: ol counter will now be reset across sections.
      How do we preserve order list numbers across sections?
        	<ol start="3"> ?
      Using attr_list extension - we manually insert
           {: start='3' }
      Remember: separate line after markdown element
      But documentation says 'implied elements ... ul, ol ... no way'
      We have to set an explicit value with each li:

        3.  content of list item 3
        {: value='3' }
            * sub-list 1
        4.  content of list item 4
        {: value='4' }
            * sub-list 1
            * sub-list 2


          '''


    # there might be <p> and <p key=val>
    htmlContent = htmlContent.replace("<p ",   '<p class="fragment" ')
    htmlContent = htmlContent.replace("<p>",   '<p class="fragment" >')

    htmlContent = htmlContent.replace("<li class=\"", '<li  class="fragment ')  # two spaces - to prevent subsequent
    # htmlContent = htmlContent.replace("<li ", '<li class="fragment" ')
    htmlContent = htmlContent.replace("<li>", '<li class="fragment" >')

    htmlContent = htmlContent.replace("<tr ", '<tr class="fragment" ')
    htmlContent = htmlContent.replace("<tr>", '<tr class="fragment" >')

    htmlContent = htmlContent.replace("<blockquote ", '<blockquote class="fragment" ')
    htmlContent = htmlContent.replace("<blockquote>", '<blockquote class="fragment" >')

    if False:
        # images always inside list items
        htmlContent = htmlContent.replace("<img ", '<img class="fragment" ')

    # htmlContent = htmlContent.replace("<blockquote class=\"", '<blockquote class="fragment ')

    #  src="./img/xyz.jpg
    #       to
    #  src="/img/doc/xyz.jpg

    # image handler for doc
    htmlContent = htmlContent.replace("src=\"./img/", "src=\"/doc/img/")



    # dump file for debug
    fnOut = os.path.join(dr, f"tmp-{fileName}-rendered.html" )
    with open( fnOut, "w", encoding='utf-8') as outFile:
        outFile.write(htmlContent)


    return render_template(
        'reveal-js-adapter.html',
        revealHTML=htmlContent,
    )





@app.route('/upload-file',methods=['GET','POST'])
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


    return render_template(
        'main.html',
        HTMLTitle="Upload file",
        contentTpl="upload-file",
        cntAfter=content,
    )





@app.route('/samples-import', methods=['GET','POST'])
def samplesImportH():

    # GET + POST params
    kvGet  = request.args.to_dict()
    kvPost = request.form.to_dict()

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


@app.route('/save-all',methods=['GET','POST'])
def saveAllH():
    saveAll(force=True)
    return "OK"



@app.route('/config-edit',methods=['GET','POST'])
def configH():

    # GET + POST params
    kvGet  = request.args.to_dict()
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
            saveAll(force=True) # before switching

            # now switch
            config.set("dataset", datasetNew)
            config.save()

            loadAll( {} )


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

    '''

    #     <a href="/" {"autofocus" if apiKeyValid else ""}  >   Home        </a>

    return render_template(
        'main.html',
        HTMLTitle="API key",
        cntBefore=content,
    )





@app.route('/contexts-edit', methods=['GET','POST'])
def contextsEditH():

    # GET + POST params
    kvGet  = request.args.to_dict()
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
    kvGet  = request.args.to_dict()
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
    kvGet  = request.args.to_dict()
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
    kvGet  = request.args.to_dict()
    kvPost = request.form.to_dict()

    beliefStatement =  ""
    if "belief-statement" in kvPost:
        beliefStatement =  kvPost["belief-statement"]

    speech          =  ""
    if "speech" in kvPost:
        speech =  kvPost["speech"]


    # requestChatCompletion is now a generator
    # returning various types of returns in a protracted way
    # we collect all chunks - and then render them in one go
    prompt = ""
    results = []
    idx1 = -1
    for res in embeddings.generateChatCompletionChunks( beliefStatement, speech):
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
    kvGet  = request.args.to_dict()
    kvPost = request.form.to_dict()
    # for k in kvPost:
    #     print(f"{k}")

    asEventStream = False
    # 'text/plain', 'text/html; charset=UTF-8'
    mType = 'text/html'

    if ("event-stream" in kvGet) or ("event-stream" in kvPost):
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
    kvGet  = request.args.to_dict()
    kvPost = request.form.to_dict()

    model  =  ""
    prompt =  ""
    role   =  ""

    try:
        kvPost = request.get_json(silent=False)

        if "prompt" in kvPost:
            prompt =  kvPost["prompt"]

        role          =  ""
        if "role" in kvPost:
            role =  kvPost["role"]

    except Exception as exc:
        print(f"request body was not JSON - probably POST")

        beliefStatement          =  ""
        if "belief-statement" in kvPost:
            beliefStatement =  kvPost["belief-statement"]

        speech          =  ""
        if "speech" in kvPost:
            speech =  kvPost["speech"]

        prompt, role, _ = embeddings.designPrompt(beliefStatement, speech)


    if "model" in kvPost:
        model =  kvPost["model"].strip()
    if model == "":
        models = config.get("modelNamesChatCompletion")
        model =  models[0]



    # if len(prompt) < 5:
    #     print(f"  too short")
    #     return app.response_class(
    #         response=f"{{ error: too short {prompt} }}   ",
    #         mimetype='application/json',
    #         status=500,
    #     )

    try:

        result = embeddings.chatCompletion(model, prompt, role)
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
    kvGet  = request.args.to_dict()
    kvPost = request.form.to_dict()

    beliefStatement =  ""
    if "belief-statement" in kvPost:
        beliefStatement =  kvPost["belief-statement"]

    speech          =  ""
    if "speech" in kvPost:
        speech =  kvPost["speech"]


    prompt, role, err = embeddings.designPrompt(beliefStatement, speech)
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
    kvGet  = request.args.to_dict()
    kvPost = request.form.to_dict()

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

    embeddings.load()
    contexts.load()
    benchmarks.load()
    samples.load()

    logTimeSince(f"loading data stop")





class Embedding(db.Model):
    __tablename__ = 'embeddings'
    id         = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    datetime   = db.Column(db.DateTime, default=datetime.utcnow)
    hash       = db.Column(db.String,   unique=True, nullable=False, index=True)
    text       = db.Column(db.Text,     nullable=False)
    embeddings = db.Column(JSON)  # SQLite > 3.9.

    modelmajor = db.Column(db.String,    nullable=False)
    modelminor = db.Column(db.String,    nullable=False)
    promptversion = db.Column(db.String, nullable=False, default="1.0")
    role       = db.Column(db.String,    nullable=False)

    def __repr__(self):
        return f"<Embedding {self.id} - {self.hash}>"



def dummyRecordEmbedding(idx):

    from models.embeddings import strHash

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




def saveAll(force=False):

    logTimeSince(f"saving  data start", startNew=True)

    if force:
        embeddings.cacheDirty = True
        contexts.cacheDirty = True
        benchmarks.cacheDirty = True
        samples.cacheDirty = True


    embeddings.save()
    contexts.save()
    benchmarks.save()
    samples.save()

    logTimeSince(f"saving  data stop")





def ifNotExistTable(tableName):
    inspector = inspect(db.engine)
    if tableName not in inspector.get_table_names():
        print(f"Table '{tableName}' does not exist. Creating tables...")
        db.create_all()
    else:
        print(f"Table '{tableName}' already exists. Skipping creation.")



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
    print(f"  app.instance_path {app2.instance_path} - change to 'data'")
    app2.instance_path='data'    # default is "instance" - sqlite file go here
    app2.debug=True

    config.load(app2)


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



    # from .models import Embedding
    with app2.app_context():
        # db.create_all()
        ifNotExistTable('embedding')

    # insert dummy records
    with app2.app_context():
        for idx in [1,2,3]:
            db.session.add( dummyRecordEmbedding(idx) )
        db.session.commit()


    loadAll(args)

    app2.run(
        host='0.0.0.0',
        debug=True,
        port=8001,
        use_reloader=False,
    )

    config.save()
    saveAll()

    return app2



UPLOAD_FOLDER = ""

if __name__ == '__main__':
    app = createAndRun(app)


