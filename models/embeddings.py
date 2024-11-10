"""
embeddings.py

This module extends the OpenAI API


"""


import sys
import re
import json

import hashlib

from datetime import datetime

from   copy     import deepcopy


from pprint import pprint, pformat


import requests

import pandas as pd
import numpy  as np
np.set_printoptions(threshold=sys.maxsize)

import matplotlib.pyplot as plt


from lib.util   import saveJson, loadJson
from lib.config import get, set

from lib.init import logTimeSince

import openai



# https://platform.openai.com/docs/models/embeddings
vectSize = 3078


# pip install py_markdown_table
from py_markdown_table.markdown_table import markdown_table


# every function called by a flask handler
# gets the request and the session passed on automtically.
# But we have to import the module from flask for this to work
#
from   flask import request, session

# usage from other module:
#       lib_openai.passingOnRequestAndSession("dummy")
def passingOnRequestAndSession(dummy1, dummy2=4):
    user_agent = request.headers.get('User-Agent')
    print( f"-- user agent: {user_agent}")
    print( f"-- session[api_key]: {get('OpenAIKey')}")


def restore_broken_words(text):
    # Remove line breaks that break words
    restored_text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # Replace remaining line breaks with space
    restored_text = restored_text.replace('\n', ' ')
    return restored_text

def removeNewlines(txt):
    # flat = re.sub(r'\n+', r' ', txt)
    flat = txt
    flat = flat.replace("\n", ' ')
    flat = flat.replace("  ", ' ')
    flat = flat.replace("  ", ' ')
    return flat

# ellipsis of a long string
def ell(s, x=16):
    s = removeNewlines(s)
    s.strip()
    if len(s) < 2*x:
        return s
    return f"{s[:x]} … {s[-x:]}"

def strHash(s):
    hashObject = hashlib.md5(s.encode())
    hsh = hashObject.hexdigest()
    return hsh


# print list of floats
def pfl(lst, x=3, digits=3, showLength=True):
    # ret = f"{lst[:x]} {lst[-x:]}"
    fstr = f"+{digits+2}.{digits}f"

    ret = ""
    for i in range(x):
        ret += f"{lst[i]:{fstr}}  "
    ret += " …   "
    for i in range(x):
        ret += f"{lst[-i]:{fstr}}  "

    if showLength:
        ret += f"-   {len(lst)} els"

    return ret

# cache
c_embeddings = {}
cacheDirty = False


# for from the max/min of embed values - within this distance - the points are plotted
# significantBand = 0.08
significantBand = 0.025
# globNeighbors=48
# globNeighbors= 2
globNeighbors= 4



