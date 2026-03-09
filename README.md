# Practice Room

A full-stack Python learning platform with an interactive code editor, progress tracking, and admin question management. Built with **NestJS** (backend), **Next.js** (frontend), and **Judge0** (sandboxed code execution — hosted externally).

---

## Quick Start

For a detailed guide, see [INSTRUCTION_GUIDE.md](./INSTRUCTION_GUIDE.md).

### Docker Setup (recommended)

```bash
# 1. Configure environment
cp .env.docker.example .env.docker
# Edit .env.docker with your database, auth, and Judge0 credentials

# 2. Build and start everything
docker compose --env-file .env.docker up --build

# 3. Seed database (first run only)
docker compose --env-file .env.docker exec backend npx prisma db seed
```

### Local Development Setup

```bash
# 1. Start Backend
cd backend && npm install && cp .env.example .env
# Edit backend/.env with your DB credentials and Judge0 URL
npx prisma migrate dev && npx prisma db seed
npm run start:dev

# 2. Start Frontend (in a new terminal)
cd frontend && npm install && cp .env.local.example .env.local
# Edit frontend/.env.local with your auth credentials
npm run dev
```

Visit **http://localhost:3000** to access the application.

---

## Project Structure

```
Practice_Room/
├── frontend/          # Next.js app (port 3000)
├── backend/           # NestJS API (port 3001)
├── questions/         # Question data, validators, and datasets
├── docker-compose.yml # Docker orchestration (frontend + backend)
└── INSTRUCTION_GUIDE.md
```

---

## Configuration

### Docker Setup
All configuration is in `.env.docker` (copy from `.env.docker.example`). See [INSTRUCTION_GUIDE.md](./INSTRUCTION_GUIDE.md) for a full variable reference.

### Local Setup
The `backend/.env` file controls the backend configuration. Key variables:

- **Database**: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- **Security**: `SECRET_KEY`
- **Judge0**: `USE_JUDGE0`, `JUDGE0_API_URL`, `JUDGE0_API_KEY`
- **App**: `PORT` (default: `3001`)

The `frontend/.env.local` file controls the frontend configuration:
- **Auth**: `AUTH_SECRET`, `AUTH_CODEBASICS_ID`, `AUTH_CODEBASICS_SECRET`
- **URLs**: `NEXT_PUBLIC_APP_URL`, `CODEBASICS_BASE_URL`

---

## Key Features

**Learners:**
- Solve coding problems in an interactive Monaco editor
- **Run Code** to test solutions (no submission saved)
- **Submit & Validate** to validate against test cases and track progress (requires authentication)
- Track completion status and streaks across modules

**Admins:**
- Manage questions and modules via a dedicated admin panel
- Upload/edit problem descriptions, validators, and datasets
- Verify questions after validation
