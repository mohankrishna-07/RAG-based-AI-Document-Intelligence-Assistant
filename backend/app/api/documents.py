from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.api.auth import current_user
from app.database.mongodb import db
from app.services.pdf_processor import extract_pages
from app.services.chunking import chunk_pages
from app.services.rag_pipeline import index_document, delete_document

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload")
async def upload(file: UploadFile = File(...), user: dict = Depends(current_user)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(400, "PDF must be smaller than 25 MB")
    import uuid
    document_id = str(uuid.uuid4())
    pages = extract_pages(content)
    chunks = chunk_pages(pages)
    chunk_count = await index_document(document_id, user["id"], file.filename, chunks)
    record = {"_id": document_id, "owner_id": user["id"], "filename": file.filename,
              "size": len(content), "page_count": len(pages), "chunk_count": chunk_count,
              "status": "ready", "created_at": datetime.now(timezone.utc)}
    await db.documents.insert_one(record)
    return {"id": document_id, "filename": file.filename, "page_count": len(pages),
            "chunk_count": chunk_count, "status": "ready"}

@router.get("")
async def list_documents(user: dict = Depends(current_user)):
    records = await db.documents.find({"owner_id": user["id"]}).sort("created_at", -1).to_list(100)
    return [{"id": r["_id"], "filename": r["filename"], "size": r["size"],
             "page_count": r["page_count"], "chunk_count": r["chunk_count"],
             "status": r["status"]} for r in records]

@router.delete("/{document_id}")
async def remove_document(document_id: str, user: dict = Depends(current_user)):
    record = await db.documents.find_one({"_id": document_id, "owner_id": user["id"]})
    if not record:
        raise HTTPException(404, "Document not found")
    delete_document(document_id, user["id"])
    await db.documents.delete_one({"_id": document_id})
    return {"success": True}

@router.post("/{document_id}/summary")
async def summarize(document_id: str, user: dict = Depends(current_user)):
    record = await db.documents.find_one({"_id": document_id, "owner_id": user["id"]})
    if not record:
        raise HTTPException(404, "Document not found")
    from app.services.rag_pipeline import retrieve
    from app.services.llm_service import generate_answer
    sources = retrieve("Provide a concise summary of the main topic, objectives, and conclusions.", user["id"], [document_id])
    answer = await generate_answer("Summarize this document.", sources)
    return {"answer": answer, "sources": sources}
