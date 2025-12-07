"""
Chatbot service using Gemini AI and Neo4j Knowledge Graph
Optimized for speed with streaming, caching, and reduced API calls
"""
from __future__ import annotations
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime, timedelta

import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL, NEO4J_DATABASE, CACHE_TTL
from services.neo4j_exec import connect_neo4j, execute_cypher
from services.query_loader import load_cypher_queries

# Initialize Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Load Cypher Query Templates from file
print("Loading Cypher queries from file...")
QUERY_TEMPLATES = load_cypher_queries()
print(f"Loaded {len(QUERY_TEMPLATES)} query templates")

# Simple in-memory cache for responses
_response_cache: Dict[str, tuple[Any, datetime]] = {}


def _get_cache(key: str) -> Optional[Any]:
    """Get cached response if not expired"""
    key = key.lower().strip()
    if key in _response_cache:
        value, timestamp = _response_cache[key]
        if datetime.now() - timestamp < timedelta(seconds=CACHE_TTL):
            return value
        else:
            del _response_cache[key]
    return None


def _set_cache(key: str, value: Any) -> None:
    """Set cache with current timestamp"""
    key = key.lower().strip()
    _response_cache[key] = (value, datetime.now())


async def detect_intent(user_query: str, system_prompt: str) -> Dict[str, Any]:
    """
    Detect user intent and extract entities using Gemini
    """
    # Quick check for greetings to save API calls
    greetings = {"hi", "hello", "xin chào", "chào", "chao", "hola"}
    if user_query.lower().strip() in greetings:
        return {
            "intent": "GREETING",
            "entities": {},
            "query_type": "greeting"
        }

    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    
    # Optimized prompt - shorter and more direct
    prompt = f"""
    Phân tích câu hỏi sau để lấy thông tin truy vấn graph database:
    User: "{user_query}"
    
    Trả về JSON:
    {{
        "intent": "STUDY|VISA|SETTLEMENT|PATHWAY|COMPARE",
        "entities": {{
             // Trích xuất keyword quan trọng: university_name, level, field, exam_type, score, visa_subclass...
        }},
        "query_type": "map_to_predefined_query_name"
    }}
    """
    
    try:
        # Use native async method
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        # Clean up json markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Intent detection error: {e}")
        return {
            "intent": "STUDY",
            "entities": {},
            "query_type": "fallback"
        }


async def execute_query(query_type: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Execute Cypher query against Neo4j (Async wrapper)
    """
    if query_type not in QUERY_TEMPLATES:
        return []
    
    query = QUERY_TEMPLATES[query_type]
    
    def _run_query():
        driver = connect_neo4j()
        if not driver:
            return []
        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(query, **params)
                data = [record.data() for record in result]
                return data
        except Exception as e:
            print(f"Query execution error: {e}")
            return []
        finally:
            driver.close()

    return await asyncio.to_thread(_run_query)


async def format_response(user_query: str, query_results: List[Dict[str, Any]], system_prompt: str) -> str:
    """
    Format query results into natural language response using Gemini (Async)
    """
    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    
    prompt = f"""
    {system_prompt}
    User: "{user_query}"
    Data: {json.dumps(query_results[:5], ensure_ascii=False)} # Limit context size
    
    Trả lời ngắn gọn, tự nhiên, format đẹp. Dùng emoji.
    """
    
    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"Response formatting error: {e}")
        return "Xin lỗi, tôi gặp lỗi khi xử lý câu trả lời."


async def chatbot_response(user_query: str, system_prompt: str) -> Dict[str, Any]:
    """
    Main chatbot function - Async
    """
    # Step 1: Detect intent
    analysis = await detect_intent(user_query, system_prompt)
    
    if analysis.get("query_type") == "greeting":
        return {
            "response": "Chào bạn! Tôi là trợ lý ảo AusVisa. Tôi có thể giúp gì cho bạn về du học và visa Úc?",
            "intent": "GREETING",
            "query_results": []
        }
    
    # Step 2: Execute query
    query_results = await execute_query(
        analysis.get("query_type", "fallback"),
        analysis.get("entities", {})
    )
    
    # Step 3: Format response
    if query_results:
        response = await format_response(user_query, query_results, system_prompt)
    else:
        # Fallback
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        try:
            # Short fallback prompt
            prompt = f"User: {user_query}\nTrả lời dựa trên kiến thức chung về visa/du học Úc. Ngắn gọn."
            fallback_response = await model.generate_content_async(prompt)
            response = fallback_response.text
        except Exception as e:
            print(f"Fallback error: {e}")
            response = "Xin lỗi, tôi không tìm thấy thông tin phù hợp."
    
    return {
        "response": response,
        "intent": analysis.get("intent"),
        "query_results": query_results
    }


async def chatbot_response_stream(user_query: str, system_prompt: str) -> AsyncGenerator[str, None]:
    """
    Stream chatbot response chunk by chunk for real-time display
    
    Args:
        user_query: User's question
        system_prompt: System prompt for context
        
    Yields:
        Response chunks as they are generated
    """
    # Check cache first
    cache_key = f"stream:{user_query.lower().strip()}"
    cached = _get_cache(cache_key)
    if cached:
        # Stream cached response word by word for smooth UX
        words = cached.split()
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.01)  # Small delay for smooth streaming
        return
    
    # Step 1: Detect intent
    analysis = await detect_intent(user_query, system_prompt)
    
    if analysis.get("query_type") == "greeting":
        yield "Chào bạn! Tôi là trợ lý ảo AusVisa. Tôi có thể giúp gì cho bạn về du học và visa Úc?"
        return

    # Step 2: Execute query
    query_results = await execute_query(
        analysis.get("query_type", "fallback"),
        analysis.get("entities", {})
    )
    
    # Step 3: Stream format_response
    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    
    if query_results:
        prompt = f"""
        {system_prompt}
        User: "{user_query}"
        Data: {json.dumps(query_results[:5], ensure_ascii=False)}
        Trả lời ngắn gọn, tự nhiên, format đẹp. Dùng emoji.
        """
    else:
        prompt = f"""
        User: "{user_query}"
        Trả lời dựa trên kiến thức chung về visa/du học Úc. Ngắn gọn.
        """
    
    try:
        # Stream response from Gemini using native async stream
        full_response = ""
        response_stream = await model.generate_content_async(prompt, stream=True)
        
        async for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
                yield chunk.text
        
        # Cache the complete response
        _set_cache(cache_key, full_response)
        
    except Exception as e:
        print(f"Streaming error: {e}")
        error_msg = "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại."
        yield error_msg
