"""
Chatbot API routes for AusVisa chatbot
"""
from __future__ import annotations
import os
import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.chatbot_service import chatbot_response, chatbot_response_stream
from services.neo4j_exec import connect_neo4j
from config import NEO4J_DATABASE

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    """Request model for chat query"""
    question: str


class ChatResponse(BaseModel):
    """Response model for chat query"""
    response: str
    intent: Optional[str] = None


class StatsResponse(BaseModel):
    """Response model for system statistics"""
    universities: int
    programs: int
    visas: int


@router.post("/query", response_model=ChatResponse)
async def chat_query(req: ChatRequest):
    """
    Process chatbot query
    
    Args:
        req: Chat request with user question
        
    Returns:
        ChatResponse with AI-generated response
    """
    try:
        # Load system prompt
        system_prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "chatbot", 
            "system_prompt.txt"
        )
        
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        else:
            system_prompt = "You are a helpful AI assistant for Australian visa, study, and settlement information."
        
        result = await chatbot_response(req.question, system_prompt)
        
        return ChatResponse(
            response=result["response"],
            intent=result.get("intent")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.post("/query-stream")
async def chat_query_stream(req: ChatRequest):
    """
    Stream chatbot response using Server-Sent Events (SSE)
    
    Args:
        req: Chat request with user question
        
    Returns:
        StreamingResponse with real-time chunks
    """
    try:
        # Load system prompt
        system_prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "chatbot", 
            "system_prompt.txt"
        )
        
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        else:
            system_prompt = "You are a helpful AI assistant for Australian visa, study, and settlement information."
        
        async def event_generator():
            """Generate SSE events"""
            try:
                async for chunk in chatbot_response_stream(req.question, system_prompt):
                    # Format as SSE with JSON payload to preserve newlines
                    payload = json.dumps({"text": chunk})
                    yield f"data: {payload}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
            except Exception as e:
                print(f"Stream generation error: {e}")
                yield f"data: Xin lỗi, đã có lỗi xảy ra.\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get Neo4j database statistics
    
    Returns:
        StatsResponse with counts of universities, programs, and visas
    """
    driver = connect_neo4j()
    if not driver:
        raise HTTPException(status_code=500, detail="Neo4j not connected")
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            stats = session.run("""
                MATCH (u:University) WITH count(u) AS unis
                MATCH (p:Program) WITH unis, count(p) AS progs
                MATCH (v:Visa) WITH unis, progs, count(v) AS visas
                RETURN unis, progs, visas
            """).single()
            
            if stats:
                return StatsResponse(
                    universities=stats["unis"],
                    programs=stats["progs"],
                    visas=stats["visas"]
                )
            else:
                return StatsResponse(
                    universities=0,
                    programs=0,
                    visas=0
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")
    finally:
        driver.close()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for chatbot service
    
    Returns:
        Status dictionary
    """
    driver = connect_neo4j()
    neo4j_status = "connected" if driver else "disconnected"
    
    if driver:
        driver.close()
    
    return {
        "status": "ok",
        "neo4j": neo4j_status
    }
