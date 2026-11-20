import hashlib
from app.config import settings

DIMENSIONS = 384

def _fallback_embeddings(text: str) -> list[float]:
    vector = [0.0] * DIMENSIONS
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode('utf-8')).digest()
        index = int.from_bytes(digest[:4], 'little') % DIMENSIONS
        sign = 1.0 if digest[4] % 2 else -1.0
        vector[index] += sign
    norm = sum(value * value for value in vector) ** 0.5 or 1.0
    return [value / norm for value in vector]

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not settings.gemini_api_key:
        return [_fallback_embeddings(text) for text in texts]
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.embed_content(
            model='gemini-embedding-001',
            contents=texts,
            config={'output_dimensionality': DIMENSIONS},
        )
        embeddings = [item.values for item in response.embeddings]
        if len(embeddings) == len(texts):
            return embeddings
    except Exception:
        pass
    return [_fallback_embeddings(text) for text in texts]

def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
