# FunnelBot - Sales Funneling Assessment Chatbot

FunnelBot is a web application designed to help assess the effectiveness of sales funneling techniques employed by sales representatives during client calls.

## Overview

Users can paste a transcript of a sales call into the application. FunnelBot then utilizes a Large Language Model (LLM), specifically Gemini 2.5, via its API to analyze the transcript based on predefined criteria for sales funneling. The application provides a rating and a qualitative assessment of how well the funneling technique was applied.

## Features

-   **Transcript Input:** A simple interface to paste call transcripts.
-   **AI-Powered Analysis:** Leverages the Gemini 2.5 API for in-depth analysis of the transcript.
-   **Funneling Assessment:** Evaluates the transcript against specific criteria related to sales funneling stages (e.g., awareness, interest, consideration, decision).
-   **Scoring/Rating:** Provides a quantitative score or rating based on the analysis.
-   **Qualitative Feedback:** Offers textual feedback on strengths and areas for improvement in the funneling technique observed.

## Technology Stack

-   **Backend:** Python (Flask)
-   **Frontend:** HTML, CSS, JavaScript
-   **LLM:** Google Gemini 2.5 Flash (via API)

## Project Structure

```
/app
  /__init__.py
  /config
    /__init__.py
    /settings.py
  /services
    /__init__.py
    /gemini_service.py
  /static
    /css
      style.css
    /js
      script.js
    /img
      favicon.svg
      checkout-logo.png
  /templates
    index.html
  routes.py
requirements.txt
run.py
run.sh
README.md
```

## Setup and Running

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd funnelBot
   ```

2. **Set up a Python virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Configure API key:**
   - You can either:
     - Edit the `run.sh` file to include your Gemini API key
     - Or set the environment variable directly:
       ```
       export GEMINI_API_KEY="your-api-key"  # On Windows: set GEMINI_API_KEY=your-api-key
       ```

5. **Run the application:**
   ```
   ./run.sh  # On Windows: run.sh
   ```
   Or directly with Python:
   ```
   python run.py
   ```

6. **Access the application:**
   Open a web browser and navigate to `http://localhost:5001`

## Deployment to Render.com

1. **Push your code to GitHub:**
   Make sure all your code is committed and pushed to GitHub.

2. **Create a new Web Service on Render.com:**
   - Sign in to Render.com
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Choose a name for your service

3. **Configure the Web Service:**
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app`
   - Add the following environment variable:
     - Key: `GEMINI_API_KEY`
     - Value: Your Gemini API key

4. **Deploy the Application:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Access your application at the URL provided by Render.com

5. **Update Environment Variables (if needed):**
   - Go to your Web Service > Environment
   - Add or update environment variables as needed 