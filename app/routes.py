from flask import Blueprint, render_template, request, jsonify, current_app, make_response, Response
import os
import logging
import traceback
import gc  # Garbage collector
import json

from app.services.gemini_service import analyze_transcript

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@main.route('/analyze', methods=['POST'])
def analyze_transcript_route():
    """Receives transcript data and speaker roles, calls Gemini API."""
    if request.method == 'POST':
        try:
            # Check content type to ensure JSON
            if not request.is_json:
                logging.warning("Non-JSON content received")
                return make_response(jsonify({'error': 'Request must be JSON. Check content-type header.'}), 400)

            # Limit request size to avoid memory issues
            content_length = request.content_length
            if content_length and content_length > 5 * 1024 * 1024:  # 5MB limit
                return make_response(jsonify({'error': 'Request too large. Please limit transcript size.'}), 413)

            try:
                data = request.get_json()
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                return make_response(jsonify({'error': 'Invalid JSON format.'}), 400)
                
            if not data:
                return make_response(jsonify({'error': 'Invalid JSON data received.'}), 400)
                
            transcript = data.get('transcript')
            sales_rep_names = data.get('sales_rep_names')
            merchant_names = data.get('merchant_names', 'Customer')  # Default to 'Customer' if not provided

            if not transcript:
                return make_response(jsonify({'error': 'No transcript provided.'}), 400)
            if not sales_rep_names:
                return make_response(jsonify({'error': 'Sales Rep name(s) not provided.'}), 400)

            # Limit transcript size to avoid memory issues
            if len(transcript) > 100000:  # Approximately 100KB
                return make_response(jsonify({'error': 'Transcript too large. Please use a shorter transcript.'}), 413)

            # Call the analysis service
            response = analyze_transcript(transcript, sales_rep_names, merchant_names)
            
            # Force garbage collection to free memory
            gc.collect()
            
            # Always return a proper JSON response
            return make_response(jsonify(response))

        except Exception as e:
            # Log the full stack trace for debugging
            logging.error(f"Error processing request: {e}")
            logging.error(traceback.format_exc())
            
            # Clean up memory
            gc.collect()
            
            # Check if it's a Google API error for more specific feedback
            if hasattr(e, 'args') and e.args and isinstance(e.args[0], str) and "API key not valid" in e.args[0]:
                 return make_response(jsonify({'error': 'Invalid Gemini API Key. Please check your configuration.'}), 500)
            return make_response(jsonify({'error': f'An error occurred processing your request: {str(e)}'}), 500) 