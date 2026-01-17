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
# ---------------- LIFESPAN (HF RECOMMENDED) ----------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag
    try:
        print("📄 Loading metadata and RAG pipeline...")
        rag = RAGPipeline()
        print("✅ RAG pipeline loaded successfully")
    except Exception as e:
        print("❌ Failed to initialize RAG:", e)
        rag = None

    yield

    print("🛑 Shutting down application...")
# ---------------- APP INIT ----------------

app = FastAPI(title="RAG Document Chatbot API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change in production
    allow_origin_regex="https://.*\\.hf\\.space",
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


# ---------------- QUERY REPHRASING ----------------

def rephrase_query(query: str, history: List[ChatTurn]):

    if not history:
        return query

    last_turn = history[-1]

    followup_words = ["this", "that", "it", "they", "those", "these"]

    is_followup = any(w in query.lower().split() for w in followup_words)

    # Also treat very short queries as follow-up
    if len(query.split()) <= 5:
        is_followup = True

    if is_followup:

        rewritten = (
            f"Previous question: {last_turn.question}. "
            f"Follow-up question: {query}. "
            f"Answer using the policy document."
        )

        return rewritten

    return query


# ---------------- MAIN CHAT ENDPOINT ----------------

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    try:

        query = request.query.strip()

        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Keep only last 5 turns (like Streamlit session memory)
        history = request.chat_history[-5:] if request.chat_history else []

        # Rephrase query
        final_query = rephrase_query(query, history)

        # Ask RAG
        answer, sources = rag.ask(final_query)

        # Fallback handling (same behavior as Streamlit)
        if not answer or len(answer.strip()) == 0:
            answer = "This information isn't in the document."
            sources = []

        return ChatResponse(
            answer=answer,
            sources=sources,
            timestamp=datetime.now()
        )

    except Exception as e:

        error_msg = str(e).lower()

        # Token limit / quota handling
        if "quota" in error_msg or "limit" in error_msg:
            return ChatResponse(
                answer="API limit reached. Please try again later.",
                sources=[],
                timestamp=datetime.now()
            )

        # Empty document / private doc
        if "permission" in error_msg or "empty" in error_msg:
            return ChatResponse(
                answer="Document is empty or access is restricted. Please check the shared link.",
                sources=[],
                timestamp=datetime.now()
            )

        raise HTTPException(status_code=500, detail=str(e))

# ---------------- HF PORT BINDING ----------------

if __name__ == "__main__":

    import uvicorn

    port = int(os.environ.get("PORT", 7860))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ))

