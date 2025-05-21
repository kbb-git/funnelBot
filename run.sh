#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  export $(grep -v '^#' .env | xargs)
fi

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
  echo "Warning: GEMINI_API_KEY is not set. Please set it in your environment or .env file."
  # Use a default/demo key for development only - replace this in production
  export GEMINI_API_KEY="AIzaSyB3X2-gyRMUPTo1jM2KCn5PLXtgy1L72Oc"
fi

# Run the Flask application
python3 run.py 