import requests
import os


def extract_doc_id(doc_url):
    return doc_url.split("/d/")[1].split("/")[0]


def fetch_google_doc_html(doc_url, save_path):

    doc_id = extract_doc_id(doc_url)

    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"

    response = requests.get(export_url)

    if response.status_code != 200:
        raise ValueError("Google Doc is not public or link is invalid.")
    
    if len(response.text.strip()) < 50:
        raise ValueError("Document appears to be empty.")

    os.makedirs(save_path, exist_ok=True)

    html_file = os.path.join(save_path, "raw_doc.html")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(response.text)

    print("✅ Raw HTML saved:", html_file)

    return response.text
