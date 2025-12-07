"""Test chatbot directly"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from services.chatbot_service import chatbot_response

async def test():
    # Load system prompt
    system_prompt_path = os.path.join(
        os.path.dirname(__file__), 
        "chatbot", 
        "system_prompt.txt"
    )
    
    if os.path.exists(system_prompt_path):
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        print(f"✅ Loaded system prompt: {len(system_prompt)} characters")
    else:
        system_prompt = "You are a helpful AI assistant."
        print("⚠️ Using default system prompt")
    
    print("\n" + "="*60)
    print("Testing chatbot with: 'bạn hãy cho tôi biết thông tin của visa 500'")
    print("="*60 + "\n")
    
    try:
        result = await chatbot_response(
            "bạn hãy cho tôi biết thông tin của visa 500",
            system_prompt
        )
        print(f"✅ SUCCESS!")
        print(f"Intent: {result.get('intent')}")
        print(f"\nResponse:\n{result['response']}")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
