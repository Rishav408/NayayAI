# Quick Setup Guide

## 🚀 Fast Start (5 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy the example file
cp env.example .env

# Edit .env and add your Gemini API key
# Get your key from: https://makersuite.google.com/app/apikey
```

### 3. Start the Server
```bash
# Option 1: Use the startup script (recommended)
python run.py

# Option 2: Direct start
python main.py
```

### 4. Test the Backend
```bash
# In another terminal, run the test suite
python test_backend.py
```

## 🔧 Quick API Test

Once running, test with curl:

```bash
# Health check
curl http://localhost:5000/health

# Chat test
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?"}'

# Search test
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "search_type": "simple"}'
```

## 📁 File Overview

- `main.py` - Flask app entry point
- `run.py` - Easy startup script
- `config.py` - Environment configuration
- `routes.py` - API endpoints
- `gemini_chain.py` - LangChain + Gemini integration
- `search_tool.py` - Online search functionality
- `document_loader.py` - Future document processing
- `test_backend.py` - Test suite
- `requirements.txt` - Dependencies
- `env.example` - Environment template

## 🆘 Troubleshooting

**Server won't start?**
- Check if port 5000 is available
- Verify your `.env` file has `GEMINI_API_KEY`
- Run `pip install -r requirements.txt`

**API calls failing?**
- Check server logs in `backend.log`
- Verify API key is valid
- Test with `/health` endpoint first

**Import errors?**
- Make sure you're in the `backend/` directory
- Activate virtual environment if using one
- Install all dependencies from `requirements.txt`
