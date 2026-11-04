import httpx
from fastapi import FastAPI, HTTPException, Query

from app.agent import ask
from app.models import AskRequest, QualityReport, Work
from app.quality import evaluate
from app.settings import backend
from app.source import search_works

app = FastAPI(title="OpenScience AI Agent (MVP)", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "backend": backend()}


@app.get("/api/search", response_model=list[Work])
async def search(query: str = Query(min_length=1, max_length=200), limit: int = Query(default=5, ge=1, le=20)):
    try:
        return await search_works(query, limit)
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Dostawca danych jest niedostępny lub odpowiedział błędem") from exc


@app.post("/api/quality", response_model=QualityReport)
def quality(work: Work):
    return evaluate(work)


@app.post("/api/ask")
async def agent_answer(request: AskRequest):
    try:
        return await ask(request.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Agent LLM jest obecnie niedostępny") from exc
