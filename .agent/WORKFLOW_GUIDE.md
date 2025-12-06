# AusVisa System - Pipeline & Workflow Guide

## 📚 Giới thiệu

Hệ thống AusVisa sử dụng **workflow pipeline** để tự động hóa các tác vụ phổ biến. Document này hướng dẫn cách sử dụng workflow có sẵn và tạo workflow mới.

---

## 🎯 Workflow có sẵn

### `/run-ausvisa-system`

**Mục đích:** Chạy toàn bộ hệ thống AusVisa chatbot

**Khi nào dùng:**
- Lần đầu setup hệ thống
- Sau khi restart máy
- Khi cần chạy lại hệ thống

**Các bước thực hiện:**
1. ✅ Configure environment (.env files)
2. ✅ Install dependencies (Python + Node.js)
3. ✅ Prepare data (Copy CSV files)
4. ✅ Import data to Neo4j
5. ✅ Start backend (port 8000)
6. ✅ Start frontend (port 3000)
7. ✅ Test system

**Cách sử dụng:**
```bash
# Trong chat với AI, gõ:
/run-ausvisa-system
```

AI sẽ tự động thực hiện các bước với `// turbo` annotation (auto-run safe commands).

---

## 🔧 Cách sử dụng Workflow

### Phương pháp 1: Slash Command

```bash
# Gõ trong chat:
/run-ausvisa-system

# AI sẽ tự động:
# - Đọc workflow
# - Thực hiện từng bước
# - Auto-run các lệnh an toàn
# - Yêu cầu confirm cho lệnh nguy hiểm
```

### Phương pháp 2: Yêu cầu trực tiếp

```
"Chạy workflow run-ausvisa-system"
"Thực hiện workflow để chạy hệ thống"
"Follow workflow /run-ausvisa-system"
```

---

## 📝 Cấu trúc Workflow File

### Location
```
d:\Source\CRAWL KG\.agent\workflows\<workflow-name>.md
```

### Format

```markdown
---
description: Short description of what this workflow does
---

# Workflow: <Name>

## Step 1: <Title>

Description of what to do

```bash
// turbo  # This command will auto-run
command-to-execute
```

## Step 2: <Title>

```bash
# No turbo annotation - will ask for confirmation
potentially-dangerous-command
```

---

## Troubleshooting

Common issues and solutions
```

### Turbo Annotations

**`// turbo`** - Đặt trên dòng trước command:
- Command sẽ **tự động chạy** không cần confirm
- Chỉ dùng cho lệnh **an toàn** (read-only, install, start server)
- **KHÔNG dùng** cho lệnh xóa, sửa file, deploy

**`// turbo-all`** - Đặt ở đầu workflow:
- **TẤT CẢ** commands trong workflow sẽ auto-run
- Cực kỳ nguy hiểm - chỉ dùng cho workflow đã test kỹ

---

## 🎨 Tạo Workflow mới

### Bước 1: Tạo file

```bash
# Tạo file trong .agent/workflows/
touch .agent/workflows/my-workflow.md
```

### Bước 2: Viết nội dung

```markdown
---
description: Deploy application to production
---

# Workflow: Deploy to Production

## Step 1: Run tests

```bash
// turbo
npm test
```

## Step 2: Build application

```bash
// turbo
npm run build
```

## Step 3: Deploy

```bash
# No turbo - requires confirmation
./deploy.sh production
```

## Troubleshooting

### Build fails
- Check Node.js version
- Clear cache: `npm cache clean --force`
```

### Bước 3: Sử dụng

```bash
/my-workflow
```

---

## 📋 Best Practices

### ✅ DO

- Sử dụng `// turbo` cho lệnh an toàn (install, start, test)
- Viết mô tả rõ ràng cho mỗi bước
- Thêm troubleshooting section
- Test workflow trước khi commit
- Dùng descriptive names (deploy-app, setup-db)

### ❌ DON'T

