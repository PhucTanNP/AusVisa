from __future__ import annotations
import argparse
import json
from services import connect_neo4j, read_schema_snapshot, execute_cypher
from flow import build_flow

def run(question: str) -> int:
    """_summary_

    Args:
        question (str): _description_

    Returns:
        int: _description_
    """
    driver = connect_neo4j()
    schema_text = read_schema_snapshot(driver)

    state = {
    "question": question,
    "schema_text": schema_text,
    "extraction": None,
    "query": None,
    "rows": None,
    }

    flow = build_flow()
    final = flow.invoke(state)

    extraction = final["extraction"]
    query = final["query"]

    print("=== Extraction ===")
    print(extraction.model_dump_json(indent=2))

    print("=== Cypher ===")
    print(query.cypher)
    print("Params:", json.dumps(query.params, ensure_ascii=False))

    rows = []
    try:
        rows = execute_cypher(driver, query.cypher, query.params)
    finally:
        if driver:
            driver.close()


    if rows:
        print("=== Rows ===")
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))
        print("(No driver or no rows)")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Text2Cypher (2-agent) CLI")
    parser.add_argument("question", help="Natural language question")
    args = parser.parse_args()
    raise SystemExit(run(args.question))

if __name__ == "__main__":
    main()