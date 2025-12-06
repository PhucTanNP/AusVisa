from __future__ import annotations
from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def connect_neo4j() -> Optional[Driver]:
    """_summary_

    Returns:
        Optional[Driver]: _description_
    """
    if NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD:
        return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return None

def execute_cypher(driver: Optional[Driver], cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """_summary_

    Args:
        driver (Optional[Driver]): _description_
        cypher (str): _description_
        params (Dict[str, Any]): _description_

    Returns:
        List[Dict[str, Any]]: _description_
    """
    if not driver:
        return []
    with driver.session() as sess:
        res = sess.run(cypher, params)
        return [r.data() for r in res]