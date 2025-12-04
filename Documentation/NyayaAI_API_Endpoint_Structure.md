# NyayaAI API Endpoint Structure

## Figure 5: API Endpoint Structure
*Comprehensive diagram of RESTful API endpoints and their relationships*

```mermaid
graph TB
    %% API Gateway
    subgraph "🌐 API Gateway (Flask Application)"
        GATEWAY[🔌 Flask API Gateway<br/>Port: 5000<br/>CORS Enabled]
        GATEWAY --> |"Blueprint Routing"| BLUEPRINTS[📋 Blueprint System]
    end
    
    %% Blueprint System
    subgraph "📋 Blueprint System"
        BLUEPRINTS --> CHAT_BP[📝 Chat Blueprint<br/>/api/chat*]
        BLUEPRINTS --> SEARCH_BP[🔍 Search Blueprint<br/>/api/search*]
        BLUEPRINTS --> UPLOAD_BP[📁 Upload Blueprint<br/>/api/chat/upload]
        BLUEPRINTS --> HEALTH_BP[💚 Health Blueprint<br/>/health]
    end
    
    %% Chat Endpoints
    subgraph "📝 Chat Endpoints (/api/chat)"
        CHAT_BP --> CHAT_BASIC[💬 POST /api/chat<br/>Basic Chat]
        CHAT_BP --> CHAT_INTEL[🧠 POST /api/chat/intelligent<br/>Intelligent Chat]
        CHAT_BP --> CHAT_FORCE[🔍 POST /api/chat/force-search<br/>Force Search Chat]
        CHAT_BP --> CHAT_MEMORY[💾 POST /api/chat/memory<br/>Memory Management]
        CHAT_BP --> CHAT_STATUS[📊 GET /api/status<br/>Chat Service Status]
    end
    
    %% Search Endpoints
    subgraph "🔍 Search Endpoints (/api/search)"
        SEARCH_BP --> SEARCH_BASIC[🌐 POST /api/search<br/>Web Search]
        SEARCH_BP --> SEARCH_MULTI[📚 POST /api/search/multi<br/>Multi Query Search]
        SEARCH_BP --> SEARCH_STATUS[📊 GET /api/status<br/>Search Service Status]
    end
    
    %% Upload Endpoints
    subgraph "📁 Upload Endpoints (/api/chat)"
        UPLOAD_BP --> UPLOAD_FILE[📄 POST /api/chat/upload<br/>Document Upload]
    end
    
    %% Health Endpoints
    subgraph "💚 Health & Status Endpoints"
        HEALTH_BP --> HEALTH_CHECK[✅ GET /health<br/>Health Check]
        HEALTH_BP --> ERROR_404[❌ GET /*<br/>404 Error Handler]
        HEALTH_BP --> ERROR_500[❌ GET /*<br/>500 Error Handler]
    end
    
    %% Request Models
    subgraph "📋 Request Models (Pydantic)"
        CHAT_REQ[💬 ChatRequest<br/>query: str<br/>session_id?: str<br/>context?: str]
        SEARCH_REQ[🔍 SearchRequest<br/>query: str<br/>max_results?: int<br/>context?: str<br/>search_type?: str]
        MULTI_REQ[📚 MultiSearchRequest<br/>queries: List[str]<br/>synthesize?: bool]
        MEMORY_REQ[💾 MemoryRequest<br/>session_id?: str<br/>action: str]
    end
    
    %% Response Models
    subgraph "📤 Response Models (JSON)"
        SUCCESS_RESP[✅ Success Response<br/>success: true<br/>data: {...}]
        ERROR_RESP[❌ Error Response<br/>success: false<br/>error: string<br/>details?: string]
        HEALTH_RESP[💚 Health Response<br/>status: "healthy"<br/>message: string]
    end
    
    %% Service Integrations
    subgraph "⚙️ Service Integrations"
        GEMINI_SVC[🤖 Gemini Chain Service<br/>gemini_chain.py]
        INTEL_SVC[🧠 Intelligent Search Service<br/>intelligent_search.py]
        SEARCH_SVC[🌐 Search Tool Service<br/>search_tool.py]
        DOC_SVC[📄 Document Loader Service<br/>document_loader.py]
    end
    
    %% Endpoint Details
    subgraph "📝 Chat Endpoint Details"
        CHAT_BASIC --> |"Basic Legal Queries"| GEMINI_SVC
        CHAT_INTEL --> |"Smart Decision Making"| INTEL_SVC
        CHAT_FORCE --> |"Mandatory Web Search"| INTEL_SVC
        CHAT_MEMORY --> |"Session Management"| GEMINI_SVC
        CHAT_STATUS --> |"Service Health"| HEALTH_RESP
    end
    
    %% Search Endpoint Details
    subgraph "🔍 Search Endpoint Details"
        SEARCH_BASIC --> |"Web Search + Synthesis"| SEARCH_SVC
        SEARCH_MULTI --> |"Multiple Queries"| SEARCH_SVC
        SEARCH_STATUS --> |"Search Service Health"| HEALTH_RESP
    end
    
    %% Upload Endpoint Details
    subgraph "📁 Upload Endpoint Details"
        UPLOAD_FILE --> |"Document Processing"| DOC_SVC
        UPLOAD_FILE --> |"Text Extraction"| DOC_SVC
    end
    
    %% Request/Response Flow
    CHAT_REQ --> CHAT_BASIC
    CHAT_REQ --> CHAT_INTEL
    CHAT_REQ --> CHAT_FORCE
    MEMORY_REQ --> CHAT_MEMORY
    
    SEARCH_REQ --> SEARCH_BASIC
    MULTI_REQ --> SEARCH_MULTI
    
    %% Response Generation
    GEMINI_SVC --> SUCCESS_RESP
    INTEL_SVC --> SUCCESS_RESP
    SEARCH_SVC --> SUCCESS_RESP
    DOC_SVC --> SUCCESS_RESP
    
    %% Error Handling
    CHAT_BASIC --> ERROR_RESP
    CHAT_INTEL --> ERROR_RESP
    CHAT_FORCE --> ERROR_RESP
    CHAT_MEMORY --> ERROR_RESP
    SEARCH_BASIC --> ERROR_RESP
    SEARCH_MULTI --> ERROR_RESP
    UPLOAD_FILE --> ERROR_RESP
    
    %% Styling
    classDef gatewayLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef blueprintLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef chatLayer fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef searchLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef uploadLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef healthLayer fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef modelLayer fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    classDef serviceLayer fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef responseLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef errorLayer fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    
    class GATEWAY gatewayLayer
    class BLUEPRINTS,CHAT_BP,SEARCH_BP,UPLOAD_BP,HEALTH_BP blueprintLayer
    class CHAT_BASIC,CHAT_INTEL,CHAT_FORCE,CHAT_MEMORY,CHAT_STATUS chatLayer
    class SEARCH_BASIC,SEARCH_MULTI,SEARCH_STATUS searchLayer
    class UPLOAD_FILE uploadLayer
    class HEALTH_CHECK,ERROR_404,ERROR_500 healthLayer
    class CHAT_REQ,SEARCH_REQ,MULTI_REQ,MEMORY_REQ modelLayer
    class GEMINI_SVC,INTEL_SVC,SEARCH_SVC,DOC_SVC serviceLayer
    class SUCCESS_RESP,HEALTH_RESP responseLayer
    class ERROR_RESP errorLayer
```

