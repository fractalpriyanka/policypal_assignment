from bs4 import BeautifulSoup
import re


def clean_text(text):
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_section_heading(text):
    """
    Matches:
    I. Welcome
    A. Policy
    1. Hiring Policy
    a. Equal Employment Policy
    """
    pattern = r"^([IVX]+|[A-Z]|\d+|[a-z])\.\s+.+"
    return re.match(pattern, text)


def parse_html_to_structured(html):

    soup = BeautifulSoup(html, "lxml")
    body = soup.body

    records = []

    # Hierarchy tracker
    hierarchy = {
        "roman": "",
        "alpha": "",
        "num": "",
        "sub": ""
    }

    current_section_id = ""
    current_title = ""
    buffer = []

    toc_skipped = False

    elements = body.find_all(["p", "div", "hr"])

    i = 0

    while i < len(elements):

        el = elements[i]

        # Ignore page break tags now
        if el.name == "hr":
            i += 1
            continue

        text = clean_text(el.get_text())

        if not text:
            i += 1
            continue

        # Skip Table of Contents
        if not toc_skipped:
            if re.match(r"^I\.\s+Welcome", text):
                toc_skipped = True
            else:
                i += 1
                continue

        # Fix broken headings
        # Example:
        # 2.
        # Hiring Policy
        if re.match(r"^(\d+|[A-Za-z]|[IVX]+)\.$", text):
            next_text = clean_text(elements[i + 1].get_text())
            text = text + " " + next_text
            i += 1

        # Detect section heading
        if is_section_heading(text):

            # Save previous section block
            if buffer:
                records.append({
                    "section_id": current_section_id,
                    "title": current_title,
                    "text": " ".join(buffer).strip()
                })
                buffer = []

            prefix, title = text.split(".", 1)
            prefix = prefix.strip()
            title = title.strip()

            # Update hierarchy stack
            if prefix.isupper() and len(prefix) > 1:
                hierarchy["roman"] = prefix
                hierarchy["alpha"] = hierarchy["num"] = hierarchy["sub"] = ""

            elif prefix.isupper():
                hierarchy["alpha"] = prefix
                hierarchy["num"] = hierarchy["sub"] = ""

            elif prefix.isdigit():
                hierarchy["num"] = prefix
                hierarchy["sub"] = ""

            else:
                hierarchy["sub"] = prefix

            current_section_id = ".".join([v for v in hierarchy.values() if v])
            current_title = title

        else:
            buffer.append(text)

        i += 1

    # Save final section
    if buffer:
        records.append({
            "section_id": current_section_id,
            "title": current_title,
            "text": " ".join(buffer).strip()
        })

    return records
