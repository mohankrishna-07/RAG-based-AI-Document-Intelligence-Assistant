from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)

def chunk_pages(pages: list[dict]) -> list[dict]:
    chunks = []
    for page in pages:
        for index, text in enumerate(splitter.split_text(page["text"])):
            chunks.append({"content": text, "page_number": page["page_number"], "chunk_index": index})
    return chunks