## Complete API Endpoint Documentation

### **Base URL**: `http://localhost:5000`

### **1. Chat Endpoints (`/api/chat`)**

#### **💬 POST /api/chat**
**Basic Chat Endpoint**
```json
Request:
{
  "query": "What is Section 420 IPC?",
  "session_id": "user123", // optional
  "context": "Additional context" // optional
}

Response:
{
  "success": true,
  "data": {
    "response": "Section 420 of the Indian Penal Code...",
    "session_id": "user123",
    "model": "gemini-2.5-flash",
    "timestamp": "2025-01-15T10:30:00Z",
    "chat_history_length": 5
  }
}
```

#### **🧠 POST /api/chat/intelligent**
**Intelligent Search Chat Endpoint**
```json
Request:
{
  "query": "Recent Supreme Court judgment on data privacy",
  "session_id": "user123" // optional
}

Response:
{
  "success": true,
  "data": {
    "response": "Based on recent developments...",
    "session_id": "user123",
    "model": "gemini-2.5-flash",
    "timestamp": "2025-01-15T10:30:00Z",
    "search_decision": {
      "should_search": true,
      "reason": "recent legal developments"
    },
    "search_used": true,
    "enhanced": true,
    "sources": [
      {
        "title": "Supreme Court Data Privacy Judgment",
        "url": "https://example.com",
        "description": "Recent judgment details"
      }
    ],
    "search_method": "duckduckgo"
  }
}
```

#### **🔍 POST /api/chat/force-search**
**Force Search Chat Endpoint**
```json
Request:
{
  "query": "Latest amendments to Companies Act",
  "session_id": "user123" // optional
}

Response:
{
  "success": true,
  "data": {
    "response": "Based on current information...",
    "session_id": "user123",
    "model": "gemini-2.5-flash",
    "timestamp": "2025-01-15T10:30:00Z",
    "search_decision": {
      "should_search": true,
      "reason": "user_requested"
    },
    "search_used": true,
    "enhanced": true,
    "sources": [...],
    "search_time": 2.5
  }
}
```

