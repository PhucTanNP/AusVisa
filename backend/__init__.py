# MongoDB Configuration (for user management - optional)
MONGO_URL=mongodb+srv://AKE-VISA:QMkJyHFsiBwJTO38@cluster0.buzwgzo.mongodb.net/?appName=Cluster0
MONGO_DB_NAME=visa_db

# PostgreSQL Configuration (for user management)
DATABASE_URL=postgresql://username:password@localhost:5432/visa_db

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Neo4j Configuration (REQUIRED for chatbot)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DATABASE=neo4j

# Google Gemini API Configuration (REQUIRED for chatbot)
GOOGLE_API_KEY=your-google-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# CSV Data Paths (optional - defaults to data/ directory)
# ABOUT_CSV=data/About_Final_Neo4j.csv
# ELIG_CSV=data/Eligibility_Final_Neo4j.csv
# STEP_CSV=data/Step_Final_Neo4j.csv
# SETTLEMENT_CSV=data/Settlement_All.csv
# STUDY_CSV=data/Uni_Info_Program_Final.csv
