from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.api.auth import current_user
from app.models.schemas import AskRequest
from app.database.mongodb import db
from app.services.rag_pipeline import retrieve
from app.services.llm_service import generate_answer

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/ask")
async def ask(body: AskRequest, user: dict = Depends(current_user)):
    sources = retrieve(body.question, user["id"], body.document_ids)
    answer = await generate_answer(body.question, sources)
    message = {"question": body.question, "answer": answer, "sources": sources,
               "owner_id": user["id"], "created_at": datetime.now(timezone.utc)}
    await db.messages.insert_one(message)
    return {"answer": answer, "sources": sources}

@router.get("/history")
async def history(user: dict = Depends(current_user)):
    records = await db.messages.find({"owner_id": user["id"]}).sort("created_at", -1).limit(50).to_list(50)
    return [{"id": str(r["_id"]), "question": r["question"], "answer": r["answer"],
             "sources": r["sources"]} for r in records]
