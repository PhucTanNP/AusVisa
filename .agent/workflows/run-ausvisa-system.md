---
description: Complete workflow to run AusVisa chatbot system
---

# Workflow: Run AusVisa Chatbot System

## Prerequisites Check

- [ ] Python 3.13+ installed
- [ ] Node.js 18+ installed  
- [ ] Neo4j Aura account created
- [ ] Google Gemini API key obtained
- [ ] CSV data files available

---

## Step 1: Configure Environment

### Backend (.env)

```bash
cd d:\Source\CRAWL KG\AKE_BE

# Copy example file
cp .env.example .env

# Edit .env and fill in:
# GOOGLE_API_KEY=your-gemini-api-key
# NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your-password
# NEO4J_DATABASE=neo4j
# GEMINI_MODEL=gemini-2.5-flash
```

### Frontend (.env.local)

```bash
cd d:\Source\CRAWL KG\AKE-UI

# File already created with:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Step 2: Install Dependencies

### Backend

```bash
cd d:\Source\CRAWL KG\AKE_BE

// turbo
python -m pip install fastapi uvicorn neo4j pandas google-generativeai python-dotenv pydantic langgraph langchain-google-genai passlib bcrypt pyjwt sqlalchemy
```

### Frontend

```bash
cd d:\Source\CRAWL KG\AKE-UI

// turbo
npm install --force
```

---

## Step 3: Prepare Data

### Copy CSV Files

Copy these 5 files to `d:\Source\CRAWL KG\AKE_BE\data\`:

1. `About_Final_Neo4j.csv`
2. `Eligibility_Final_Neo4j.csv`
3. `Step_Final_Neo4j.csv`
4. `Settlement_All.csv`
5. `Uni_Info_Program_Final.csv`

### Import to Neo4j

```bash
cd d:\Source\CRAWL KG\AKE_BE

// turbo
python scripts/run_all.py
```

**Expected output:**
```
Starting data import...
✓ Importing visa data...
✓ Importing settlement data...
✓ Importing study data...
✓ Creating cross-relationships...
Import complete!
```

---

## Step 4: Start Backend

```bash
cd d:\Source\CRAWL KG\AKE_BE

// turbo
python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

**Wait for:**
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

---

## Step 5: Start Frontend

**Open NEW terminal:**

```bash
cd d:\Source\CRAWL KG\AKE-UI

// turbo
npm run dev
```

**Wait for:**
```
✓ Ready in XXXms
- Local: http://localhost:3000
```

**Keep this terminal open!**

---

## Step 6: Test System

### Browser Test

1. Open: http://localhost:3000
2. Click: "Trò chuyện với AI"
3. Send message: "Xin chào"
4. Verify response from chatbot

### API Test

```bash
// turbo
curl -X POST "http://localhost:8000/api/chatbot/query" -H "Content-Type: application/json" -d "{\"question\": \"Hello\"}"
```

### Check Stats

```bash
// turbo
curl http://localhost:8000/api/chatbot/stats
```

**Expected:**
```json
{
  "universities": XX,
  "programs": XXX,
  "visas": XX
}
```

---

## Step 7: Monitor Logs

### Backend Logs (Terminal 1)

Watch for:
- ✅ `POST /api/chatbot/query` - Successful requests
- ❌ `500 Internal Server Error` - Check error details

### Frontend Logs (Terminal 2)

Watch for:
- ✅ Page compilations
- ❌ Build errors

### Browser Console (F12)

Check for:
- Network requests to backend
- API responses
- JavaScript errors

---

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError`
```bash
python -m pip install <missing-module>
```

**Error:** `Neo4j connection failed`
- Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env
- Verify Neo4j Aura is running

### Frontend won't start

**Error:** `npm install` fails
```bash
npm install --force
```

**Error:** `Module not found`
```bash
rm -rf node_modules package-lock.json
npm install --force
```

### Chatbot returns errors

**Error:** `500 Internal Server Error`
- Check backend logs for details
- Verify GOOGLE_API_KEY is valid
- Check Neo4j connection

**Error:** `No data returned`
- Verify data import completed
- Check Neo4j has data: `curl http://localhost:8000/api/chatbot/stats`

---

## Stop System

### Stop Backend
In Terminal 1: Press `Ctrl+C`

### Stop Frontend
In Terminal 2: Press `Ctrl+C`

---

## Quick Restart

```bash
# Terminal 1 - Backend
cd d:\Source\CRAWL KG\AKE_BE
python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd d:\Source\CRAWL KG\AKE-UI
npm run dev
```

---

## URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main UI |
| Chat Page | http://localhost:3000/chat | Chatbot interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Status check |

---

## Next Steps

After system is running:
1. Test various chatbot queries
2. Customize system prompt in `chatbot/system_prompt.txt`
3. Add more Cypher query templates
4. Enhance UI/UX
5. Deploy to production

---

**Workflow Complete!** 🎉
