from fastapi import APIRouter, Request
from fastapi.responses   import Response, HTMLResponse, JSONResponse

router = APIRouter()


@router.get("/completions/sync", response_class=HTMLResponse)
async def chatCompletionSynchroneousH(request: Request):
    print("chatCompletionSynchroneousH dummy")


@router.get("/completions/json", response_class=HTMLResponse)
async def chatCompletionJsonH(request: Request):
    print("chatCompletionJsonH dummy")


@router.get("/completions/jsh", response_class=HTMLResponse)
async def chatCompletionJSH(request: Request):
    print("chatCompletionJSH dummy")
