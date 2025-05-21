from flask import Flask

def create_app():
    """Initialize the Flask application."""
    app = Flask(__name__)
    
    # Configure a secret key for session management
    import os
    app.config['SECRET_KEY'] = os.urandom(24)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app 