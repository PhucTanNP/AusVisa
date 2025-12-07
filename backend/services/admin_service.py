"""Admin service for Neo4j graph operations and admin utilities"""
from typing import Dict, List, Any, Optional
from services.neo4j_exec import connect_neo4j
from config import NEO4J_DATABASE


class AdminService:
    """Service for admin-specific operations"""
    
    @staticmethod
    def get_neo4j_graph_data() -> Dict[str, Any]:
        """
        Get Neo4j graph data for visualization
        Returns nodes and edges from the graph
        """
        driver = connect_neo4j()
        if not driver:
            return {"nodes": [], "edges": []}
        
        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                # Fetch nodes and relationships
                # Limit to 300 to avoid overwhelming the frontend
                result = session.run("""
                    MATCH (n)-[r]->(m)
                    RETURN n, r, m
                    LIMIT 300
                """)
                
                nodes_dict = {}
                edges_list = []
                
                for record in result:
                    n = record["n"]
                    r = record["r"]
                    m = record["m"]
                    
                    # Process source node
                    # Use element_id if available (Neo4j 5+), fallback to id
                    n_id = getattr(n, "element_id", str(n.id))
                    if n_id not in nodes_dict:
                        nodes_dict[n_id] = {
                            "id": n_id,
                            "label": n.get("name") or n.get("title") or n_id, # Try common name properties
                            "type": list(n.labels)[0] if n.labels else "Node",
                            "properties": dict(n)
                        }
                        
                    # Process target node
                    m_id = getattr(m, "element_id", str(m.id))
                    if m_id not in nodes_dict:
                        nodes_dict[m_id] = {
                            "id": m_id,
                            "label": m.get("name") or m.get("title") or m_id,
                            "type": list(m.labels)[0] if m.labels else "Node",
                            "properties": dict(m)
                        }
                    
                    # Process relationship
                    edges_list.append({
                        "from": n_id,
                        "to": m_id,
                        "type": r.type,
                        "properties": dict(r)
                    })
                
                return {
                    "nodes": list(nodes_dict.values()),
                    "edges": edges_list
                }
        except Exception as e:
            print(f"Error fetching Neo4j graph data: {e}")
            return {"nodes": [], "edges": []}
        finally:
            driver.close()
    
    @staticmethod
    def get_neo4j_stats() -> Dict[str, Any]:
        """
        Get Neo4j graph statistics
        Returns counts of nodes by label and relationships by type
        """
        driver = connect_neo4j()
        if not driver:
            return {"node_counts": [], "rel_counts": []}
        
        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                # Count nodes by label
                node_result = session.run("""
                    MATCH (n)
                    RETURN labels(n)[0] as label, count(*) as count
                    ORDER BY count DESC
                """)
                
                # Count relationships by type
                rel_result = session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(*) as count
                    ORDER BY count DESC
                """)
                
                return {
                    "node_counts": [
                        {"label": record["label"] or "Unlabeled", "count": record["count"]}
                        for record in node_result
                    ],
                    "rel_counts": [
                        {"type": record["type"], "count": record["count"]}
                        for record in rel_result
                    ]
                }
        except Exception as e:
            print(f"Error fetching Neo4j stats: {e}")
            return {"node_counts": [], "rel_counts": []}
        finally:
            driver.close()

    @staticmethod
    def verify_admin_role(user_role: str) -> bool:
        """
        Verify if user has admin role
        
        Args:
            user_role: User's role string
            
        Returns:
            True if user is admin, False otherwise
        """
        return user_role == "admin"
