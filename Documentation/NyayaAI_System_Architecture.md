# NyayaAI System Architecture Diagram

## Overview
This document contains the complete system architecture diagram for the NyayaAI project, showing all components, data flows, and integrations.

## System Architecture Diagram

```mermaid
graph TB
    %% User Layer
    subgraph "User Interface Layer"
        UI[🌐 Frontend Interface]
        UI --> |"Static HTML/CSS/JS"| UI_COMP[Frontend Components]
        UI_COMP --> |"ThemeManager"| THEME[Dark/Light Theme]
        UI_COMP --> |"APIClient"| API_CLIENT[HTTP Client]
        UI_COMP --> |"ConversationManager"| CONV_MGR[Thread Management]
        UI_COMP --> |"ChatInterface"| CHAT_UI[Message Handling]
        UI_COMP --> |"FileUploadHandler"| FILE_UI[Document Upload]
    end

    %% API Gateway Layer
    subgraph "API Gateway Layer"
        API_GW[🔌 Flask API Gateway<br/>Port: 5000]
        API_GW --> |"CORS Enabled"| CORS[CORS Configuration]
        API_GW --> |"Error Handling"| ERROR_H[Global Error Handlers]
        API_GW --> |"Health Check"| HEALTH[/health endpoint]
    end

    %% Blueprint Layer
    subgraph "Blueprint Layer"
        CHAT_BP[📝 Chat Blueprint<br/>/api/chat*]
        SEARCH_BP[🔍 Search Blueprint<br/>/api/search*]
        UPLOAD_BP[📁 Upload Blueprint<br/>/api/chat/upload]
        
        CHAT_BP --> |"POST /chat"| CHAT_ENDPOINT[Basic Chat]
        CHAT_BP --> |"POST /chat/intelligent"| INTEL_ENDPOINT[Intelligent Chat]
        CHAT_BP --> |"POST /chat/force-search"| FORCE_ENDPOINT[Force Search Chat]
        CHAT_BP --> |"POST /chat/memory"| MEMORY_ENDPOINT[Memory Management]
        
        SEARCH_BP --> |"POST /search"| SEARCH_ENDPOINT[Web Search]
        SEARCH_BP --> |"POST /search/multi"| MULTI_ENDPOINT[Multi Query Search]
        
        UPLOAD_BP --> |"POST /upload"| UPLOAD_ENDPOINT[Document Processing]
    end

    %% Core Service Layer
    subgraph "Core Service Layer"
        GEMINI_SVC[🤖 Gemini Chain Service<br/>gemini_chain.py]
        INTEL_SVC[🧠 Intelligent Search Service<br/>intelligent_search.py]
        SEARCH_SVC[🌐 Search Tool Service<br/>search_tool.py]
        DOC_SVC[📄 Document Loader Service<br/>document_loader.py]
    end

    %% AI/ML Layer
    subgraph "AI/ML Processing Layer"
        LANGCHAIN[🔗 LangChain Framework]
        GEMINI_LLM[🧠 Google Gemini 2.5 Flash]
        MEMORY_MGR[💾 Conversation Memory<br/>BufferMemory]
        PROMPT_ENG[📝 Custom Legal Prompts]
        
        LANGCHAIN --> |"Orchestration"| GEMINI_LLM
        LANGCHAIN --> |"Memory Management"| MEMORY_MGR
        LANGCHAIN --> |"Prompt Templates"| PROMPT_ENG
    end

    %% External Services Layer
    subgraph "External Services Layer"
        GEMINI_API[🔑 Google Gemini API<br/>ai.google.dev]
        DDG_API[🦆 DuckDuckGo Search<br/>duckduckgo-search]
        WEB_SEARCH[🌍 Web Search Results]
    end

    %% Data Storage Layer
    subgraph "Data Storage Layer"
        LOCAL_STORAGE[💾 Browser LocalStorage<br/>Conversation History]
        TEMP_FILES[📁 Temporary Files<br/>Document Processing]
        LOGS[📊 Application Logs<br/>backend.log]
        CONFIG[⚙️ Environment Config<br/>.env file]
    end

    %% Configuration Layer
    subgraph "Configuration Layer"
        CONFIG_MGR[⚙️ Config Manager<br/>config.py]
        ENV_VARS[🔧 Environment Variables]
        VALIDATION[✅ Pydantic Validation]
    end

    %% Data Flow Connections
    UI --> |"HTTP Requests"| API_GW
    API_GW --> |"Blueprint Routing"| CHAT_BP
    API_GW --> |"Blueprint Routing"| SEARCH_BP
    API_GW --> |"Blueprint Routing"| UPLOAD_BP

    %% Chat Flow
    CHAT_ENDPOINT --> |"Direct Chat"| GEMINI_SVC
    INTEL_ENDPOINT --> |"Smart Decision"| INTEL_SVC
    FORCE_ENDPOINT --> |"Forced Search"| INTEL_SVC

    %% Search Flow
    SEARCH_ENDPOINT --> |"Web Search"| SEARCH_SVC
    MULTI_ENDPOINT --> |"Multi Query"| SEARCH_SVC

    %% Upload Flow
    UPLOAD_ENDPOINT --> |"Document Processing"| DOC_SVC

    %% Service Interactions
    GEMINI_SVC --> |"LangChain Integration"| LANGCHAIN
    INTEL_SVC --> |"Decision Making"| GEMINI_SVC
    INTEL_SVC --> |"Search Integration"| SEARCH_SVC
    SEARCH_SVC --> |"Web Search"| DDG_API
    DOC_SVC --> |"File Processing"| TEMP_FILES

    %% External API Calls
    LANGCHAIN --> |"API Calls"| GEMINI_API
    DDG_API --> |"Search Results"| WEB_SEARCH

    %% Data Persistence
    CONV_MGR --> |"Thread Storage"| LOCAL_STORAGE
    GEMINI_SVC --> |"Session Memory"| MEMORY_MGR
    API_GW --> |"Application Logs"| LOGS

    %% Configuration
    CONFIG_MGR --> |"Load Config"| ENV_VARS
    CONFIG_MGR --> |"Validation"| VALIDATION
    API_GW --> |"Configuration"| CONFIG_MGR

    %% Styling
    classDef userLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef apiLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef aiLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef externalLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef storageLayer fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef configLayer fill:#e0f2f1,stroke:#004d40,stroke-width:2px

    class UI,UI_COMP,THEME,API_CLIENT,CONV_MGR,CHAT_UI,FILE_UI userLayer
    class API_GW,CORS,ERROR_H,HEALTH,CHAT_BP,SEARCH_BP,UPLOAD_BP,CHAT_ENDPOINT,INTEL_ENDPOINT,FORCE_ENDPOINT,MEMORY_ENDPOINT,SEARCH_ENDPOINT,MULTI_ENDPOINT,UPLOAD_ENDPOINT apiLayer
    class GEMINI_SVC,INTEL_SVC,SEARCH_SVC,DOC_SVC serviceLayer
    class LANGCHAIN,GEMINI_LLM,MEMORY_MGR,PROMPT_ENG aiLayer
    class GEMINI_API,DDG_API,WEB_SEARCH externalLayer
    class LOCAL_STORAGE,TEMP_FILES,LOGS,CONFIG storageLayer
    class CONFIG_MGR,ENV_VARS,VALIDATION configLayer
```

