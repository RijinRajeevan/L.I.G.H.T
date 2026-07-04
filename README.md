<div align="center">

# ⚖️ NYAYA-VAANI

### Production-Grade Distributed AI Legal & Civic Assistance Platform

Semantic Legal Search • Multi-Agent AI • LangGraph • ChromaDB • FastAPI • Celery • Redis • React

</div>


## 📖 Overview

**L.I.G.H.T.** (Legal Information & Guidance Help Terminal) is a production-grade, distributed AI assistant tailored for the Indian legal and civic domain. It is designed to act as an accessible terminal where citizens can ask questions in multiple languages (English/Malayalam), analyze legal documents, and understand their rights.

Under the hood, L.I.G.H.T. utilizes an event-driven, multi-container architecture. Heavy ML tasks—like Optical Character Recognition (OCR) and Natural Language Processing (NLP)—run on isolated background workers to ensure the main API remains fast, responsive, and crash-proof.

## ✨ Features

- **Multilingual Support**: Real-time voice and text interaction in English and Malayalam.
- **Semantic Legal Search**: Queries Indian legal codes (IPC, BSA) and case laws using local vector embeddings (ChromaDB) for high accuracy.
- **Agentic Orchestration (LangGraph)**: Stateful, deterministic graph executions map the logic flow to securely process sensitive user queries.
- **Heavy Document Processing (OCR)**: Integrates PaddleOCR within an isolated Celery worker to extract text from physical documents/images, completely mitigating OOM (Out Of Memory) crashes on the main thread.
- **Audio Playback**: Built-in text-to-speech for accessible, screen-free interaction.
- **Premium UI/UX**: Built with React 19, Tailwind CSS v4, and Framer Motion for a stunning, responsive frontend.

## 🏗 Architecture & Data Flow

This system splits responsibilities across a robust distributed network:

1. **FastAPI (Backend API)**: The core entry point, routing asynchronous HTTP traffic and managing WebSockets.
2. **LangGraph State Engine**: Orchestrates security filtering and decision routing with SQLite-backed checkpoint states.
3. **ChromaDB**: Local vector database containing dense embeddings for accurate legal document retrieval.
4. **Celery Worker (OCR)**: A dedicated, concurrency-restricted background worker queue. It loads heavy ML models asynchronously, preventing Uvicorn from crashing under memory pressure.
5. **Redis Queue**: The message broker acting as the nervous system between FastAPI and Celery.

## 💻 Tech Stack

| Category | Technologies |
|---|---|
| **Backend Core** | Python, FastAPI, Uvicorn |
| **AI / Machine Learning** | LangGraph, ChromaDB, Sentence Transformers, PaddleOCR, LiteLLM / Groq |
| **Infrastructure / DevOps** | Celery, Redis, PostgreSQL, Docker |
| **Frontend UI** | React 19, TypeScript, Vite, Tailwind CSS v4, Framer Motion |

## 🚀 Getting Started (Production Deployment)

> ⚠️ **IMPORTANT**: Do not run this application monolithically on a single thread. It is designed as a multi-container deployment. 

### 1. Start Infrastructure (PostgreSQL & Redis)
Ensure you have Docker installed and running on your system.
```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=secret postgres:15
docker run -d -p 6379:6379 redis
```

### 2. Configure Environment & Start Core API
Create a `.env` file in the `backend` directory with your database config and API keys (e.g. `GROQ_API_KEY`).
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or .\venv\Scripts\Activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Start OCR Celery Worker
*Because PaddleOCR is highly demanding, we restrict concurrency and add a memory limit per child process to prevent cascading OOM failures.*
```bash
cd backend
source venv/bin/activate
celery -A app.services.job_queue.celery_app worker --loglevel=info --concurrency=1 --max-memory-per-child=1024000
```

### 4. Start Frontend Client
```bash
cd frontend
npm install
npm run build
npm run dev
```
Navigate to `http://localhost:5173` to access the L.I.G.H.T. interface!

## 📂 Dataset Setup (Optional but Recommended)

For the vector database to function fully, populate the `backend/app/data/` directory with legal CSV/PDF datasets (e.g., from Kaggle).
- `backend/app/data/ipc/`
- `backend/app/data/bsa/`
- `backend/app/data/case_laws/`

The agents will auto-detect these files on the next backend reboot.

## 📜 License
[MIT License](LICENSE)
