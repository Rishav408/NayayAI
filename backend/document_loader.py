"""
Document loader module for future expansion.

This module provides utilities for loading and processing various document types
including PDFs, text files, and web content for future features like summarization.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import mimetypes
import tempfile

# Lightweight parsers
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    import docx  # python-docx
except Exception:
    docx = None

# LangChain document loaders (imported conditionally for future use)
try:
    from langchain_community.document_loaders import (
        PyPDFLoader,
        TextLoader,
        WebBaseLoader,
        DirectoryLoader
    )
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    Document loader for processing various file types.
    
    This class provides methods for loading and processing documents
    from different sources for future summarization and analysis features.
    """
    
    def __init__(self):
        """Initialize the document loader."""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain document loaders not available. Install langchain-community for full functionality.")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        ) if LANGCHAIN_AVAILABLE else None

    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract raw text content from supported files (PDF, TXT, DOCX).

        This is a lightweight path intended for chat context ingestion.
        Returns at most ~50k characters to avoid oversized payloads.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}

            extension = path.suffix.lower()

            # TXT - fastest path
            if extension == '.txt':
                text = path.read_text(encoding='utf-8', errors='ignore')
                return self._format_extract_response(path.name, text)

            # PDF
            if extension == '.pdf':
                if not PyPDF2:
                    return {"success": False, "error": "PDF support not available (PyPDF2 missing)"}
                try:
                    text_parts: List[str] = []
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            try:
                                page_text = page.extract_text() or ''
                            except Exception:
                                page_text = ''
                            if page_text:
                                text_parts.append(page_text)
                    text = "\n\n".join(text_parts)
                    return self._format_extract_response(path.name, text, meta={"pages": len(getattr(reader, 'pages', []))})
                except Exception as e:
                    logger.error(f"PDF extraction failed: {e}")
                    return {"success": False, "error": f"PDF extraction failed: {e}"}

            # DOCX
            if extension == '.docx':
                if not docx:
                    return {"success": False, "error": "DOCX support not available (python-docx missing)"}
                try:
                    document = docx.Document(file_path)
                    text = "\n".join(p.text for p in document.paragraphs)
                    return self._format_extract_response(path.name, text)
                except Exception as e:
                    logger.error(f"DOCX extraction failed: {e}")
                    return {"success": False, "error": f"DOCX extraction failed: {e}"}

            # Legacy .doc not supported reliably without external tools
            if extension == '.doc':
                return {"success": False, "error": ".doc files are not supported. Please convert to .docx"}

            # Fallback unsupported
            return {"success": False, "error": f"Unsupported file type: {extension}"}
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return {"success": False, "error": str(e)}

    def _format_extract_response(self, filename: str, text: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        text = (text or '').strip()
        # Limit payload size
        MAX_CHARS = 50000
        truncated = False
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS]
            truncated = True
        response: Dict[str, Any] = {
            "success": True,
            "filename": filename,
            "characters": len(text),
            "truncated": truncated,
            "text": text,
        }
        if meta:
            response["meta"] = meta
        return response
    
    def load_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Load and process a PDF document.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[str, Any]: Loaded document data
        """
        if not LANGCHAIN_AVAILABLE:
            return {
                "error": "LangChain not available",
                "message": "Install langchain-community to use document loading features"
            }
        
        try:
            logger.info(f"Loading PDF document: {file_path}")
            
            # Validate file exists
            if not Path(file_path).exists():
                return {"error": "File not found", "file_path": file_path}
            
            # Load PDF
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            result = {
                "success": True,
                "file_path": file_path,
                "document_count": len(documents),
                "chunk_count": len(chunks),
                "total_pages": len(documents),
                "chunks": [
                    {
                        "page": doc.metadata.get("page", 0),
                        "content": doc.page_content,
                        "chunk_index": i
                    }
                    for i, doc in enumerate(chunks)
                ]
            }
            
            logger.info(f"Successfully loaded PDF: {len(documents)} pages, {len(chunks)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return {
                "error": "Failed to load PDF",
                "message": str(e),
                "file_path": file_path
            }
    
    def load_text(self, file_path: str) -> Dict[str, Any]:
        """
        Load and process a text document.
        
        Args:
            file_path (str): Path to the text file
            
        Returns:
            Dict[str, Any]: Loaded document data
        """
        if not LANGCHAIN_AVAILABLE:
            return {
                "error": "LangChain not available",
                "message": "Install langchain-community to use document loading features"
            }
        
        try:
            logger.info(f"Loading text document: {file_path}")
            
            # Validate file exists
            if not Path(file_path).exists():
                return {"error": "File not found", "file_path": file_path}
            
            # Load text file
            loader = TextLoader(file_path)
            documents = loader.load()
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            result = {
                "success": True,
                "file_path": file_path,
                "document_count": len(documents),
                "chunk_count": len(chunks),
                "chunks": [
                    {
                        "content": doc.page_content,
                        "chunk_index": i
                    }
                    for i, doc in enumerate(chunks)
                ]
            }
            
            logger.info(f"Successfully loaded text file: {len(chunks)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error loading text file: {e}")
            return {
                "error": "Failed to load text file",
                "message": str(e),
                "file_path": file_path
            }
    
    def load_web_content(self, url: str) -> Dict[str, Any]:
        """
        Load and process content from a web URL.
        
        Args:
            url (str): URL to load content from
            
        Returns:
            Dict[str, Any]: Loaded document data
        """
        if not LANGCHAIN_AVAILABLE:
            return {
                "error": "LangChain not available",
                "message": "Install langchain-community to use document loading features"
            }
        
        try:
            logger.info(f"Loading web content: {url}")
            
            # Load web content
            loader = WebBaseLoader([url])
            documents = loader.load()
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            result = {
                "success": True,
                "url": url,
                "document_count": len(documents),
                "chunk_count": len(chunks),
                "chunks": [
                    {
                        "content": doc.page_content,
                        "source": doc.metadata.get("source", url),
                        "chunk_index": i
                    }
                    for i, doc in enumerate(chunks)
                ]
            }
            
            logger.info(f"Successfully loaded web content: {len(chunks)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error loading web content: {e}")
            return {
                "error": "Failed to load web content",
                "message": str(e),
                "url": url
            }
    
    def load_directory(self, directory_path: str, file_pattern: str = "**/*") -> Dict[str, Any]:
        """
        Load and process all files from a directory.
        
        Args:
            directory_path (str): Path to the directory
            file_pattern (str): File pattern to match
            
        Returns:
            Dict[str, Any]: Loaded document data
        """
        if not LANGCHAIN_AVAILABLE:
            return {
                "error": "LangChain not available",
                "message": "Install langchain-community to use document loading features"
            }
        
        try:
            logger.info(f"Loading directory: {directory_path}")
            
            # Validate directory exists
            if not Path(directory_path).exists():
                return {"error": "Directory not found", "directory_path": directory_path}
            
            # Load directory
            loader = DirectoryLoader(directory_path, glob=file_pattern)
            documents = loader.load()
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Group by file type
            file_types = {}
            for doc in documents:
                source = doc.metadata.get("source", "unknown")
                file_type = Path(source).suffix.lower()
                if file_type not in file_types:
                    file_types[file_type] = 0
                file_types[file_type] += 1
            
            result = {
                "success": True,
                "directory_path": directory_path,
                "file_pattern": file_pattern,
                "document_count": len(documents),
                "chunk_count": len(chunks),
                "file_types": file_types,
                "chunks": [
                    {
                        "content": doc.page_content,
                        "source": doc.metadata.get("source", "unknown"),
                        "chunk_index": i
                    }
                    for i, doc in enumerate(chunks)
                ]
            }
            
            logger.info(f"Successfully loaded directory: {len(documents)} files, {len(chunks)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error loading directory: {e}")
            return {
                "error": "Failed to load directory",
                "message": str(e),
                "directory_path": directory_path
            }
    
    def detect_file_type(self, file_path: str) -> Dict[str, Any]:
        """
        Detect the type of a file based on its extension and content.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Dict[str, Any]: File type information
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {"error": "File not found", "file_path": file_path}
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # Get file extension
            extension = path.suffix.lower()
            
            # Determine supported file types
            supported_types = {
                '.pdf': 'PDF Document',
                '.txt': 'Text File',
                '.md': 'Markdown File',
                '.html': 'HTML File',
                '.htm': 'HTML File',
                '.doc': 'Word Document',
                '.docx': 'Word Document'
            }
            
            file_type_info = {
                "file_path": file_path,
                "filename": path.name,
                "extension": extension,
                "mime_type": mime_type,
                "file_type": supported_types.get(extension, "Unknown"),
                "supported": extension in supported_types,
                "file_size": path.stat().st_size
            }
            
            return file_type_info
            
        except Exception as e:
            logger.error(f"Error detecting file type: {e}")
            return {
                "error": "Failed to detect file type",
                "message": str(e),
                "file_path": file_path
            }

# Global instance for the application
document_loader = DocumentLoader()
