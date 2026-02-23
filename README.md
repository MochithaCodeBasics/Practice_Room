# Practice Room

A full-stack Python learning platform with an interactive code editor, progress tracking, and admin question management. Built with **NestJS** (backend), **Next.js** (frontend), and **Judge0** (sandboxed code execution).

---

## Quick Start

For a detailed guide, see [INSTRUCTION_GUIDE.md](./INSTRUCTION_GUIDE.md).

### 1. Judge0 Setup (Code Execution)

```bash
cd judge0
docker-compose up -d
```

### 2. Backend Setup (NestJS)

```bash
cd backend

npm install

# Configure environment
cp .env.example .env
# Edit .env to match your local DB credentials

# Run database migrations
npx prisma migrate dev

# Seed database with modules and questions
npx prisma db seed

# Start server (port 3001)
npm run start:dev
```

### 3. Frontend Setup (Next.js)

```bash
cd frontend

npm install

# Start dev server (port 3000)
npm run dev
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
└── INSTRUCTION_GUIDE.md
```

---

## Configuration

The `backend/.env` file controls the backend configuration. Key variables:

- **Database**: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- **Security**: `JWT_SECRET`
- **Judge0**: `JUDGE0_API_URL` (default: `http://localhost:2358`)
- **App**: `PORT` (default: `3001`)

Ensure your **MariaDB** server is running before starting the backend.

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
