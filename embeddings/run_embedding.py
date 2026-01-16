import json
import yaml
import numpy as np
from embeddings.embedder import EmbeddingModel
from embeddings.vector_store import FAISSStore


def load_config():
    try:
        with open("config/config.yaml") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ config.yaml file not found")
        exit()


def load_chunks(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            print("❌ Chunk file is empty")
            exit()

        return data

    except FileNotFoundError:
        print("❌ Chunk input file not found")
        exit()


def main():

    config = load_config()

    input_path = config["paths"]["chunked_input"]
    index_path = config["paths"]["vector_index"]
    metadata_path = config["paths"]["vector_metadata"]

    model_name = config["embedding"]["model_name"]

    print("📂 Loading chunked data...")
    chunks = load_chunks(input_path)

    # Safe text extraction
    texts = []

    for chunk in chunks:
        if "text" in chunk and chunk["text"].strip():
            texts.append(chunk["text"])

    if not texts:
        print("❌ No valid text found for embedding")
        return

    try:
        embedder = EmbeddingModel(model_name)
        embeddings = embedder.generate_embeddings(texts)
    except Exception as e:
        print("❌ Embedding generation failed")
        print(e)
        return

    embeddings = np.array(embeddings).astype("float32")

    print("📦 Creating FAISS index...")
    store = FAISSStore(embeddings.shape[1])
    store.add_embeddings(embeddings)

    try:
        print("💾 Saving FAISS index...")
        store.save(index_path)

        print("💾 Saving metadata...")
        store.save_metadata(chunks, metadata_path)

    except Exception as e:
        print("❌ Failed while saving index or metadata")
        print(e)
        return

    print("\n✅ STEP 3 — EMBEDDING + INDEXING COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
