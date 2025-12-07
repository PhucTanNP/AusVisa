import requests
import json

print("Testing chatbot with real question about visa 500")
print("="*60)

try:
    response = requests.post(
        "http://localhost:8000/api/chatbot/query",
        json={"question": "cho tôi biết thông tin về visa 500"},
        timeout=30
    )
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"\n📊 Intent: {result.get('intent')}")
    print(f"\n💬 Response:\n{result['response']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
