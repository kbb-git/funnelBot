import os
import logging
import google.generativeai as genai
import gc  # For garbage collection
import functools
import time
import signal
from contextlib import contextmanager

# Configure Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    logging.warning("Warning: GEMINI_API_KEY environment variable not set.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Class to handle timeout exceptions
class TimeoutException(Exception):
    pass

# Context manager for timeouts
@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    
    # Set the timeout handler
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        # Reset the alarm
        signal.alarm(0)

# Retry decorator for API calls
def retry_api_call(max_retries=3, backoff_factor=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    logging.warning(f"API call failed, retrying ({retries}/{max_retries}): {e}")
                    # Exponential backoff
                    time.sleep(backoff_factor * (2 ** (retries - 1)))
                    # Force garbage collection before retry
                    gc.collect()
            return None  # Should never reach here
        return wrapper
    return decorator

def chunk_text(text, max_chunk_size=25000):
    """
    Split text into manageable chunks to prevent memory issues.
    For transcripts, we'll create logical breaks at speaker changes.
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for the newline
        if current_size + line_size > max_chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

@retry_api_call(max_retries=2)
def analyze_transcript(transcript, sales_rep_names, merchant_names):
    """
    Analyzes a transcript using Gemini AI.
    
    Args:
        transcript (str): The transcript to analyze
        sales_rep_names (str): Names of sales representatives
        merchant_names (str): Names of merchants
        
    Returns:
        dict: Analysis results or error message
    """
    try:
        # Check if API key is configured before making API call 
        if not GEMINI_API_KEY:
            logging.error("Gemini API key not configured.")
            return {'error': 'AI service not configured. API key is missing.'}

        # Hard limit transcript size to prevent memory issues
        max_transcript_length = 30000  # Characters
        if len(transcript) > max_transcript_length:
            truncated_transcript = transcript[:max_transcript_length] + "\n...[transcript truncated due to length limits]"
            logging.warning(f"Transcript truncated from {len(transcript)} to {len(truncated_transcript)} characters")
            transcript = truncated_transcript

        # Construct the prompt for Gemini, keeping everything else the same
        prompt = f"""# Funnel‑Coach‑Gem v1‑2025‑05‑21 (Rev 7)‑explore‑100pt (Explore‑stage calls)

## ROLE

You are a revenue‑enablement coach. As a revenue‑enablement coach, your evaluation of these Explore‑stage calls is critical because this stage is designed to build trust, thoroughly understand the merchant's business, establish their needs and wants, identify barriers, and ultimately gain the merchant's acceptance of requirements. Evaluate **Explore‑stage** sales‑call transcripts for:

* Effective use of the **funneling technique**
* How thoroughly the seller uncovers **pains**, **motivations**, and secures **commitments**

---

## 1 Pre‑check: Speaker roles

**Inspect the speaker labels first.** Based on the user's input: Sales Rep(s): {sales_rep_names}. Merchant(s): {merchant_names}.

If it is **not explicitly clear** from the transcript who the sales‑rep(s) is/are and who the merchant(s) is/are, even with this information:

1. **Do NOT score the call.**
2. Respond **exactly** with:

```
NEED_SPEAKER_ROLES: Please specify which speaker(s) is/are the sales rep(s) and which is/are the merchant(s) so I can evaluate the call.
```

3. Wait for clarification, then continue.

Only proceed once roles are unambiguous.

---

## 2 Funneling technique definition

The funnel technique progresses from broad to specific: starting with Thinking questions (Triggers), moving to multiple Explore questions to gather details, then to Narrow/Confirm questions to verify understanding, and often concluding with a Sweeper question.

| Stage                | Purpose & Typical Use                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Typical form                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **Thinking**         | Wide and unbiased questions that will result in long answers. Normally used to start a new funnel or to provoke thinking during an existing funnel.                                                                                                                                                                                                                                                                                                                                                                             | Open "How/Why" question (e.g., "How do payments affect your company goals?")                       |
|                      | **Non-Examples / Common Pitfalls for Thinking Questions:**  - A question that primarily seeks factual recall (e.g., "What system do you use?") is typically Explore, not Thinking.  - A question that is very narrow or seeks a yes/no answer is likely Narrow/Confirm.                                                                                                                                                                                                                                                         |                                                                                                    |
| **Explore (broad)**  | In response to a trigger, in‑order to learn more about a topic. Normally used to drill deeper during an existing funnel, or to start a new funnel in response to a trigger.                                                                                                                                                                                                                                                                                                                                                     | Who, what, when, where, why, which, how (e.g., "When did this start happening?")                   |
|                      | **Non-Examples / Common Pitfalls for Explore Questions:**  - A simple statement like 'That's interesting' or 'Tell me more' (without a question mark or interrogative structure) is not an Explore question. It must be phrased as a question.  - A question that is primarily seeking a yes/no answer to validate information (e.g., 'So, you're saying X is the main issue?') is a Narrow/Confirm question.                                                                                                                   |                                                                                                    |
| **Narrow / Confirm** | Narrow questions to confirm something. Normally used at the end of funnels, or if there is no need for a funnel, in response to something said by the customer.                                                                                                                                                                                                                                                                                                                                                                 | If / do / is / are style (e.g., "If you fix this problem, will it help you to achieve your goal?") |
|                      | **Non-Examples / Common Pitfalls for Narrow/Confirm Questions:**  - An open‑ended question like 'What are your thoughts on that solution?' is likely Thinking or Explore, not Narrow/Confirm. Narrow/Confirm questions are typically closed‑ended and seek specific validation of information already discussed.  - Simply repeating a merchant's statement as a statement (e.g., "So, APMs are costing you sales.") is not a Narrow/Confirm question unless phrased interrogatively (e.g., "So, are APMs costing you sales?"). |                                                                                                    |
| **Sweeper**          | Surface anything missed or summarise problem/next steps.                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | "Is there anything else we should cover?" / summary statement                                      |
|                      | **Non-Examples / Common Pitfalls for Sweeper Questions:**  - A question that introduces a completely new topic is likely a Thinking question, not a Sweeper.  - A generic closing like "Thanks for your time" is not a Sweeper question/statement for scoring purposes unless it also explicitly asks if anything was missed or summarises.                                                                                                                                                                                     |                                                                                                    |

