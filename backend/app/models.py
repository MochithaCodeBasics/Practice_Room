from sqlmodel import SQLModel, Field
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import UniqueConstraint

# --- BASE MODELS (Reusable fields, no DB table) ---

class ModuleBase(SQLModel):
    name: str
    description: Optional[str] = None
    base_image: str = "practice-room-python:latest" # Default image

class QuestionBase(SQLModel):
    id: str = Field(primary_key=True)
    folder_name: str
    title: str
    module_id: str = Field(foreign_key="module.id")
    difficulty: str = "easy"
    topic: str = "General"
    tags: Optional[str] = None
    
    # These fields are computed or stored in the DB
    question_py: Optional[str] = None
    initial_code: Optional[str] = None
    validator_py: Optional[str] = None
    # solution_py removed
    hint: Optional[str] = None
    sample_data: Optional[str] = None

# --- TABLE MODELS (Actual DB tables) ---

class Module(ModuleBase, table=True):
    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Question(QuestionBase, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Verification status (replaces solution.py check)
    is_verified: bool = Field(default=False)
    
    # UI temporary fields (excluded from table storage)
    is_completed: bool = Field(default=False, exclude=True)
    is_attempted: bool = Field(default=False, exclude=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = Field(default="learner")
    disabled: bool = Field(default=False)
    groq_api_key: Optional[str] = Field(default=None, exclude=True) # Per-user API key (hidden from API)
    has_groq_api_key: bool = Field(default=False) # Public indicator
    openai_api_key: Optional[str] = Field(default=None, exclude=True)
    has_openai_api_key: bool = Field(default=False)
    anthropic_api_key: Optional[str] = Field(default=None, exclude=True)
    has_anthropic_api_key: bool = Field(default=False)
    default_llm_provider: str = Field(default="groq")
    current_streak: int = Field(default=0)
    last_completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProgress(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("username", "question_id"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    question_id: str = Field(foreign_key="question.id")
    status: str # "completed" or "attempted"
    user_code: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# SECURITY: Token-based password reset
class PasswordResetToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token_hash: str = Field(index=True)  # Store hash, not plaintext
    expires_at: datetime
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# SECURITY: Token Revocation (Blacklist)
class RevokedToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    jti: str = Field(index=True, unique=True) # JWT ID
    revoked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime # When the token would naturally expire

# --- USER SCHEMAS ---

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    # SECURITY: role field removed - never accept from client input

class UserSettingsUpdate(BaseModel):
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: Optional[str] = None

# --- API MODELS (Pure Pydantic for JSON transfer, NOT SQLModel) ---

class QuestionRead(QuestionBase):
    id: str
    is_completed: bool = False
    is_attempted: bool = False
    is_verified: bool = False
    created_at: datetime

class QuestionDetail(BaseModel):
    id: str
    folder_name: str
    title: str
    module_id: str
    difficulty: str
    topic: str
    tags: Optional[str] = None
    question_py: Optional[str] = None
    initial_code: Optional[str] = None
    validator_py: Optional[str] = None
    # solution_py removed
    hint: Optional[str] = None
    sample_data: Optional[str] = None
    data_files: List[str] = []
    is_verified: bool = False
    is_completed: bool = False
    is_attempted: bool = False

class ExecutionRequest(BaseModel):
    code: str
    question_id: str
    module_id: str

class ExecutionResult(BaseModel):
    stdout: str
    stderr: str
    validation_output: Optional[str] = None
    artifacts: List[str] = []
    status: str
    run_id: Optional[str] = None
    current_streak: Optional[int] = None
