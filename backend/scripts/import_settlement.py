import os
import re
from typing import Optional

import pandas as pd
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError
from dotenv import load_dotenv, find_dotenv

# ============================================================
# LOAD .env + KẾT NỐI NEO4J AURA
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
      NEO4J_PASSWORD=xxxxx
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
# CLEAN / PARSE HELPERS
# ============================================================

def clean(x):
    if pd.isna(x):
        return ""
    x = str(x).replace("\xa0", " ")
    x = re.sub(r"\s+", " ", x)
    return x.strip()


def parse_hierarchy(path):
    """
    "Employment -> Finding a job -> Applying for a job"
      → ['Employment', 'Finding a job', 'Applying for a job']
    """
    if not path:
        return []
    return [clean(p) for p in str(path).split("->") if clean(p)]


def get_label(level):
    return {
        "h2": "MainSection",
        "h3": "Subsection",
        "h4": "DetailSection",
        "h5": "SpecificSection",
    }.get(level, "Section")


# ============================================================
# IMPORT SETTLEMENT
# ============================================================

def import_settlement(driver, db, csv_path: str):
    df = pd.read_csv(csv_path)

    try:
        with driver.session(database=db) as session:
            # -----------------------------------------
            # (Optional) CONSTRAINTS cho Settlement KG
            # -----------------------------------------
            constraints = """
            CREATE CONSTRAINT IF NOT EXISTS FOR (c:SettlementCategory)   REQUIRE c.name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (t:SettlementTaskGroup)  REQUIRE t.name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (p:SettlementPage)       REQUIRE p.title IS UNIQUE;
            """
            for stmt in [q.strip() for q in constraints.split(";") if q.strip()]:
                session.execute_write(lambda tx, q=stmt: tx.run(q).consume())

            # -----------------------------------------
            # 1) SettlementCategory
            # -----------------------------------------
            for cat in df["TYPE"].dropna().unique():
                name = clean(cat)
                if not name:
                    continue
                session.run(
                    "MERGE (:SettlementCategory {name:$n})",
                    n=name,
                )

            # -----------------------------------------
            # 2) SettlementTaskGroup
            # -----------------------------------------
            for _, row in df[["TYPE", "TYPE_TASK"]].drop_duplicates().iterrows():
                cat = clean(row["TYPE"])
                task = clean(row["TYPE_TASK"])
                if not cat or not task:
                    continue

                session.run(
                    """
                    MATCH (c:SettlementCategory {name:$cat})
                    MERGE (t:SettlementTaskGroup {name:$task})
                    MERGE (c)-[:HAS_GROUP]->(t)
                    """,
                    cat=cat,
                    task=task,
                )

            # -----------------------------------------
            # 3) SettlementPage
            # -----------------------------------------
            for _, row in df[["TYPE_TASK", "page_title", "url"]].drop_duplicates().iterrows():
                task = clean(row["TYPE_TASK"])
                title = clean(row["page_title"])
                url = clean(row["url"])

                if not task or not title:
                    continue

                session.run(
                    """
                    MATCH (t:SettlementTaskGroup {name:$task})
                    MERGE (p:SettlementPage {title:$title})
                      ON CREATE SET p.url = $url
                      SET p.url = coalesce(p.url, $url)
                    MERGE (t)-[:CONTAINS_SETTLEMENT_PAGE]->(p)
                    """,
                    task=task,
                    title=title,
                    url=url,
                )

            # -----------------------------------------
            # 4) Sections (MainSection/Subsection/Detail/Specific)
            # -----------------------------------------
            all_sections = {}

            for _, r in df.iterrows():
                page_title = clean(r["page_title"])
                path = clean(r["path"])
                url = clean(r["url"])

                if not path or not page_title:
                    continue

                parts = parse_hierarchy(path)
                for i, part in enumerate(parts):
                    if i == 0:
                        # cấp 0 = tiêu đề page, bỏ qua
                        continue

                    # h2 cho level1, h3 cho level2, h4 cho level3, h5 cho level4+
                    level = ["h2", "h3", "h4", "h5"][min(i - 1, 3)]
                    current_path = " -> ".join(parts[: i + 1])
                    parent_path = " -> ".join(parts[:i])  # có thể dùng sau nếu muốn nối parent-child

                    all_sections[(page_title, current_path)] = {
                        "title": part,
                        "level": level,
                        "parent_path": parent_path,
                        "url": url,
                    }

            # Tạo Section nodes + link tới SettlementPage
            for (page, path), info in all_sections.items():
                label = get_label(info["level"])
                title = info["title"]
                url = info["url"]

                session.run(
                    f"""
                    MATCH (p:SettlementPage {{title:$page}})
                    MERGE (s:{label} {{path:$path}})
                      ON CREATE SET
                        s.title = $title,
                        s.url   = $url
                      SET
                        s.url   = coalesce(s.url, $url)
                    MERGE (p)-[:HAS_SETTLEMENT_SECTION]->(s)
                    """,
                    page=page,
                    path=path,
                    title=title,
                    url=url,
                )

        print(" DONE SETTLEMENT IMPORT")

    except Neo4jError as e:
        raise RuntimeError(f"Neo4j error: {e}") from e


# ============================================================
# 🏁 MAIN
# ============================================================

if __name__ == "__main__":
    # Có thể override bằng ENV
    CSV_PATH = (
        os.getenv("SETTLEMENT_CSV")
        or r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\Crawl_Dinh_Cu\Settlement_All.csv"
    )

    driver, db = connect_driver()
    try:
        import_settlement(driver, db, CSV_PATH)
    finally:
        driver.close()
