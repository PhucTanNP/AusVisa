# Setup Guide - AusVisa Complete System

## Tổng quan

Hệ thống AusVisa bao gồm 3 phần chính:
- **AKE_BE**: Backend API (FastAPI + Neo4j + PostgreSQL)
- **AKE_UI**: Frontend (Next.js)
- **Data Import**: Scripts để import dữ liệu vào Neo4j

## Prerequisites

- Python 3.10+
- Node.js 18+
- Neo4j Aura account (hoặc Neo4j local)
- PostgreSQL database (cho user management)
- Google Gemini API key

## 1. Backend Setup (AKE_BE)

### Bước 1: Install dependencies

```bash
cd d:\Source\CRAWL KG\AKE_BE
pip install -r requirements.txt
```

### Bước 2: Configure environment

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Cập nhật các biến trong `.env`:

```env
# Google Gemini API
GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Neo4j
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# PostgreSQL (cho user management)
DATABASE_URL=postgresql://username:password@localhost:5432/visa_db

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Bước 3: Import data vào Neo4j

**Quan trọng**: Copy các file CSV vào thư mục `data/`:
- `About_Final_Neo4j.csv`
- `Eligibility_Final_Neo4j.csv`
- `Step_Final_Neo4j.csv`
- `Settlement_All.csv`
- `Uni_Info_Program_Final.csv`

Sau đó chạy import:

```bash
# Import tất cả dữ liệu
python scripts/run_all.py

# Hoặc import từng phần
python scripts/import_visa.py
python scripts/import_settlement.py
python scripts/import_study.py
python scripts/import_cross_rel.py
```

### Bước 4: Run backend server

```bash
uvicorn api.server:app --reload
```

Backend sẽ chạy tại: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## 2. Frontend Setup (AKE_UI)

### Bước 1: Install dependencies

```bash
cd d:\Source\CRAWL KG\AKE-UI
npm install
```

### Bước 2: Configure environment

File `.env.local` đã được tạo với:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Bước 3: Run frontend

```bash
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

## 3. Testing

### Test Backend API

```bash
# Test chatbot endpoint
curl -X POST "http://localhost:8000/api/chatbot/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tìm chương trình Master về Computer Science tại UNSW"}'

# Test stats endpoint
curl "http://localhost:8000/api/chatbot/stats"

# Test health check
curl "http://localhost:8000/api/chatbot/health"
```

### Test Frontend

1. Mở browser: http://localhost:3000
2. Click "Trò chuyện với AI"
3. Gửi câu hỏi test
4. Verify response từ backend

## 4. Endpoints

### Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chatbot/query` | Xử lý câu hỏi chatbot |
| GET | `/api/chatbot/stats` | Thống kê hệ thống |
| GET | `/api/chatbot/health` | Health check |
| POST | `/api/users/register` | Đăng ký user |
| POST | `/api/users/login` | Đăng nhập |
| GET | `/api/users/me` | Thông tin user hiện tại |

### Frontend Pages

| Path | Description |
|------|-------------|
| `/` | Landing page |
| `/chat` | Chatbot interface |
| `/login` | Đăng nhập |
| `/register` | Đăng ký |
| `/news` | Tin tức |

## 5. Troubleshooting

### Backend không kết nối được Neo4j

- Kiểm tra `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` trong `.env`
- Verify Neo4j Aura đang chạy
- Test connection: `python -c "from services.neo4j_exec import connect_neo4j; print(connect_neo4j())"`

### Import data bị lỗi

- Kiểm tra các file CSV có tồn tại trong thư mục `data/`
- Xem logs trong thư mục `logs/`
- Verify Neo4j connection

### Frontend không gọi được backend

- Kiểm tra backend đang chạy tại port 8000
- Verify `NEXT_PUBLIC_API_URL` trong `.env.local`
- Check browser console cho CORS errors

### Gemini API errors

- Verify `GOOGLE_API_KEY` trong `.env`
- Check API quota: https://aistudio.google.com/app/apikey
- Đảm bảo model name đúng: `gemini-2.0-flash-exp`

## 6. Development Workflow

### Chạy toàn bộ hệ thống

Terminal 1 - Backend:
```bash
cd d:\Source\CRAWL KG\AKE_BE
uvicorn api.server:app --reload
```

Terminal 2 - Frontend:
```bash
cd d:\Source\CRAWL KG\AKE-UI
npm run dev
```

### Import lại dữ liệu

```bash
cd d:\Source\CRAWL KG\AKE_BE
python scripts/run_all.py
```

## 7. Production Deployment

### Backend

```bash
# Build
pip install -r requirements.txt

# Run with gunicorn
gunicorn api.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
# Build
npm run build

# Start
npm start
```

## 8. Next Steps

1. ✅ Setup backend và frontend
2. ✅ Import dữ liệu vào Neo4j
3. ✅ Test chatbot functionality
4. 🔄 Customize system prompt (`chatbot/system_prompt.txt`)
5. 🔄 Add more query templates
6. 🔄 Enhance UI/UX
7. 🔄 Deploy to production

## Support

Nếu gặp vấn đề, check:
- Backend logs: Console output của uvicorn
- Frontend logs: Browser console
- Import logs: `logs/` directory
- API docs: http://localhost:8000/docs
