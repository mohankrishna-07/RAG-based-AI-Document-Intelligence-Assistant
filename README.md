# AI Document Intelligence Assistant

A full-stack RAG application for PDF search and grounded AI chat.

## Stack

- React 19 and Vite
- FastAPI
- MongoDB
- ChromaDB
- PyMuPDF
- Sentence Transformers
- Google Gemini
- JWT authentication

## Required setup

1. Install MongoDB locally or provide an Atlas connection string.
2. Copy `backend/.env.example` to `backend/.env` if needed.
3. Add `GEMINI_API_KEY` to `backend/.env` for generated answers.
4. Change `SECRET_KEY` to a random value.

A Gemini key is optional for startup. Without it, the application returns retrieved PDF context instead of a generated answer.

## Start the application

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Backend:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open `http://localhost:5173`.

## API documentation

Open `http://localhost:8000/docs` for the FastAPI Swagger interface.
