# RAG-based AI Document Intelligence Assistant

A full-stack RAG application for secure PDF search and citation-based AI chat.

## Stack

- React 19 and Vite
- Tailwind-style custom CSS
- Python and FastAPI
- MongoDB Atlas
- ChromaDB
- PyMuPDF
- Sentence Transformers
- LangChain text splitters
- Google Gemini
- JWT authentication

## Architecture

React communicates with FastAPI through REST APIs. FastAPI validates uploads and authentication, extracts PDF text, generates embeddings, stores vectors in ChromaDB, stores application records in MongoDB, retrieves relevant PDF chunks, and sends grounded context to Gemini.

## Setup

```powershell
cd frontend
npm install
npm run dev
```

```powershell
cd backend
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:5173` and configure MongoDB Atlas plus the Gemini API key in `backend/.env`.

## API Documentation

Open `http://127.0.0.1:8000/docs` after starting FastAPI.

## Main Features

- JWT registration and login
- PDF upload and deletion
- Page-level text extraction
- Overlapping text chunking
- Semantic vector search
- User-isolated document retrieval
- Citation-based Gemini answers
- Document summaries
- MongoDB chat history
