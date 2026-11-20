import asyncio
from app.config import settings

async def generate_answer(question: str, sources: list[dict]) -> str:
    preview = "\n\n".join(
        f"Source: {s['filename']} — Page {s['page_number']}\n{s['content'][:700]}"
        for s in sources[:4]
    )
    if not sources:
        return "No relevant document context was found."
    if not settings.gemini_api_key:
        return "Gemini API key is not configured. Retrieved relevant context:\n\n" + preview

    try:
        from google import genai
        context = "\n\n".join(
            f"[Source {i + 1}: {s['filename']} | Page {s['page_number']}]\n{s['content']}"
            for i, s in enumerate(sources[:8])
        )
        prompt = (
            "You are answering questions from a PDF knowledge base. "
            "Use only the supplied sources. Read all sources carefully. "
            "Answer directly and accurately, distinguish facts from interpretations, "
            "and cite the source number and page for every substantive claim. "
            "If the sources do not contain enough evidence, explicitly say that the PDF does not provide the answer. "
            "Do not invent filenames, page numbers, or facts.\n\n"
            f"Sources:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )
        client = genai.Client(api_key=settings.gemini_api_key)

        models_to_try = [settings.gemini_model, 'gemini-2.5-flash']
        for model_name in dict.fromkeys(models_to_try):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=model_name,
                        contents=prompt,
                    ),
                    timeout=20,
                )
                if getattr(response, "text", None):
                    return response.text
            except Exception:
                continue

        return "Gemini is temporarily busy. Relevant PDF context:\n\n" + preview
    except Exception:
        return "Gemini is temporarily unavailable. Relevant PDF context:\n\n" + preview
