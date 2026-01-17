import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from rag.rag_pipeline import RAGPipeline
from datetime import datetime

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="RAG Document Chatbot",
    page_icon="📄",
    layout="wide"
)

st.title("📄 RAG Document Chatbot")
st.caption("Semantic Search + Gemini Answer Generation")

# ---------------- PIPELINE LOADER (FASTAPI LIFESPAN EQUIVALENT) ----------------

@st.cache_resource(show_spinner=False)
def load_rag():
    return RAGPipeline()

# ---------------- QUERY REPHRASING ----------------

def rephrase_query(query, history):

    if not history:
        return query

    last_turn = history[-1]

    followup_words = ["this", "that", "it", "they", "those", "these"]

    is_followup = any(w in query.lower().split() for w in followup_words)

    if len(query.split()) <= 5:
        is_followup = True

    if is_followup:

        rewritten = (
            f"Previous question: {last_turn['question']}. "
            f"Follow-up question: {query}. "
            f"Answer using the policy document."
        )

        return rewritten

    return query


# ---------------- SESSION STATE ----------------

if "rag" not in st.session_state:
    with st.spinner("🚀 Loading RAG pipeline..."):
        st.session_state.rag = load_rag()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------- USER INPUT ----------------

query = st.text_input(
    "Ask a question from the document:",
    placeholder="Example: What is the conflict of interest policy?"
)


# ---------------- QUERY PROCESSING ----------------

if st.button("Ask"):

    if not query.strip():
        st.warning("⚠️ Query cannot be empty")
    else:

        with st.spinner("🔍 Retrieving and generating answer..."):

            try:

                # Keep last 5 turns (like API)
                history = st.session_state.chat_history[-5:]

                final_query = rephrase_query(query, history)

                answer, sources = st.session_state.rag.ask(final_query)

                # Fallback handling
                if not answer or len(answer.strip()) == 0:
                    answer = "This information isn't in the document."
                    sources = []

                st.session_state.chat_history.append(
                    {
                        "question": query,
                        "answer": answer,
                        "sources": sources,
                        "time": datetime.now()
                    }
                )

            except Exception as e:

                error_msg = str(e).lower()

                # Quota / token error handling
                if "quota" in error_msg or "limit" in error_msg:
                    st.error("🚫 API limit reached. Please try again later.")

                # Document permission / empty doc
                elif "permission" in error_msg or "empty" in error_msg:
                    st.error("📄 Document is empty or access is restricted.")

                else:
                    st.error("❌ Internal error occurred")
                    st.exception(e)


# ---------------- DISPLAY CHAT ----------------

for chat in reversed(st.session_state.chat_history):

    st.markdown("### 🧑 User")
    st.write(chat["question"])

    st.markdown("### 🤖 Assistant")
    st.write(chat["answer"])

    if chat["sources"]:

        with st.expander("📚 Sources Used"):
            for src in chat["sources"]:
                st.markdown(
                    f"""
                    **Section:** {src['section_id']}  
                    **Title:** {src['title']}  
                    **Chunk ID:** {src['chunk_id']}
                    """
                )

    st.divider()


# ---------------- FOOTER ----------------

st.markdown("---")
st.caption("Powered by FAISS + Sentence Transformers + Gemini")
