# Practice Room

A full-stack Python learning platform with an interactive code editor, progress tracking, and admin question management. The platform leverages **NestJS** for a robust backend, **Next.js** for a dynamic frontend, and **Judge0** for secure, sandboxed code execution.

This is a **Practice Zone** building project designed to help users master coding concepts through hands-on challenges.

---

## 🚀 Quick Start

Follow these simple instructions to get the project up and running. For a detailed guide, see [INSTRUCTION_GUIDE.md](./INSTRUCTION_GUIDE.md).

### 1. Judge0 Setup (Code Execution)

Start the code execution engine first using Docker.

```bash
cd judge0
docker-compose up -d
```

### 2. Backend Setup (NestJS)

Configure the backend, run migrations, and seed the database.

```bash
cd backend-nest

# Install dependencies
npm install

# Configure Environment
cp .env.example .env
# Edit .env to match your local DB credentials and settings

# Run Database Migrations
npx prisma migrate dev

# Seed Database
npx prisma db seed

# Start Backend Server (Runs on port 3001)
npm run start:dev
```

### 3. Frontend Setup (Next.js)

Start the user interface.

```bash
cd frontend

# Install dependencies
npm install

# Start Frontend Server (Runs on port 3000)
npm run dev
```

Visit **http://localhost:3000** to access the application.

---

## 🛠 Configuration details

The `backend-nest/.env` file controls the backend configuration. Key variables include:

- **Database**: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- **Security**: `JWT_SECRET`
- **Judge0**: `JUDGE0_API_URL` (default: `http://localhost:2358`)
- **App**: `PORT` (default: `3001`)

Ensure your **MariaDB** server is running before starting the backend.

---

## 💡 Project Ideation

**Practice Room** allows learners to:
- Solve coding problems in an interactive editor (Monaco Editor).
- Get instant feedback via test case validation.
- Track progress across different modules (e.g., Python, Data Science).

**Admins** can:
- Manage questions and modules via a dedicated admin panel.
- Update test cases and problem descriptions.
