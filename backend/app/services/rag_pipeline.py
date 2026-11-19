import uuid
from app.database.chroma import collection
from app.services.embedding import embed_texts, embed_query

async def index_document(document_id: str, user_id: str, filename: str, chunks: list[dict]):
    if not chunks:
        return 0
    ids = [f"{document_id}:{i}:{uuid.uuid4()}" for i in range(len(chunks))]
    embeddings = embed_texts([c["content"] for c in chunks])
    metadatas = [{"document_id": document_id, "user_id": user_id, "filename": filename,
                  "page_number": c["page_number"]} for c in chunks]
    collection.add(ids=ids, embeddings=embeddings, documents=[c["content"] for c in chunks], metadatas=metadatas)
    return len(chunks)

def retrieve(question: str, user_id: str, document_ids: list[str] | None = None, limit: int = 6):
    filters = {"user_id": user_id}
    if document_ids:
        filters = {"$and": [{"user_id": user_id}, {"document_id": {"$in": document_ids}}]}
    result = collection.query(query_embeddings=[embed_query(question)], n_results=limit,
                              where=filters, include=["documents", "metadatas", "distances"])
    sources = []
    if result.get("documents"):
        for content, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
            sources.append({"content": content, "page_number": metadata["page_number"],
                            "filename": metadata["filename"], "document_id": metadata["document_id"],
                            "score": round(max(0, 1 - distance), 4)})
    return sources

def delete_document(document_id: str, user_id: str):
    collection.delete(where={"$and": [{"document_id": document_id}, {"user_id": user_id}]})
