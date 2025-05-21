from flask import Flask, jsonify, request

def create_app():
    """Initialize the Flask application."""
    app = Flask(__name__)
    
    # Configure a secret key for session management
    import os
    app.config['SECRET_KEY'] = os.urandom(24)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Add error handlers
    @app.errorhandler(500)
    def handle_500_error(e):
        if request_wants_json():
            return jsonify({"error": "Internal server error"}), 500
        return e

    @app.errorhandler(404)
    def handle_404_error(e):
        if request_wants_json():
            return jsonify({"error": "Resource not found"}), 404
        return e
        
    @app.errorhandler(400)
    def handle_400_error(e):
        if request_wants_json():
            return jsonify({"error": "Bad request"}), 400
        return e
    
    @app.errorhandler(413)
    def handle_413_error(e):
        if request_wants_json():
            return jsonify({"error": "Request too large. Please reduce the size of your input."}), 413
        return e
    
    def request_wants_json():
        """Check if the request is expecting a JSON response."""
        best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
        return (best == 'application/json' or 
                (request.path and request.path.startswith('/analyze')) or
                request.headers.get('Content-Type') == 'application/json')
    
    return app 