from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from .state import FlowState
from agents import run_extraction, run_cypher_gen

def node_extract(state: FlowState) -> FlowState:
    """_summary_

    Args:
        state (FlowState): _description_

    Returns:
        FlowState: _description_
    """
    extraction = run_extraction(state["question"], state["schema_text"])
    state["extraction"] = extraction
    return state

def node_generate(state: FlowState) -> FlowState:
    """_summary_

    Args:
        state (FlowState): _description_

    Raises:
        RuntimeError: _description_

    Returns:
        FlowState: _description_
    """
    if not state.get("extraction"):
        raise RuntimeError("Extraction missing in state.")
    cy = run_cypher_gen(state["extraction"], state["schema_text"])
    state["query"] = cy
    return state

def build_flow():
    """_summary_

    Returns:
        _type_: _description_
    """
    graph = StateGraph(FlowState)
    graph.add_node("extract", node_extract)
    graph.add_node("generate", node_generate)
    graph.add_edge(START, "extract")
    graph.add_edge("extract", "generate")
    graph.add_edge("generate", END)
    return graph.compile()