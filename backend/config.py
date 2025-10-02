"""
Configuration management for the backend application.

This module handles environment variables, API keys, and application settings.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Application configuration class.
    
    Loads all configuration from environment variables with sensible defaults.
    """
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = os.environ.get('GEMINI_API_KEY')
    
    # LangChain configuration
    LANGCHAIN_TRACING_V2 = os.environ.get('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    LANGCHAIN_API_KEY = os.environ.get('LANGCHAIN_API_KEY')
    LANGCHAIN_PROJECT = os.environ.get('LANGCHAIN_PROJECT', 'nayay-backend')
    
    # Gemini model configuration
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
    GEMINI_TEMPERATURE = float(os.environ.get('GEMINI_TEMPERATURE', '0.7'))
    GEMINI_MAX_TOKENS = int(os.environ.get('GEMINI_MAX_TOKENS', '8192'))
    
    # Search configuration
    SEARCH_MAX_RESULTS = int(os.environ.get('SEARCH_MAX_RESULTS', '5'))
    SEARCH_TIMEOUT = int(os.environ.get('SEARCH_TIMEOUT', '30'))
    
    # Memory configuration
    CONVERSATION_MEMORY_SIZE = int(os.environ.get('CONVERSATION_MEMORY_SIZE', '10'))
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Please set it in your .env file.")
        
        return True

def get_config() -> Config:
    """
    Get the application configuration instance.
    
    Returns:
        Config: Configuration instance
        
    Raises:
        ValueError: If required configuration is missing
    """
    Config.validate_config()
    return Config