#### **💾 POST /api/chat/memory**
**Memory Management Endpoint**
```json
Request (Clear Memory):
{
  "action": "clear",
  "session_id": "user123" // optional
}

Request (Get History):
{
  "action": "get_history",
  "session_id": "user123" // optional
}

Response (Clear):
{
  "success": true,
  "data": {
    "message": "Conversation memory cleared successfully",
    "session_id": "user123",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}

Response (Get History):
{
  "success": true,
  "data": {
    "conversation_history": [
      {"role": "human", "content": "What is Article 21?"},
      {"role": "ai", "content": "Article 21 of the Constitution..."}
    ],
    "session_id": "user123",
    "message_count": 2,
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

#### **📊 GET /api/status**
**Chat Service Status**
```json
Response:
{
  "success": true,
  "service": "chat",
  "status": "operational",
  "gemini_model": "gemini-2.5-flash"
}
```

### **2. Search Endpoints (`/api/search`)**

#### **🌐 POST /api/search**
**Web Search Endpoint**
```json
Request:
{
  "query": "Indian data protection laws 2024",
  "search_type": "synthesized", // "synthesized" or "simple"
  "max_results": 5, // optional
  "context": "Legal research context" // optional
}

Response:
{
  "success": true,
  "data": {
    "query": "Indian data protection laws 2024",
    "search_response": "Based on current information...",
    "sources": [
      {
        "title": "Digital Personal Data Protection Act 2023",
        "url": "https://example.com",
        "description": "Official act details"
      }
    ],
    "search_method": "duckduckgo",
    "model": "gemini-2.5-flash",
    "timestamp": "2025-01-15T10:30:00Z",
    "search_used": true
  }
}
```

#### **📚 POST /api/search/multi**
**Multi Query Search Endpoint**
```json
Request:
{
  "queries": [
    "Supreme Court judgments 2024",
    "Legal technology trends",
    "Indian law amendments"
  ],
  "synthesize": true // optional
}

Response:
{
  "success": true,
  "data": {
    "queries": ["Supreme Court judgments 2024", "..."],
    "individual_results": [
      {
        "query_index": 1,
        "query": "Supreme Court judgments 2024",
        "result": {...}
      }
    ],
    "synthesis": "Comprehensive analysis of all queries...",
    "timestamp": "2025-01-15T10:30:00Z",
    "multi_query": true
  }
}
```

#### **📊 GET /api/status**
**Search Service Status**
```json
Response:
{
  "success": true,
  "service": "search",
  "status": "operational",
  "search_tool": "DuckDuckGo"
}
```

### **3. Upload Endpoints (`/api/chat`)**

#### **📄 POST /api/chat/upload**
**Document Upload Endpoint**
```json
Request (Multipart Form Data):
Content-Type: multipart/form-data
Body: file (PDF, TXT, DOC, DOCX)

Response:
{
  "success": true,
  "data": {
    "filename": "legal_document.pdf",
    "text": "Extracted text content...",
    "characters": 15420,
    "truncated": false,
    "meta": {
      "pages": 25,
      "file_type": "pdf"
    }
  }
}
```

### **4. Health & Status Endpoints**

#### **✅ GET /health**
**Health Check Endpoint**
```json
Response:
{
  "status": "healthy",
  "message": "Backend is running successfully"
}
```

#### **❌ Error Endpoints**
**404 Not Found**
```json
Response:
{
  "error": "Endpoint not found"
}
```

**500 Internal Server Error**
```json
Response:
{
  "error": "Internal server error"
}
```

## Request/Response Models

### **Pydantic Request Models**

```python
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    context: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = None
    context: Optional[str] = None
    search_type: Optional[str] = "synthesized"

class MultiSearchRequest(BaseModel):
    queries: List[str]
    synthesize: Optional[bool] = True

class MemoryRequest(BaseModel):
    session_id: Optional[str] = None
    action: str  # "clear" or "get_history"
```

### **Response Structure**

```python
# Success Response
{
    "success": True,
    "data": {
        # Endpoint-specific data
    }
}

# Error Response
{
    "success": False,
    "error": "Error message",
    "details": "Additional error details" // optional
}
```

## HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid request format or validation error |
| 404 | Not Found | Endpoint not found |
| 500 | Internal Server Error | Server-side processing error |

## CORS Configuration

```python
CORS(app, 
     origins=["*"],  # Development only
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True)
```

## Rate Limiting & Security

- **Input Validation**: All requests validated with Pydantic models
- **Error Handling**: Comprehensive error catching and logging
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Logging**: All requests logged to `backend.log`
- **Session Management**: Session-based conversation memory

This API structure provides a comprehensive, RESTful interface for the NyayaAI legal assistant platform with proper error handling, validation, and service integration.