- Dùng `// turbo` cho lệnh xóa file
- Dùng `// turbo` cho lệnh deploy production
- Dùng `// turbo-all` trừ khi workflow cực kỳ đơn giản
- Viết workflow quá dài (>10 steps)
- Skip troubleshooting section

---

## 🔍 Workflow Examples

### Example 1: Simple Install

```markdown
---
description: Install project dependencies
---

# Workflow: Install Dependencies

## Step 1: Install Python packages

```bash
// turbo
pip install -r requirements.txt
```

## Step 2: Install Node packages

```bash
// turbo
npm install
```
```

### Example 2: Database Setup

```markdown
---
description: Setup and seed database
---

# Workflow: Setup Database

## Step 1: Create database

```bash
# Requires confirmation
createdb myapp_db
```

## Step 2: Run migrations

```bash
// turbo
python manage.py migrate
```

## Step 3: Seed data

```bash
// turbo
python manage.py seed
```
```

### Example 3: Development Server

```markdown
---
description: Start development servers
---

# Workflow: Start Dev Servers

// turbo-all

## Step 1: Start backend

```bash
uvicorn main:app --reload
```

## Step 2: Start frontend

```bash
npm run dev
```
```

---

## 🚀 Advanced Usage

### Conditional Steps

```markdown
## Step 3: Deploy (Production only)

**Skip this step if in development**

```bash
./deploy.sh
```
```

### Multiple Commands

```markdown
## Step 2: Setup environment

```bash
// turbo
cp .env.example .env
```

Then edit `.env` and fill in:
- DATABASE_URL
- API_KEY
```

### Error Handling

```markdown
## Troubleshooting

### Error: Port already in use

```bash
// turbo
lsof -ti:8000 | xargs kill -9
```

### Error: Module not found

```bash
// turbo
pip install --upgrade -r requirements.txt
```
```

---

## 📊 Workflow Lifecycle

```
1. User triggers workflow
   ↓
2. AI reads workflow file
   ↓
3. AI executes each step:
   - Turbo commands → Auto-run
   - Normal commands → Ask confirmation
   ↓
4. AI monitors output
   ↓
5. If error → Show troubleshooting
   ↓
6. Workflow complete
```

---

## 🎯 Current Workflows

| Workflow | Description | Turbo | Steps |
|----------|-------------|-------|-------|
| `/run-ausvisa-system` | Run complete AusVisa system | Partial | 7 |

---

## 💡 Tips & Tricks

### Tip 1: Chain Workflows

```
"Run /setup-database then /run-ausvisa-system"
```

### Tip 2: Dry Run

```
"Show me what /run-ausvisa-system will do without executing"
```

### Tip 3: Skip Steps

```
"Run /run-ausvisa-system but skip step 3"
```

### Tip 4: Debug Mode

```
"Run /run-ausvisa-system with verbose output"
```

---

## 📖 Reference

### Workflow File Locations

```
.agent/
└── workflows/
    ├── run-ausvisa-system.md    # Main system workflow
    ├── setup-database.md         # Database setup (example)
    └── deploy-production.md      # Deploy workflow (example)
```

### Turbo Annotation Rules

| Annotation | Behavior | Use Case |
|------------|----------|----------|
| `// turbo` | Auto-run single command | Safe commands |
| `// turbo-all` | Auto-run all commands | Fully automated workflows |
| (none) | Ask confirmation | Dangerous commands |

---

## 🆘 Getting Help

### View Available Workflows

```
"List all available workflows"
"Show me workflow options"
```

### View Workflow Content

```
"Show me the /run-ausvisa-system workflow"
"What does /setup-database do?"
```

### Create Custom Workflow

```
"Create a workflow to backup database"
"Help me write a deployment workflow"
```

---

## ✅ Quick Reference

**Run workflow:**
```bash
/workflow-name
```

**Create workflow:**
```bash
.agent/workflows/name.md
```

**Turbo command:**
```bash
// turbo
safe-command
```

**No turbo:**
```bash
dangerous-command
```

---

**Happy Workflow Automation! 🚀**
