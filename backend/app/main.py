from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .routers import questions, modules, execute
from .database import create_db_and_tables
from .core.config import settings

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Math & Stats Practice Room API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Note: Migration script (migrate_to_sqlite.py) should be run manually during initial setup
    # Run: python migrate_to_sqlite.py


# CORS configuration - use settings for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Response

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

from fastapi.staticfiles import StaticFiles
import os

# Ensure runs directory exists
if not os.path.exists("runs"):
    os.makedirs("runs")

# SECURITY: Removed public static mount for /api/runs
# User code runs should only be accessible through authenticated endpoints

app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(modules.router, prefix="/api/modules", tags=["modules"])
app.include_router(execute.router, prefix="/api/execute", tags=["execute"])
from .routers import auth, admin
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Practice Room API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
