from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Node(BaseModel):
    label: str = Field(..., description="The Neo4j label, e.g. 'Person' or 'Movie'")
    key: Optional[str] = Field(None, description="Variable name to reference this node in Cypher (e.g. 'p', 'm')")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Constraints like {'name': 'Tom Hanks'}")


class Relationship(BaseModel):
    type: str = Field(..., description="Relationship type, e.g. 'ACTED_IN'")
    start_key: str = Field(..., description="Variable key of start node")
    end_key: str = Field(..., description="Variable key of end node")
    direction: str = Field("->", description="'->', '<-', or '-' for undirected")
    properties: Dict[str, Any] = Field(default_factory=dict)


class Filter(BaseModel):
    sion: str = Field(..., description="English boolean filter, e.g. 'release year > 2010'")


class Extraction(BaseModel):
    intent: str = Field(..., description="Brief statement of user intent")
    nodes: List[Node] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    filters: List[Filter] = Field(default_factory=list)
    returns: List[str] = Field(default_factory=list, description="Fields or node keys to return")


class CypherResult(BaseModel):
    cypher: str
    params: Dict[str, Any] = Field(default_factory=dict)