# Debug Guide - Backend bị treo

## 🔍 Hiện trạng

**Services đang chạy:**
- ✅ Backend: Port 8000 (PID 19852) - LISTENING
- ✅ Frontend: Port 3000 (PID 19852) - LISTENING

**Vấn đề:**
- ❌ Backend không response khi curl
- ⏳ Backend có thể đang loading hoặc bị lỗi

---

## 🛠️ Cách kiểm tra

### 1. Xem logs trong terminal backend

**Trong terminal đang chạy backend**, tìm dòng:
```
INFO: Application startup complete.
```

**Nếu THẤY:** ✅ Backend OK  
**Nếu KHÔNG THẤY:** ❌ Backend bị lỗi khi start

### 2. Kiểm tra lỗi

**Tìm các dòng lỗi:**
- `RuntimeError: Missing GOOGLE_API_KEY`
- `ModuleNotFoundError`
- `ImportError`
- `SyntaxError`

### 3. Test API

**Mở browser:**
```
http://localhost:8000/docs
```

**Nếu load được:** ✅ Backend OK  
**Nếu không load:** ❌ Backend bị lỗi

---

## 🔧 Các lỗi thường gặp

### Lỗi 1: Missing GOOGLE_API_KEY

**Triệu chứng:**
```
RuntimeError: Missing GOOGLE_API_KEY
```

**Nguyên nhân:**
- File `.env` không có GOOGLE_API_KEY
- File `.env` có lỗi format
- File `.env` không được load

**Fix:**
```bash
cd d:\Source\CRAWL KG\AusVisa\backend

# Kiểm tra file .env
cat .env | grep GOOGLE_API_KEY

# Nếu rỗng hoặc không có, thêm vào:
echo "GOOGLE_API_KEY=your-actual-api-key" >> .env

# Restart backend
# Ctrl+C trong terminal backend
# Chạy lại: python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

### Lỗi 2: Module not found

**Triệu chứng:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Fix:**
```bash
cd d:\Source\CRAWL KG\AusVisa\backend
python -m pip install xxx
```

### Lỗi 3: Port already in use

**Triệu chứng:**
```
OSError: [Errno 98] Address already in use
```

**Fix:**
```bash
# Kill process cũ
lsof -ti:8000 | xargs kill -9

# Hoặc trên Windows:
netstat -ano | findstr :8000
# Tìm PID, sau đó:
taskkill /PID <PID> /F
```

---

## ✅ Checklist Debug

1. [ ] Xem logs trong terminal backend
2. [ ] Tìm dòng "Application startup complete"
3. [ ] Kiểm tra có lỗi không
4. [ ] Test http://localhost:8000/docs
5. [ ] Kiểm tra file .env có GOOGLE_API_KEY
6. [ ] Restart backend nếu cần

---

## 📋 Logs cần xem

**Terminal Backend - Tìm:**
```
INFO: Started server process [XXXX]
INFO: Waiting for application startup.
INFO: Application startup complete.
```

**Nếu thấy 3 dòng này:** ✅ Backend OK

**Nếu thấy lỗi trước dòng "startup complete":** ❌ Fix lỗi đó

---

## 🚀 Quick Fix

**Nếu backend vẫn bị treo:**

1. **Dừng backend:** Ctrl+C
2. **Kiểm tra .env:**
   ```bash
   cd d:\Source\CRAWL KG\AusVisa\backend
   cat .env
   ```
3. **Đảm bảo có:**
   ```
   GOOGLE_API_KEY=AIza...
   NEO4J_URI=neo4j+s://...
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=...
   ```
4. **Chạy lại:**
   ```bash
   python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
   ```
5. **Chờ thấy:** `Application startup complete.`

---

**Bạn đang thấy gì trong terminal backend?**
