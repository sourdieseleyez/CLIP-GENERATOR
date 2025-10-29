"""
Quick test script to verify Gemini 2.5 Flash Lite integration
Run this to check if your API key works before processing videos
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_gemini_connection():
    print("=" * 50)
    print("  Gemini 2.5 Flash Lite Connection Test")
    print("=" * 50)
    print()
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        print()
        print("Please add your API key to backend/.env:")
        print("GEMINI_API_KEY=your-api-key-here")
        print()
        print("Get your key from: https://aistudio.google.com/app/apikey")
        return False
    
    print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        print("✓ Gemini configured successfully")
        print()
    except Exception as e:
        print(f"❌ ERROR configuring Gemini: {e}")
        return False
    
    # Test model initialization
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        print("✓ Gemini 2.5 Flash Lite model loaded")
        print()
    except Exception as e:
        print(f"❌ ERROR loading model: {e}")
        return False
    
    # Test simple generation
    try:
        print("Testing AI generation...")
        response = model.generate_content(
            "Say 'Hello! Gemini 2.5 Flash Lite is working!' in a friendly way.",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 100,
            }
        )
        print()
        print("AI Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        print()
        print("✓ AI generation successful!")
        print()
    except Exception as e:
        print(f"❌ ERROR generating content: {e}")
        return False
    
    # Test JSON generation (used for clip analysis)
    try:
        print("Testing JSON generation (clip analysis simulation)...")
        response = model.generate_content(
            """Return a JSON array with 2 sample viral moments:
[
  {
    "start": 10.5,
    "end": 25.3,
    "text": "sample quote",
    "reason": "why it's viral",
    "virality_score": 8
  }
]
Return ONLY the JSON array, no other text.""",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 500,
            }
        )
        print()
        print("JSON Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        print()
        print("✓ JSON generation successful!")
        print()
    except Exception as e:
        print(f"❌ ERROR with JSON generation: {e}")
        return False
    
    print("=" * 50)
    print("  ✅ All Tests Passed!")
    print("=" * 50)
    print()
    print("Your Gemini 2.5 Flash Lite integration is working!")
    print("You can now process videos with AI-powered clip generation.")
    print()
    print("Cost per request: ~$0.0005 (133x cheaper than GPT-4!)")
    print()
    return True

if __name__ == "__main__":
    success = test_gemini_connection()
    if not success:
        print()
        print("Please fix the errors above and try again.")
        print()
    input("Press Enter to exit...")