## Component Details

### 1. User Interface Layer
- **Frontend Interface**: Static HTML/CSS/JavaScript application
- **ThemeManager**: Dark/light theme switching with localStorage persistence
- **APIClient**: Centralized HTTP client with retry logic and error handling
- **ConversationManager**: Thread CRUD operations and history management
- **ChatInterface**: Message rendering, composer logic, and error handling
- **FileUploadHandler**: Document picker, upload processing, and UI feedback

### 2. API Gateway Layer
- **Flask Application**: Main application factory with CORS support
- **Error Handling**: Global 404/500 error handlers with JSON responses
- **Health Check**: `/health` endpoint for monitoring and status checks
- **Blueprint Registration**: Modular route organization

### 3. Blueprint Layer
- **Chat Blueprint**: Handles all chat-related endpoints
  - `/api/chat` - Basic chat with optional context
  - `/api/chat/intelligent` - Smart search decision making
  - `/api/chat/force-search` - Forced web search integration
  - `/api/chat/memory` - Session memory management
- **Search Blueprint**: Web search functionality
  - `/api/search` - Single query search with synthesis
  - `/api/search/multi` - Multiple query search and synthesis
- **Upload Blueprint**: Document processing
  - `/api/chat/upload` - File upload and text extraction

### 4. Core Service Layer
- **Gemini Chain Service**: LangChain integration with Google Gemini
- **Intelligent Search Service**: Decision-making system for search necessity
- **Search Tool Service**: Web search integration with DuckDuckGo
- **Document Loader Service**: File processing for PDF, DOCX, and text files

