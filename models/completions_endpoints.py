import json


from fastapi             import APIRouter, Request
from fastapi.responses   import Response, HTMLResponse, JSONResponse
from fastapi             import Depends

from sqlalchemy.orm import Session

router = APIRouter()


from    models.jinja import templates
import  lib.config          as cfg
from    models.db5 import get_db

from    models.embeds import designPrompt, chatCompletion


def addPreflightCORS():
    rsp = Response()
    rsp.headers["Access-Control-Allow-Origin"]  = "*"
    rsp.headers["Access-Control-Allow-Headers"] = "*"
    rsp.headers["Access-Control-Allow-Methods"] = "*"
    return rsp

def addActualCORS(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    return response






async def extractParams(request: Request):

    if False:
        # prevents request.json() below
        kvGet = dict(request.query_params)
        kvPst = await request.form()
        kvPst = dict(kvPst) # after async complete


    beliefStatement =  ""
    speech          =  ""

    model  =  ""
    role   =  ""
    prompt =  ""


    try:
        jsn = await request.json()

        if "model" in jsn:
            model  =  jsn["model"].strip()

        if "role" in jsn:
            role   =  jsn["role"]

        if "prompt" in jsn:
            prompt = jsn["prompt"]


    except Exception as exc:
        print(f"\trequest body was not JSON - probably POST {request.url=}")
        print(f"\t{exc=}")

        kvPst = await request.form()
        kvPst = dict(kvPst) # after async complete


        if "model" in kvPst:
            model =  kvPst["model"].strip()

        if "belief-statement" in kvPst:
            beliefStatement =  kvPst["belief-statement"]

        if "speech" in kvPst:
            speech =  kvPst["speech"]

        # overriding role
        prompt, role, err = designPrompt(beliefStatement, speech)
        if err != "":
            raise Exception(f"error designing prompt: {err} \n {beliefStatement=} {speech=} ")


    if model == "":
        models = cfg.get("modelNamesChatCompletion")
        model =  models[0]


    if len(prompt) < 5:
        raise Exception(f"prompt too short {prompt}")


    return model, prompt, role, beliefStatement, speech





async def chatCompletionSynchroneousH(request: Request, db: Session):

    _, prompt, role, beliefStatement, speech = await extractParams(request)

    results = [] # responses

    listSeeds = [100,101,102]
    listSeeds = [100] # seeds are only BETA - output should be mostly *deterministic*
    models=cfg.get("modelNamesChatCompletion")

    # sequential - generator stuff breaks down in fastapi
    for idx1, model in enumerate(models):
        for idx2, seed in enumerate(listSeeds):
            res = chatCompletion(db, model, prompt, role, seed)
            results.append(res)


    return templates.TemplateResponse(
        "main.html",
        {
            "request":     request,
            "HTMLTitle":   "Ask ChatGPT",
            "contentTpl":  "llm-answer-sync",
            "beliefStatement":    beliefStatement,
            "speech":             speech,
            "prompt":             prompt,
            "results":            results,
        },
    )



# we collect all responses and render them at once
@router.get( "/completions/sync", response_class=HTMLResponse)
async def chatCompletionSynchroneousHGet(request: Request, db: Session = Depends(get_db)):
    return await chatCompletionSynchroneousH(request, db)

@router.post("/completions/sync", response_class=HTMLResponse)
async def chatCompletionSynchroneousHPost(request: Request, db: Session = Depends(get_db)):
    return await chatCompletionSynchroneousH(request, db)




# options
@router.options("/completions/json", response_class=HTMLResponse)
async def chatCompletionJsonHOptions(request: Request):
    return addPreflightCORS()


@router.post("/completions/json", response_class=JSONResponse)
async def chatCompletionJsonHPost(request: Request, db: Session = Depends(get_db)):

    model, prompt, role, _ , _ = await extractParams(request)

    result = chatCompletion(db, model, prompt, role)
    rsp = Response(
        json.dumps(result, indent=4),
        headers={
            "Content-Type": "application/json"                 
        },
    )
    return addActualCORS(rsp)




async def chatCompletionAsyncH(request: Request, useSvelte):

    _, prompt, role, beliefStatement, speech = await extractParams(request)

    return templates.TemplateResponse(
        "main.html",
        {
            "request":          request,
            "HTMLTitle":        "Ask ChatGPT",
            "contentTpl":       "llm-answer-js",
            "urlEndpoint":      request.url_for("chatCompletionJsonHPost"),
            "beliefStatement":  beliefStatement,
            "speech":           speech,
            "prompt":           prompt,
            "role":             role,
        },
    )



# returns HTML - first part of the page
#   makes JS requests
#   renders JSON responses
@router.get( "/completions/async-javascript", response_class=HTMLResponse)
async def chatCompletionAsyncHGet(request: Request):
    return await chatCompletionAsyncH(request)

@router.post("/completions/async-javascript", response_class=HTMLResponse)
async def chatCompletionAsyncHPost(request: Request, useSvelte: bool = False):
    return await chatCompletionAsyncH(request, useSvelte)