# significant data points of a single embedding
# values being close to min or max
# returns min and max and delta a display string - rng
# returns mn and max
# return strsNegPos - list of significant key-val - each element formatted as string
# returns list of value and indexes as string
# returns list of dicts, sorted by index and sorted by value
def significants(embd, idx1=-1, band=significantBand, neighbors=globNeighbors):

    strsNeg = [] # strings negative    - els < 0; list, each element is a formatted string
    strsPos = [] # strings positive    - els > 0; list, each element is a formatted string
    ksVsNeg = [] # key-values negative - els < 0; list, each element is sublist [index, value]
    ksVsPos = [] # key-values positive - els > 0; list, each element is sublist [index, value]

    mx = max(embd)
    mn = min(embd)

    rng = f"min {mn:6.3f}   max {mx:6.3f}   Δ {(mx-mn):4.2f}"
    if idx1 > -1:
        rng = f"idx {idx1:2}   {rng}"
    # print(rng)


    if False:
        mxT = (mx - band)
        mnT = (mn + band)
        neighborsCutOff = 0.025
        for idx2, v in enumerate(embd):
            try:
                if v > mxT:
                    for idx3 in range(-neighbors, neighbors+1):
                        displ = idx2+idx3
                        if embd[displ] > (mxT - neighborsCutOff):
                            strsPos.append( f"{round(embd[displ],5):6.3f} {displ:4}"  )
                            ksVsPos.append( [displ,embd[displ]] )
                if v < mnT:
                    for idx3 in range(-neighbors, neighbors+1):
                        displ = idx2+idx3
                        if embd[displ] < (mnT + neighborsCutOff):
                            strsNeg.append( f"{round(embd[displ],5):6.3f} {displ:4}"  )
                            ksVsNeg.append( [displ,embd[displ]] )
                else:
                    pass
            except IndexError:
                print(f"significant neighbor index out of bounds")


        # sort and combine neg and pos strings
        strsNeg.sort(reverse=True)
        strsPos.sort()
        strsNegPos = deepcopy(strsNeg)
        strsNegPos.extend(strsPos)

        # combine neg and pos key-values
        kvsNegPos = deepcopy(ksVsNeg)
        kvsNegPos.extend(ksVsPos)


        kvsNegPosByKey = sorted(kvsNegPos, key=lambda el: el[0])
        kvsNegPosByVal = sorted(kvsNegPos, key=lambda el: el[1])

    # different approach
    # ---------------------------

    kvRaw = []
    for idx2, v in enumerate(embd):
        kvRaw.append( [idx2, v] )
    kvSorted = sorted(kvRaw, key=lambda el: el[1])


    strsNeg = []
    strsPos = []
    ksVsNeg = []
    ksVsPos = []

    lengthTail = 8
    lengthTail = 16
    lengthTail = 32
    # first x elements
    for idx2, kv in enumerate(kvSorted[:lengthTail]):
        strsNeg.append( f"{round(kv[1],5):6.3f} {kv[0]:4}"  )
        ksVsNeg.append( [kv[0],kv[1]] )
    # last  x elements
    for idx2, kv in enumerate(kvSorted[-lengthTail:]):
        strsPos.append( f"{round(kv[1],5):6.3f} {kv[0]:4}"  )
        ksVsPos.append( [kv[0],kv[1]] )


    # combine neg and pos key-values - 1
    strsNegPos = deepcopy(strsNeg)
    strsNegPos.extend(strsPos)

    # combine neg and pos key-values - 2
    kvsNegPos = deepcopy(ksVsNeg)
    kvsNegPos.extend(ksVsPos)

    kvsNegPosByKey = sorted(kvsNegPos, key=lambda el: el[0])
    kvsNegPosByVal = sorted(kvsNegPos, key=lambda el: el[1])


    return (
        rng,
        mn, mx,
        strsNegPos,
        kvsNegPos,
        kvsNegPosByKey,
        kvsNegPosByVal,
    )



def significantsForPlot(embds, band=significantBand, neighbors=globNeighbors):

    allIdxs = []
    allVals = []

    mn = -0.0000001
    mx = +0.0000001


    for idx1, embd in enumerate(embds):

        idxs = []  # significant indizes for single embedding
        vals = []  # significant values  for single embedding


        mnS = min(embd)
        if mnS < mn:
            mn = mnS
        mxS = max(embd)
        if mxS > mx:
            mx = mxS

        plotNeighbors = globNeighbors
        plotNeighbors = 8
        plotNeighbors = 16
        rng, mn, mx, sign2, kvsNegPos ,  _ , _ = significants(embd, idx1, neighbors=plotNeighbors )

        for idx2, kv in enumerate(kvsNegPos):
            idxs.append(kv[0])
            vals.append(kv[1])

        allIdxs.append(idxs)
        allVals.append(vals)

        if False:
            print(f"  {len(allVals[idx1]):4} significant embed values for {len(embd)} computed")
            dmp = deepcopy( allIdxs[idx1] )
            dmp.sort()
            print(f"    {dmp[:20]}...")


    permutes = {}
    numSeries = len(allIdxs)
    for idx1, series in enumerate(allIdxs):
        for xcoord in series:
            occurrences = 0
            for idx3 in range(numSeries):
                if xcoord in allIdxs[idx3]:
                    occurrences +=1
            if xcoord in permutes:
                permutes[xcoord]  += occurrences
            else:
                permutes[xcoord]   = occurrences



    overlaps = []
    for k in permutes:
        if permutes[k] > 1:
            overlaps.append(k)

    # print(f"  {len(overlaps):4} overlaps")
    overlaps.sort()

    if False:
        print(f"    ", end="")
        for idx, k in enumerate(overlaps):
            # print(f"{k:3}-{permutes[k]} ", end="")
            print(f"{k:3} ", end="")
            if idx > 20:
                break
        print("")


    return (allIdxs, allVals, mn, mx, overlaps)




