"""
Main Flask application entry point for the LangChain + Gemini API backend.

This module initializes the Flask application, configures logging,
and registers all API routes.
"""

import logging
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from routes import chat_bp, search_bp, upload_bp

def create_app():
    """
    Application factory pattern for creating Flask app.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS for frontend integration.
    # In production, set the ALLOWED_ORIGINS env var on Render to your Firebase URL,
    # e.g. ALLOWED_ORIGINS=https://nyayaai-abc12.web.app
    # Locally it defaults to "*" so development is unaffected.
    raw_origins = os.environ.get('ALLOWED_ORIGINS', '*')
    allowed_origins = [o.strip() for o in raw_origins.split(',')] if raw_origins != '*' else ['*']

    CORS(app,
         origins=allowed_origins,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         expose_headers=["Content-Type"],
         supports_credentials=False,  # must be False when origins != ['*']
         vary_header=True)

    # Ensure CORS headers are present on every response (including error responses)
    # This is critical when running behind Render's proxy layer.
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin', '')
        if allowed_origins == ['*']:
            response.headers['Access-Control-Allow-Origin'] = '*'
        elif origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        return response
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('backend.log'),
            logging.StreamHandler()
        ]
    )
    
    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            "status": "healthy",
            "message": "Backend is running successfully"
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting backend server on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
