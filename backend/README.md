# Practice Room - Backend

NestJS API server for the Practice Room platform. Handles authentication, question management, code execution, and progress tracking.

## Prerequisites

- Node.js v18+
- MariaDB
- Docker (for Judge0 code execution)

## Setup

```bash
npm install

# Configure environment
cp .env.example .env

# Run database migrations
npx prisma migrate dev

# Seed database
npx prisma db seed

# Start development server
npm run start:dev
```

The server runs on **http://localhost:3001** by default.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MariaDB host | `localhost` |
| `DB_PORT` | MariaDB port | `3306` |
| `DB_USER` | Database user | `root` |
| `DB_PASSWORD` | Database password | — |
| `DB_NAME` | Database name | `practice_room` |
| `JWT_SECRET` | JWT signing secret | — |
| `JUDGE0_API_URL` | Judge0 API endpoint | `http://localhost:2358` |
| `USE_JUDGE0` | Enable Judge0 execution | `true` |
| `PORT` | Server port | `3001` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

## API Endpoints

### Questions
- `GET /api/questions` — List questions (filterable by difficulty, status)
- `GET /api/questions/:id` — Get question detail

### Modules
- `GET /api/modules` — List modules
- `GET /api/modules/:slug/questions` — Questions by module

### Execution
- `POST /api/execute/run` — Run code (requires auth)
- `POST /api/execute/validate` — Submit & validate code (requires auth, saves progress)
- `GET /api/execute/runs/:runId/:filename` — Get execution artifacts (images)

### Admin
- `POST /api/v1/admin/questions` — Create question
- `PUT /api/v1/admin/questions/:id` — Update question
- `DELETE /api/v1/admin/questions/:id` — Delete question
- `POST /api/v1/admin/questions/:id/verify` — Toggle verification

## Scripts

| Command | Description |
|---------|-------------|
| `npm run start:dev` | Start in watch mode |
| `npm run build` | Build for production |
| `npm run start:prod` | Run production build |
| `npm run test` | Run unit tests |
| `npm run lint` | Lint and fix |
