# AusVisa - Hệ thống Chatbot Tư vấn Visa Úc

Hệ thống chatbot AI tích hợp Neo4j Knowledge Graph, PostgreSQL, FastAPI và Next.js để tư vấn visa Úc.

## ✨ Tính năng chính

### 🤖 Chatbot AI
- **RAG với Neo4j**: Truy vấn Knowledge Graph bằng Text-to-Cypher
- **Gemini AI**: Tích hợp Google Gemini 2.0 Flash
- **Streaming Response**: Real-time streaming cho câu trả lời mượt mà
- **Chat History**: Lưu trữ và quản lý lịch sử hội thoại

### 👥 Quản lý người dùng
- **Authentication**: JWT-based với secure password hashing
- **User Roles**: Phân quyền user/admin
- **Session Management**: Theo dõi phiên đăng nhập và thống kê
- **Admin Panel**: Quản lý users, activate/suspend/delete

### 📊 Neo4j Analytics
- **Knowledge Graph Visualization**: Biểu đồ thống kê dữ liệu Neo4j
- **Interactive Charts**: Bar & Pie charts với filtering
- **Node Statistics**: Thống kê theo loại node và relationship

---

## 📋 Yêu cầu hệ thống

- **Docker Desktop** (cho PostgreSQL, pgAdmin)
- **Python 3.10+**
- **Node.js 18+** và npm
- **Neo4j** (local hoặc Aura)
- **Google API Key** (cho Gemini)

---

## 🚀 Hướng dẫn cài đặt

### Bước 1: Clone Project

```bash
git clone https://github.com/your-username/AusVisa.git
cd AusVisa
```

### Bước 2: Setup Backend

#### 2.1. Tạo file .env

Tạo file `.env` trong thư mục `backend` với nội dung:

```env
# Database
DATABASE_URL=postgresql://postgres:123456@localhost:5433/visa_db

# JWT
SECRET_KEY=your-secret-key-change-in-production-make-it-long-and-random
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DATABASE=neo4j

# Google Gemini
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp
```

#### 2.2. Cài đặt Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 2.3. Khởi động Docker Services

```bash
docker-compose up -d
```

#### 2.4. Khởi tạo Database

```bash
python scripts/init_db.py
```

Script sẽ tạo:
- Tables: users, chat_sessions, chat_messages
- Admin account mặc định: `admin@ausvisa.ai` / `admin123`

### Bước 3: Setup Frontend

```bash
cd ../frontend
npm install
```

### Bước 4: Khởi động Services

#### Terminal 1 - Backend API:
```bash
cd backend
python -m api.server
# hoặc
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

---

## 🎯 Truy cập ứng dụng

### Frontend
- **Trang chủ**: http://localhost:3000
- **Đăng ký**: http://localhost:3000/register
- **Đăng nhập**: http://localhost:3000/login
- **Chat**: http://localhost:3000/chat
- **Admin Panel**: http://localhost:3000/admin *(chỉ admin)*

### Backend
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Database
- **pgAdmin**: http://localhost:5050
  - Email: `admin@ausvisa.ai`
  - Password: `admin123`

---

## 🛠️ Cập nhật Dependencies

### Backend (Python)
```bash
cd backend
pip install --upgrade -r requirements.txt
```

### Frontend (Node.js)
```bash
cd frontend
npm update
# hoặc cập nhật toàn bộ
npm install
```

---

## 📚 Cấu trúc Project

```
AusVisa/
├── backend/
│   ├── api/
│   │   ├── server.py           # FastAPI application
│   │   ├── chatbot_routes.py   # Chatbot endpoints
│   │   ├── user_routes.py      # Authentication endpoints
│   │   └── admin_routes.py     # Admin management endpoints
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models
│   │   └── user.py             # Pydantic schemas
│   ├── services/
│   │   ├── auth.py             # JWT & password hashing
│   │   ├── user_service.py     # User CRUD operations
│   │   ├── admin_service.py    # Admin operations & Neo4j stats
│   │   └── chatbot_service.py  # RAG chatbot logic
│   ├── scripts/
│   │   └── init_db.py          # Database initialization
│   ├── docker-compose.yml      # PostgreSQL + pgAdmin
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables
│
└── frontend/
    ├── app/
    │   ├── page.tsx            # Home/Landing page
    │   ├── login/              # Login page
    │   ├── register/           # Registration page
    │   ├── chat/               # Chat interface
    │   └── admin/              # Admin dashboard
    ├── components/
    │   ├── admin/
    │   │   ├── knowledge-graph.tsx   # Neo4j analytics charts
    │   │   ├── user-management.tsx   # User management UI
    │   │   └── admin-sidebar.tsx     # Admin navigation
    │   ├── ui/                       # Shadcn UI components
    │   └── protected-route.tsx       # Route protection
    ├── contexts/
    │   └── auth-context.tsx          # Authentication context
    ├── lib/
    │   └── api.ts                    # API client
    └── package.json                  # Node dependencies
