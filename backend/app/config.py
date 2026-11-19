from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    app_name: str = "AI Document Intelligence"
    secret_key: str = "change-this-secret-key"
    access_token_minutes: int = 1440
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "document_intelligence"
    chroma_dir: str = str(BASE_DIR / "data" / "chroma")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

settings = Settings()
