from fastapi import APIRouter, Request
from fastapi.responses   import Response, HTMLResponse, JSONResponse

import json

router = APIRouter()

from models.embeds import designPrompt, chatCompletion
import  lib.config          as cfg


def addPreflightCORS():
    rsp = Response()
    rsp.headers["Access-Control-Allow-Origin"]  = "*"
    rsp.headers["Access-Control-Allow-Headers"] = "*"
    rsp.headers["Access-Control-Allow-Methods"] = "*"
    return rsp

def addActualCORS(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    return response




@router.get("/completions/sync", response_class=HTMLResponse)
async def chatCompletionSynchroneousH(request: Request):
    print("chatCompletionSynchroneousH dummy")



@router.get("/completions/jsh", response_class=HTMLResponse)
async def chatCompletionJSH(request: Request):
    print("chatCompletionJSH dummy")



# options
@router.options("/completions/json", response_class=HTMLResponse)
async def chatCompletionJsonHOptions(request: Request):
    return addPreflightCORS()


@router.post("/completions/json", response_class=JSONResponse)
async def chatCompletionJsonHPost(request: Request):

    kvGet = dict(request.query_params)
    kvPst = await request.form()
    kvPst = dict(kvPst) # after async complete

    model  =  ""
    role   =  ""
    prompt =  ""

    try:
        jsn = await request.json()

        if "model" in jsn:
            model =  jsn["model"].strip()

        if "role" in jsn:
            role   =  jsn["role"]

        if "prompt" in jsn:
            prompt =  jsn["prompt"]


    except Exception as exc:
        print(f"request body was not JSON - probably POST")

        if "model" in kvPst:
            model =  kvPst["model"].strip()

        beliefStatement          =  ""
        if "belief-statement" in kvPst:
            beliefStatement =  kvPst["belief-statement"]

        speech          =  ""
        if "speech" in kvPst:
            speech =  kvPst["speech"]

        prompt, _, _ = designPrompt(beliefStatement, speech)


    if model == "":
        models = cfg.get("modelNamesChatCompletion")
        model =  models[0]



    if len(prompt) < 5:
        raise Exception(f"error: too short {prompt}")


    result = chatCompletion(model, prompt, role)
    rsp = Response(
        json.dumps(result, indent=4),
        mimetype='application/json',
    )
    return addActualCORS(rsp)



