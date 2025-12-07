---
description: Hướng dẫn khởi động lại toàn bộ hệ thống AusVisa
---

# 🚀 Workflow: Khởi động lại hệ thống AusVisa

## 📋 Kiểm tra trước khi bắt đầu

- [ ] Docker Desktop đang chạy
- [ ] Python 3.10+ đã cài đặt
- [ ] Node.js 18+ đã cài đặt
- [ ] Neo4j đang chạy (local hoặc Aura)
- [ ] Google API Key đã có

---

## Bước 1: Kill tất cả processes cũ (QUAN TRỌNG!)

### Kiểm tra processes đang chạy

```bash
// turbo
netstat -ano | findstr :8000
```

### Kill backend processes nếu có

Nếu thấy processes đang chạy trên port 8000, kill chúng:

```bash
# Thay <PID> bằng số process ID thực tế
taskkill /PID <PID> /F
```

**Hoặc:** Bấm `Ctrl+C` trong tất cả terminals đang chạy uvicorn

### Kiểm tra frontend processes

```bash
// turbo
netstat -ano | findstr :3000
```

Kill nếu cần thiết.

---

## Bước 2: Khởi động Docker Services

```bash
cd "d:\Source\CRAWL KG\AusVisa\backend"

// turbo
docker-compose up -d
```

**Chờ đợi:** PostgreSQL và pgAdmin khởi động (khoảng 10-15 giây)

### Kiểm tra services

```bash
// turbo
docker-compose ps
```

**Kết quả mong đợi:**
- `visa_postgres` - UP (port 5433)
- `visa_pgadmin` - UP (port 5050)

---

## Bước 3: Khởi động Backend API

**Mở Terminal 1:**

```bash
cd "d:\Source\CRAWL KG\AusVisa\backend"

# Activate virtual environment (nếu có)
source venv/Scripts/activate

// turbo
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

**Chờ thấy:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**⚠️ GIỮ TERMINAL NÀY MỞ!**

### Test backend

**Mở terminal mới:**

```bash
// turbo
curl http://localhost:8000/health
```

**Kết quả:** `{"status":"healthy"}` hoặc `{"status":"ok"}`

---

## Bước 4: Khởi động Frontend

**Mở Terminal 2 (terminal mới):**

```bash
cd "d:\Source\CRAWL KG\AusVisa\frontend"

// turbo
npm run dev
```

**Chờ thấy:**
```
✓ Ready in XXXms
- Local: http://localhost:3000
```

**⚠️ GIỮ TERMINAL NÀY MỞ!**

---

## Bước 5: Test toàn bộ hệ thống

### 5.1. Test Backend API

Mở browser: http://localhost:8000/docs

Bạn sẽ thấy Swagger UI với các endpoints:
- `/health` - Health check
- `/api/auth/register` - Đăng ký
- `/api/auth/login` - Đăng nhập
- `/api/chatbot/query` - Chat
- `/api/admin/*` - Admin endpoints

### 5.2. Test Frontend

Mở browser: http://localhost:3000

Bạn sẽ thấy trang chủ AusVisa

### 5.3. Test Đăng ký User

1. Vào: http://localhost:3000/register
2. Nhập thông tin:
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `test123`
3. Click "Register"
4. Nếu thành công → redirect về `/login`

**Nếu lỗi:**
- Mở DevTools (F12) → Console tab
- Mở Network tab
- Thử register lại
- Kiểm tra error message

### 5.4. Test Đăng nhập

1. Vào: http://localhost:3000/login
2. Nhập email và password vừa đăng ký
3. Click "Login"
4. Nếu thành công → redirect về `/chat`

### 5.5. Test Chatbot

1. Sau khi login, vào: http://localhost:3000/chat
2. Gõ câu hỏi: "Xin chào"
3. Chatbot sẽ trả lời

**Test câu hỏi về visa:**
- "Visa 189 là gì?"
- "Điều kiện xin visa Úc?"
- "Các loại visa Úc có những gì?"

---

## Bước 6: Truy cập pgAdmin (Optional)

1. Mở: http://localhost:5050
2. Login:
   - Email: `admin@ausvisa.ai`
   - Password: `admin123`
3. Add Server (lần đầu):
   - Name: `AusVisa DB`
   - Host: `postgres` (hoặc `localhost`)
   - Port: `5432` (internal) hoặc `5433` (external)
   - Database: `visa_db`
   - Username: `postgres`
   - Password: `123456`

### Xem users đã đăng ký

```sql
SELECT email, username, role, is_active, created_at 
FROM users 
ORDER BY created_at DESC;
```

---

## 🛑 Dừng hệ thống

### Dừng Frontend
Trong Terminal 2: Bấm `Ctrl+C`

### Dừng Backend
Trong Terminal 1: Bấm `Ctrl+C`

### Dừng Docker (Optional)

```bash
cd "d:\Source\CRAWL KG\AusVisa\backend"
docker-compose down
```

**Lưu ý:** Dừng Docker sẽ mất kết nối database nhưng data vẫn còn.

**Xóa hết data (CẢNH BÁO!):**
```bash
docker-compose down -v
```

---

## 🔄 Khởi động lại nhanh (Quick Restart)

Nếu đã chạy ít nhất 1 lần và muốn khởi động lại:

```bash
# Terminal 1 - Backend
cd "d:\Source\CRAWL KG\AusVisa\backend"
docker-compose up -d
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend  
cd "d:\Source\CRAWL KG\AusVisa\frontend"
npm run dev
```

---

## 🔍 Troubleshooting

### Lỗi: Port 8000 đã được sử dụng

```bash
# Tìm process
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Lỗi: Cannot connect to database

```bash
# Kiểm tra Docker
docker-compose ps

# Xem logs
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

### Lỗi: CORS blocked

**Nguyên nhân:** Có nhiều backend processes chạy cùng lúc

**Giải pháp:**
1. Kill tất cả processes trên port 8000
2. Chỉ chạy 1 backend duy nhất
3. Hard refresh browser: `Ctrl+Shift+R`

### Lỗi: Module not found (Python)

```bash
cd "d:\Source\CRAWL KG\AusVisa\backend"
pip install -r requirements.txt
```

### Lỗi: npm packages not found

```bash
cd "d:\Source\CRAWL KG\AusVisa\frontend"
rm -rf node_modules package-lock.json
npm install
```

### Reset database hoàn toàn

```bash
cd "d:\Source\CRAWL KG\AusVisa\backend"
docker-compose down -v
docker-compose up -d
python scripts/init_db.py
```

---

## 📚 URLs tham khảo

| Service | URL | Mô tả |
|---------|-----|-------|
| Frontend | http://localhost:3000 | Trang chủ |
| Register | http://localhost:3000/register | Đăng ký |
| Login | http://localhost:3000/login | Đăng nhập |
| Chat | http://localhost:3000/chat | Chatbot |
| Admin | http://localhost:3000/admin | Admin panel |
| Backend API | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Kiểm tra backend |
| pgAdmin | http://localhost:5050 | Quản lý database |

---

## ✅ Checklist hoàn thành

- [ ] Docker services đang chạy
- [ ] Backend API đang chạy (port 8000)
- [ ] Frontend đang chạy (port 3000)
- [ ] Test health check thành công
- [ ] Test đăng ký user thành công
- [ ] Test đăng nhập thành công
- [ ] Test chatbot thành công

---

**🎉 Hệ thống đã sẵn sàng!**
