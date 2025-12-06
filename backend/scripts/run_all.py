import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv, find_dotenv

# ============================================================
# CẤU HÌNH
# ============================================================

SCRIPTS = [
    r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\IMPORT_FINAL\import_visa.py",
    r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\IMPORT_FINAL\import_settlement.py",
    r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\IMPORT_FINAL\import_study.py",
    r"C:\Users\PAT95\OneDrive - The University of Technology\Desktop\Kysu_Ki1\CK_CNTT\IMPORT_FINAL\import_cross_rel.py",
]

LOG_DIR = Path("logs")

load_dotenv(find_dotenv(), override=True)


# ============================================================
# NEO4J KẾT NỐI & THỐNG KÊ
# ============================================================

def connect_driver():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pw = os.getenv("NEO4J_PASSWORD")
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    if not uri or not user or not pw:
        raise RuntimeError("Thiếu biến môi trường NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD trong .env")

    driver = GraphDatabase.driver(uri, auth=basic_auth(user, pw))
    driver.verify_connectivity()
    return driver, db


def get_graph_stats(driver, db):
    """Trả về (num_nodes, num_relationships)."""
    with driver.session(database=db) as session:
        nodes = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        rels  = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    return nodes, rels


# ============================================================
# TIỆN ÍCH LOG
# ============================================================

def create_log_file(prefix: str = "run_all") -> Path:
    LOG_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"{prefix}_{ts}.log"
    return log_path


def log(msg: str, log_file: Path | None = None):
    """In ra console và (nếu có) ghi vào file log tổng."""
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {msg}"
    print(line)
    if log_file is not None:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def write_raw_to_file(path: Path, header: str, content: str):
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n===== {header} =====\n")
        if content:
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")


def run_script(script_name: str, pipeline_log: Path, driver, db):
    """
    Chạy 1 script:
    - Tạo log riêng: logs/<script>_YYYYMMDD_HHMMSS.log
    - Ghi stdout/stderr vào log riêng + pipeline log
    - Đếm nodes/relationships trước và sau
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_stem = Path(script_name).stem
    per_script_log = LOG_DIR / f"{script_stem}_{ts}.log"

    log(f"==============================", pipeline_log)
    log(f"▶ BẮT ĐẦU CHẠY: {script_name}", pipeline_log)
    log(f"   Log riêng: {per_script_log}", pipeline_log)
    log(f"==============================", pipeline_log)

    # Thống kê trước khi chạy
    nodes_before, rels_before = get_graph_stats(driver, db)
    log(f"[BEFORE {script_name}] Nodes: {nodes_before}, Relationships: {rels_before}", pipeline_log)

    start = datetime.now()

    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=True,
        text=True,
        check=False,
    )

    duration = (datetime.now() - start).total_seconds()

    # Ghi stdout/stderr vào log riêng
    write_raw_to_file(per_script_log, f"{script_name} STDOUT", result.stdout)
    write_raw_to_file(per_script_log, f"{script_name} STDERR", result.stderr)

    # Đồng thời vẫn log tóm tắt stdout/stderr vào pipeline log (nếu muốn gọn hơn có thể bỏ)
    if result.stdout:
        log(f"[{script_name}] Có STDOUT (xem chi tiết trong {per_script_log.name})", pipeline_log)
    if result.stderr:
        log(f"[{script_name}] Có STDERR (xem chi tiết trong {per_script_log.name})", pipeline_log)

    if result.returncode != 0:
        log(
            f"❌ LỖI: {script_name} (exit code {result.returncode}, took {duration:.2f} s)",
            pipeline_log,
        )
        return False

    # Thống kê sau khi chạy
    nodes_after, rels_after = get_graph_stats(driver, db)
    dn = nodes_after - nodes_before
    dr = rels_after - rels_before

    log(f"✅ HOÀN THÀNH: {script_name} (took {duration:.2f} s)", pipeline_log)
    log(
        f"[AFTER {script_name}] Nodes: {nodes_after} (Δ {dn}), "
        f"Relationships: {rels_after} (Δ {dr})",
        pipeline_log,
    )

    return True


# ============================================================
# MAIN PIPELINE
# ============================================================

if __name__ == "__main__":
    pipeline_log = create_log_file(prefix="run_all")
    log("🚀 BẮT ĐẦU PIPELINE IMPORT (Visa + Settlement + Study + Cross-Rel)", pipeline_log)
    log(f"📄 Pipeline log: {pipeline_log.resolve()}", pipeline_log)

    # Kiểm tra file tồn tại
    for s in SCRIPTS:
        if not os.path.exists(s):
            log(f"❌ File KHÔNG TỒN TẠI: {s}", pipeline_log)
            log("⛔ DỪNG PIPELINE do thiếu file.", pipeline_log)
            sys.exit(1)

    # Kết nối Neo4j để đọc stats
    try:
        driver, db = connect_driver()
    except Exception as e:
        log(f"❌ LỖI KẾT NỐI NEO4J: {e}", pipeline_log)
        sys.exit(1)

    overall_start = datetime.now()
    ok = True

    for script in SCRIPTS:
        success = run_script(script, pipeline_log, driver, db)
        if not success:
            ok = False
            log("⛔ PIPELINE DỪNG DO LỖI Ở SCRIPT TRÊN.", pipeline_log)
            break

    total_time = (datetime.now() - overall_start).total_seconds()

    if ok:
        log("======================================", pipeline_log)
        log(f"🎉 TẤT CẢ IMPORT CHẠY THÀNH CÔNG! Tổng thời gian: {total_time:.2f} s", pipeline_log)
        log("======================================", pipeline_log)
        sys.exit(0)
    else:
        log("======================================", pipeline_log)
        log(f"⚠️ PIPELINE KẾT THÚC VỚI LỖI. Tổng thời gian: {total_time:.2f} s", pipeline_log)
        log("📌 Xem chi tiết log từng file trong thư mục: {LOG_DIR}", pipeline_log)
        log("======================================", pipeline_log)
        sys.exit(1)
