import json
import re

def clean_json_response(text: str) -> str:
    """
    Extracts the first JSON object or array found in the text.
    Handles Markdown code blocks and triple quotes.
    """
    if not text:
        return ""
    
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Remove triple quotes if LLM used them
    text = text.strip().strip('"""').strip("'''").strip()
    
    # Find the first { or [ and the last } or ]
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        return match.group(1)
    
    # Fallback: if it contains "status": but no braces, try to wrap it
    if '"status":' in text and not text.strip().startswith('{'):
        return "{" + text.strip() + "}"
    
    return text.strip()

def parse_json_safely(text: str, default=None):
    """Parses JSON with cleaning and fallback."""
    try:
        cleaned = clean_json_response(text)
        return json.loads(cleaned)
    except Exception as e:
        safe_text = str(text)[:200] if text is not None else "None"
        print(f"JSON Parsing Error: {e}\nRaw Text: {safe_text}...")
        return default
