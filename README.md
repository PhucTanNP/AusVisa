# AusVisa - AI Chatbot for Australian Visa & Study Abroad

🤖 **AusVisa** là hệ thống chatbot AI thông minh giúp tư vấn về visa Úc, du học, và định cư, sử dụng Neo4j Knowledge Graph và Google Gemini AI.

## ✨ Tính năng

- 🎓 **Tư vấn du học Úc**: Tìm kiếm chương trình, trường đại học phù hợp
- ✈️ **Thông tin visa**: Hướng dẫn chi tiết về các loại visa Úc
- 🏠 **Định cư Úc**: Tư vấn về con đường định cư
- 💬 **Chat AI thông minh**: Sử dụng Google Gemini AI
- 📊 **Knowledge Graph**: Dữ liệu được tổ chức bằng Neo4j
- 🔐 **Xác thực người dùng**: Đăng ký, đăng nhập an toàn
- 💾 **Lịch sử chat**: Lưu trữ và quản lý cuộc trò chuyện

## 🏗️ Kiến trúc

```
AusVisa/
├── backend/           # FastAPI backend
│   ├── api/          # API routes
│   ├── services/     # Business logic
│   ├── models/       # Database models
│   ├── chatbot/      # Chatbot configuration
│   └── data/         # Data files
├── frontend/         # Next.js frontend
│   ├── app/         # Pages
│   ├── components/  # UI components
│   └── lib/         # Utilities
└── docs/            # Documentation
```

## 🚀 Công nghệ

### Backend
- **FastAPI** - Modern Python web framework
- **Google Gemini AI** - Large Language Model
- **Neo4j** - Graph database
- **SQLite** - User & chat history storage
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components

## 📋 Yêu cầu

- Python 3.9+
- Node.js 18+
- Neo4j Database (AuraDB hoặc local)
- Google Gemini API Key

## 🔧 Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/yourusername/AusVisa.git
cd AusVisa
```

### 2. Cài đặt Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env
cp .env.example .env
```

Cập nhật file `.env`:
```env
GOOGLE_API_KEY=your_gemini_api_key
NEO4J_URI=neo4j+s://your-neo4j-uri
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
GEMINI_MODEL=gemini-1.5-flash
SECRET_KEY=your_secret_key_for_jwt
```

### 3. Cài đặt Frontend

```bash
cd ../frontend
npm install

# Tạo file .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 4. Khởi tạo Database

```bash
cd ../backend
python models/database.py
```

## 🎯 Chạy ứng dụng

### Chạy Backend

```bash
cd backend
python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

Backend sẽ chạy tại: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Chạy Frontend

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

## 📚 API Documentation

Sau khi chạy backend, truy cập Swagger UI tại:
```
http://localhost:8000/docs
```

### Main Endpoints

#### Chatbot
- `POST /api/chatbot/query` - Gửi câu hỏi đến chatbot
- `GET /api/chatbot/stats` - Thống kê hệ thống
- `GET /api/chatbot/health` - Health check

#### Users (Coming soon)
- `POST /api/users/register` - Đăng ký tài khoản
- `POST /api/users/login` - Đăng nhập
- `GET /api/users/me` - Thông tin user hiện tại

#### Conversations (Coming soon)
- `POST /api/conversations` - Tạo cuộc trò chuyện mới
- `GET /api/conversations` - Lấy danh sách cuộc trò chuyện
- `GET /api/conversations/{id}` - Chi tiết cuộc trò chuyện
- `POST /api/conversations/{id}/messages` - Thêm tin nhắn

## 🗄️ Database Schema

### SQLite (User & Chat History)
- **users** - Thông tin người dùng
- **conversations** - Cuộc trò chuyện
- **messages** - Tin nhắn trong cuộc trò chuyện

### Neo4j (Knowledge Graph)
- **University** - Trường đại học
- **Program** - Chương trình học
- **Visa** - Loại visa
- **Requirement** - Yêu cầu
- Relationships: OFFERS, REQUIRES, LEADS_TO, etc.

## 🔐 Bảo mật

- ⚠️ **KHÔNG** commit file `.env` lên Git
- ⚠️ **KHÔNG** chia sẻ API keys
- ✅ Sử dụng environment variables
- ✅ JWT tokens cho authentication
- ✅ Password hashing với bcrypt

## 🤝 Đóng góp

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Tác giả

- **Your Name** - [GitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Google Gemini AI
- Neo4j
- FastAPI
- Next.js
- shadcn/ui

## 📞 Liên hệ

- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

---

Made with ❤️ for Vietnamese students dreaming of studying in Australia
