import google.generativeai as genai
import os

# Debug env
api_key = os.getenv("GEMINI_API_KEY")
print(f"Env Key: {str(api_key)}")
if not api_key:
    print("API Key is missing/empty")

try:
    genai.configure(api_key=api_key)
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
    print("\nAttempting CHAT generation with deep-research...")
    model = genai.GenerativeModel('models/deep-research-pro-preview-12-2025')
    chat = model.start_chat()
    response = chat.send_message("Hello")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
