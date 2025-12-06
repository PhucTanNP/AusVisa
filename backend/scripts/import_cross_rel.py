import os
from typing import Optional

from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError
from dotenv import load_dotenv, find_dotenv

# ============================================================
# 🔧 LOAD .env + KẾT NỐI NEO4J AURA
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
# ⚙️ CẤU HÌNH CROSS-MAPPING (CÓ THỂ CHỈNH SAU)
# ============================================================

# Student visa subclass – bạn đã chuẩn hóa subclass thành chuỗi "500" kiểu "500"
STUDENT_VISA_SUBCLASSES = ["500"]

# Skilled / PR visa – dùng cho mapping sang SettlementCategory việc làm, định cư lâu dài
SKILLED_VISA_SUBCLASSES = ["189", "190", "191", "491", "494", "186", "187"]

# Keyword để nối StudyCategory ↔ SettlementCategory
STUDY_SETTLEMENT_KEYWORDS = [
    "education",
    "study",
    "school",
    "training",
    "english",
]


# ============================================================
# 🔗 CÁC HÀM TẠO QUAN HỆ
# ============================================================

def link_student_visas_to_study_levels(session):
    """
    (1) Visa subclass 500 → StudyLevel (Bachelor, Master, Doctor)
    Mối quan hệ: (:Visa)-[:ALLOWS_STUDY_LEVEL]->(:StudyLevel)
    """
    print(" Link Student Visa -> StudyLevel…")
    session.run(
        """
        MATCH (v:Visa)
        WHERE v.subclass IN $subs
        MATCH (sl:StudyLevel)
        MERGE (v)-[:ALLOWS_STUDY_LEVEL]->(sl)
        """,
        subs=STUDENT_VISA_SUBCLASSES,
    )


def link_student_visas_to_universities(session):
    """
    (2) Visa subclass 500 → University
    Mối quan hệ: (:Visa)-[:RELEVANT_FOR_UNIVERSITY]->(:University)
    → Cho phép chatbot trả lời kiểu: "Với visa 500 bạn có thể học tại các trường sau…"
    """
    print(" Link Student Visa -> University…")
    session.run(
        """
        MATCH (v:Visa)
        WHERE v.subclass IN $subs
        MATCH (u:University)
        MERGE (v)-[:RELEVANT_FOR_UNIVERSITY]->(u)
        """,
        subs=STUDENT_VISA_SUBCLASSES,
    )


def link_student_visas_to_program_levels(session):
    """
    (3) Visa subclass 500 → ProgramLevel
    Mối quan hệ: (:Visa)-[:ALLOWS_PROGRAM_LEVEL]->(:ProgramLevel)
    """
    print(" Link Student Visa -> ProgramLevel…")
    session.run(
        """
        MATCH (v:Visa)
        WHERE v.subclass IN $subs
        MATCH (pl:ProgramLevel)
        MERGE (v)-[:ALLOWS_PROGRAM_LEVEL]->(pl)
        """,
        subs=STUDENT_VISA_SUBCLASSES,
    )


def link_skilled_visas_to_settlement_employment(session):
    """
    (4) Skilled / PR visa → SettlementCategory liên quan Employment / Work
    Mối quan hệ: (:Visa)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(:SettlementCategory)
    """
    print("Link Skilled/PR Visa -> SettlementCategory (employment)…")
    session.run(
        """
        MATCH (v:Visa)
        WHERE v.subclass IN $subs
        MATCH (c:SettlementCategory)
        WHERE toLower(c.name) CONTAINS 'employ'
           OR toLower(c.name) CONTAINS 'work'
           OR toLower(c.name) CONTAINS 'job'
        MERGE (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(c)
        """,
        subs=SKILLED_VISA_SUBCLASSES,
    )


def link_student_visas_to_settlement_study_related(session):
    """
    (5) Student visa → SettlementCategory liên quan tới education / english / study
    Mối quan hệ: (:Visa)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(:SettlementCategory)
    """
    print(" Link Student Visa -> SettlementCategory (education/english)…")
    session.run(
        """
        MATCH (v:Visa)
        WHERE v.subclass IN $subs
        MATCH (c:SettlementCategory)
        WHERE
            ANY(kw IN $kws WHERE toLower(c.name) CONTAINS kw)
        MERGE (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(c)
        """,
        subs=STUDENT_VISA_SUBCLASSES,
        kws=[k.lower() for k in STUDY_SETTLEMENT_KEYWORDS],
    )


def link_study_category_to_settlement_category(session):
    """
    (6) StudyCategory ↔ SettlementCategory
    Match tên gần giống nhau (chứa nhau) → tạo quan hệ:
    (:StudyCategory)-[:RELATED_TO_SETTLEMENT_CATEGORY]->(:SettlementCategory)
    """
    print(" Link StudyCategory <-> SettlementCategory (name similarity)…")
    session.run(
        """
        MATCH (sc:StudyCategory), (sc2:SettlementCategory)
        WHERE
            toLower(sc.name) CONTAINS toLower(sc2.name)
            OR toLower(sc2.name) CONTAINS toLower(sc.name)
        MERGE (sc)-[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc2)
        """
    )


def link_university_to_settlement_page(session):
    """
    (7) University → SettlementPage
    Hiện tại không có thông tin city/state để match chính xác,
    nên tạo 1 quan hệ generic:
    (:University)-[:HAS_RELEVANT_SETTLEMENT_INFO]->(:SettlementPage)

    Chatbot có thể dùng để trả lời:
    – 'Bạn học ở Uni X thì nên đọc thêm các trang định cư sau…'
    """
    print(" Link University -> SettlementPage (generic)…")
    session.run(
        """
        MATCH (u:University), (p:SettlementPage)
        MERGE (u)-[:HAS_RELEVANT_SETTLEMENT_INFO]->(p)
        """
    )


# ============================================================
# 🧩 HÀM CHẠY TOÀN BỘ CROSS-REL
# ============================================================

def run_cross_relations(driver, db):
    try:
        with driver.session(database=db) as session:
            # 1) Visa 500 ↔ Study (levels, universities)
            link_student_visas_to_study_levels(session)
            link_student_visas_to_universities(session)
            link_student_visas_to_program_levels(session)

            # 2) Skilled visas ↔ Settlement (việc làm / định cư)
            link_skilled_visas_to_settlement_employment(session)

            # 3) Student visas ↔ Settlement (education-related)
            link_student_visas_to_settlement_study_related(session)

            # 4) StudyCategory ↔ SettlementCategory (dựa trên tên gần giống)
            link_study_category_to_settlement_category(session)

            # 5) University ↔ SettlementPage (generic)
            link_university_to_settlement_page(session)

        print(" DONE CROSS-RELATIONS (Visa <-> Study <-> Settlement)")

    except Neo4jError as e:
        raise RuntimeError(f"Neo4j error: {e}") from e


# ============================================================
# 🏁 MAIN
# ============================================================

if __name__ == "__main__":
    driver, db = connect_driver()
    try:
        run_cross_relations(driver, db)
    finally:
        driver.close()
