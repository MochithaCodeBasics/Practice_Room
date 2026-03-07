# Practice Room - Instruction Guide

This guide covers two ways to run the application:
- **Option A: Docker Setup** (recommended for deployment and quick onboarding)
- **Option B: Local Development Setup** (for active development without Docker)

---

## Prerequisites

### For Docker Setup (Option A)
- **Docker Engine**: v20+ with Docker Compose v2
- **External MySQL/MariaDB**: (e.g. AWS RDS, PlanetScale, or a self-managed instance)
- **External Judge0 instance**: separately hosted (see Judge0 section below)
- **Git**

### For Local Development (Option B)
- **Node.js**: v18+
- **MariaDB**: (local database)
- **External Judge0 instance**: or run it locally (see Judge0 section below)
- **Git**

---

## Option A: Docker Setup

This runs the Frontend and Backend via a single `docker compose` command. The database and Judge0 code execution service are **external** — you provide the connection details.

### Architecture

```
docker compose up
  ├── frontend   → Next.js        → port 3000
  └── backend    → NestJS + Prisma → port 3001

External:
  ├── MySQL/MariaDB  → Your RDS or managed DB instance
  └── Judge0         → Your separately hosted Judge0 instance
```

### Step 1: Configure Environment Variables

```bash
cp .env.docker.example .env.docker
```

Open `.env.docker` and fill in the required values:

#### Database (required)

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | MySQL/MariaDB host | `my-db.xxxx.rds.amazonaws.com` |
| `DB_PORT` | Database port | `3306` |
| `DB_USER` | Database user | `practiceroom` |
| `DB_PASSWORD` | Database password | `your-secure-password` |
| `DB_NAME` | Database name | `practice_room` |

#### Backend Security (required)

| Variable | Description | How to generate |
|----------|-------------|-----------------|
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `DEFAULT_ADMIN_PASSWORD` | Initial admin password | Choose a strong password |
| `DEFAULT_ADMIN_EMAIL` | Admin email address | `admin@yourdomain.com` |

#### Frontend Auth (required)

| Variable | Description | How to generate |
|----------|-------------|-----------------|
| `AUTH_SECRET` | NextAuth.js secret | `openssl rand -base64 32` |
| `AUTH_CODEBASICS_ID` | Codebasics OAuth client ID | From Codebasics developer panel |
| `AUTH_CODEBASICS_SECRET` | Codebasics OAuth client secret | From Codebasics developer panel |

#### Judge0 (required for code execution)

| Variable | Description | Example |
|----------|-------------|---------|
| `USE_JUDGE0` | Enable Judge0 execution | `true` |
| `JUDGE0_API_URL` | URL of your Judge0 instance | `https://judge0.yourdomain.com` |
| `JUDGE0_API_KEY` | Auth token (if configured) | leave empty if self-hosted without auth |
| `JUDGE0_PYTHON_LANGUAGE_ID` | Python language ID (auto-detected if empty) | `71` |

#### URLs (update for production)

| Variable | Default | When to change |
|----------|---------|----------------|
| `NEXT_PUBLIC_APP_URL` | `http://localhost:3000` | Set to your production domain |
| `FRONTEND_URL` | `http://localhost:3000` | Set to your production domain |
| `CODEBASICS_BASE_URL` | `https://beta.codebasics.io` | Change when moving to production CB |

#### Email / SMTP (optional)

