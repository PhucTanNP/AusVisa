# 🚀 AusVisa - Hướng dẫn Deploy lên GitHub

## 📋 Chuẩn bị trước khi deploy

### 1. Cập nhật Dependencies

#### Backend (Python)
```bash
cd backend
pip install --upgrade -r requirements.txt
```

#### Frontend (Node.js)
```bash
cd frontend
npm update
```

### 2. Kiểm tra file .gitignore

Đảm bảo các file sau KHÔNG được commit:
```gitignore
# Backend
backend/.env
backend/__pycache__/
backend/*.pyc
backend/.pytest_cache/

# Frontend
frontend/.env.local
frontend/node_modules/
frontend/.next/
frontend/out/

# Database
*.db
postgres_data/

# IDE
.vscode/
.idea/
*.swp
```

### 3. Tạo file .env.example

#### Backend (.env.example)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5433/visa_db

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# Google Gemini
GOOGLE_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp
```

#### Frontend (.env.local.example)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🔧 Các bước Deploy

### Bước 1: Khởi tạo Git Repository (nếu chưa có)

```bash
cd "d:\Source\CRAWL KG\AusVisa"
git init
```

### Bước 2: Tạo .gitignore (nếu chưa có)

```bash
# Tạo file .gitignore ở root
cat > .gitignore << 'EOF'
# Environment files
**/.env
**/.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.pytest_cache/

# Node
node_modules/
.next/
out/
.turbo/

# Database
*.db
**/postgres_data/
**/pgadmin_data/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
EOF
```

### Bước 3: Add và Commit files

```bash
# Add tất cả files
git add .

# Kiểm tra files sẽ được commit
git status

# Commit
git commit -m "feat: Complete AusVisa chatbot system

- Implement JWT authentication with user/admin roles
- Add RAG chatbot with Neo4j Knowledge Graph
- Create admin panel with user management
- Add Neo4j analytics with interactive charts
- Implement streaming chat responses
- Add session and message history tracking"
```

### Bước 4: Tạo Remote Repository trên GitHub

1. Truy cập https://github.com
2. Click **"New repository"**
3. Điền thông tin:
   - **Repository name**: `AusVisa`
   - **Description**: `AI Chatbot for Australian Visa Consultation with Neo4j Knowledge Graph`
   - **Visibility**: Public hoặc Private (tùy chọn)
4. **KHÔNG** chọn "Initialize with README" (vì đã có sẵn)
5. Click **"Create repository"**

### Bước 5: Connect Local với GitHub

```bash
# Add remote repository
git remote add origin https://github.com/your-username/AusVisa.git

# Kiểm tra remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### Bước 6: Verify trên GitHub

1. Refresh trang GitHub repository
2. Kiểm tra:
   - ✅ README.md hiển thị đầy đủ
   - ✅ File structure đúng
   - ✅ .env KHÔNG có trong repository
   - ✅ All code files đã được upload

---

## 📦 Update sau này

### Khi có thay đổi code:

```bash
# Kiểm tra files đã thay đổi
git status

# Add files mới/đã sửa
git add .

# Commit với message rõ ràng
git commit -m "fix: Update Neo4j analytics charts filtering"

# Push lên GitHub
git push
```

### Các loại commit message:

- `feat:` - Tính năng mới
- `fix:` - Sửa bug
- `docs:` - Cập nhật documentation
- `style:` - Format code, không thay đổi logic
- `refactor:` - Refactor code
- `test:` - Thêm tests
- `chore:` - Cập nhật dependencies, build tools

---

## 🔒 Security Checklist

Trước khi push lên GitHub:

- [ ] File `.env` đã có trong `.gitignore`
- [ ] Tạo file `.env.example` với placeholder values
- [ ] Không có API keys hoặc passwords trong code
- [ ] SECRET_KEY được generate random
- [ ] PostgreSQL password đã thay đổi từ default
- [ ] Admin password đã thay đổi sau lần đầu login

---

## 🌐 Clone Project từ GitHub

### Người khác muốn chạy project:

```bash
# 1. Clone repository
git clone https://github.com/your-username/AusVisa.git
cd AusVisa

# 2. Copy và config .env files
cd backend
cp .env.example .env
# Edit .env với credentials thực

cd ../frontend
cp .env.local.example .env.local
# Edit nếu cần

# 3. Install dependencies
cd ../backend
pip install -r requirements.txt

cd ../frontend
npm install

# 4. Setup database
cd ../backend
docker-compose up -d
python scripts/init_db.py

# 5. Run services
# Terminal 1
python -m api.server

# Terminal 2
cd ../frontend
npm run dev
```

---

## 📊 GitHub Repository Setup

### Recommended settings:

1. **About section**:
   - Description: `🤖 AI Chatbot for Australian Visa Consultation with Neo4j Knowledge Graph`
   - Topics: `chatbot`, `neo4j`, `fastapi`, `nextjs`, `gemini-ai`, `rag`, `knowledge-graph`
   - Website: Your demo URL (nếu có)

2. **README badges** (optional):
```markdown
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![Neo4j](https://img.shields.io/badge/Neo4j-5.14+-blue)
```

3. **Branch protection**:
   - Protect `main` branch
   - Require pull request reviews (nếu team)

---

## 🎯 Quick Deploy Commands

```bash
# >> Workflow hoàn chỉnh <<

# 1. Update dependencies
cd backend && pip install --upgrade -r requirements.txt
cd ../frontend && npm update

# 2. Test local
cd ../backend && python -m api.server &
cd ../frontend && npm run dev

# 3. Git workflow
cd ..
git add .
git commit -m "feat: Your commit message"
git push

# Done! ✅
```

---

## 📞 Troubleshooting Deploy

### Lỗi: Permission denied (publickey)
```bash
# Tạo SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add SSH key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy và paste vào GitHub Settings > SSH Keys
```

### Lỗi: Repository not found
```bash
# Kiểm tra remote URL
git remote -v

# Update remote URL
git remote set-url origin https://github.com/your-username/AusVisa.git
```

### Lỗi: Merge conflicts
```bash
# Pull latest changes
git pull origin main

# Resolve conflicts trong editor
# Sau đó:
git add .
git commit -m "Merge conflicts resolved"
git push
```

---

## ✅ Post-Deployment Checklist

- [ ] README.md hiển thị đúng trên GitHub
- [ ] Dependencies đã được update
- [ ] .env files không có trong repo
- [ ] Clone và test từ GitHub để đảm bảo hoạt động
- [ ] Documentation đầy đủ cho người mới
- [ ] Commit messages rõ ràng và có ý nghĩa

---

Happy Deploying! 🚀
