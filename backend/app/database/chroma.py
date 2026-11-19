import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings

client = chromadb.PersistentClient(
    path=settings.chroma_dir,
    settings=ChromaSettings(anonymized_telemetry=False),
)
collection = client.get_or_create_collection("documents", metadata={"hnsw:space": "cosine"})