# compute significant data points for a embeddings in the module
def significantsList():
    rng, lStr, lIdxVal, idxValByIdx, idxValByVal = {},{},{},{},{}
    for idx, k in enumerate(c_embeddings):
        rng[k], mn, mx , lStr[k], lIdxVal[k], idxValByIdx[k], idxValByVal[k] = significants(c_embeddings[k], idx, neighbors=0)
    return (rng, lStr, lIdxVal, idxValByIdx, idxValByVal)





prop_cycle = plt.rcParams['axes.prop_cycle']
plotColors = prop_cycle.by_key()['color']

plotColors2 = [
    'blue',
    'green',
    'red',
    'cyan',
    'magenta',
    '#aabbcc',
    '#ffbb11',
    '#c2a',
    '#aac',

# repeat - to avoid index out of bounds
    'blue',
    'green',
    'red',
    'cyan',
    'magenta',
    '#aabbcc',
    '#ffbb11',
    '#c2a',
    '#aac',
]
plotColors.extend(plotColors2)


# creating scatter plot of data points as a JPG file
#  groupSize - color n rows in similar color
def scatterPlot(lbl, idxs, vals, mnVls, mxVls, overlaps=[], groupSize=1):

    # markerSize = 10
    markerSize = 1
    markerSize = 2
    markerSize = 4

    plt.figure(figsize=(16, 5))

    try:

        for idx1, seriesIdxs in enumerate(idxs):

            # print(f" multi series {idx1} {len(idxs)}  {len(vals)}")
            seriesVals = vals[idx1]

            # s=10 is the markers size

            # shift x-coords to see overlapp
            seriesIdxsCX = []
            dx = int(idx1*(0.8*markerSize)) # variable could be cx
            for idx2, idxOld in enumerate(seriesIdxs):
                idxNew = idxOld + dx
                if idxNew < vectSize:
                    seriesIdxsCX.append(idxNew)
                else:
                    seriesIdxsCX.append(idxOld)

            colr = plotColors[idx1+1]
            if groupSize > 1:
                colr = plotColors[int(idx1/groupSize)+1]


            plt.scatter(seriesIdxsCX, seriesVals, color=colr, s=markerSize )


        plt.axhline(0, color='gray', linestyle='--', linewidth=1)

        plt.xlim([    0, 3072])

        plt.ylim([ -0.2,  0.2])
        plt.ylim([ -0.12,  0.12])

        floorDY = 0.12 # min height of chart Y-area - upwards and downwards
        if mnVls > -floorDY:
            mnVls = -floorDY
        if mxVls < +floorDY:
            mxVls = floorDY

        plt.ylim([ mnVls-0.02, mxVls+0.02])

        vertHalf =    -(mnVls-0.02) / ( (mxVls+0.02) -  (mnVls-0.02))
        for xcoord in overlaps:
            plt.axvline(x=xcoord, ymin=(vertHalf-0.03), ymax=(vertHalf+0.03), color='lightgrey',)


        # plt.ylabel('PCA')
        # plt.xlabel('Idx')

        # minimize horizontal margins
        plt.subplots_adjust(left=0.04, right=0.99)

        # vertical margins - *ATTENTION*  bottom up
        plt.subplots_adjust( top=0.91,bottom=0.05)

        lblShrt = (lbl[:44] + " … " + lbl[-44:]) if len(lbl) > (2*44) else lbl
        lblShrt = lblShrt.replace("\n"," ")

        overlapDensity = float(len(overlaps) / len(idxs[0])) * 100

        plt.title(f"Significant embeds - {overlapDensity:5.0f}% overlaps \n-{lblShrt}- ")

    except Exception as error:
        print(f"ERROR plotting: {str(error)}")

    # fn = cleanFileName(lbl)

    lblHash =  strHash(lbl)
    fn = lblHash

    plt.savefig(f'./static/img/dynamic/{lblHash}.jpg', format='jpg')
    print(f"     plot saved for lbl '{lbl[:44]}'")

    # Show plot for review
    # plt.show()
    plt.close()





