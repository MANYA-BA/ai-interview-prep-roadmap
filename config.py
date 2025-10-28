"""
Configuration for the Gemini / Google Generative AI API key.

Instructions to get a free Gemini API key:
1. Visit https://ai.google.dev (Google AI) or Google AI Studio.
2. Sign in with your Google account and create an API key in the "API Keys" or "Credentials" section.
3. Copy the API key and store it in a `.env` file as `GOOGLE_API_KEY=your_key_here`.

Note: Keys and access management may change; consult Google AI documentation for the latest instructions.
"""
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    # Provide a helpful warning; some parts of the project work offline but LLM calls require the key
    print("Warning: GOOGLE_API_KEY not found in environment. Set it in a .env file or your environment before using LLM features.")
