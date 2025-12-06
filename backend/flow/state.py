from __future__ import annotations
from typing import Any, Dict, List, Optional, TypedDict
from models import Extraction, CypherResult

class FlowState(TypedDict):
    question: str
    schema_text: str
    extraction: Optional[Extraction]
    query: Optional[CypherResult]
    rows: Optional[List[Dict[str, Any]]]