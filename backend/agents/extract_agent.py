from __future__ import annotations
from langchain_core.messages import SystemMessage, HumanMessage
from llm import get_chat
from models import Extraction

EXTRACT_SYS = (
"You are a precise information extraction agent for building Cypher queries. "
"Read the user's question and extract minimal nodes, relationships, filters, and returns."
)


EXTRACT_USER_TMPL = (
    "Schema summary (may be incomplete):\n"
    "{schema}\n\n"
"Question: {question}"
"Return JSON ONLY — following this pydantic schema:"
"Extraction(intent: str, nodes: List[Node], relationships: List[Relationship], filters: List[Filter], returns: List[str])."
)


def run_extraction(question: str, schema_text: str) -> Extraction:
    """_summary_

    Args:
        question (str): _description_
        schema_text (str): _description_

    Returns:
        Extraction: _description_
    """
    llm = get_chat(temperature=0).with_structured_output(Extraction)
    prompt = EXTRACT_USER_TMPL.format(schema=schema_text, question=question)
    return llm.invoke([
        SystemMessage(content=EXTRACT_SYS),
        HumanMessage(content=prompt),
    ])