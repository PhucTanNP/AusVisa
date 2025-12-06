import os
from typing import Any, Optional

import pandas as pd
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError
from dotenv import load_dotenv, find_dotenv

# ============================================================
#  LOAD .env + KẾT NỐI NEO4J AURA
# ============================================================

load_dotenv(find_dotenv(), override=True)


def _env(name: str, required: bool = True, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name, default)
    if required and not v:
        raise RuntimeError(f"Missing env `{name}` in .env")
    return v

def connect_driver():
    """
    Kết nối Neo4j từ .env:
      NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
      NEO4J_USERNAME=neo4j
      NEO4J_PASSWORD=xxxx
      NEO4J_DATABASE=neo4j   (optional)
    """
    uri = _env("NEO4J_URI")
    user = _env("NEO4J_USERNAME")
    pw = _env("NEO4J_PASSWORD")
    db = os.getenv("NEO4J_DATABASE")  # có thể None → dùng default DB

    driver = GraphDatabase.driver(uri, auth=basic_auth(user, pw))
    driver.verify_connectivity()
    return driver, db


# ============================================================
#  UTIL: CLEAN VALUE
# ============================================================

def clean_value(text: Any) -> Optional[str]:
    if pd.isna(text):
        return None
    s = str(text).replace("\n", " ").strip()
    return s if s else None


# ============================================================
#  COMMON HEADER CYPHER
#   VisaType + Visa (có subclass)
# ============================================================

COMMON_HEADER_CYPHER = """
MERGE (t:VisaType {name_display: $type})

MERGE (v:Visa {unique_name_kg: $unique_name_kg})
  ON CREATE SET
    v.name_visa = $name_visa,
    v.url       = $url,
    v.type      = $type,
    v.subclass  = $subclass
  ON MATCH SET
    v.name_visa = coalesce(v.name_visa, $name_visa),
    v.url       = coalesce(v.url,       $url),
    v.type      = coalesce(v.type,      $type),
    v.subclass  = coalesce(v.subclass,  $subclass)

MERGE (v)-[:BELONGS_TO_TYPE]->(t)
"""


# ============================================================
# 1) ABOUT
# ============================================================

def upsert_about_tx(tx, row: dict, content_cols):
    """
    row: 1 dòng từ df_about (có Type, Unique_Name_KG, Name Visa, URL, subclass)
    content_cols: danh sách tên cột nội dung About
    """
    base_params = {
        "type":           row["Type"],
        "unique_name_kg": row["Unique_Name_KG"],
        "name_visa":      row["Name Visa"],
        "url":            row["URL"],
        "subclass":       clean_value(row.get("subclass")),
    }

    for col in content_cols:
        raw_val = row.get(col, None)
        content = clean_value(raw_val)
        if not content:
            continue

        params = base_params | {
            "field":   col,
            "content": content,
        }

        cypher = COMMON_HEADER_CYPHER + """
        // AboutInfo chung theo (field, content)
        MERGE (a:AboutInfo {
            field:   $field,
            content: $content
        })

        MERGE (v)-[:HAS_ABOUT_INFO]->(a)
        """

        tx.run(cypher, **params)


def import_about(driver, db, about_csv_path: str):
    df_about = pd.read_csv(about_csv_path)

    # các cột meta
    common_cols = ["Type", "Unique_Name_KG", "Name Visa", "URL", "subclass"]
    content_cols = [c for c in df_about.columns if c not in common_cols]

    with driver.session(database=db) as session:
        for _, row in df_about.iterrows():
            session.execute_write(upsert_about_tx, row.to_dict(), content_cols)

    print(" Import ABOUT xong")


# ============================================================
# 2) ELIGIBILITY
# ============================================================

