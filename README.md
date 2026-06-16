# NyayaAI

NyayaAI is an AI-powered Indian legal assistant with a static frontend and a Flask backend. It is designed to help users ask legal questions, keep local conversation history, upload documents for context-aware answers, and optionally use web search to improve responses when current information is needed.

## Overview

This repository contains a two-part application:

1. A static frontend in `frontend/` built with HTML, Tailwind via CDN, and vanilla JavaScript.
2. A Python Flask backend in `backend/` that integrates Gemini, LangChain, document text extraction, and search tooling.

The frontend handles the user experience and stores conversation threads in browser `localStorage`. The backend handles model calls, search decisions, upload processing, and per-session conversation memory.

## Current feature set

- Multi-page frontend: landing, features, about, contact, and chat.
- Chat UI with thread history, new chat, rename, delete, and theme toggle.
- Local conversation persistence in the browser.
- Standard chat with Gemini.
- Context-aware chat using uploaded document text.
- Intelligent chat mode that decides whether search is needed.
- Forced-search mode from the frontend search toggle.
- File upload support for `pdf`, `txt`, and `docx`.
- Health and status endpoints for backend services.

## How it works

### Frontend flow

- The user opens `frontend/chat.html`.
- `frontend/assets/js/main.js` initializes the client-side app.
- The frontend stores threads and messages in `localStorage`.
- When the user sends a message, the frontend chooses one of these API paths:
  - `POST /api/chat` when a document is attached
  - `POST /api/chat/intelligent` for normal chat
  - `POST /api/chat/force-search` when the search toggle is enabled

### Backend flow

- `backend/main.py` creates the Flask app, enables CORS, configures logging, and registers routes.
- `backend/routes.py` validates payloads using Pydantic and dispatches requests.
- `backend/gemini_chain.py` handles normal model-backed chat and session memory.
- `backend/intelligent_search.py` decides whether a message should trigger search.
- `backend/search_tool.py` performs search and fallback logic.
- `backend/document_loader.py` extracts plain text from uploaded files.

## Architecture

### Frontend

- Static HTML pages served separately from Flask.
- Tailwind loaded from CDN.
- Plain JavaScript, no build step.
- Backend URL expected by the frontend:

```text
http://localhost:5000
```

### Backend

- Flask REST API.
- CORS enabled for local frontend integration.
- Gemini via `langchain-google-genai`.
- LangChain-powered chat/search orchestration.
- Lightweight document ingestion for upload context.

## API summary

Base backend URL:

```text
http://localhost:5000
```

Important endpoints:

- `GET /health`
- `POST /api/chat`
- `POST /api/chat/intelligent`
- `POST /api/chat/force-search`
- `POST /api/chat/memory`
- `POST /api/chat/upload`
- `POST /api/search`
- `POST /api/search/multi`
- `GET /api/status`
- `GET /api/search/status`

### Request patterns

`POST /api/chat`

```json
{
  "query": "What is Article 21?",
  "session_id": "thread-id",
  "context": "optional document text"
}
```

`POST /api/chat/memory`

```json
{
  "action": "clear",
  "session_id": "thread-id"
}
```

## Folder structure

```text
NayayAI/
├─ backend/
│  ├─ .env
│  ├─ backend.log
│  ├─ config.py
│  ├─ document_loader.py
│  ├─ gemini_chain.py
│  ├─ intelligent_search.py
│  ├─ main.py
│  ├─ requirements.txt
│  ├─ routes.py
│  ├─ run.py
│  ├─ search_tool.py
│  ├─ README.md
│  ├─ SETUP.md
│  └─ test_*.py
├─ frontend/
│  ├─ index.html
│  ├─ chat.html
│  ├─ features.html
│  ├─ about.html
│  ├─ contact.html
│  └─ assets/
│     └─ js/
│        └─ main.js
├─ Documentation/
├─ test_connection.html
├─ .gitignore
└─ README.md
```

## Configuration

Backend configuration is defined in `backend/config.py` and loaded from environment variables via `python-dotenv`.

Important environment variables:

