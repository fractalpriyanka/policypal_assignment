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


# ---------------- STATIC RECOMMENDED QUESTIONS ----------------

RECOMMENDED_QUESTIONS = [
    "What is the conflict of interest policy?",
    "Who is responsible for compliance?",
    "What actions are prohibited under this policy?",
    "How are policy violations handled?",
    "What is the data privacy policy?",
    "When does this policy apply?",
]


# ---------------- PIPELINE LOADER ----------------

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


# ---------------- FOLLOW-UP QUESTION GENERATOR ----------------

def generate_followups(last_question):

    templates = [
        "Who is responsible for this?",
        "How is this implemented?",
        "What happens if this is violated?",
        "When does this apply?",
        "Are there any exceptions?",
    ]

    return templates


# ---------------- SESSION STATE ----------------

if "rag" not in st.session_state:
    with st.spinner("🚀 Loading RAG pipeline..."):
        st.session_state.rag = load_rag()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "prefilled_query" not in st.session_state:
    st.session_state.prefilled_query = ""


# ---------------- STATIC RECOMMENDED UI ----------------

st.markdown("### 💡 Try These Questions")

cols = st.columns(3)

for i, q in enumerate(RECOMMENDED_QUESTIONS):
    if cols[i % 3].button(q):
        st.session_state.prefilled_query = q
        st.experimental_rerun()


# ---------------- USER INPUT ----------------

query = st.text_input(
    "Ask a question from the document:",
    value=st.session_state.prefilled_query,
    placeholder="Example: What is the conflict of interest policy?"
)


# ---------------- QUERY PROCESSING ----------------

if st.button("Ask"):

    if not query.strip():
        st.warning("⚠️ Query cannot be empty")

    else:

        with st.spinner("🔍 Retrieving and generating answer..."):

            try:

                # Use last 5 messages for context
                history = st.session_state.chat_history[-5:]

                final_query = rephrase_query(query, history)

                answer, sources = st.session_state.rag.ask(final_query)

                # Fallback
                if not answer or len(answer.strip()) == 0:
                    answer = "This information isn't in the document."
                    sources = []

                followups = generate_followups(query)

                st.session_state.chat_history.append(
                    {
                        "question": query,
                        "answer": answer,
                        "sources": sources,
                        "time": datetime.now(),
                        "followups": followups
                    }
                )

                st.session_state.prefilled_query = ""

            except Exception as e:

                error_msg = str(e).lower()

                if "quota" in error_msg or "limit" in error_msg:
                    st.error("🚫 API limit reached. Please try again later.")

                elif "permission" in error_msg or "empty" in error_msg:
                    st.error("📄 Document is empty or access is restricted.")

                else:
                    st.error("❌ Internal server error")
                    st.exception(e)


# ---------------- CHAT DISPLAY ----------------

for chat in reversed(st.session_state.chat_history):

    st.markdown("### 🧑 User")
    st.write(chat["question"])

    st.markdown("### 🤖 Assistant")
    st.write(chat["answer"])

    # -------- SOURCES --------

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

    # -------- FOLLOW-UP SUGGESTIONS --------

    if "followups" in chat:

        st.markdown("#### 🔁 Related Questions")

        cols = st.columns(3)

        for i, fq in enumerate(chat["followups"]):

            if cols[i % 3].button(
                fq,
                key=f"{chat['time']}_{i}"
            ):
                st.session_state.prefilled_query = fq
                st.experimental_rerun()

    st.divider()


# ---------------- FOOTER ----------------

st.markdown("---")
st.caption("Powered by FAISS + Sentence Transformers + Gemini")
