from __future__ import annotations
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# from flow import build_flow  # Not needed for chatbot
# from services import connect_neo4j, read_schema_snapshot, execute_cypher  # Not needed for chatbot
# from services.database import init_db  # Not needed for chatbot
# from .user_routes import router as user_router  # Not needed for chatbot (requires PostgreSQL)
from .chatbot_routes import router as chatbot_router
from .user_routes import router as user_router
from .admin_routes import router as admin_router

class Text2CypherRequest(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    question: str
    execute: bool = False

class Text2CypherResponse(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    extraction: Dict[str, Any]
    cypher: str
    params: Dict[str, Any]
    rows: Optional[List[Dict[str, Any]]] = None

app = FastAPI(
    title="AusVisa API",
    description="API for Australian Visa Chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include user routes
app.include_router(user_router)

# Include chatbot routes
app.include_router(chatbot_router)

# Include admin routes
app.include_router(admin_router)

# Deprecated event handlers - commented out to avoid AssertionError
# @app.on_event("startup")
# def _startup() -> None:
#     # Initialize database tables (commented out - not needed for chatbot)
#     # init_db()
#     pass
    
#     # Build once; reuse between requests
#     # app.state.flow = build_flow()
#     # app.state.driver = connect_neo4j()
#     # app.state.schema_text = read_schema_snapshot(app.state.driver)

# @app.on_event("shutdown")
# def _shutdown() -> None:
#     driver = getattr(app.state, "driver", None)
#     if driver:
#         driver.close()

@app.get("/health")
def health():
    """Health check endpoint
    
    Returns:
        dict: Status message
    """
    return {"status": "ok"}

@app.get("/debug-config")
def debug_config():
    import config
    import os
    # Reload config to be super sure we get current state of module
    import importlib
    importlib.reload(config)
    
    key = config.GOOGLE_API_KEY
    masked = key[:5] + "..." + key[-5:] if key and len(key) > 10 else "None"
    
    return {
        "loaded_key": masked,
        "model": config.GEMINI_MODEL,
        "env_file_key": os.getenv("GOOGLE_API_KEY")[:5] + "..." if os.getenv("GOOGLE_API_KEY") else "None"
    }

# Text2Cypher endpoints commented out - not needed for chatbot
# @app.get("/schema")
# def schema():
#     return {"schema": app.state.schema_text}

# @app.post("/text2cypher", response_model=Text2CypherResponse)
# def text2cypher(req: Text2CypherRequest):
#     try:
#         state = {
#             "question": req.question,
#             "schema_text": app.state.schema_text,
#             "extraction": None,
#             "query": None,
#             "rows": None,
#         }
#         final = app.state.flow.invoke(state)
#         extraction = final["extraction"]
#         query = final["query"]
#         rows = None
#         if req.execute:
#             rows = execute_cypher(app.state.driver, query.cypher, query.params)
#         return Text2CypherResponse(
#             extraction=extraction.model_dump(),
#             cypher=query.cypher,
#             params=query.params,
#             rows=rows,
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e)) from e