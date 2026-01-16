import faiss
import numpy as np
import json
import os


class FAISSStore:

    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)

    def add_embeddings(self, embeddings):
        self.index.add(embeddings)

    def save(self, index_path):
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        faiss.write_index(self.index, index_path)

    @staticmethod
    def load(index_path):
        return faiss.read_index(index_path)

    @staticmethod
    def save_metadata(metadata, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    @staticmethod
    def load_metadata(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


# ---------- NEW HELPER ----------

def faiss_exists(index_path):
    return os.path.exists(index_path)