#  scatter plot of data points as a JPG file
def significantsAsPlots(lbls, embds, numCtxs):

    allIdxs, allVals, mn, mx, overlaps = significantsForPlot(embds)


    for idx1, embd in enumerate(embds):
        lbl = lbls[idx1]
        scatterPlot(lbl,  [allIdxs[idx1]] , [allVals[idx1]], min(allVals[idx1]), max(allVals[idx1]) )

    scatterPlot( ", ".join(lbls), allIdxs, allVals, mn, mx, groupSize=numCtxs, overlaps=overlaps)


def checkAPIKeyOuter(apiKey):

    apiKeyValid = True
    invalidMsg = ""
    successMsg = ""

    # SET OPENAI_API_KEY=sk-iliEn...YVfODh5
    if apiKey.startswith("your secret"):
        apiKeyValid = False
        invalidMsg += "replace init placeholder 'your secret'<br>\n"
    elif (apiKey is None) or not apiKey.startswith("sk-"):
        apiKeyValid = False
        invalidMsg += "must start with 'sh-'    <br>\n"
    elif len(apiKey) < 50:
        apiKeyValid = False
        invalidMsg += "must be 50 chars or more <br>\n"

    if not apiKeyValid:
        pass
    else:
        liveCheck, msg = checkAPIKeyInner(apiKey)
        if not liveCheck:
            apiKeyValid = False
            invalidMsg += msg + "<br>\n"
        else:
            successMsg += "connection to OpenAI API succeeded<br>\n"
            session['api_key'] = apiKey
            set("OpenAIKey", apiKey)

    return (
        apiKeyValid,
        successMsg,
        invalidMsg,
    )



def load():
    global c_embeddings  # in order to _write_ to module variable

    c_embeddings = loadJson("embeddings", subset=get("dataset"), onEmpty="dict")


    if False:
    # if True:
        keysToDelete = []
        for idx,k in enumerate(c_embeddings):
            if "price" in k or "Price" in k :
                keysToDelete.append(k)
        for k in keysToDelete:
            del( c_embeddings[k] )
            print(f"deleting {k[:20]}")
        global cacheDirty
        cacheDirty = True


    for idx,k in enumerate(c_embeddings):
        print(f"  {ell(k,x=24) :>51} - embds { pfl(c_embeddings[k],showLength=False) }")
        if idx > 4:
            break



# save embeddings
def save():
    if not cacheDirty:
        print(f"\tembeddings are unchanged ({len(c_embeddings):3} entries). ")
        return

    rng, lStr, _ ,  _ , _ = significantsList()
    lStr["ranges"] = rng # add as additional info
    saveJson(lStr, "embeddings-significant", subset=get("dataset"), tsGran=1)


    saveJson(c_embeddings, "embeddings", subset=get("dataset"))




# is newKey valid
def checkAPIKeyInner(newKey):

    try:
        headers = {
            "Authorization": f"Bearer {newKey}",
        }
        response = requests.get("https://api.openai.com/v1/models", headers=headers)
        if response.status_code == 200:
            return (True, "API key is valid.")
        else:
            return (False,  f"API key is invalid. Status code: {response.status_code}, Response: {response.text}" )



    except Exception as error:
            errStr = str(error)
            pos = errStr.find("Failed to establish a new connection")
            if pos != -1:
                return (True,  f"API key could not be validated - proceeding anyway" )

            return (False,  f"API key could not be validated: \n\t{error}" )


