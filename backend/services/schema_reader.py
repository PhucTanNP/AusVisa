from __future__ import annotations
from typing import Optional
from neo4j import Driver

DEFAULT_SCHEMA = (
"Labels: Person(name, born), Movie(title, released), Genre(name); "
"Relationships: (Person)-[:ACTED_IN]->(Movie), (Person)-[:DIRECTED]->(Movie), (Movie)-[:IN_GENRE]->(Genre)"
)

def read_schema_snapshot(driver: Optional[Driver]) -> str:
    """Create a short, human-readable schema snapshot. Avoid heavy introspection for speed."""
    if not driver:
        return DEFAULT_SCHEMA

    with driver.session() as sess:
        labels = ", ".join(sorted(sess.run("CALL db.labels()").value()))
        rel_types = ", ".join(sorted(sess.run("CALL db.relationshipTypes()").value()))
        props = ", ".join(sorted(sess.run("CALL db.propertyKeys()").value()))
    return f"Labels: {labels}; Relationships: {rel_types}; Properties: {props}"