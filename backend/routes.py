"""
API routes for the LangChain + Gemini backend.

This module defines all REST API endpoints including chat, search,
and future expansion endpoints.
"""

import logging
import os
import tempfile
from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError
from typing import Optional, List
from gemini_chain import gemini_chain
from search_tool import search_tool
from intelligent_search import intelligent_search
from document_loader import document_loader

logger = logging.getLogger(__name__)

# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model."""
    query: str
    session_id: Optional[str] = None
    context: Optional[str] = None

class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    max_results: Optional[int] = None
    context: Optional[str] = None
    search_type: Optional[str] = "synthesized"  # "synthesized" or "simple"

class MultiSearchRequest(BaseModel):
    """Multi-query search request model."""
    queries: List[str]
    synthesize: Optional[bool] = True

class MemoryRequest(BaseModel):
    """Memory management request model."""
    session_id: Optional[str] = None
    action: str  # "clear" or "get_history"

# Create blueprints
chat_bp = Blueprint('chat', __name__)
search_bp = Blueprint('search', __name__)
upload_bp = Blueprint('upload', __name__)

# Chat Endpoints
@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for conversational AI.
    
    Processes user queries through the Gemini chain with optional context.
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        chat_request = ChatRequest(**data)
        
        logger.info(f"Chat request received: {chat_request.query[:100]}...")
        
        # Process chat request
        if chat_request.context:
            response = gemini_chain.chat_with_context(
                user_input=chat_request.query,
                context=chat_request.context,
                session_id=chat_request.session_id
            )
        else:
            response = gemini_chain.chat(
                user_input=chat_request.query,
                session_id=chat_request.session_id
            )
        
        return jsonify({
            "success": True,
            "data": response
        }), 200
        
    except ValidationError as e:
        logger.error(f"Validation error in chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Invalid request format",
            "details": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

@chat_bp.route('/chat/intelligent', methods=['POST'])
def intelligent_chat():
    """
    Intelligent chat endpoint with automatic search integration.
    
    Automatically determines when to use web search and provides
    enhanced responses combining LLM knowledge with current information.
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        chat_request = ChatRequest(**data)
        
        logger.info(f"Intelligent chat request received: {chat_request.query[:100]}...")
        
        # Process intelligent chat request
        response = intelligent_search.intelligent_chat(
            user_input=chat_request.query,
            session_id=chat_request.session_id
        )
        
        return jsonify({
            "success": True,
            "data": response
        }), 200
        
    except ValidationError as e:
        logger.error(f"Validation error in intelligent chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Invalid request format",
            "details": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error in intelligent chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

@chat_bp.route('/chat/force-search', methods=['POST'])
def force_search_chat():
    """
    Force search chat endpoint.
    
    Always performs web search regardless of query type.
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        chat_request = ChatRequest(**data)
        
        logger.info(f"Force search chat request received: {chat_request.query[:100]}...")
        
        # Process forced search chat request
        response = intelligent_search.force_search_chat(
            user_input=chat_request.query,
            session_id=chat_request.session_id
        )
        
        return jsonify({
            "success": True,
            "data": response
        }), 200
        
    except ValidationError as e:
        logger.error(f"Validation error in force search chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Invalid request format",
            "details": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error in force search chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

@chat_bp.route('/chat/memory', methods=['POST'])
def manage_memory():
    """
    Memory management endpoint.
    
    Supports clearing conversation memory or retrieving chat history.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        memory_request = MemoryRequest(**data)
        
        logger.info(f"Memory management request: {memory_request.action}")
        
        if memory_request.action == "clear":
            response = gemini_chain.clear_memory(session_id=memory_request.session_id)
        elif memory_request.action == "get_history":
            response = gemini_chain.get_conversation_history(session_id=memory_request.session_id)
        else:
            return jsonify({
                "success": False,
                "error": "Invalid action. Use 'clear' or 'get_history'"
            }), 400
        
        return jsonify({
            "success": True,
            "data": response
        }), 200
        
    except ValidationError as e:
        logger.error(f"Validation error in memory endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Invalid request format",
            "details": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error in memory endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

# Upload Endpoints
@upload_bp.route('/chat/upload', methods=['POST'])
def upload_document():
    """
    Upload a document and extract its text for chat context.

    Accepts multipart/form-data with field name 'file'. Returns extracted text
    (truncated if necessary) and filename. The frontend can pass this text as
    'context' in subsequent chat calls.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "Empty filename"}), 400

        # Save to temp file
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file.save(tmp)
            tmp_path = tmp.name

        # Extract text
        extract = document_loader.extract_text_from_file(tmp_path)

        # Cleanup temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass

        if not extract.get('success'):
            return jsonify({"success": False, "error": extract.get('error', 'Extraction failed')}), 400

        return jsonify({
            "success": True,
            "data": {
                "filename": extract.get('filename'),
                "text": extract.get('text'),
                "characters": extract.get('characters'),
                "truncated": extract.get('truncated', False),
                "meta": extract.get('meta', {})
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

# Search Endpoints
@search_bp.route('/search', methods=['POST'])
def search():
    """
    Search endpoint for online information retrieval.
    
    Performs web search and optionally synthesizes results with Gemini.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        search_request = SearchRequest(**data)
        
        logger.info(f"Search request received: {search_request.query[:100]}...")
        
        # Process search request based on type
        if search_request.search_type == "simple":
            response = search_tool.simple_search(
                query=search_request.query,
                max_results=search_request.max_results
            )
        elif search_request.context:
            response = search_tool.search_with_context(
                query=search_request.query,
                context=search_request.context,
                max_results=search_request.max_results
            )
        else:
            response = search_tool.search_and_synthesize(
                query=search_request.query,
                max_results=search_request.max_results
            )
        
        return jsonify({
            "success": True,
            "data": response
        }), 200
        
    except ValidationError as e:
        logger.error(f"Validation error in search endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Invalid request format",
            "details": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

@search_bp.route('/search/multi', methods=['POST'])
def multi_search():
    """
    Multi-query search endpoint.
    
    Performs multiple searches and optionally synthesizes results.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        multi_search_request = MultiSearchRequest(**data)
        
        logger.info(f"Multi-search request received with {len(multi_search_request.queries)} queries")
        
        response = search_tool.multi_query_search(
            queries=multi_search_request.queries,
            synthesize=multi_search_request.synthesize
        )
        
        return jsonify({
            "success": True,
            "data": response
        }), 200
        
    except ValidationError as e:
        logger.error(f"Validation error in multi-search endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Invalid request format",
            "details": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error in multi-search endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

# Future Expansion Endpoints (Placeholders)
@chat_bp.route('/summarize', methods=['POST'])
def summarize():
    """
    Document summarization endpoint (Future implementation).
    
    This endpoint is prepared for future document summarization functionality.
    """
    return jsonify({
        "success": False,
        "error": "Feature not yet implemented",
        "message": "Document summarization will be available in a future update"
    }), 501

@chat_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Analysis endpoint for deepfake detection (Future implementation).
    
    This endpoint is prepared for future deepfake detection functionality.
    """
    return jsonify({
        "success": False,
        "error": "Feature not yet implemented", 
        "message": "Deepfake detection will be available in a future update"
    }), 501

# Health and Status Endpoints
@chat_bp.route('/status', methods=['GET'])
def status():
    """Get the status of chat services."""
    return jsonify({
        "success": True,
        "service": "chat",
        "status": "operational",
        "gemini_model": gemini_chain.config.GEMINI_MODEL
    }), 200

@search_bp.route('/status', methods=['GET'])
def search_status():
    """Get the status of search services."""
    return jsonify({
        "success": True,
        "service": "search",
        "status": "operational",
        "search_tool": "DuckDuckGo"
    }), 200
