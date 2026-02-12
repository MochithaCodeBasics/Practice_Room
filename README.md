# 🐍 Practice Room

A full-stack Python learning platform with an interactive code editor, progress tracking, and admin question management.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-38B2AC)

---

## ✨ Features

- **Interactive Code Editor** - Monaco Editor with Python syntax highlighting
- **Run & Validate** - Execute code and validate against test cases
- **Progress Tracking** - Track completed/attempted questions per user
- **Learning Streaks** - Gamified streak counter for motivation
- **Admin Panel** - Create, edit, and delete questions
- **PDF Export** - Download solutions as formatted PDFs
- **Filtering** - Filter by difficulty, topic, and completion status

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, Tailwind CSS, Monaco Editor |
| Backend | FastAPI, SQLModel, SQLite |
| Auth | JWT (OAuth2 Bearer tokens) |

---

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **npm** or **yarn**

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd practice_room
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your settings (see Configuration section)

# Run the backend
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## ⚙️ Configuration

Create a `.env` file in the `backend/` directory:

```env
# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secure-secret-key-here

# Default Admin Credentials
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=your-secure-password
DEFAULT_ADMIN_EMAIL=admin@example.com

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 📁 Project Structure

```
practice_room/
├── backend/
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── core/         # Configuration
│   │   ├── models.py     # Database models
│   │   └── main.py       # FastAPI app
│   ├── data/             # SQLite database
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/        # Route components
│       ├── components/   # Reusable UI
│       ├── context/      # Auth state
│       └── services/     # API client
└── questions/            # Question files
    └── question_XX/
        ├── question.py
        └── validator.py
```

---

## 🔐 Default Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin |
| Learner | learner | learner |

> ⚠️ **Change these credentials in production!**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | User login |
| `POST` | `/api/v1/auth/signup` | User registration |
| `GET` | `/api/questions/` | List all questions |
| `GET` | `/api/questions/{id}` | Get question detail |
| `POST` | `/api/execute/run` | Execute code |
| `POST` | `/api/execute/validate` | Validate solution |

View full API docs at `http://localhost:8000/docs`

---

## 🧪 Development

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

### Build for Production
```bash
# Frontend
cd frontend
npm run build
```

---

## 📜 License

MIT License

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request
