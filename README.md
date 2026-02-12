# Practice Room

A full-stack Python learning platform with an interactive code editor, progress tracking, and admin question management.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-38B2AC)

---

## Features

- **Interactive Code Editor** - Monaco Editor with Python syntax highlighting
- **Run & Validate** - Execute code and validate against test cases
- **Progress Tracking** - Track completed/attempted questions per user
- **Learning Streaks** - Gamified streak counter for motivation
- **Admin Panel** - Create, edit, and delete questions
- **PDF Export** - Download solutions as formatted PDFs
- **Filtering** - Filter by difficulty, topic, and completion status

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, React 18, Tailwind CSS, shadcn/ui, Monaco Editor |
| Backend | FastAPI, SQLModel, SQLite |
| Auth | JWT (OAuth2 Bearer tokens) |
| Code Execution | Docker (sandboxed containers) |

---

## Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **npm**
- **Docker** (optional, for sandboxed code execution)

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/MochithaCodeBasics/Practice_Room.git
cd Practice_Room
```

### 2. Install dependencies

```bash
setup_dependencies.bat
```

This installs both backend (Python) and frontend (Node.js) dependencies in one step.

### 3. Configure environment

Copy `backend/.env.example` to `backend/.env` and update values as needed (see [Configuration](#configuration)).

### 4. Start the application

```bash
start_app.bat
```

This starts both services automatically:
- **Backend** - FastAPI at http://localhost:8000
- **Frontend** - Next.js at http://localhost:3000

---

## Logging In

### Admin

Navigate to `http://localhost:3000/admin/login` and log in with the credentials configured in your `backend/.env` file (`DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD`).

### Learner

Learners must **sign up** before logging in:

1. Go to `http://localhost:3000/signup`
2. Create an account
3. Log in at `http://localhost:3000/login` with your new credentials

---

## Configuration

Reference for all available environment variables in `backend/.env`:

```env
# Environment (set to 'production' to enable security validation)
ENVIRONMENT=development

# Security - REQUIRED: Must be at least 32 characters in production
SECRET_KEY=your-super-secure-secret-key-here

# Default Admin Credentials - REQUIRED: Strong password in production
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=YourSecurePassword123!
DEFAULT_ADMIN_EMAIL=admin@yourdomain.com

# CORS - comma-separated list of allowed origins (NEVER use * in production)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Docker Execution (SECURITY: Set to true in production)
USE_DOCKER_EXECUTOR=true
DOCKER_MEMORY_LIMIT=128m
DOCKER_CPU_LIMIT=0.5
DOCKER_TIMEOUT=30

# Email Settings (for password reset)
# For Gmail: Use an App Password, not your regular password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=Your App Name <your-email@gmail.com>

# Frontend URL (for password reset links)
FRONTEND_URL=http://localhost:3000
```

---

## Project Structure

```
Practice_Room/
├── backend/
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── core/           # Configuration
│   │   ├── models.py       # Database models
│   │   └── main.py         # FastAPI app
│   ├── data/               # SQLite database
│   ├── docker/             # Dockerfiles and requirements per module
│   └── requirements.txt
├── frontend/
│   ├── app/                # Next.js App Router pages
│   ├── components/         # Reusable UI components
│   ├── context/            # Auth state
│   ├── services/           # API client
│   └── next.config.js      # Rewrites /api -> backend:8000
├── questions/              # Question files
│   └── question_XX/
│       ├── question.py
│       └── validator.py
├── reports/                # Documentation and audits
├── setup_dependencies.bat  # Dependency installer
└── start_app.bat           # Startup script
```

---

## Docker Code Execution

User-submitted code runs inside isolated Docker containers for security. Without Docker, the system falls back to local execution (not recommended for production).

### How it works

1. User submits code via the editor
2. Backend creates a Docker container with resource limits
3. Code runs in isolation with access to data science libraries
4. Results are captured and returned to the user
5. Container is destroyed after execution

### Pre-built images

The project uses 6 Docker images, each tailored to a specific module:

| Image | Purpose |
|-------|---------|
| `practice-room-python` | Base image - pandas, numpy, matplotlib, seaborn, scipy |
| `practice-room-ml` | Machine Learning - scikit-learn, xgboost, imbalanced-learn |
| `practice-room-dl` | Deep Learning - torch, torchvision, scikit-learn |
| `practice-room-nlp` | NLP - spacy, transformers, torch |
| `practice-room-genai` | Generative AI - langchain, LLM SDKs, transformers |
| `practice-room-agentic` | Agentic AI - langchain, OpenAI, Anthropic |

Each module in the database specifies which image to use (defaults to `practice-room-python`).

### Building images (first time only)

If Docker images are not already present, build them from the project root:

```bash
# Base image (required - all others depend on this)
docker build -t practice-room-python:latest -f backend/docker/Dockerfile.python .

# Specialized images (build only what you need)
docker build -t practice-room-ml:latest -f backend/docker/Dockerfile.ml .
docker build -t practice-room-dl:latest -f backend/docker/Dockerfile.dl .
docker build -t practice-room-nlp:latest -f backend/docker/Dockerfile.nlp .
docker build -t practice-room-genai:latest -f backend/docker/Dockerfile.genai .
docker build -t practice-room-agentic:latest -f backend/docker/Dockerfile.agentic .
```

To verify your images are available:

```bash
docker images | findstr practice-room
```

### Container limits

| Resource | Default |
|----------|---------|
| Memory | 128 MB |
| CPU | 50% of one core |
| Timeout | 30 seconds |
| Max concurrent | 5 containers |
| Network | Disabled (enabled for GenAI/Agentic/NLP modules) |

These can be configured via `.env` (see [Configuration](#configuration)).

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | User login |
| `POST` | `/api/v1/auth/signup` | User registration |
| `POST` | `/api/v1/auth/logout` | User logout |
| `GET` | `/api/v1/auth/me` | Get current user info |
| `POST` | `/api/v1/auth/forgot-password` | Request password reset email |
| `POST` | `/api/v1/auth/reset-password` | Reset password with token |

### Questions and Modules
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/questions/` | List all questions |
| `GET` | `/api/questions/{id}` | Get question detail |
| `GET` | `/api/modules/` | List all modules |

### Code Execution
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/execute/run` | Execute code |
| `POST` | `/api/execute/validate` | Validate solution against test cases |

### Admin (requires admin role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/admin/questions` | Create question |
| `PUT` | `/api/v1/admin/questions/{id}` | Update question |
| `DELETE` | `/api/v1/admin/questions/{id}` | Delete question |

View full API docs at `http://localhost:8000/docs`