def createClient():
    # print( f"")
    print( f"  OpenAI API key is -{get('OpenAIKey')}-   ", end="")
    try:
        clientNew = openai.OpenAI(
            api_key = get('OpenAIKey'),
            timeout=10,
        )
        print( f" - client created")
        return (clientNew, "")

    except requests.exceptions.Timeout:
        errStr = "request to openAI timed out."
        print(errStr)
        return (None, errStr)
    except Exception as exc:
        errStr = f"error during client creation: {exc}"
        print(errStr)
        return (None, errStr)


# lst python list of statements or sentences,
# for example ['inflation will be high', 'inflation will be low']
# We get "loadings" for a principal components analysis (PCA).
# There are 3072 'components' in ChatGPT-O.
# Embeddings for a sequence of tokens (i.e. a sentence) is created by weighing the embeddings of each token.
# Weights are dynamically derived by the LLM using the context and using "attention".
#
# Usage
#   e1,s = lib_openai.getEmbeddings(statements, contexts)
#
#   https://blog.teclado.com/destructuring-in-python/
#
# returns a List of np.arrays - containing embeddings as
defaultContext = {"short": "", "long": ""}
def getEmbeddings(stmts, ctxs=[], ctxScalar=defaultContext):

    global c_embeddings  # in order to access module variable
    # print(f"cached embeddings 'embeddings' - size {len(c_embeddings)} - type {type(c_embeddings)}   ")

    # append context to requested input sentences
    if len(ctxs) == 0:
        if ctxScalar["long"].strip() != "":
            for idx2, stmt in enumerate(stmts):
                stmts[idx2] = f"Context: { ctxScalar['long'].strip() } \nSentence: {stmt}"
    else:
        stmtsWCtx =  []
        for idx1, stmt in enumerate(stmts):
            for idx2, ctxL in enumerate(ctxs):
                if ctxL["long"].strip() != "":
                    tmp = f"Context: { ctxL['long'].strip() } \nSentence: {stmt}"
                    stmtsWCtx.append(tmp)
                else:
                    # tmp = ctxL['long'].strip()
                    # tmp = f"Context:                          \nSentence: {inp}"
                    stmtsWCtx.append(stmt)
        stmts = stmtsWCtx

        if False:
            pprint(stmts)
            print("-----")
            for idx, val in enumerate(stmtsWCtx):
                print(f"{idx+1} {ell(val, x=48)}")
            print("====")
            print(" ")


    stmtsNotInC = [] # statements not in cache
    embdsByK    = {} # requested embeddings by statement - cached and newly retrieved

    for idx2, stmt in enumerate(stmts):
        if stmt in c_embeddings:
            embdsByK[stmt] = c_embeddings[stmt]  # take from cache
            print(f"     ffor-a {ell(stmt,x=32)}")
            print(f"     embs from cache  {pfl( c_embeddings[stmt], x=5)}")
        else:
            # print(f"     embeddings for {stmt} not in cache")
            stmtsNotInC.append(stmt)

    print(f"   {len(stmts)} embs requested - {len(stmtsNotInC)} not in cache")

    # not yet in cache
    #       => retrieve from OpenAI
    #       => add to cache
    if len(stmtsNotInC)>0:

        clnt, errStr = createClient()
        if errStr != "":
            return ([], errStr)

        try:
            response = clnt.embeddings.create(
                input=stmtsNotInC,
                model=get("modelNameEmbeddings"),
            )
        except Exception as exc:
            errStr = f"error during embeddings retrieval: {exc}"
            print(errStr)
            return ([], errStr)

        # add newly retrieved to return and cache
        for idx2, record in enumerate(response.data):
            stmt = stmtsNotInC[idx2]
            embdsByK[stmt] = record.embedding
            print(f"     ffor-b {ell(stmt,x=32)}")
            print(f"     embs from openai {pfl( record.embedding,x=5) }")
            # arr.append( np.array(record.embedding) )

            # add to cache
            c_embeddings[stmt] = record.embedding
            global cacheDirty
            cacheDirty = True

        # save()
        print(f"   {len(stmtsNotInC):2} new embs saved ")


    # ---- retrieval stop

    # embdsByK *may* be ordered differently from stmts
    embds = []
    for stmt in stmts:
        embds.append( embdsByK[stmt] )


    # following operations expect a list of a numpy arrays
    arrNp = []
    for row in embds:
        arrNp.append(  np.array(row) )
    print(f"   {len(arrNp)} return vals converted {len(stmts)}")


    return arrNp


