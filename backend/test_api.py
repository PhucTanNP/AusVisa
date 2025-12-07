import requests
import json

# Test health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    print(f"✅ Health check: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

print("\n" + "="*60)

# Test chatbot query endpoint
try:
    response = requests.post(
        "http://localhost:8000/api/chatbot/query",
        json={"question": "xin chào"},
        timeout=30
    )
    print(f"✅ Chatbot query: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"❌ Chatbot query failed: {e}")
    import traceback
    traceback.print_exc()
