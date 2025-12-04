# Nayay Backend - LangChain + Gemini API Integration

A modular, scalable backend system that integrates LangChain with Google Gemini API and online search capabilities for AI-powered applications.

## 🚀 Features

- **Conversational AI**: Chat with Google Gemini using LangChain pipeline
- **Online Search**: Real-time web search with DuckDuckGo integration
- **Memory Management**: Conversation history and context retention
- **Modular Design**: Easy to extend with new features
- **REST API**: Clean JSON API endpoints for frontend integration
- **Production Ready**: Comprehensive logging, error handling, and configuration management

## 📁 Project Structure

```
backend/
├── main.py                 # Flask application entry point
├── routes.py              # API route definitions
├── config.py              # Configuration management
├── gemini_chain.py        # LangChain + Gemini integration
├── search_tool.py         # Online search functionality
├── document_loader.py     # Document processing (future features)
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
└── README.md             # This documentation
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup

1. **Clone and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

The server will start on `http://localhost:5000` by default.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | - |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.5-flash` |
| `GEMINI_TEMPERATURE` | Model creativity (0-1) | `0.7` |
| `GEMINI_MAX_TOKENS` | Maximum response tokens | `8192` |
| `DEBUG` | Enable debug mode | `false` |
| `PORT` | Server port | `5000` |
| `CONVERSATION_MEMORY_SIZE` | Chat history limit | `10` |

## 📡 API Endpoints

### Chat Endpoints

#### `POST /api/chat`
Send a message to the AI assistant.

**Request:**
```json
{
  "query": "What is the capital of France?",
  "session_id": "user123",
  "context": "Optional additional context"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "The capital of France is Paris...",
    "session_id": "user123",
    "model": "gemini-1.5-flash",
    "timestamp": "2024-01-15T10:30:00",
    "chat_history_length": 2
  }
}
```

#### `POST /api/chat/memory`
Manage conversation memory.

**Request:**
```json
{
  "action": "clear",  // or "get_history"
  "session_id": "user123"
}
```

### Search Endpoints

#### `POST /api/search`
Search the web and get AI-synthesized results.

**Request:**
```json
{
  "query": "latest AI developments 2024",
  "search_type": "synthesized",  // or "simple"
  "max_results": 5,
  "context": "Optional context"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "latest AI developments 2024",
    "search_response": "Based on recent developments...",
    "model": "gemini-1.5-flash",
    "timestamp": "2024-01-15T10:30:00",
    "search_used": true
  }
}
```

#### `POST /api/search/multi`
Perform multiple searches and synthesize results.

**Request:**
```json
{
  "queries": [
    "AI developments 2024",
    "machine learning trends",
    "natural language processing advances"
  ],
  "synthesize": true
}
```

### Status Endpoints

#### `GET /health`
Health check endpoint.

#### `GET /api/status`
Service status information.

## 🔄 Usage Examples

### Basic Chat
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain quantum computing in simple terms"}'
```

### Web Search
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Python best practices 2024", "search_type": "synthesized"}'
```

### Python Client Example
```python
import requests

# Chat example
chat_response = requests.post('http://localhost:5000/api/chat', json={
    'query': 'What is machine learning?',
    'session_id': 'user123'
})

print(chat_response.json())

# Search example
search_response = requests.post('http://localhost:5000/api/search', json={
    'query': 'renewable energy trends',
    'search_type': 'synthesized'
})

print(search_response.json())
```

## 🏗️ Architecture

### Core Components

1. **Flask Application** (`main.py`): Entry point and server configuration
2. **Configuration** (`config.py`): Environment variable management
3. **Gemini Chain** (`gemini_chain.py`): LangChain + Gemini integration
4. **Search Tool** (`search_tool.py`): Online search capabilities
5. **Routes** (`routes.py`): API endpoint definitions
6. **Document Loader** (`document_loader.py`): Future document processing

### Data Flow

```
Frontend Request → Flask Routes → LangChain Pipeline → Gemini API → Response
                                      ↓
                              Online Search Tools → Web Results → Synthesis
```

## 🔮 Future Expansion

The modular design allows for easy addition of new features:

- **Document Summarization** (`/summarize`): PDF and text document processing
- **Deepfake Detection** (`/analyze`): AI-powered content verification
- **Custom Tools**: Add specialized LangChain tools
- **Database Integration**: Persistent conversation storage
- **Authentication**: User management and API keys
- **Rate Limiting**: API usage controls

## 🚨 Error Handling

The API provides comprehensive error handling:

- **Validation Errors**: Invalid request format (400)
- **Authentication Errors**: Missing or invalid API keys (401)
- **Rate Limiting**: Too many requests (429)
- **Server Errors**: Internal processing errors (500)

## 📝 Logging

The application includes comprehensive logging:

- **File Logging**: All logs saved to `backend.log`
- **Console Logging**: Real-time development feedback
- **Structured Logging**: JSON format for production monitoring

## 🧪 Testing

Run tests with:
```bash
pytest tests/
```

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables:**
   ```bash
   export DEBUG=false
   export SECRET_KEY=your_production_secret
   ```

2. **Use a production WSGI server:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 main:app
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the logs in `backend.log`
2. Verify your API keys in `.env`
3. Ensure all dependencies are installed
4. Check the health endpoint: `GET /health`

## 🔗 Related Links

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [DuckDuckGo Search API](https://pypi.org/project/duckduckgo-search/)
