from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, documents, chat

app = FastAPI(title=settings.app_name, version="1.0.0")
origins = [origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()] or ["*"]
allow_all_origins = "*" in origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/api/health")
async def health():
    from app.database.mongodb import healthcheck
    return {"status": "ok", "mongodb": await healthcheck(), "gemini_configured": bool(settings.gemini_api_key)}
