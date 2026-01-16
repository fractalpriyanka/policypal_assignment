import yaml
import json
import os

from ingestion.fetch_doc import fetch_google_doc_html
from ingestion.normalize import parse_html_to_structured


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def save_json(data, path, filename):

    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Structured JSON saved:", file_path)


def main():

    config = load_config()

    doc_url = config["google_doc_url"]
    raw_path = config["paths"]["raw_data"]
    processed_path = config["paths"]["processed_data"]

    print("\n📥 Fetching Google Doc HTML...")
    html = fetch_google_doc_html(doc_url, raw_path)

    print("🧠 Normalizing HTML into structured JSON (section-based)...")
    structured_data = parse_html_to_structured(html)

    print("💾 Saving structured JSON...")
    save_json(structured_data, processed_path, "structured_doc.json")

    print("\n✅ INGESTION + NORMALIZATION COMPLETED")


if __name__ == "__main__":
    main()
