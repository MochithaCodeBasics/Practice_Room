@echo off
echo Starting Backend (FastAPI on http://localhost:8000)...
start cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo Starting Frontend (Next.js on http://localhost:3000)...
start cmd /k "cd frontend && npm run dev"

echo App started! Open http://localhost:3000 in your browser.
