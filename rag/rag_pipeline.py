import os
import yaml
from dotenv import load_dotenv
from google import genai

from retrieval.retriever import Retriever


load_dotenv()


class RAGPipeline:

    def __init__(self):

        # Load config
        try:
            with open("config/config.yaml") as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print("❌ Failed to load config.yaml")
            print(e)
            return

        # Gemini Client (NEW SDK)
        try:
            self.client = genai.Client(
                api_key=os.getenv("GEMINI_API_KEY")
            )
        except Exception as e:
            print("❌ Failed to initialize Gemini client")
            print(e)
            return

        self.model_name = self.config["gemini"]["model_name"]

        # Retriever init
        try:
            self.retriever = Retriever(
    model_name=self.config["embedding"]["model_name"],
    index_path=self.config["paths"]["vector_index"],
    metadata_path=self.config["paths"]["vector_metadata"],
    chunk_path=self.config["paths"]["chunked_input"]
)

        except Exception as e:
            print("❌ Failed to initialize Retriever")
            print(e)
            return

        self.top_k = self.config["retrieval"]["top_k"]

    def build_prompt(self, query, contexts):

        context_block = ""

        for i, ctx in enumerate(contexts, 1):

            context_block += (
                f"\n[Source {i}] "
                f"Section {ctx['section_id']} — {ctx['title']}\n"
                f"{ctx['text']}\n"
            )

        prompt = f"""
You are an AI assistant answering questions strictly from the provided policy document.

RULES:
- Use bullet points or numbered lists when listing policies.
- Keep answers concise.
- Use line breaks.
- Highlight headings in bold.
- Always include inline citations like (Section IV.A.1).
- If answer not found say: "This information isn't in the document."

CONTEXT:
{context_block}

QUESTION:
{query}

FORMAT:
Use Markdown formatting.

ANSWER:
"""


        return prompt.strip()

    def ask(self, query):

        if not query.strip():
            print("❌ Empty user query")
            return "", []

        print("🔍 Performing semantic retrieval...")
        retrieved_chunks = self.retriever.search(query, self.top_k)

        if not retrieved_chunks:
            print("⚠ No relevant context found")

        prompt = self.build_prompt(query, retrieved_chunks)

        print("🤖 Sending prompt to Gemini...")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

        except Exception as e:

            error_msg = str(e).lower()

            # ---- Daily free tier / quota exhausted ----
            if "quota" in error_msg or "rate limit" in error_msg or "exceeded" in error_msg:
                print("⚠ Free tier usage limit reached")
                return "Today's free usage limit is over. Please try again later.", retrieved_chunks

            # ---- Token / context length overflow ----
            if "token" in error_msg or "context length" in error_msg:
                print("⚠ Token limit exceeded")
                return "The document context is too large. Please try a shorter question.", retrieved_chunks

            print("❌ Gemini API call failed")
            print(e)
            return "", retrieved_chunks

        return response.text, retrieved_chunks
