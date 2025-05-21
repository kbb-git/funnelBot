from flask import Blueprint, render_template, request, jsonify
import os
import logging

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
            data = request.get_json()
            transcript = data.get('transcript')
            sales_rep_names = data.get('sales_rep_names')
            merchant_names = data.get('merchant_names', 'Customer')  # Default to 'Customer' if not provided

            if not transcript:
                return jsonify({'error': 'No transcript provided.'}), 400
            if not sales_rep_names:
                return jsonify({'error': 'Sales Rep name(s) not provided.'}), 400

            # Call the analysis service
            response = analyze_transcript(transcript, sales_rep_names, merchant_names)
            return jsonify(response)

        except Exception as e:
            logging.error(f"Error processing request: {e}")
            # Check if it's a Google API error for more specific feedback
            if hasattr(e, 'args') and e.args and isinstance(e.args[0], str) and "API key not valid" in e.args[0]:
                 return jsonify({'error': 'Invalid Gemini API Key. Please check your configuration.'}), 500
            return jsonify({'error': f'An error occurred processing your request: {str(e)}'}), 500 