**Classification rules:**

1. *Each seller utterance can belong to **one and only one** question category (Thinking, Explore, Narrow/Confirm, or Sweeper). Never double‑classify the same question.*
2. *If an utterance contains **two or more distinct questions**, classify the **first interrogative clause** only; ignore the rest for scoring.*

A **successful (complete) funnel** = **Thinking ➜ Explore ➜ ≥ 1 Narrow/Confirm** question asked by the **sales rep**.

---

## 3 Input assumptions

* Transcript is plain text.
* Each line begins with a speaker name followed by a colon (e.g., `Alice:`).
* Timestamps like `[00:03:21]` are optional.
* **No un‑redacted card data or personal identifiers.** If detected, respond exactly with `DATA_NOT_REDACTED`.

---

## 6 Style rules

* Quote all utterances verbatim in bullet lists.
* Use **British spelling**.
* Never fabricate dialogue.
* If transcript exceeds context length, analyse the earliest portion that contains at least the first two complete funnels if possible, or up to the first 15 rep utterances if two funnels aren't present that early.
* If the input is not a transcript or is nonsensical, respond `UNSUPPORTED_INPUT`.

---

## Version tag

`Funnel‑Coach‑Gem v1‑2025‑05‑21 (Rev 7)‑explore‑100pt`

---

## CALL TRANSCRIPT TO ANALYZE:

Sales Rep(s) indicated as: {sales_rep_names}
Merchant(s) indicated as: {merchant_names}

```text
{transcript}
```

## ANALYSIS AND EVALUATION:
(Begin your analysis here, focusing only on identifying the basic question types and funnels. Due to space constraints, provide a simplified analysis with these key elements:)
1. Identify the main question types (Thinking, Explore, Narrow/Confirm, Sweeper)
2. Find complete funnels following the Thinking → Explore → Narrow/Confirm pattern
3. Note any significant pains articulated by the merchant
4. Provide a brief score estimation

Keep your response concise and under 2000 words.
"""

        # Use a more optimized model configuration with lower temperature for memory efficiency
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', 
                                    generation_config=genai.GenerationConfig(
                                        temperature=0,
                                        top_p=0.1,
                                        max_output_tokens=5000  # Reduced output size
                                    ))
        
        # Make the API call with retry and timeout protection
        try:
            # Set a timeout for the entire operation
            with time_limit(300):  # 5 minute timeout
                # Force garbage collection before API call
                gc.collect()
                response = model.generate_content(prompt)
                # Force garbage collection immediately after API call
                gc.collect()
        except TimeoutException:
            logging.error("Gemini API call timed out after 5 minutes")
            return {'error': 'Analysis timed out. Please try with a shorter transcript.'}
        except Exception as e:
            logging.error(f"First API call failed, retrying: {e}")
            # Clean up memory before retrying
            gc.collect()
            # Retry with a shorter prompt if needed
            if len(transcript) > 15000:
                transcript = transcript[:15000] + "\n...[transcript truncated due to length]"
                prompt = prompt.replace("{transcript}", transcript)
            # Try again with a delay
            time.sleep(1)
            
            try:
                with time_limit(300):  # 5 minute timeout for retry
                    response = model.generate_content(prompt)
                    gc.collect()
            except TimeoutException:
                logging.error("Retry API call also timed out")
                return {'error': 'Analysis timed out. Please try again with a much shorter transcript.'}
        
        # Force garbage collection to free memory
        gc.collect()
        
        # Handle specific error responses
        if not hasattr(response, 'text'):
            logging.error(f"Gemini API returned an empty or malformed response: {response}")
            return {'error': 'AI service returned an empty response. Please try again with a shorter transcript.'}
            
        if response.text == "NEED_SPEAKER_ROLES: Please specify which speaker(s) is/are the sales rep(s) and which is/are the merchant(s) so I can evaluate the call.":
            return {'analysis_text': response.text, 'is_error': True}
        elif response.text == "DATA_NOT_REDACTED":
            return {'analysis_text': response.text, 'is_error': True}
        elif response.text == "UNSUPPORTED_INPUT":
            return {'analysis_text': response.text, 'is_error': True}
        
        # Check for empty response
        if not response.text or not response.text.strip():
            logging.error(f"Gemini API returned an empty or malformed response: {response}")
            prompt_feedback_msg = ""
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason'):
                prompt_feedback_msg = f" (Reason: {response.prompt_feedback.block_reason_message})"
            return {'error': f'AI service returned no content.{prompt_feedback_msg}'}
            
        # Return successful response
        return {'analysis_text': response.text}
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        # Clean up memory
        gc.collect()
        # Check if it's a Google API error for more specific feedback
        if hasattr(e, 'args') and e.args and isinstance(e.args[0], str) and "API key not valid" in e.args[0]:
             return {'error': 'Invalid Gemini API Key. Please check your configuration.'}
        return {'error': f'An error occurred processing your request: {str(e)}'}