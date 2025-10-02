#!/usr/bin/env python3
"""
Simple startup script for the Nayay backend.

This script provides an easy way to start the backend server with
proper environment setup and error handling.
"""

import os
import sys
import logging
from pathlib import Path

def setup_environment():
    """Setup the environment for running the backend."""
    # Add the backend directory to Python path
    backend_dir = Path(__file__).parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    # Check if .env file exists
    env_file = backend_dir / '.env'
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("📝 Please copy env.example to .env and add your API keys:")
        print(f"   cp {backend_dir}/env.example {backend_dir}/.env")
        print("   Then edit .env and add your GEMINI_API_KEY")
        print()
    
    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY not found in environment!")
        print("📝 Please add your Gemini API key to the .env file")
        print("🔗 Get your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)

def main():
    """Main entry point for the startup script."""
    print("🚀 Starting Nayay Backend Server...")
    print("=" * 50)
    
    try:
        # Setup environment
        setup_environment()
        
        # Import and run the Flask app
        from main import create_app
        
        app = create_app()
        
        # Get configuration
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print(f"✅ Backend configured successfully!")
        print(f"🌐 Server will start on: http://localhost:{port}")
        print(f"🔧 Debug mode: {debug}")
        print(f"📊 Health check: http://localhost:{port}/health")
        print("=" * 50)
        
        # Start the server
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        logging.error(f"Server startup error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
