import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    PROJECT_NAME: str = "Math & Stats Practice Room"
    API_V1_STR: str = "/api/v1"
    
    # Path to the backend directory
    BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
    BASE_DIR = BACKEND_DIR # Alias for consistency
    
    # Path to the root workspace (where questions/ is)
    ROOT_DIR = BACKEND_DIR.parent
    
    QUESTIONS_DIR = ROOT_DIR / "questions"
    MASTER_CSV = QUESTIONS_DIR / "master_question_list.csv"

    # Auth - SECURITY: Environment variables required for production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-insecure-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    
    # We need to expose this for the router to use in Depends
    @property
    def oauth2_scheme(self):
         from fastapi.security import OAuth2PasswordBearer
         return OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

    # Default credentials - SECURITY: Use strong passwords via environment variables
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "")  # REQUIRED in production
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    
    # CORS - SECURITY: Explicit origins only, no wildcard in production
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")

    # Docker Configuration
    DOCKER_TIMEOUT: int = int(os.getenv("DOCKER_TIMEOUT", "60"))
    NLP_TIMEOUT: int = int(os.getenv("NLP_TIMEOUT", str(DOCKER_TIMEOUT))) # Default to DOCKER_TIMEOUT if not set
    DOCKER_MEMORY_LIMIT: str = os.getenv("DOCKER_MEMORY_LIMIT", "1.5g")  # Increased from 512m for PyTorch/ML workloads
    DOCKER_HF_CACHE_VOLUME: str = os.getenv("DOCKER_HF_CACHE_VOLUME", "practice-room-hf-cache")
    
    # Environment check
    IS_PRODUCTION: bool = os.getenv("ENVIRONMENT", "development") == "production"
    
    def validate_security(self):
        """Validate security settings - call on startup in production"""
        if self.IS_PRODUCTION:
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
            if not self.DEFAULT_ADMIN_PASSWORD or len(self.DEFAULT_ADMIN_PASSWORD) < 12:
                raise ValueError("DEFAULT_ADMIN_PASSWORD must be at least 12 characters in production")
            if "*" in self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS cannot contain wildcard (*) in production")
    
    @property
    def cors_origins_list(self):
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()

