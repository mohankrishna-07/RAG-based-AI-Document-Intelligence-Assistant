from sentence_transformers import SentenceTransformer
from app.config import settings

model = SentenceTransformer(settings.embedding_model)

def embed_texts(texts: list[str]) -> list[list[float]]:
    return model.encode(texts, normalize_embeddings=True).tolist()

def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