```

---

## 🔍 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM cho PostgreSQL
- **Neo4j**: Knowledge Graph database
- **Google Gemini**: AI model (2.0 Flash)
- **LangGraph**: Orchestration cho RAG pipeline
- **JWT**: Token-based authentication

### Frontend
- **Next.js 16**: React framework với App Router
- **TypeScript**: Type safety
- **Tailwind CSS 4**: Utility-first styling
- **Shadcn UI**: Premium component library
- **Recharts**: Data visualization
- **Lucide Icons**: Beautiful icons

### Infrastructure
- **Docker**: Containerization
- **PostgreSQL**: Relational database
- **pgAdmin**: Database management

---

## 🔐 Security Features

- ✅ JWT-based authentication
- ✅ Bcrypt password hashing
- ✅ Protected routes (client & server)
- ✅ CORS configuration
- ✅ Role-based access control
- ✅ Session tracking

---

## 📝 API Endpoints

### Authentication
- `POST /api/users/register` - Đăng ký user mới
- `POST /api/users/login` - Đăng nhập
- `GET /api/users/me` - Lấy thông tin user hiện tại
- `POST /api/users/logout` - Đăng xuất

### Chatbot
- `POST /api/chatbot/stream` - Chat với streaming response
- `GET /api/chatbot/sessions` - Lấy danh sách chat sessions
- `GET /api/chatbot/sessions/{id}` - Lấy chi tiết session
- `DELETE /api/chatbot/sessions/{id}` - Xóa session

### Admin
- `GET /api/admin/users` - Danh sách users
- `PATCH /api/admin/users/{id}/activate` - Activate user
- `PATCH /api/admin/users/{id}/suspend` - Suspend user
- `DELETE /api/admin/users/{id}` - Xóa user
- `GET /api/admin/neo4j/stats` - Thống kê Neo4j
- `GET /api/admin/neo4j/graph` - Lấy graph data

---

## 🧪 Testing

### Test Registration
```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"test123"}'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

## 🐛 Troubleshooting

### Port đã được sử dụng
Thay đổi ports trong `docker-compose.yml`:
```yaml
ports:
  - "5434:5432"  # PostgreSQL
  - "5051:80"    # pgAdmin
```

### Không kết nối được Database
```bash
docker-compose ps
docker-compose logs postgres
docker-compose restart postgres
```

### Reset Database hoàn toàn
```bash
cd backend
docker-compose down -v
docker-compose up -d
python scripts/init_db.py
```

---

## 🚀 Deploy to GitHub

### Cập nhật dependencies
```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd ../frontend
npm update
```

### Git commands
```bash
# Initialize git (nếu chưa có)
git init

# Add all files
git add .

# Commit
git commit -m "feat: Complete AusVisa chatbot system with Neo4j analytics"

# Add remote repository
git remote add origin https://github.com/your-username/AusVisa.git

# Push to GitHub
git push -u origin main
```

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs: `docker-compose logs -f`
2. Kiểm tra services: `docker-compose ps`
3. Xem API docs: http://localhost:8000/docs
4. Reset database: `docker-compose down -v && docker-compose up -d`

---

## 🎉 Quick Start

```bash
# 1. Clone & setup
git clone https://github.com/your-username/AusVisa.git
cd AusVisa

# 2. Backend
cd backend
docker-compose up -d
python scripts/init_db.py
python -m api.server

# 3. Frontend (terminal mới)
cd ../frontend
npm install
npm run dev

# 4. Truy cập
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
# Admin: admin@ausvisa.ai / admin123
```

---

## 📄 License

MIT License - Feel free to use for your projects!

---

Enjoy your AusVisa Chatbot! 🚀🇦🇺