def upsert_eligibility_tx(tx, row: dict):
    cypher = COMMON_HEADER_CYPHER + """
    // Group Eligibility: gom chung theo group_key
    MERGE (g:EligibilityGroup {
        group_key: $group_key
    })

    // Requirement: gom chung theo (group_key, content)
    MERGE (r:EligibilityRequirement {
        group_key: $group_key,
        content:   $content
    })
      ON CREATE SET r.key = $key
      ON MATCH SET  r.key = coalesce(r.key, $key)

    MERGE (v)-[:HAS_ELIGIBILITY_GROUP]->(g)
    MERGE (g)-[:HAS_REQUIREMENT]->(r)
    MERGE (v)-[:HAS_ELIGIBILITY_REQUIREMENT]->(r)
    """

    params = {
        "type":           row["Type"],
        "unique_name_kg": row["Unique_Name_KG"],
        "name_visa":      row["Name Visa"],
        "url":            row["URL"],
        "subclass":       clean_value(row.get("subclass")),
        "group_key":      row["group_key"],
        "key":            row["key"],
        "content":        clean_value(row.get("content")),
    }

    if not params["content"]:
        return

    tx.run(cypher, **params)


def import_eligibility(driver, db, elig_csv_path: str):
    df_elig = pd.read_csv(elig_csv_path)
    df_elig = df_elig[df_elig["content"].notna()].copy()

    with driver.session(database=db) as session:
        for _, row in df_elig.iterrows():
            session.execute_write(upsert_eligibility_tx, row.to_dict())

    print(" Import ELIGIBILITY xong")


# ============================================================
# 3) STEP BY STEP
# ============================================================

def upsert_step_tx(tx, row: dict):
    cypher = COMMON_HEADER_CYPHER + """
    // Step: instance riêng cho từng visa
    MERGE (s:VisaStep {
        unique_name_kg: $unique_name_kg,
        step_order:     $step_order
    })
      ON CREATE SET
        s.title = $step_title,
        s.code  = $step_code,
        s.url   = $step_url,
        s.body  = $step_body
      ON MATCH SET
        s.title = coalesce(s.title, $step_title),
        s.code  = coalesce(s.code,  $step_code),
        s.url   = coalesce(s.url,   $step_url),
        s.body  = coalesce(s.body,  $step_body)

    MERGE (v)-[:HAS_STEP]->(s)
    """

    params = {
        "type":           row["Type"],
        "unique_name_kg": row["Unique_Name_KG"],
        "name_visa":      row["Name Visa"],
        "url":            row["URL"],
        "subclass":       clean_value(row.get("subclass")),
        "step_url":       row.get("step_url"),
        "step_order":     int(row["step_order"]),
        "step_code":      row.get("step_code"),
        "step_title":     clean_value(row.get("step_title")),
        "step_body":      clean_value(row.get("step_body")),
    }

    tx.run(cypher, **params)


def import_steps(driver, db, step_csv_path: str):
    df_steps = pd.read_csv(step_csv_path)

    with driver.session(database=db) as session:
        for _, row in df_steps.iterrows():
            session.execute_write(upsert_step_tx, row.to_dict())

    print(" Import STEP xong")


# ============================================================
# 🏁 MAIN
# ============================================================

if __name__ == "__main__":
    # Bạn có thể override bằng ENV nếu muốn
    ABOUT_CSV = os.getenv("ABOUT_CSV") or r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\Final\About_Final_Neo4j.csv"
    ELIG_CSV  = os.getenv("ELIG_CSV")  or r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\Final\Eligibility_Final_Neo4j.csv"
    STEP_CSV  = os.getenv("STEP_CSV")  or r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\Final\Step_Final_Neo4j.csv"

    driver, db = connect_driver()

    try:
        import_about(driver, db, ABOUT_CSV)
        import_eligibility(driver, db, ELIG_CSV)
        import_steps(driver, db, STEP_CSV)

        print("\nDONE! Visa KG (About + Eligibility + Step) da duoc import vao Neo4j Aura.")
    except Neo4jError as e:
        raise RuntimeError(f"Neo4j error: {e}") from e
    finally:
        driver.close()