### 5. AI/ML Processing Layer
- **LangChain Framework**: AI orchestration and pipeline management
- **Google Gemini 2.5 Flash**: Primary language model for legal reasoning
- **Conversation Memory**: Session-based conversation history management
- **Custom Legal Prompts**: Specialized prompts for Indian legal context

### 6. External Services Layer
- **Google Gemini API**: AI language model service
- **DuckDuckGo Search**: Web search service for current information
- **Web Search Results**: Real-time information retrieval

### 7. Data Storage Layer
- **Browser LocalStorage**: Client-side conversation history and preferences
- **Temporary Files**: Server-side temporary file processing
- **Application Logs**: Structured logging with timestamps and error tracking
- **Environment Configuration**: API keys and application settings

### 8. Configuration Layer
- **Config Manager**: Environment variable management and validation
- **Pydantic Validation**: Request/response data validation
- **Environment Variables**: API keys, model settings, and application configuration

## Data Flow Patterns

### 1. Basic Chat Flow
```
User Input → Chat Interface → API Gateway → Chat Blueprint → Gemini Service → LangChain → Gemini API → Response
```

### 2. Intelligent Search Flow
```
User Input → Chat Interface → API Gateway → Intelligent Chat Endpoint → Intelligent Search Service → Decision Making → [Gemini Service OR Search Service] → Response Synthesis
```

### 3. Document Upload Flow
```
File Upload → File Handler → API Gateway → Upload Blueprint → Document Loader Service → Text Extraction → Context Integration
```

### 4. Web Search Flow
```
Search Query → Search Interface → API Gateway → Search Blueprint → Search Tool Service → DuckDuckGo API → Web Results → Response Synthesis
```

## Key Architectural Patterns

### 1. **Modular Design**
- Blueprint-based route organization
- Service-oriented architecture
- Separation of concerns

### 2. **Error Handling**
- Comprehensive error catching and logging
- Graceful degradation for service failures
- User-friendly error messages

### 3. **Scalability**
- Stateless server design
- Session-based memory management
- Modular service components

### 4. **Security**
- Input validation with Pydantic
- CORS configuration
- Secure API key management

### 5. **Performance**
- Efficient memory management
- Caching strategies for frequently accessed data
- Optimized API response times

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | HTML5, CSS3, Vanilla JS, Tailwind CSS | User interface and experience |
| Backend | Python 3.8+, Flask 3.0.0 | Web framework and API |
| AI/ML | LangChain 0.1.0, Google Gemini 2.5 Flash | AI orchestration and language model |
| Search | DuckDuckGo Search API | Web search functionality |
| Validation | Pydantic 2.5.0 | Data validation and serialization |
| CORS | Flask-CORS 4.0.0 | Cross-origin resource sharing |
| Logging | Python logging | Application monitoring and debugging |

This architecture provides a robust, scalable foundation for the NyayaAI legal assistant platform with clear separation of concerns and efficient data flow patterns.
