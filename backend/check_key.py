
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Force reload of .env
load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")

print("-" * 50)
if api_key:
    masked_key = api_key[:5] + "..." + api_key[-5:]
    print(f"✅ Loaded API Key: {masked_key}")
    print(f"Length: {len(api_key)}")
    
    # Test quickly
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Hi")
        print("✅ API Test Success: ", response.text)
    except Exception as e:
        print("❌ API Test Warning:", e)
else:
    print("❌ NO API KEY FOUND")
print("-" * 50)
