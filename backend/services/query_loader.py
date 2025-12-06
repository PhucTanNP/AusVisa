"""
Query loader - Load Cypher queries from cypher_queries.cypher file
"""
import os
import re
from typing import Dict

def load_cypher_queries() -> Dict[str, str]:
    """
    Load Cypher queries from cypher_queries.cypher file
    
    Returns:
        Dictionary mapping query names to Cypher query strings
    """
    queries = {}
    
    # Get file path
    current_dir = os.path.dirname(__file__)
    cypher_file = os.path.join(current_dir, '..', 'cypher_queries.cypher')
    
    if not os.path.exists(cypher_file):
        print(f"Warning: {cypher_file} not found, using default queries")
        return get_default_queries()
    
    try:
        with open(cypher_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse queries by sections
        # Format: // 1.1. QUERY_NAME
        #         // Use case: "..."
        #         MATCH ...
        
        # Split by section markers (e.g., // 1.1., // 2.1., etc.)
        sections = re.split(r'//\s+\d+\.\d+\.', content)
        
        for section in sections[1:]:  # Skip first empty section
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            # Extract query name from first line
            first_line = lines[0].strip()
            query_name = first_line.lower().replace(' ', '_').replace('-', '_')
            query_name = re.sub(r'[^\w_]', '', query_name)
            
            # Find the actual Cypher query (starts with MATCH, WITH, etc.)
            query_lines = []
            in_query = False
            
            for line in lines:
                stripped = line.strip()
                
                # Start of query
                if stripped.startswith(('MATCH', 'WITH', 'RETURN', 'OPTIONAL', 'WHERE', 'CREATE', 'MERGE')):
                    in_query = True
                
                # End of query (empty line or next comment)
                if in_query and (not stripped or stripped.startswith('//')):
                    break
                
                if in_query:
                    query_lines.append(line)
            
            if query_lines:
                query = '\n'.join(query_lines).strip()
                if query and len(query) > 10:  # Valid query
                    queries[query_name] = query
        
        print(f"Loaded {len(queries)} queries from {cypher_file}")
        return queries
        
    except Exception as e:
        print(f"Error loading queries: {e}")
        return get_default_queries()


def get_default_queries() -> Dict[str, str]:
    """
    Fallback default queries if file loading fails
    """
    return {
        "find_programs_by_university": """
            MATCH (u:University {name: $university_name})
            MATCH (u)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
                  -[:HAS_LEVEL]->(pl:ProgramLevel {name: $level})
                  -[:OFFERS]->(p:Program)
            OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
            RETURN u.name AS university,
                   p.name AS program_name,
                   p.url AS program_url,
                   p.starting_months AS starting_months,
                   collect({exam: e.name, score: es.value}) AS requirements
            LIMIT 10
        """,
        
        "find_programs_by_ielts": """
            MATCH (p:Program)-[:HAS_REQUIRED]->(es:ExamScore)
                  <-[:HAS_SCORE]-(e:Exam {name: "IELTS"})
            WHERE es.value <= $max_score
            MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)
                  <-[:HAS_LEVEL]-(pg:ProgramGroup)
                  <-[:HAS_PROGRAMS]-(u:University)
            RETURN u.name AS university,
                   p.name AS program_name,
                   es.value AS ielts_required,
                   p.url AS url
            ORDER BY es.value ASC
            LIMIT 10
        """,
        
        "visa_info": """
            MATCH (v:Visa {subclass: $subclass})
            OPTIONAL MATCH (v)-[:HAS_ABOUT_INFO]->(a:AboutInfo)
            RETURN v.name_visa AS visa_name,
                   v.subclass AS subclass,
                   v.url AS official_url,
                   collect({field: a.field, content: a.content}) AS about_information
        """,
        
        "visa_eligibility": """
            MATCH (v:Visa {subclass: $subclass})
                  -[:HAS_ELIGIBILITY_GROUP]->(eg:EligibilityGroup)
                  -[:HAS_REQUIREMENT]->(er:EligibilityRequirement)
            RETURN v.name_visa AS visa_name,
                   eg.group_key AS requirement_group,
                   collect({key: er.key, content: er.content}) AS requirements
            ORDER BY eg.group_key
        """,
        
        "settlement_info": """
            MATCH (cat:SettlementCategory)
            WHERE toLower(cat.name) CONTAINS toLower($keyword)
            MATCH (cat)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
                  -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
            RETURN cat.name AS category,
                   collect(DISTINCT {
                       task_group: tg.name,
                       page_title: sp.title,
                       page_url: sp.url
                   }) AS related_info
            LIMIT 5
        """,
        
        "comprehensive_pathway": """
            MATCH (p:Program)-[:FOCUSES_ON]->(subj:Subject)
            WHERE toLower(subj.name) CONTAINS toLower($field)
            MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
                  <-[:HAS_PROGRAMS]-(u:University)
            OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
            WITH u, p, collect({exam: e.name, score: es.value}) AS requirements
            LIMIT 3
            MATCH (v:Visa {subclass: "500"})
            MATCH (vpr:Visa)
            WHERE vpr.subclass IN ["189", "190"]
            RETURN {
                study: {
                    university: u.name,
                    program: p.name,
                    requirements: requirements,
                    url: p.url
                },
                student_visa: {
                    name: v.name_visa,
                    subclass: v.subclass
                },
                pr_visas: collect(DISTINCT {
                    name: vpr.name_visa,
                    subclass: vpr.subclass
                })
            } AS pathway
        """
    }


def get_query(query_name: str) -> str:
    """
    Get a specific query by name
    
    Args:
        query_name: Name of the query to retrieve
        
    Returns:
        Cypher query string or empty string if not found
    """
    queries = load_cypher_queries()
    return queries.get(query_name, "")


def list_available_queries() -> list:
    """
    List all available query names
    
    Returns:
        List of query names
    """
    queries = load_cypher_queries()
    return sorted(queries.keys())


if __name__ == "__main__":
    # Test the loader
    queries = load_cypher_queries()
    print(f"\nLoaded {len(queries)} queries:")
    for name in sorted(queries.keys())[:10]:
        print(f"  - {name}")
    
    print(f"\n... and {len(queries) - 10} more")
