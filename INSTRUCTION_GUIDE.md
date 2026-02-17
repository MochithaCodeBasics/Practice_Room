# Practice Room - Instruction Guide

This detailed guide covers the setup, configuration, and running of the Practice Room application.

## Prerequisites

Ensure you have the following installed:
- **Node.js**: v18+ (for Backend and Frontend)
- **Docker & Docker Compose**: (for Code Execution Engine)
- **MariaDB**: (Database for Backend)
- **Git**: Version control

---

## 1. Backend Setup (NestJS)

The backend handles API requests, authentication, and communication with the database and code execution engine.

### Steps:

1.  **Navigate to the backend directory:**
    ```bash
    cd backend-nest
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Environment Variables:**
    - Copy the example environment file:
      ```bash
      cp .env.example .env
      ```
    - Open `.env` and update the following:
      - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: Database connection details.
      - `JWT_SECRET`: Secret key for authentication.
      - `JUDGE0_API_URL`: URL for the Judge0 service (default: `http://localhost:2358`).

4.  **Database Migration:**
    - Ensure your MariaDB service is running and the database exists (or let Prisma create it if configured).
    - Run migrations to set up the schema:
      ```bash
      npx prisma migrate dev
      ```

5.  **Seed the Database:**
    - Populate the database with initial data (modules, questions):
      ```bash
      npx prisma db seed
      ```

6.  **Start the Backend:**
    ```bash
    npm run start:dev
    ```
    - The server will start on **http://localhost:3001** (or the port specified in `.env`).

---

## 2. Judge0 Setup (Code Execution Engine)

Judge0 is used to execute user-submitted code in a sandboxed environment.

### Steps:

1.  **Navigate to the judge0 directory:**
    ```bash
    cd judge0
    ```

2.  **Start Services:**
    ```bash
    docker-compose up -d
    ```
    - This will start the Judge0 server, worker, database (Postgres), and Redis.

3.  **Verify:**
    - Check if containers are running:
      ```bash
      docker ps
      ```
    - The Judge0 API should be accessible at **http://localhost:2358**.

---

## 3. Frontend Setup (Next.js)

The frontend provides the user interface for the application.

### Steps:

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Start the Frontend:**
    ```bash
    npm run dev
    ```
    - The application will be available at **http://localhost:3000**.
    - API requests to `/api/*` are proxied to the backend at `http://localhost:3001`.

---

## 4. Troubleshooting

- **Port Conflicts:** Ensure ports `3000` (Frontend), `3001` (Backend), and `2358` (Judge0) are free.
- **Database Connection:** Verify MariaDB is running and credentials in `.env` match.
- **Judge0:** If code execution fails, ensure Docker containers are running and the backend can reach `http://localhost:2358`.