def getEmbeddingsHTML(stmts, embds, ctxs, strFormat="simple", ):

    # display as HTML
    # ========================
    s  = ""
    # s += "Vector embeddings for:  \n"
    prev = "-1"  # previous statement
    for idx2, stmt in enumerate(stmts):


        if len(ctxs) == 0:
            disIdx = idx2+1
        else:
            disIdx = int(idx2 / len(ctxs) + 1)

        colr = plotColors[idx2+1]
        if len(ctxs) > 1:
            colr = plotColors[int(idx2/len(ctxs))+1]


        if stmt.__contains__("\nSentence:"):
            inps = stmt.split("\nSentence:",1)
            if len(inps)== 2:
                lCtx = inps[0]
                lCtx = lCtx[9:]
                if inps[1] != prev:
                    s += f'''<p class='inp' style='color:{colr}'> {disIdx:2}: {inps[1]}
                                <span class='context1'> {ell(lCtx,x=64)}  </span>
                            </p>\n'''
                else:
                    s += f'''<p class='inp' style='color:{colr}'>
                                <span class='context1'> {ell(lCtx,x=64)}  </span>
                            </p>\n'''
                prev = inps[1]
                # print(f"1 prev now -{prev}-")

            else:
                if stmt != prev:
                    s += f'''<p class='inp' style='color:{colr}'> {disIdx:2}: {stmt}
                                <span class='context1'> None  </span>
                            </p>\n'''
                else:
                    pass
                prev = stmt
                # print(f"2 prev now -{prev}-")
        else:
            if stmt != prev:
                s += f'''<p class='inp' style='color:{colr}'>    {disIdx:2}: {stmt}
                                <span class='context1'> None  </span>
                        </p>\n'''
            else:
                pass

            prev = " "+stmt
            # print(f"3 prev now -{prev}-")



        s += f" <p class='embeds'> <span class='embed-pre'>vect embed's</span>  {pfl(embds[idx2], x=5)} </p>\n"

        numEls = 3
        if strFormat == "extended":
            rng, mn, mx , sign2,  _ ,  _ , _ = significants(embds[idx2], neighbors=0)
            frst3 = ", ".join(sign2[:numEls])
            last3 = ", ".join(sign2[-numEls:])
            s += f"<p class='embeds'> <span class='embed-pre'>significant</span>  {frst3}    …   {last3} </p> \n"
            s += f"<p class='embeds'> <span class='embed-pre'>range </span>  {rng}  </p> \n"
            # s += f"<p class='embeds'>  {pfl(sign2, x=5)} </p> \n"

        if False:
            s += f" <img  width='90%' height='220px' width='100%'  src='../static/img/dynamic/{strHash(stmt)}.jpg' />     \n"



    hLbl = strHash( ", ".join(stmts) )
    s += f" <img  width='90%' height='400px' width='100%'  src='../static/img/dynamic/{hLbl}.jpg' />     \n"

    s += "\n"


    return s


def getEmbeddingsPlot(stmts, embds, ctxs):
    significantsAsPlots(stmts, embds, len(ctxs))



def getEmbeddingCached(s):
    pass




def helperCosineSimilarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def distance(a, b):
    return 1 - helperCosineSimilarity(a, b)


# unused
def view_correlations(table, texts):
    df = pd.DataFrame(table)
    index = {i: name for i,name in enumerate(texts)}
    df.rename(columns=index, inplace = True)

    data = df.to_dict(orient='records')

    markdown = markdown_table(data).get_markdown()
    # print(markdown)
    return markdown

