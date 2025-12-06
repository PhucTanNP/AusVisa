from __future__ import annotations
from langchain_core.messages import SystemMessage, HumanMessage
from llm import get_chat
from models import Extraction, CypherResult

CYPHER_SYS = (
"You are a senior Neo4j Cypher engineer. Generate parameterized Cypher matching the extraction."
"Rules: Prefer MATCH with node labels, use parameters for literal values, include WHERE for filters,"
" and produce a concise RETURN. Use variable names from extraction nodes if provided."
)

CYPHER_USER_TMPL = (
    "Schema summary (may be incomplete): {schema}\n"
    "Extraction JSON: {extraction_json}\n"
    "Output JSON ONLY as CypherResult(cypher: str, params: dict)."
)

def run_cypher_gen(extraction: Extraction, schema_text: str) -> CypherResult:
    """_summary_

    Args:
        extraction (Extraction): _description_
        schema_text (str): _description_

    Returns:
        CypherResult: _description_
    """
    llm = get_chat(temperature=0).with_structured_output(CypherResult)
    prompt = CYPHER_USER_TMPL.format(schema=schema_text, extraction_json=extraction.model_dump_json())
    return llm.invoke([
        SystemMessage(content=CYPHER_SYS),
        HumanMessage(content=prompt),
    ])