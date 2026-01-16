# 📄 RAG-Based Google Doc Chatbot (Gemini + FAISS + Sentence Transformers)

A full-stack **Retrieval-Augmented Generation (RAG)** chatbot that automatically ingests content from a publicly shared Google Document and answers user queries with **accurate, citation-grounded responses**.

The system uses **Sentence Transformers for embeddings**, **FAISS for vector search**, and **Google Gemini (latest SDK)** for answer generation. It includes a **FastAPI backend** and a **web-based HTML/CSS/JS frontend UI**.

---

## 🚀 Features

- ✅ Automatic Google Doc ingestion (no manual uploads)
- ✅ Structured document parsing (section-aware)
- ✅ Semantic chunking with overlap
- ✅ Dense vector embeddings (Sentence Transformers)
- ✅ Fast similarity search using FAISS
- ✅ Gemini-powered grounded answer generation
- ✅ Inline section citations
- ✅ Multi-source scalable architecture
- ✅ FastAPI backend API
- ✅ Web chat UI (HTML/CSS/JS)
- ✅ Config-driven pipeline
- ✅ Production-ready modular design

---

## 🏗 System Architecture

```text
Public Google Doc Link
        ↓
Ingestion Layer
        ↓
Structured Parsing
        ↓
Semantic Chunking
        ↓
Sentence Transformer Embeddings
        ↓
FAISS Vector Index
        ↓
Query Embedding
        ↓
Similarity Search
        ↓
Gemini RAG Generation
        ↓
FastAPI Backend
        ↓
HTML/JS Frontend UI

```

---

## 📂 Project Folder Structure

```text
rag-chatbot/
│
├── config/
│   └── config.yaml
│
├── ingestion/
│   ├── fetch_doc.py
│   ├── normalize.py
│   └── run_ingestion.py
│
├── chunking/
│   ├── semantic_chunker.py
│   └── run_chunking.py
│
├── embeddings/
│   ├── embedder.py
│   ├── vector_store.py
│   └── run_embedding.py
│
├── retrieval/
│   └── retriever.py
│
├── rag/
│   ├── rag_pipeline.py
│
│
├── ui/
│   ├── frontend/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   │
│   └── backend/
│       └── app.py     (FastAPI)
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── vector_db/
│
├── .env
├── requirements.txt
└── README.md

```

---

## ⚙ Tech Stack

| Component             | Technology                               |
| --------------------- | ---------------------------------------- |
| LLM                   | Google Gemini (google-genai SDK)         |
| Embeddings            | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB             | FAISS                                    |
| Backend               | FastAPI                                  |
| Frontend              | HTML, CSS, JavaScript                    |
| Config                | YAML                                     |
| Environment Variables | python-dotenv                            |

---

## 🔑 Prerequisites

- Python 3.9+
- Google Gemini API Key
- Public Google Document link

---

## 🔧 Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
```

### 2️⃣ Install Dependencies

pip install -r requirements.txt

### 3️⃣ Set Environment Variables

Create .env file:

GEMINI_API_KEY=your_api_key_here

### 4️⃣ Update Config File

config/config.yaml

google_doc_url: "PASTE_PUBLIC_GOOGLE_DOC_LINK"

embedding:
model_name: all-MiniLM-L6-v2

retrieval:
top_k: 3

gemini:
model_name: gemini-1.5-flash
temperature: 0.2
max_output_tokens: 1024

### ▶ Pipeline Execution (Step-by-Step)

✅ Step 1 — Document Ingestion
python ingestion/run_ingestion.py
Fetches Google Doc and creates structured document.

✅ Step 2 — Semantic Chunking
python chunking/run_chunking.py
Splits document into embedding-safe chunks.

✅ Step 3 — Embedding + Vector Indexing
python embeddings/run_embedding.py
Creates FAISS vector database.

✅ Step 4 — RAG Testing (CLI)
python rag/test_rag.py

Test question answering in terminal.
