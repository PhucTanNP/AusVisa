"""
Test streaming endpoint directly to see actual exception
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import asyncio
from services.chatbot_service import chatbot_response_stream

async def test_stream():
    system_prompt = "Bạn là trợ lý AI AusVisa chuyên về visa và du học Úc."
    
    print("Testing chatbot_response_stream...")
    print("Question: 'Visa 500 là gì?'")
    print("-" * 50)
    
    try:
        async for chunk in chatbot_response_stream("Visa 500 là gì?", system_prompt):
            print(f"Chunk: {chunk}")
    except Exception as e:
        import traceback
        print(f"\nException caught: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_stream())
