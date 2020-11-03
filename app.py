import asyncio
from search import query
from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
async def run(request: Request, input_: str):
    rank_by_score, rank_by_time = await query(input_)
    return templates.TemplateResponse("result.html", {
        "request": request,
        "input_": input_,
        "rank_by_score": rank_by_score,
        "rank_by_time": rank_by_time
    })


@app.get("/api")
async def run(input_: str):
    rank_by_score, rank_by_time = await query(input_)
    return dict({
        "status": 200,
        "rank_by_score": rank_by_score,
        "rank_by_time": rank_by_time
    })