| Variable | Description |
|----------|-------------|
| `SMTP_HOST` | SMTP server (default: `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (default: `587`) |
| `SMTP_USER` | SMTP username |
| `SMTP_PASSWORD` | SMTP password or app-specific password |
| `SMTP_FROM_EMAIL` | Sender email address |

### Step 2: Ensure Database is Ready

Before starting Docker, make sure your external MySQL/MariaDB is:
1. Running and accessible from the server
2. The database specified in `DB_NAME` exists (create it if not):
   ```sql
   CREATE DATABASE IF NOT EXISTS practice_room;
   ```
3. The user specified in `DB_USER` has full access to this database

### Step 3: Build and Start

```bash
docker compose --env-file .env.docker up --build
```

This will:
1. Build the frontend and backend Docker images
2. Start all services with health checks
3. Run database migrations automatically (via backend entrypoint)

Wait for all services to become healthy. First run may take a few minutes for image builds.

### Step 4: Seed the Database (first run only)

After all services are up, seed the database with modules and questions:

```bash
docker compose --env-file .env.docker exec backend npx prisma db seed
```

### Step 5: Verify

| Check | URL |
|-------|-----|
| Frontend loads | http://localhost:3000 |
| Backend API responds | http://localhost:3001/api |
| Judge0 (external) | `<your JUDGE0_API_URL>/languages` |

### Common Docker Commands

```bash
# Start all services (detached)
docker compose --env-file .env.docker up --build -d

# View logs
docker compose logs -f              # all services
docker compose logs -f backend      # backend only
docker compose logs -f frontend     # frontend only

# Restart a single service
docker compose --env-file .env.docker restart backend

# Stop all services
docker compose down

# Stop and remove all data volumes (full reset)
docker compose down -v

# Run a command inside the backend container
docker compose --env-file .env.docker exec backend <command>
```

### Security on Server

After creating `.env.docker` on the server, restrict file permissions:

```bash
chmod 600 .env.docker
```

This ensures only the file owner can read the credentials.

---

## Option B: Local Development Setup

Use this when you're actively developing and want hot-reload for frontend and backend.

### 1. Backend Setup (NestJS)

```bash
cd backend

npm install

# Configure environment
cp .env.example .env
# Edit .env — set DB credentials, SECRET_KEY, and Judge0 URL

# Run database migrations
npx prisma migrate dev

# Seed database with modules and questions
npx prisma db seed

# Start server (port 3001)
npm run start:dev
```

### 2. Frontend Setup (Next.js)

```bash
cd frontend

npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local — set AUTH_SECRET and OAuth credentials

# Start dev server (port 3000)
npm run dev
```

Visit http://localhost:3000 to access the application.

---

## Judge0 (External Code Execution)

Judge0 is not bundled with this project. You need to run it as a separate service and point the backend at it via `JUDGE0_API_URL`.

**Options:**
- **Self-hosted**: Deploy the [Judge0 repository](https://github.com/judge0/judge0) on your own server or VM
- **Managed**: Use a hosted Judge0 API endpoint

**Local development without Judge0:**
Set `USE_JUDGE0=false` and `USE_DOCKER_EXECUTOR=true` in `backend/.env` to use the local Docker-based executor instead. This requires Docker to be running and the `practice-room-python:latest` image to be built.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port conflicts** | Ensure ports `3000` and `3001` are free. Use `lsof -i :PORT` to check. |
| **Database connection refused** | Verify MySQL/MariaDB is running and credentials in `.env.docker` (or `backend/.env`) are correct. |
| **Judge0 not responding** | Check that `JUDGE0_API_URL` is reachable and `JUDGE0_API_KEY` is correct if auth is enabled. |
| **Backend health check failing** | Check `docker compose logs backend`. Common cause: database not reachable. |
| **Migrations fail** | Ensure the database exists and the user has DDL permissions (CREATE, ALTER, DROP). |
| **Frontend can't reach backend** | In Docker: this is handled internally. In local dev: ensure backend is running on port 3001. |

---

## Project Structure

```
Practice_Room/
├── frontend/               # Next.js app (port 3000)
│   ├── Dockerfile          # Multi-stage production build
│   └── .dockerignore
├── backend/                # NestJS API (port 3001)
│   ├── Dockerfile          # Multi-stage production build
│   ├── docker-entrypoint.sh # Runs migrations + starts server
│   └── .dockerignore
├── questions/              # Question data, validators, and datasets
├── docker-compose.yml      # Orchestrates frontend + backend
├── .env.docker.example     # Environment variable template for Docker
└── INSTRUCTION_GUIDE.md    # This file
```