- `GEMINI_API_KEY`
- `SECRET_KEY`
- `DEBUG`
- `PORT`
- `LANGCHAIN_TRACING_V2`
- `LANGCHAIN_API_KEY`
- `LANGCHAIN_PROJECT`
- `GEMINI_MODEL`
- `GEMINI_TEMPERATURE`
- `GEMINI_MAX_TOKENS`
- `SEARCH_MAX_RESULTS`
- `SEARCH_TIMEOUT`
- `CONVERSATION_MEMORY_SIZE`

Current default values in code include:

- `PORT=5000`
- `GEMINI_MODEL=gemini-1.5-flash`

Your local `backend/.env` can override these values.

## Running the project

Use two terminals.

### 1. Start the backend

```powershell
cd backend
python main.py
```

Health check:

```text
http://127.0.0.1:5000/health
```

Important:

- Opening `http://127.0.0.1:5000/` in a browser will return `404`.
- That is expected because the backend is an API server, not a page server.

### 2. Start the frontend

```powershell
cd frontend
python -m http.server 8000
```

Then open:

```text
http://127.0.0.1:8000/chat.html
```

## Dependency setup

The repository includes `backend/requirements.txt`, but some pinned versions may be stale or may conflict depending on the package index state and your local Python environment.

If a plain requirements install fails, this compatible install set has been used successfully for the current codebase:

```powershell
python -m pip install --user flask==3.0.0 flask-cors==4.0.0 langchain==0.1.0 langchain-google-genai==1.0.1 duckduckgo-search==5.1.0 PyPDF2==3.0.1 python-docx==1.1.0 beautifulsoup4==4.12.2 pydantic==2.5.0 python-dotenv==1.0.0 requests==2.31.0 urllib3==2.1.0 structlog==23.2.0 waitress==2.1.2
```

For cleaner local development, using a dedicated virtual environment is recommended.

## Frontend implementation notes

`frontend/assets/js/main.js` currently contains:

- backend health checking
- API retry logic
- search toggle handling
- local thread management
- document upload integration
- connection test handling
- UI error display

The frontend now uses relative links and relative asset paths, so serving directly from the `frontend/` folder works correctly.

## Backend implementation notes

### `backend/gemini_chain.py`

- Maintains per-session conversation memory.
- Builds the NyayaAI legal-assistant prompt.
- Supports normal chat and context chat.

### `backend/intelligent_search.py`

- Decides whether a query needs external search.
- Routes between model-only and search-enhanced responses.

### `backend/search_tool.py`

- Uses DuckDuckGo as the main search tool.
- Includes fallbacks when search fails.
- Supports search synthesis through the LLM.

### `backend/document_loader.py`

- Supports lightweight extraction from:
  - `.txt`
  - `.pdf`
  - `.docx`
- Rejects legacy `.doc`.
- Caps returned text payload size for chat use.

## Logging and persistence

- Backend logs are written to `backend.log` in the backend working directory.
- Conversation threads are stored in browser `localStorage`.
- Uploaded files are processed through temporary files and converted into text context.

## Known behavior and caveats

- The backend may print a LangChain deprecation warning for `initialize_agent`; it does not block startup.
- The backend root route `/` is not implemented, so `404` there is normal.
- Search quality depends on network availability and third-party services.
- The frontend is static and currently has no bundler or automated build pipeline.
- `backend/requirements.txt` likely needs cleanup for fully reproducible installs.

## Git and ignored files

This repository now includes a `.gitignore` that excludes common local-only files, including:

- `backend/.env`
- virtual environments such as `.venv/`
- `__pycache__/`
- `.log` files
- editor folders such as `.vscode/` and `.idea/`

Things that should be committed:

- source code
- HTML/JS/Python files
- project documentation
- safe example config files such as `.env.example`

Things that should not be committed:

- secrets
- local environments
- runtime caches
- generated logs

## Recommended next improvements

- Clean up `backend/requirements.txt` so it installs reliably without manual adjustments.
- Add a repo-safe `.env.example` if you want a shareable config template in git.
- Add backend tests for chat, search, and upload endpoints.
- Add a frontend smoke test.
- Consider a one-command local startup script for frontend + backend together.

## Usage note

This project is best treated as an educational and experimental legal AI application unless further production hardening is added. Before production use, review:

- API provider terms
- privacy and logging behavior
- legal accuracy requirements
- secrets management
- rate limits and monitoring
