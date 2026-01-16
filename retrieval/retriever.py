import numpy as np
import json

from sentence_transformers import SentenceTransformer
from embeddings.vector_store import FAISSStore, faiss_exists
from embeddings.embedder import EmbeddingModel


class Retriever:

    def __init__(
        self,
        model_name,
        index_path,
        metadata_path,
        chunk_path
    ):

        print("🔄 Loading embedding model...")
        self.model = SentenceTransformer(model_name)

        self.index_path = index_path
        self.metadata_path = metadata_path

        # ---------- LOAD OR BUILD INDEX ----------

        if faiss_exists(index_path):

            print("✅ FAISS index found — loading...")
            self.index = FAISSStore.load(index_path)

            print("✅ Loading metadata...")
            self.metadata = FAISSStore.load_metadata(metadata_path)

        else:

            print("⚠ FAISS not found — building index from chunks...")

            with open(chunk_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)

            texts = [chunk["text"] for chunk in chunks]

            embedder = EmbeddingModel(model_name)

            embeddings = embedder.generate_embeddings(texts)
            embeddings = np.array(embeddings).astype("float32")

            store = FAISSStore(embeddings.shape[1])
            store.add_embeddings(embeddings)

            print("💾 Saving FAISS index...")
            store.save(index_path)

            print("💾 Saving metadata...")
            store.save_metadata(chunks, metadata_path)

            self.index = store.index
            self.metadata = chunks

    # ---------- SEARCH ----------

    def search(self, query, top_k):

        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        results = []

        for idx in indices[0]:
            results.append(self.metadata[idx])

        return results
