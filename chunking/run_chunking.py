import json
import yaml
from chunking.semantic_chunker import chunk_section


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def load_structured_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chunks(chunks, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"✅ Chunked file saved at: {path}")


def main():

    config = load_config()

    input_path = config["paths"]["structured_input"]
    output_path = config["paths"]["chunked_output"]

    max_tokens = config["chunking"]["max_tokens"]
    overlap = config["chunking"]["overlap_tokens"]

    print("📂 Loading structured document...")
    structured_sections = load_structured_data(input_path)

    all_chunks = []

    print("✂ Chunking sections...")

    for section in structured_sections:
        section_chunks = chunk_section(section, max_tokens, overlap)
        all_chunks.extend(section_chunks)

    print(f"📊 Total chunks created: {len(all_chunks)}")

    save_chunks(all_chunks, output_path)

    print("\n✅ STEP 2 CHUNKING COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    
    main()
