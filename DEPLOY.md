# Practice Room — Deployment Guide

## Stack

| Component | Technology |
|-----------|-----------|
| Frontend  | Next.js 15 (App Router, standalone output) |
| Backend   | NestJS 11 |
| Database  | MySQL 8 / MariaDB (external — managed separately) |
| ORM       | Prisma 7 (with MariaDB adapter) |
| Auth      | NextAuth.js 5 (Codebasics OAuth2) + JWT |
| Code Execution | Judge0 (external service) |
| Ports     | Frontend: 3000 · Backend: 3001 |

---

## Prerequisites

### Required Environment Variables

Copy `.env.docker.example` to `.env.docker` and fill in every value:

```bash
cp .env.docker.example .env.docker
chmod 600 .env.docker   # lock permissions on server
```

| Variable | Where to get it |
|----------|----------------|
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME` | Your MySQL/MariaDB server credentials |
| `SECRET_KEY` | `openssl rand -base64 32` |
| `AUTH_SECRET` | `openssl rand -base64 32` |
| `AUTH_CODEBASICS_ID` | Codebasics OAuth app ID |
| `AUTH_CODEBASICS_SECRET` | Codebasics OAuth app secret |
| `CODEBASICS_BASE_URL` | `https://beta.codebasics.io` (or prod URL) |
| `NEXT_PUBLIC_APP_URL` | Public URL of your frontend (e.g. `https://practice.yourdomain.com`) |
| `FRONTEND_URL` | Same as above (used by backend for CORS) |
| `DEFAULT_ADMIN_PASSWORD` | Strong password for the first admin account |
| `DEFAULT_ADMIN_EMAIL` | Email for the first admin account |
| `JUDGE0_API_URL` | URL of your Judge0 instance (e.g. `https://judge0.yourdomain.com`) |
| `JUDGE0_API_KEY` | Judge0 auth token (if your instance has `AUTH_TOKEN` set) |
| `CB_OAUTH_CLIENT_ID` / `CB_OAUTH_CLIENT_SECRET` | Same as `AUTH_CODEBASICS_ID/SECRET` — used by backend to validate tokens |

Optional:
| Variable | Purpose |
|----------|---------|
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | Email notifications |
| `NEXT_PUBLIC_CB_IMAGE_PREFIX` | Codebasics CDN image prefix |

---

## Local Testing (with Docker Compose + MySQL)

Use `docker-compose.local.yml` which bundles a MySQL 8 container — no external DB needed.

```bash
# 1. Copy and fill env file
cp .env.docker.example .env.docker
# Edit .env.docker — at minimum set AUTH_SECRET, AUTH_CODEBASICS_ID/SECRET, JUDGE0_API_URL

# 2. Build and start everything (DB + Backend + Frontend)
docker compose -f docker-compose.local.yml --env-file .env.docker up --build

# 3. Open http://localhost:3000

# 4. Tear down (keeps DB volume)
docker compose -f docker-compose.local.yml down

# 5. Tear down and wipe DB
docker compose -f docker-compose.local.yml down -v
```

Health endpoints:
- Frontend: http://localhost:3000/api/health
- Backend:  http://localhost:3001/api

---

## Production Deployment (docker-compose.yml — external DB)

Use the root `docker-compose.yml` which expects an **external** MySQL/MariaDB database (e.g. managed DB on Coolify, AWS RDS, PlanetScale):

```bash
docker compose --env-file .env.docker up --build -d
```

The backend entrypoint automatically runs `prisma migrate deploy` on every start before launching the server.

---

## Coolify Deployment

1. Push this repository to your Git remote.
2. In Coolify, create a new **Docker Compose** service pointing to this repo.
3. Set the **Env File** contents from your filled-in `.env.docker`.
4. Update `NEXT_PUBLIC_APP_URL`, `FRONTEND_URL`, and `CORS_ORIGINS` to your public domain.
5. Provision a **MySQL 8** database resource in Coolify and copy its **Internal Connection** details into `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.
6. Deploy. Coolify will build both images and start them in order.

> The backend waits for itself to be healthy before the frontend starts (via `depends_on: condition: service_healthy`).

---

## App-Specific Notes

- **Judge0 is required** for code execution. You must host your own Judge0 instance or use a hosted one and set `JUDGE0_API_URL`.
- **Codebasics OAuth** is the only login method. Users must have a Codebasics account. Configure the OAuth app at beta.codebasics.io.
- **Questions directory** (`./questions/`) is mounted read-only into the backend at `/app/questions`. Questions are imported via the Admin panel.
- **Prisma migrations** run automatically on every backend container start. This is safe to run against a live database.
- **Admin seeding** runs on first start only (via `prisma/seed.ts`). Set `DEFAULT_ADMIN_EMAIL` and `DEFAULT_ADMIN_PASSWORD` before first launch.
- The frontend proxies all `/api/*` calls to the backend via Next.js rewrites — no CORS issues in the browser.
