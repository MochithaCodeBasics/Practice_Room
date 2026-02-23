# Practice Room

A full-stack Python learning platform with an interactive code editor, progress tracking, and admin question management. Built with **NestJS** (backend), **Next.js** (frontend), and **Judge0** (sandboxed code execution).

---

## Quick Start

For a detailed guide, see [INSTRUCTION_GUIDE.md](./INSTRUCTION_GUIDE.md).

### Docker Setup (recommended)

```bash
# 1. Configure environment
cp .env.docker.example .env.docker
# Edit .env.docker with your database and auth credentials

# 2. Set Judge0 passwords
# Edit judge0/judge0.conf — set REDIS_PASSWORD and POSTGRES_PASSWORD

# 3. Build and start everything
docker compose --env-file .env.docker up --build

# 4. Seed database (first run only)
docker compose --env-file .env.docker exec backend npx prisma db seed
```

### Local Development Setup

```bash
# 1. Start Judge0
cd judge0 && docker-compose up -d && cd ..

# 2. Start Backend
cd backend && npm install && cp .env.example .env
# Edit backend/.env with your DB credentials
npx prisma migrate dev && npx prisma db seed
npm run start:dev

# 3. Start Frontend (in a new terminal)
cd frontend && npm install && npm run dev
```

Visit **http://localhost:3000** to access the application.

---

## Project Structure

```
Practice_Room/
├── frontend/          # Next.js app (port 3000)
├── backend/           # NestJS API (port 3001)
├── judge0/            # Judge0 code execution engine (port 2358)
├── questions/         # Question data, validators, and datasets
├── docker-compose.yml # Docker orchestration for all services
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
- **Judge0**: `JUDGE0_API_URL` (default: `http://localhost:2358`)
- **App**: `PORT` (default: `3001`)

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
