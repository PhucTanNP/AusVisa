"""
Chatbot service using Gemini AI and Neo4j Knowledge Graph
"""
from __future__ import annotations
import json
from typing import Dict, Any, List, Optional

import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL, NEO4J_DATABASE
from services.neo4j_exec import connect_neo4j, execute_cypher
from services.query_loader import load_cypher_queries

# Initialize Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Load Cypher Query Templates from file
print("Loading Cypher queries from file...")
QUERY_TEMPLATES = load_cypher_queries()
print(f"Loaded {len(QUERY_TEMPLATES)} query templates")


def detect_intent(user_query: str, system_prompt: str) -> Dict[str, Any]:
    """
    Detect user intent and extract entities using Gemini
    
    Args:
        user_query: User's question
        system_prompt: System prompt for context
        
    Returns:
        Dictionary with intent, entities, and query_type
    """
    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    
    prompt = f"""
    {system_prompt}
    
    Phân tích câu hỏi sau và trả về JSON:
    
    User: "{user_query}"
    
    Trả về format:
    {{
        "intent": "STUDY|VISA|SETTLEMENT|PATHWAY|COMPARE",
        "entities": {{
            "university_name": "...",
            "level": "Bachelor|Master|Doctor",
            "field": "...",
            "exam_type": "IELTS|TOEFL",
            "score": 6.5,
            "visa_subclass": "500",
            "keyword": "..."
        }},
        "query_type": "find_programs_by_university|find_programs_by_ielts|visa_info|..."
    }}
    
    Chỉ trả về JSON, không giải thích.
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        return result
    except Exception as e:
        print(f"Intent detection error: {e}")
        return {
            "intent": "STUDY",
            "entities": {},
            "query_type": "fallback"
        }


def execute_query(query_type: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Execute Cypher query against Neo4j
    
    Args:
        query_type: Type of query to execute
        params: Parameters for the query
        
    Returns:
        List of result dictionaries
    """
    if query_type not in QUERY_TEMPLATES:
        return []
    
    query = QUERY_TEMPLATES[query_type]
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


def format_response(user_query: str, query_results: List[Dict[str, Any]], system_prompt: str) -> str:
    """
    Format query results into natural language response using Gemini
    
    Args:
        user_query: Original user question
        query_results: Results from Neo4j query
        system_prompt: System prompt for context
        
    Returns:
        Formatted natural language response
    """
    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    
    prompt = f"""
    {system_prompt}
    
    User hỏi: "{user_query}"
    
    Kết quả từ database:
    {json.dumps(query_results, ensure_ascii=False, indent=2)}
    
    Hãy trả lời user một cách TỰ NHIÊN, thân thiện với:
    - Emoji phù hợp
    - Format đẹp (bullets, bold)
    - Đầy đủ thông tin
    - Gợi ý bước tiếp theo
    - Links (nếu có)
    
    Không nói về JSON hay database.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Response formatting error: {e}")
        return "Xin lỗi, tôi gặp lỗi khi xử lý câu trả lời. Vui lòng thử lại."


def chatbot_response(user_query: str, system_prompt: str) -> Dict[str, Any]:
    """
    Main chatbot function - processes user query and returns response
    
    Args:
        user_query: User's question
        system_prompt: System prompt for context
        
    Returns:
        Dictionary with response, intent, and query_results
    """
    # Step 1: Detect intent & extract entities
    analysis = detect_intent(user_query, system_prompt)
    
    # Step 2: Execute query
    query_results = execute_query(
        analysis.get("query_type", "fallback"),
        analysis.get("entities", {})
    )
    
    # Step 3: Format response
    if query_results:
        response = format_response(user_query, query_results, system_prompt)
    else:
        # Fallback: Gemini answers directly
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        try:
            fallback_response = model.generate_content(f"""
            {system_prompt}
            
            User hỏi: "{user_query}"
            
            Không tìm thấy kết quả chính xác. 
            Hãy trả lời dựa trên kiến thức của bạn về du học, visa, định cư Úc.
            Nhắc user có thể hỏi cụ thể hơn.
            """)
            response = fallback_response.text
        except Exception as e:
            print(f"Fallback response error: {e}")
            response = "Xin lỗi, tôi không tìm thấy thông tin phù hợp. Bạn có thể hỏi cụ thể hơn được không?"
    
    return {
        "response": response,
        "intent": analysis.get("intent"),
        "query_results": query_results
    }
