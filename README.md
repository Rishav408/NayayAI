NyayaAI
========

An AI-powered legal assistant that combines an elegant, offline-capable frontend with a Flask API backend that orchestrates Gemini + LangChain and smart web search. NyayaAI helps users ask legal questions, attach documents for context-aware answers, and browse sources when the model augments its knowledge with the web.

Contents
- What this project is
- Key features
- Architecture overview
- Data flow / pipeline
- Backend API (endpoints)
- Frontend overview
- Local development setup
- Configuration and environment
- Project structure
- Logging, errors, and troubleshooting
- Roadmap ideas

What this project is
- A two-part app: a static frontend with a rich chat UI, and a Flask backend exposing chat, intelligent chat with web search, document upload, and search APIs.
- Stateless by default on the server; conversation state is stored in the browser (per session/thread) and referenced by a `session_id` when calling the backend.

Key features
- Conversations sidebar with create/rename/delete and persistent local history.
- Multiline, auto-resizing composer with tools (document upload placeholder, mic placeholder, web-search toggle) and keyboard shortcuts.
- Context-aware chat when a document is attached; otherwise, intelligent mode can auto-decide to search the web.
- Optional forced-search mode.
- Health/status endpoints and robust error handling.

Architecture overview
- Frontend (static)
  - Plain HTML + Tailwind (via CDN) + vanilla JS (`frontend/assets/js/main.js`).
  - Stores threads in `localStorage` and emits DOM events to synchronize UI.
  - Talks to backend via CORS to `http://localhost:5000/api`.
- Backend (Flask)
  - Blueprints for chat, search, and upload (`backend/routes.py`).
  - App factory (`backend/main.py`) sets up CORS, logging, health, and error handlers.
  - Integrations are abstracted into helper modules: `gemini_chain.py`, `intelligent_search.py`, `search_tool.py`, and `document_loader.py`.
- Persistence
  - Client-side conversation state: title, messages, timestamps.
  - Server-side memory is logical (per `session_id`), cleared via `/chat/memory`.

Data flow / pipeline
1) User composes a message in the frontend.
2) Frontend decides which endpoint to use:
   - With an attached document: `/api/chat` with `context` text.
   - Search toggle on: `/api/chat/force-search`.
   - Default: `/api/chat/intelligent` (backend decides to search or not).
3) Backend validates payload (Pydantic models), logs request, and routes to the appropriate chain:
   - `gemini_chain.chat(...)` or `chat_with_context(...)` for pure model reasoning.
   - `intelligent_search.intelligent_chat(...)` or `force_search_chat(...)` for search-enhanced answers.
4) Backend responds with a normalized payload: model, timestamp, `search_used`, `search_decision`, sources, etc.
5) Frontend renders the message, stores it to the active thread, and refreshes the sidebar.

Backend API (endpoints)
- Base URL: `http://localhost:5000`
- Health
  - `GET /health` → `{ status: "healthy" }`
- Chat
  - `POST /api/chat` (body: `{ query, session_id?, context? }`) → Model-only response; uses `context` if provided.
  - `POST /api/chat/intelligent` (body: `{ query, session_id? }`) → Backend decides to search; returns `search_used`, `search_decision`, `sources` when applicable.
  - `POST /api/chat/force-search` (body: `{ query, session_id? }`) → Always uses web search.
  - `POST /api/chat/memory` (body: `{ action: 'clear'|'get_history', session_id? }`) → Manage per-session memory.
- Search
  - `POST /api/search` (body: `{ query, search_type?='synthesized'|'simple', max_results?, context? }`)
  - `POST /api/search/multi` (body: `{ queries: string[], synthesize? }`)
- Upload (placeholder but wired)
  - `POST /api/chat/upload` (multipart `file`) → Extracted text metadata for use as chat `context`.

Frontend overview
- Pages under `frontend/` with the main chat at `frontend/chat.html`.
- Core JS at `frontend/assets/js/main.js` implements:
  - `ThemeManager`: dark/light theme persisted to `localStorage`.
  - `APIClient`: centralized HTTP calls with retry.
  - `ConversationManager`: thread CRUD and history rendering.
  - `ChatInterface`: message rendering, composer logic, search toggle, error handling.
  - `FileUploadHandler`: document picker, upload call, and UI chip.

Local development setup
1) Backend
   - Python 3.10+ recommended.
   - Create venv and install dependencies:
     ```bash
     pip install -r backend/requirements.txt
     ```
   - Run:
     ```bash
     python backend/main.py
     ```
   - Health check: open `http://localhost:5000/health`.
2) Frontend
   - Open the HTML files (`frontend/chat.html`, `frontend/index.html`) directly in a browser or serve via a static server.
   - The JS expects the backend at `http://localhost:5000` (config at top of `main.js`).

Configuration and environment
- `backend/config.py` provides `Config` consumed by `main.py`.
- Common envs:
  - `PORT` (default 5000)
  - `DEBUG` ("true" to enable Flask debug)
  - Provider/API keys used by `gemini_chain.py` / search integrations (see those modules for details).

Project structure
```
Nayay/
  backend/
    config.py                # Flask config
    main.py                  # App factory + run
    routes.py                # All API routes
    gemini_chain.py          # Gemini + LangChain orchestration
    intelligent_search.py    # Smart search-or-not decision logic
    search_tool.py           # Web search utilities
    document_loader.py       # File text extraction
    requirements.txt         # Backend deps
    README.md, SETUP.md      # Backend docs
  frontend/
    chat.html                # Chat UI
    index.html, about.html, contact.html, features.html
    assets/js/main.js        # Frontend logic
  backend.log                # Runtime logs
  test_connection.html       # Simple manual test page
```

Logging, errors, and troubleshooting
- Logging
  - `logging` configured in `backend/main.py` streams to console and `backend.log`.
- Error handling
  - JSON error responses for 404 and 500 with messages.
  - Frontend surfaces a friendly, actionable error banner.
- Common issues
  - CORS/connection errors: ensure backend is running on port 5000 and matches `API_BASE_URL` in `main.js`.
  - Uploads fail: verify backend keys/services and file type/size (see `CONFIG.ALLOWED_FILE_TYPES`).
  - Search toggle does nothing: ensure `intelligent_search.py` and `search_tool.py` providers are configured.

Roadmap ideas
- Markdown/LaTeX rendering with copy/quote actions.
- Document comparison and clause finder.
- Per-jurisdiction knowledge controls and confidence indicators.
- Shareable read-only conversation links and PDF/Docx exports.
- Streaming responses, offline-ready PWA, advanced keyboard shortcuts.

License
This project is provided as-is for educational and experimental use. Review third‑party model and search provider licenses/terms before production use.


