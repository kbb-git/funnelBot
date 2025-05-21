# FunnelBot Project Structure

This document explains the organization of the FunnelBot project after restructuring.

## Purpose of Restructuring

The project has been reorganized to follow best practices for Flask applications:

1. **Modular Architecture**: Code is now organized into logical modules
2. **Separation of Concerns**: Different components are isolated in their own directories
3. **Easier Maintenance**: The new structure is more scalable and easier to maintain
4. **Better Configuration Management**: Environment variables and settings are centralized

## Directory Structure

```
/funnelBot
  ├── app/                          # Main application package
  │   ├── __init__.py               # Application factory
  │   ├── config/                   # Configuration management
  │   │   ├── __init__.py
  │   │   └── settings.py           # Application settings
  │   ├── services/                 # Service modules
  │   │   ├── __init__.py
  │   │   └── gemini_service.py     # Gemini API integration
  │   ├── static/                   # Static assets
  │   │   ├── css/
  │   │   │   └── style.css         # CSS styles
  │   │   ├── js/
  │   │   │   └── script.js         # JavaScript functionality
  │   │   └── img/                  # Images and icons
  │   │       ├── checkout_logo.jpeg
  │   │       └── favicon.svg
  │   ├── templates/                # HTML templates
  │   │   └── index.html            # Main page template
  │   └── routes.py                 # Application routes
  ├── .gitignore                    # Git ignore rules
  ├── PROJECT_STRUCTURE.md          # This file
  ├── README.md                     # Project documentation
  ├── requirements.txt              # Python dependencies
  ├── run.py                        # Application entry point
  └── run.sh                        # Shell script to run application
```

## Key Changes

1. **Application Factory**: Using the Flask application factory pattern in `app/__init__.py`
2. **Modular Design**: Logic separated into specialized modules
3. **API Services**: API logic separated into the services module
4. **Configuration Management**: Centralized configuration in the config module
5. **Routes Organization**: Routes moved to a separate file for better organization
6. **Environment Variables**: Proper environment variable usage for sensitive data

## How to Run

1. Make sure Python 3.7+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Set your Gemini API key: `export GEMINI_API_KEY="your-api-key"`
4. Run the application: `./run.sh` or `python run.py`
5. Access the application at http://localhost:5000 