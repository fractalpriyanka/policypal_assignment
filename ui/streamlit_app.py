import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from rag.rag_pipeline import RAGPipeline


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="RAG Document Chatbot",
    page_icon="📄",
    layout="wide"
)

st.title("📄 RAG Document Chatbot")
st.caption("Semantic Search + Gemini Answer Generation")

# ---------------- SESSION STATE ----------------

if "rag" not in st.session_state:
    with st.spinner("Loading RAG pipeline..."):
        st.session_state.rag = RAGPipeline()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------- USER INPUT ----------------

query = st.text_input(
    "Ask a question from the document:",
    placeholder="Example: What is the conflict of interest policy?"
)


# ---------------- QUERY PROCESSING ----------------

if st.button("Ask") and query:

    with st.spinner("Retrieving and generating answer..."):

        answer, sources = st.session_state.rag.ask(query)

        st.session_state.chat_history.append(
            {
                "question": query,
                "answer": answer,
                "sources": sources
            }
        )


# ---------------- DISPLAY CHAT ----------------

for chat in reversed(st.session_state.chat_history):

    st.markdown("### 🧑 User")
    st.write(chat["question"])

    st.markdown("### 🤖 Assistant")
    st.write(chat["answer"])

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
