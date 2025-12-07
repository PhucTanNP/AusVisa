from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Chatbot optimization settings
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes cache

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# CSV Data Paths for import scripts
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ABOUT_CSV = os.getenv("ABOUT_CSV", os.path.join(DATA_DIR, "About_Final_Neo4j.csv"))
ELIG_CSV = os.getenv("ELIG_CSV", os.path.join(DATA_DIR, "Eligibility_Final_Neo4j.csv"))
STEP_CSV = os.getenv("STEP_CSV", os.path.join(DATA_DIR, "Step_Final_Neo4j.csv"))
SETTLEMENT_CSV = os.getenv("SETTLEMENT_CSV", os.path.join(DATA_DIR, "Settlement_All.csv"))
STUDY_CSV = os.getenv("STUDY_CSV", os.path.join(DATA_DIR, "Uni_Info_Program_Final.csv"))

if not GOOGLE_API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY. Put it in .env or environment.")