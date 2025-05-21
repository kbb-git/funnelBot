import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use 5001 as default
    port = int(os.environ.get('PORT', 5001))
    
    # In production, disable debug mode
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port) 