import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from rag.rag_pipeline import RAGPipeline


# ---------------- GLOBAL PIPELINE ----------------

rag = None


# ---------------- LIFESPAN (IMPORTANT) ----------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag
    try:
        print("📄 Loading metadata and RAG pipeline...")
        rag = RAGPipeline()
        print("✅ RAG pipeline loaded successfully")
    except Exception as e:
        print("❌ Failed to initialize RAG:", repr(e))
        rag = None

    yield

    print("🛑 Shutting down application...")


# ---------------- APP INIT ----------------
# 🔥 lifespan MUST be passed here

app = FastAPI(
    title="RAG Document Chatbot API",
    lifespan=lifespan
)


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- DATA MODELS ----------------

class Source(BaseModel):
    section_id: str
    title: str
    chunk_id: str


class ChatTurn(BaseModel):
    question: str
    answer: str


class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[ChatTurn]] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    timestamp: datetime


# ---------------- HEALTH ----------------

@app.get("/")
def root():
    return {"status": "RAG API Running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/debug/rag")
def debug_rag():
    return {
        "rag_is_none": rag is None,
        "rag_type": str(type(rag))
    }


# ---------------- QUERY REPHRASING ----------------

def rephrase_query(query: str, history: List[ChatTurn]) -> str:
    if not history:
        return query

    last_turn = history[-1]

    followup_words = {"this", "that", "it", "they", "those", "these"}

    is_followup = any(w in query.lower().split() for w in followup_words)

    # Very short queries are likely follow-ups
    if len(query.split()) <= 5:
        is_followup = True

    if is_followup:
        return (
            f"Previous question: {last_turn.question}. "
            f"Follow-up question: {query}. "
            f"Answer using the policy document."
        )

    return query


# ---------------- MAIN CHAT ENDPOINT ----------------

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if rag is None:
        raise HTTPException(
            status_code=500,
            detail="RAG pipeline not initialized"
        )

    try:
        query = request.query.strip()

        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        history = request.chat_history[-5:] if request.chat_history else []

        final_query = rephrase_query(query, history)

        print("🔍 Final query:", final_query)

        answer, sources = rag.ask(final_query)
        answer, raw_sources = rag.ask(final_query)

        # Convert raw sources to exact metadata (NO "Source 1")
        sources = [
            Source(
                section_id=src.get("section_id", "N/A"),
                title=src.get("title", "Unknown Section"),
                chunk_id=src.get("chunk_id", "N/A")
            )
            for src in raw_sources
        ]

        if not answer or not answer.strip():
            answer = "This information isn't in the document."
            sources = []


        
        return ChatResponse(
            answer=answer,
            sources=sources,
            timestamp=datetime.now()
        )

    except Exception as e:
        error_msg = str(e).lower()
        print("🔥 CHAT ERROR:", repr(e))

        if "quota" in error_msg or "limit" in error_msg:
            return ChatResponse(
                answer="API limit reached. Please try again later.",
                sources=[],
                timestamp=datetime.now()
            )

        if "permission" in error_msg or "empty" in error_msg:
            return ChatResponse(
                answer="Document is empty or access is restricted.",
                sources=[],
                timestamp=datetime.now()
            )

        raise HTTPException(status_code=500, detail=str(e))


# ---------------- LOCAL / HF RUN ----------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