# unused
def correlationsAsMarkdown(texts, embeddings):

    table = []
    for idx1, x in enumerate(embeddings):
        table.append([])
        for idx2, y in enumerate(embeddings):
            if idx1 != idx2:
                table[-1].append(f'{helperCosineSimilarity(x,y):.02f}')
            else:
                table[-1].append('--')

    df = pd.DataFrame(table)
    index = {i: name for i,name in enumerate(texts)}
    df.rename(columns=index, inplace = True)

    data = df.to_dict(orient='records')
    markdown = markdown_table(data).get_markdown()
    return (table, markdown)



# x-axis
def correlationsXY(
        tX, # texts x axis
        embsX,
        tY, # texts y axis
        embsY,
):

    if len(tX) != len(embsX):
        msg = f"  x-axis len(tX) != len(embsX) - {len(tX)} != {len(embsX)} "
        print(msg)
        return ( [[],[]], msg)

    if len(tY) != len(embsY):
        msg = f"  y-axis len(tY) != len(embsY) - {len(tY)} != {len(embsY)} "
        print(msg)
        return ( [[],[]], msg)


    coeffsMatr = []
    for idx1, y in enumerate(embsY):
        coeffsMatr.append([])
        for idx2, x in enumerate(embsX):
            if tY[idx1] != tX[idx2]:
                coeffsMatr[-1].append(f'{helperCosineSimilarity(x,y):.03f}')
            else:
                coeffsMatr[-1].append('--')

    return (coeffsMatr,"  ")



def designPrompt(beliefStatement, speech):

    role = get("role")

    # Optional prompt enhancements:
    #   "Which specific arguments or parts of the speech support or contradict the belief?"
    #   "Does the speech include any caveats or conditions that modify the central argument?"


    prompt = f"""
{role}

The belief statement is: "{beliefStatement}"

The speech text is: "{speech}"

Make sure to give an objective analysis based on the content of the speech.

I need a thorough textual analysis on how much the speech aligns with the belief statement.

Determine whether the speech agrees, disagrees, or remains neutral on the belief.

Provide a percentage score for alignment.

Use the following json format for your response:

{{
    "agreement":        "<agrees/disagrees/neutral>",
    "alignment":         <percentage_score>
    "textual_analysis":  <text>
}}
    """

    prompt = prompt.strip()

    if len(beliefStatement.strip()) < 5 or len(speech.strip()) < 5:
        return prompt, role, "too short"


    return prompt, role, ""


def resDummy():
    dummy = {
        "model":             "-",
        "agreement":         "-",
        "alignment":          0,
        "textual_analysis":  "-"
    } 
    return dummy


# platform.openai.com/docs/guides/text-generation/conversations-and-context
#   the chunking is not used
def generateChatCompletionChunks(beliefStatement, speech):

    prompt, role, err = designPrompt(beliefStatement, speech)
    if err != "":
        yield prompt
        results = []
        results.append(
            {
                "ident":      "-",
                "jsonResult": resDummy(),
                "error"     : err,
            }
        )
        yield results[-1]


    yield prompt


    # load from file cache
    hsh = strHash(prompt)
    results = loadJson(f"chat-completion-{hsh}", subset=get("dataset"))
    if len(results) > 0:
        for result in results:
            yield result
        
        logTimeSince(f"\tchat completion - cache", startNew=True)
        yield  "end-of-func"
        return


    models=get("modelNamesChatCompletion")

    listSeeds = [100,101,102]
    listSeeds = [100] # seeds are only BETA - output should be mostly *deterministic*
    results = [] # responses
    # results.append( {"prompt":prompt} )

    clnt, errStr = createClient()
    if errStr != "":
        results.append( { "error" : errStr}  )
        return results


    for idx1, model in enumerate(models):
        for idx2, seed in enumerate(listSeeds):

            ident = f"{idx1+1}{idx2+1}--model{model}-seed{seed}"
            logTimeSince(f"\tchat completion start {ident}", startNew=True)

            # https://platform.openai.com/docs/api-reference/chat/create
            respFmt = { "type": "json_object" }
            if model != "gpt-4o":
                respFmt = openai.NOT_GIVEN

            msgs = [
                    {
                        "role":      "system",
                        "content":  f"{role}"
                    },
                    {
                        "role":     "user",
                        "content":   prompt,
                    }
                ]
            # print(  json.dumps(msgs, indent=4) )

            completion = clnt.chat.completions.create(
                model=model,
                response_format= respFmt ,
                messages=msgs,
                max_completion_tokens=get("tokens_max"),    # Limit for response tokens
                temperature=get("temperature"),
                n=1,                # Number of completions to generate
                stop=None,          # Specify stop sequences if needed
                seed=seed,
            )

            txt = completion.choices[0].message.content


            try:
                jsonResult = json.loads(txt)
                results.append(
                    {
                        "ident":      ident,
                        "jsonResult": jsonResult,
                        "error"     : "",
                    }
                )
            except json.JSONDecodeError as exc:
                results.append(
                    {
                        "ident":      ident,
                        "jsonResult": resDummy(),
                        "error"     : f"Failed to parse GPT output as JSON \n{exc}",
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "ident":      ident,
                        "jsonResult": resDummy(),
                        "error"     : f"Common exc parsing GPT output as JSON \n{exc}",
                    }
                )

            logTimeSince(f"\tchat completion stop  {ident} - len {len(txt)} chars")

            yield results[-1]


    ts = f"-{datetime.now():%m-%d-%H-%M}"
    saveJson(results, f"chat-completion-{ts}", subset=get("dataset"))

    saveJson(results, f"chat-completion-{hsh}", subset=get("dataset"))


    yield  "end-of-func"
    # return results


