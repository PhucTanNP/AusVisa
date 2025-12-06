import os
import re
import json
import ast
import unicodedata
from urllib.parse import urlsplit, urlunsplit
from typing import List, Dict, Any, Iterable, Optional

import pandas as pd
from neo4j.exceptions import Neo4jError
from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv, find_dotenv

# ============================================================
# 🔧 LOAD ENV + CONNECT NEO4J AURA
# ============================================================

load_dotenv(find_dotenv(), override=True)

def _env(name: str, required: bool = True, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name, default)
    if required and not v:
        raise RuntimeError(f"Missing env `{name}` in .env")
    return v

def connect_driver():
    uri  = _env("NEO4J_URI")
    user = _env("NEO4J_USERNAME")
    pw   = _env("NEO4J_PASSWORD")
    db   = os.getenv("NEO4J_DATABASE")

    driver = GraphDatabase.driver(uri, auth=basic_auth(user, pw))
    driver.verify_connectivity()
    return driver, db

# ============================================================
# 🔧 TEXT CLEANING UTILS
# ============================================================

ZWS_RE = re.compile(r"[\u200B-\u200F\uFEFF]")

def clean_text(x):
    """Remove invisible unicode, normalize whitespace, remove \\xa0."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    s = ZWS_RE.sub("", str(x)).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()

def slugify(s: str) -> str:
    """Convert to URL-friendly identifier."""
    t = clean_text(s)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t or "na"

def normalize_url(u: str) -> str:
    u = clean_text(u)
    if not u:
        return ""
    try:
        parts = urlsplit(u)
        if not parts.scheme and not parts.netloc:
            return re.sub(r"[?#].*$", "", u).rstrip("/")
        scheme = (parts.scheme or "").lower()
        netloc = (parts.netloc or "").lower()
        path   = (parts.path or "").rstrip("/")
        return urlunsplit((scheme, netloc, path, "", ""))
    except Exception:
        return u.rstrip("/")

# ============================================================
# 🔧 STUDY-SPECIFIC HELPERS
# ============================================================

def parse_exam_scores(s):
    """Exam Scores field may contain Python dict, JSON or malformed."""
    s = clean_text(s)
    if not s:
        return {}
    try:
        if s.startswith("{") and s.endswith("}"):
            try:
                return json.loads(s.replace("'", '"'))
            except Exception:
                return ast.literal_eval(s)
        return ast.literal_eval(s)
    except Exception:
        return {}

def parse_score(raw):
    """Parse score value: '6.5+' → (6.5, True, '6.5+')"""
    r = clean_text(raw)
    if not r:
        return 0.0, False, ""
    plus = r.endswith("+")
    try:
        val = float(r.rstrip("+").strip())
    except ValueError:
        val = 0.0
    return val, plus, r

def detect_program_type(name: str) -> str:
    n = (name or "").lower()
    if "bachelor" in n:
        return "Bachelor"
    if "doctor" in n or "phd" in n:
        return "Doctor"
    return "Master"

MONTHS = {"jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"}

def extract_months(s: str | None) -> list[str]:
    if not s:
        return []
    tokens = re.split(r"[,/;]\s*|\s+", s)
    out = []
    for t in tokens:
        if not t:
            continue
        k = t[:3].lower()
        if k in MONTHS:
            out.append(t[:3].title())
    # unique preserving order
    seen, res = set(), []
    for m in out:
        if m not in seen:
            seen.add(m)
            res.append(m)
    return res

def _chunks(it: Iterable[Dict[str, Any]], size: int):
    batch = []
    for x in it:
        batch.append(x)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

LEVEL_TITLE = {
    "bachelor": "Bachelor",
    "master": "Master",
    "doctor": "Doctor"
}

# ============================================================
# 📥 MAIN IMPORT FUNCTION (BEGINNING)
# ============================================================

def import_study_data(csv_path: str, wipe: bool = False, batch_size: int = 1000):
    """
    Import toàn bộ KG DU HỌC vào Neo4j Aura.
    Đây là phiên bản tối ưu đã chuẩn hóa Category → StudyCategory.
    """
    driver, db = connect_driver()

    try:
        # ============================================================
        # 1) ĐỌC CSV + CHUẨN HOÁ DATAFRAME
        # ============================================================
        df = pd.read_csv(csv_path, encoding="utf-8-sig").fillna("")

        if "university_name" not in df.columns and "name_university" in df.columns:
            df["university_name"] = df["name_university"]

        if "record_type" not in df.columns:
            raise ValueError("CSV missing required column `record_type`")

        df["record_type_norm"] = df["record_type"].astype(str).str.strip().str.lower()
        df_prog = df[df["record_type_norm"].eq("program")].copy()
        df_info = df[df["record_type_norm"].isin(["infomation", "information"])].copy()

        def uniq(series) -> List[str]:
            return sorted({clean_text(v) for v in series if clean_text(v)})

        # Lookup values
        levels   = [{"level": v} for v in uniq(df_prog.get("study_level", []))]
        modes    = [{"mode": v}  for v in uniq(df_prog.get("study_mode", []))]
        cats     = [{"name": v}  for v in uniq(df_prog.get("category", []))]
        subjects = [{"name": v}  for v in uniq(df_prog.get("main_subject", []))]
        degrees  = [{"code": v}  for v in uniq(df_prog.get("degree", []))]

        unis_all = sorted({clean_text(v) for v in df.get("university_name", []) if clean_text(v)})
        unis = [{"name": u} for u in unis_all]

        # Exams
        lang = {"IELTS", "TOEFL", "PTE Academic", "Cambridge CAE Advanced"}
        acad = {"SAT", "International Baccalaureate", "ATAR"}

        exam_names = set()
        for raw in df_prog.get("exam_scores", []):
            exam_names.update(parse_exam_scores(raw).keys())

        exams = [
            {
                "name": ex,
                "type": (
                    "Language" if ex in lang else
                    ("Academic" if ex in acad else "Standardized")
                ),
            }
            for ex in sorted(exam_names)
        ]

        # ============================================================
        # 2) BUILD PROGRAM STRUCTURES
        # ============================================================
        programs   = []
        scores     = []
        majors_rel = []
        months_rel = []
        components = []

        for _, row in df_prog.iterrows():
            uni    = clean_text(row.get("university_name"))
            pname  = clean_text(row.get("program_name"))
            if not uni or not pname:
                continue

            degree = clean_text(row.get("degree"))
            slevel = clean_text(row.get("study_level"))
            smode  = clean_text(row.get("study_mode"))
            cat    = clean_text(row.get("category"))
            subj   = clean_text(row.get("main_subject"))
            smonth = clean_text(row.get("starting_months"))
            desc   = clean_text(row.get("description"))
            url    = normalize_url(clean_text(row.get("url")))

            relation = clean_text(row.get("relation")) or "single"
            majoring = clean_text(row.get("majoring in"))

            progA   = clean_text(row.get("program_name_A"))
            progB   = clean_text(row.get("program_name_B"))
            lvlAraw = clean_text(row.get("degree_level_A")).lower()
            lvlBraw = clean_text(row.get("degree_level_B")).lower()

            ptype = detect_program_type(pname)
            uid   = f"{slugify(uni)}|{slugify(pname)}"

            programs.append({
                "uid": uid,
                "uni": uni,
                "name": pname,
                "url": url,
                "ptype": ptype,
                "smonths": smonth,
                "desc": desc,
                "degree": degree,
                "slevel": slevel,
                "smode": smode,
                "cat": cat,
                "subj": subj,
                "relation": relation,
            })

            if majoring:
                majors_rel.append({"uid": uid, "major": majoring})

            for mon in extract_months(smonth):
                months_rel.append({"uid": uid, "month": mon})

            # Combined programs
            if relation in ("combined", "combined_cross_level"):
                lvlA = LEVEL_TITLE.get(lvlAraw) or detect_program_type(progA)
                lvlB = LEVEL_TITLE.get(lvlBraw) or detect_program_type(progB)

                if progA:
                    components.append({
                        "parent_uid": uid,
                        "comp_uid": f"{uid}#comp::{slugify(progA)}",
                        "uni": uni,
                        "name": progA,
                        "level": lvlA,
                        "pos": 1,
                    })
                if progB:
                    components.append({
                        "parent_uid": uid,
                        "comp_uid": f"{uid}#comp::{slugify(progB)}",
                        "uni": uni,
                        "name": progB,
                        "level": lvlB,
                        "pos": 2,
                    })

            ex_map = parse_exam_scores(row.get("exam_scores"))
            for ex_name, raw in ex_map.items():
                val, plus, rtext = parse_score(raw)
                scores.append({
                    "uid": uid,
                    "exam": ex_name,
                    "val": float(val),
                    "plus": bool(plus),
                    "raw": rtext,
                })

        # Info sections
        info_cols = [
            ("overview", "Overview"),
            ("campus_locations", "Campus Locations"),
            ("admission_bachelor", "Admission Bachelor"),
            ("admission_master", "Admission Master"),
            ("cost_accommodation", "Cost Accommodation"),
            ("cost_food", "Cost Food"),
            ("cost_transport", "Cost Transport"),
            ("cost_utilities", "Cost Utilities"),
        ]
        infos = []
        for _, row in df_info.iterrows():
            uni = clean_text(row.get("university_name"))
            if not uni:
                continue
            url = clean_text(row.get("url"))
            for col, key in info_cols:
                val = clean_text(row.get(col))
                if val:
                    infos.append({
                        "uni": uni,
                        "key": key,
                        "val": val,
                        "url": url,
                    })

        # ============================================================
        # 3) BẮT ĐẦU GHI VÀO NEO4J
        # ============================================================

        def _run(session, q, **params):
            return session.execute_write(lambda tx: tx.run(q, **params).consume())

        with driver.session(database=db) as session:
            # ----- CONSTRAINTS -----
            print("Creating CONSTRAINTS...")

            CONSTRAINTS = """
            CREATE CONSTRAINT IF NOT EXISTS FOR (ug:UniversityGroup) REQUIRE ug.name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (u:University)       REQUIRE u.name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (pg:ProgramGroup)    REQUIRE pg.university_name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (pl:ProgramLevel)    REQUIRE (pl.university_name, pl.name) IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (p:Program)          REQUIRE p.uid IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (e:Exam)             REQUIRE e.name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (x:ExamScore)        REQUIRE (x.exam, x.value, x.plus) IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (ip:InfoPage)        REQUIRE ip.university_name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (is:InfoSection)     REQUIRE (is.university_name, is.key) IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (sc:StudyCategory)   REQUIRE sc.name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (s:Subject)          REQUIRE s.name IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (d:Degree)           REQUIRE d.code IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (sl:StudyLevel)      REQUIRE sl.level IS UNIQUE;
            CREATE CONSTRAINT IF NOT EXISTS FOR (sm:StudyMode)       REQUIRE sm.mode IS UNIQUE;
            """
            for stmt in [q.strip() for q in CONSTRAINTS.split(";") if q.strip()]:
                _run(session, stmt)
            print("   Done CONSTRAINTS\n")

            # ----- Lookup nodes -----
            print(" Import LOOKUP nodes…")
            if levels:
                _run(session, "UNWIND $rows AS r MERGE (:StudyLevel {level:r.level})", rows=levels)
            if modes:
                _run(session, "UNWIND $rows AS r MERGE (:StudyMode {mode:r.mode})", rows=modes)
            if cats:
                _run(session, "UNWIND $rows AS r MERGE (:StudyCategory {name:r.name})", rows=cats)
            if subjects:
                _run(session, "UNWIND $rows AS r MERGE (:Subject {name:r.name})", rows=subjects)
            if degrees:
                _run(session, "UNWIND $rows AS r MERGE (:Degree {code:r.code})", rows=degrees)
            if exams:
                _run(session, """
                UNWIND $rows AS r
                MERGE (e:Exam {name:r.name})
                  ON CREATE SET e.type = r.type, e.created = datetime()
                """, rows=exams)
            print("    Lookup nodes imported\n")

            # ----- Universities + ProgramGroup + ProgramLevel + InfoPage -----
            print(" Import UNIVERSITIES…")
            if unis:
                _run(session, """
                UNWIND $rows AS r
                MERGE (u:University {name:r.name})
                WITH u
                MERGE (ug:UniversityGroup {name:$g})
                MERGE (ug)-[:HAS_UNIVERSITY]->(u)
                MERGE (pg:ProgramGroup {university_name:u.name})
                  ON CREATE SET pg.name = u.name + ' Programs', pg.created = datetime()
                MERGE (u)-[:HAS_PROGRAMS]->(pg)
                FOREACH (lvl IN ['Bachelor','Master','Doctor'] |
                    MERGE (pl:ProgramLevel {university_name:u.name, name:lvl})
                    MERGE (pg)-[:HAS_LEVEL]->(pl)
                )
                MERGE (ip:InfoPage {university_name:u.name})
                  ON CREATE SET ip.name = u.name + ' Info', ip.created = datetime()
                MERGE (u)-[:HAS_INFO]->(ip)
                """, rows=unis, g="Australian Universities")
            print("    Universities imported\n")

            # ----- PROGRAMS (cha: single + combined wrapper) -----
            print(" Import PROGRAMS…")

            if programs:
                q_programs = """
                UNWIND $rows AS p
                MATCH (pl:ProgramLevel {university_name:p.uni, name:p.ptype})

                MERGE (pr:Program {uid:p.uid})
                  ON CREATE SET
                    pr.university_name = p.uni,
                    pr.name            = p.name,
                    pr.program_type    = p.ptype,
                    pr.created         = datetime(),
                    pr.url             = p.url,
                    pr.urls            = CASE WHEN p.url = '' THEN [] ELSE [p.url] END,
                    pr.is_component    = false,
                    pr.parent_uid      = NULL

                  SET pr.starting_months = p.smonths,
                      pr.description     = p.desc,
                      pr.relation        = p.relation,
                      pr.degree_code     = p.degree,
                      pr.study_level     = p.slevel,
                      pr.study_mode      = p.smode,
                      pr.category        = p.cat,
                      pr.main_subject    = p.subj

                // cập nhật url & urls nếu có nhiều bản ghi trùng uid
                SET pr.url = CASE
                    WHEN p.url <> '' THEN p.url
                    ELSE pr.url
                END,
                pr.urls = CASE
                    WHEN p.url = '' OR pr.urls IS NULL OR p.url IN pr.urls THEN
                      coalesce(pr.urls, CASE WHEN p.url = '' THEN [] ELSE [p.url] END)
                    ELSE pr.urls + p.url
                END

                MERGE (pl)-[:OFFERS]->(pr)

                // Degree (reference)
                FOREACH (deg IN CASE WHEN p.degree = '' THEN [] ELSE [p.degree] END |
                  MERGE (d:Degree {code:deg})
                  MERGE (pr)-[:AWARDS]->(d)
                )

                WITH pr, p, p.slevel AS lv, p.smode AS md, p.cat AS ct, p.subj AS sj

                OPTIONAL MATCH (sl:StudyLevel    {level:lv})
                OPTIONAL MATCH (sm:StudyMode     {mode:md})
                OPTIONAL MATCH (sc:StudyCategory {name:ct})
                OPTIONAL MATCH (sb:Subject       {name:sj})

                FOREACH (_ IN CASE WHEN lv = '' OR sl IS NULL THEN [] ELSE [1] END |
                  MERGE (pr)-[:STUDY_LEVEL]->(sl)
                )
                FOREACH (_ IN CASE WHEN md = '' OR sm IS NULL THEN [] ELSE [1] END |
                  MERGE (pr)-[:STUDY_MODE]->(sm)
                )
                FOREACH (_ IN CASE WHEN ct = '' OR sc IS NULL THEN [] ELSE [1] END |
                  MERGE (pr)-[:IN_STUDY_CATEGORY]->(sc)
                )
                FOREACH (_ IN CASE WHEN sj = '' OR sb IS NULL THEN [] ELSE [1] END |
                  MERGE (pr)-[:FOCUSES_ON]->(sb)
                )
                """

                for batch in _chunks(programs, batch_size):
                    _run(session, q_programs, rows=batch)

            print("    Programs imported\n")

            # ----- MAJORS -----
            print(" Import MAJORS…")

            if majors_rel:
                for batch in _chunks(majors_rel, batch_size):
                    _run(session, """
                    UNWIND $rows AS r
                    MATCH (pr:Program {uid:r.uid})
                    MERGE (m:Major {name:r.major})
                    MERGE (pr)-[:HAS_MAJOR]->(m)
                    """, rows=batch)

            print("    Majors imported\n")

            # ----- STARTING MONTHS -----
            print(" Import STARTING MONTHS…")

            if months_rel:
                for batch in _chunks(months_rel, batch_size):
                    _run(session, """
                    UNWIND $rows AS r
                    MATCH (pr:Program {uid:r.uid})
                    MERGE (mm:Month {name:r.month})
                    MERGE (pr)-[:STARTS_IN]->(mm)
                    """, rows=batch)

            print("    Months imported\n")

            # ----- COMBINED COMPONENTS -----
            print(" Import COMBINED PROGRAM COMPONENTS…")

            if components:
                for batch in _chunks(components, batch_size):
                    _run(session, """
                    UNWIND $rows AS r
                    MATCH (parent:Program {uid:r.parent_uid})
                    MATCH (pl:ProgramLevel {university_name:r.uni, name:r.level})

                    MERGE (c:Program {uid:r.comp_uid})
                      ON CREATE SET
                        c.university_name = parent.university_name,
                        c.name            = r.name,
                        c.program_type    = r.level,
                        c.is_component    = true,
                        c.parent_uid      = parent.uid,
                        c.created         = datetime()

                    MERGE (parent)-[:HAS_COMPONENT {pos:r.pos}]->(c)
                    MERGE (c)-[:HAS_LEVEL]->(pl)
                    """, rows=batch)

            print("    Combined components imported\n")

            # ----- EXAM SCORES -----
            print(" Import EXAM SCORES…")

            if scores:
                for batch in _chunks(scores, batch_size):
                    _run(session, """
                    UNWIND $rows AS s
                    MATCH (pr:Program {uid:s.uid})
                    MERGE (e:Exam {name:s.exam})
                    MERGE (sc:ExamScore {exam:s.exam, value:s.val, plus:s.plus})
                      ON CREATE SET sc.raw = s.raw
                    MERGE (e)-[:HAS_SCORE]->(sc)
                    MERGE (pr)-[:HAS_REQUIRED]->(sc)
                    """, rows=batch)

            print("    Exam scores imported\n")

            # ----- INFO PAGES + INFO SECTIONS -----
            print(" Import INFO PAGES & SECTIONS…")

            if infos:
                for batch in _chunks(infos, batch_size):
                    _run(session, """
                    UNWIND $rows AS r
                    MERGE (ip:InfoPage {university_name:r.uni})
                    MERGE (sec:InfoSection {university_name:r.uni, key:r.key})
                      ON CREATE SET sec.created = datetime()
                      SET sec.content = r.val,
                          sec.url     = r.url
                    MERGE (ip)-[:HAS_SECTION]->(sec)
                    """, rows=batch)

            print("    Info pages & sections imported\n")

            print(" DONE STUDY KG IMPORT")

    except Neo4jError as e:
        raise RuntimeError(f"Neo4j error: {e}") from e

    finally:
        driver.close()

# ============================================================
# 🏁 MAIN ENTRY
# ============================================================

if __name__ == "__main__":
    # Bạn có thể set CSV_PATH trong .env, nếu không thì dùng path mặc định
    CSV_PATH = os.getenv("CSV_PATH") or r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\Crawl_DuHoc\Chuan hoa & Import Neo4j\Uni_Info_Program_Final.csv"
    import_study_data(CSV_PATH, wipe=False, batch_size=1000)
