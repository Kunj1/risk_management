# gemini_client.py
import os
import google.generativeai as genai

def get_gemini_client():
    """Initialize and return a Gemini API client"""
    # Set up the API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    genai.configure(api_key=api_key)
    
    # Generate text with the gemini-pro model
    model = genai.GenerativeModel('gemini-pro')
    return model