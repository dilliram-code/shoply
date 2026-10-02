from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from main import answer_user_query, load_knowledge_base

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="ShopEase Support Assistant")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# Plain `def` endpoints run in a worker thread, so the blocking OpenAI and
# Pinecone calls will not freeze the server.
@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty.")
    try:
        return ChatResponse(answer=answer_user_query(question))
    except Exception as exc:  # surface a clean error to the UI
        print(f"[chat error] {exc}")
        raise HTTPException(status_code=500, detail="The assistant could not answer right now.")


# Run this once (or whenever your PDFs change) instead of on every question:
#   curl -X POST http://127.0.0.1:8000/api/ingest
@app.post("/api/ingest")
def ingest() -> dict:
    return {"chunks_loaded": load_knowledge_base()}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
