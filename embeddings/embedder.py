from sentence_transformers import SentenceTransformer


class EmbeddingModel:

    def __init__(self, model_name):
        print("🔄 Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        print("✅ Embedding model loaded")

    def generate_embeddings(self, texts):
        return self.model.encode(texts, show_progress_bar=True)