# makes request to OpenAI
# returns result as dict - read for usage as JSON 
def chatCompletion(model, prompt, role, seed=100):

    # load from file cache
    hsh = strHash(prompt)
    res = loadJson(f"chat-completion-{model}-{hsh}", subset=get("dataset"), onEmpty="dict")
    if "model" in res   and   res["model"] == model:
        return res


    clnt, errStr = createClient()
    if errStr != "":
        res = {
            "model":      model,
            "ident":      "-",
            "jsonResult": resDummy(),
            "error"     : errStr,
        }
        return res


    maxCompletionTokens=get("tokens_max")    # Limit for response tokens
    celsius=get("temperature")
    ident = f"{model}-{celsius}d-{maxCompletionTokens}t"
    res = [] # responses
    respFmt = { "type": "json_object" }
    if model != "gpt-4o":
        respFmt = openai.NOT_GIVEN  # unsupported  -  platform.openai.com/docs/api-reference/chat/create

    logTimeSince(f"\tchat completion start {ident}", startNew=True)

    msgs = [
            {
                "role":      "system",
                "content":  f"{role}"
            },
            {
                "role":     "user",
                "content":   prompt,
            }
        ]
    # print(  json.dumps(msgs, indent=4) )

    completion = clnt.chat.completions.create(
        model=model,
        response_format= respFmt ,
        messages=msgs,
        max_completion_tokens=maxCompletionTokens,    # Limit for response tokens
        temperature=celsius,
        n=1,                # Number of completions to generate
        stop=None,          # Specify stop sequences if needed
        seed=seed,
    )

    txt = completion.choices[0].message.content

    try:
        jsonResult = json.loads(txt)
        res = {
                "model":      model,
                "ident":      ident,
                "jsonResult": jsonResult,
                "error"     : "",
            }
    except json.JSONDecodeError as exc:
        res = {
                "model":      model,
                "ident":      ident,
                "jsonResult": resDummy(),
                "error"     : f"Failed to parse GPT output as JSON \n{exc}",
            }
    except Exception as exc:
        res = {
                "model":      model,
                "ident":      ident,
                "jsonResult": resDummy(),
                "error"     : f"Common exc parsing GPT output as JSON \n{exc}",
            }

    logTimeSince(f"\tchat completion stop  {ident} - len {len(txt)} chars")


    ts = f"-{datetime.now():%m-%d-%H-%M}"
    saveJson(res, f"chat-completion-{model}-{hsh}-{ts}",  subset=get("dataset"))
    saveJson(res, f"chat-completion-{model}-{hsh}", subset=get("dataset"))

    return res    



