from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import traceback
import logging
import os

from .routers import questions, modules, execute, auth, admin
from .database import create_db_and_tables
from .core.config import settings
from .core.limiter import limiter

app = FastAPI(title="Practice Room API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_logger = logging.getLogger("errors")
    error_trace = traceback.format_exc()
    error_logger.error(f"Global Exception on {request.url.path}: {str(exc)}\n{error_trace}")

    error_msg = str(exc)
    details = error_msg

    if "Validation execution failed" in error_msg:
        details = "Code validation failed. Check your implementation against the requirements."
    elif "Question not found" in error_msg:
        details = "The question could not be found. Please refresh and try again."
    elif "Question directory not found" in error_msg:
        details = "Question resources are missing. Contact support."
    elif isinstance(exc, AttributeError):
        details = f"Missing variable or function: {error_msg}. Check your variable names."

    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "detail": details,
            "type": type(exc).__name__
        },
    )


@app.on_event("startup")
def on_startup():
    # SECURITY: Validate security settings on startup
    settings.validate_security()
    create_db_and_tables()


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Ensure runs directory exists
if not os.path.exists("runs"):
    os.makedirs("runs")

app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(modules.router, prefix="/api/modules", tags=["modules"])
app.include_router(execute.router, prefix="/api/execute", tags=["execute"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Practice Room API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
