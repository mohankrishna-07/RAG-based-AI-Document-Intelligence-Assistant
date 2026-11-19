import fitz

def extract_pages(content: bytes) -> list[dict]:
    pages = []
    with fitz.open(stream=content, filetype="pdf") as pdf:
        for number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"page_number": number, "text": text})
    return pages
