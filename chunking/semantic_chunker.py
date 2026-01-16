import math


def estimate_tokens(text):
    """
    Approx token estimation (works well for English text)
    """
    return int(len(text.split()) * 1.3)


def split_text(text, max_tokens=800, overlap=100):
    """
    Sliding window semantic chunking
    """

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + max_tokens

        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append(chunk_text)

        start = end - overlap

        if start < 0:
            start = 0

    return chunks


def chunk_section(section_data, max_tokens, overlap):
    """
    Chunk single section safely
    """

    full_text = f"{section_data['title']}. {section_data['text']}"

    chunks = split_text(full_text, max_tokens, overlap)

    processed_chunks = []

    for idx, chunk in enumerate(chunks, 1):

        processed_chunks.append({
            "doc_id": section_data.get("doc_id", "employee_handbook_v1"),
            "section_id": section_data["section_id"],
            "chunk_id": f"{section_data['section_id']}_chunk_{idx}",
            "title": section_data["title"],
            "text": chunk,
            "token_count": estimate_tokens(chunk)
        })

    return processed_chunks
