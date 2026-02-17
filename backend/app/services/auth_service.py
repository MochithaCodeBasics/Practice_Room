from datetime import datetime, timedelta
from typing import Optional, Union
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.core.config import settings
from app.models import User, UserInDB, UserCreate
from app.database import engine
from app.services.progress_service import progress_service
from sqlmodel import Session, select

# Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    current_streak: int = 0

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# Security
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username_or_email: str):
    """Get user by username or email."""
    with Session(engine) as session:
        # Try to find user by username first, then by email
        statement = select(User).where(
            (User.username == username_or_email) | (User.email == username_or_email)
        )
        db_user = session.exec(statement).first()
        if db_user:
            progress_service.refresh_streak(db_user.username)
        return db_user

def create_user(user_create: UserCreate):
    with Session(engine) as session:
        hashed_password = pwd_context.hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            role="learner"  # SECURITY: Always force learner role - never trust client input
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

def reset_password(username: str, email: str, new_password: str):
    """
    SECURITY FIX: This is a simplified secure reset for demo purposes.
    In production, implement a two-step flow:
    1. initiate_password_reset(email) - sends token to email
    2. complete_password_reset(token, new_password) - validates token and resets
    
    For now, we keep the username+email verification but add password strength check.
    """
    import re
    
    # Password strength validation
    if len(new_password) < 8:
        return False
    if not re.search(r'[A-Z]', new_password):
        return False
    if not re.search(r'[a-z]', new_password):
        return False
    if not re.search(r'[0-9]', new_password):
        return False
    
    with Session(engine) as session:
        statement = select(User).where(User.username == username, User.email == email)
        db_user = session.exec(statement).first()
        if not db_user:
            return False
        
        db_user.hashed_password = pwd_context.hash(new_password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return True


# SECURITY: Secure token-based password reset functions
import secrets
import hashlib

def generate_reset_token(email: str) -> Optional[tuple]:
    """Generate a secure password reset token for the user. Returns (username, token) or None."""
    from app.models import PasswordResetToken
    
    with Session(engine) as session:
        # Find user by email
        statement = select(User).where(User.email == email)
        db_user = session.exec(statement).first()
        if not db_user:
            return None  # Don't reveal if email exists
        
        # Invalidate any existing tokens for this user
        existing_tokens = session.exec(
            select(PasswordResetToken).where(PasswordResetToken.user_id == db_user.id)
        ).all()
        for t in existing_tokens:
            t.used = True
            session.add(t)
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store token with 1 hour expiry
        reset_token = PasswordResetToken(
            user_id=db_user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        session.add(reset_token)
        session.commit()
        
        return (db_user.username, token)  # Return username and plaintext token


def verify_and_reset_password(token: str, new_password: str) -> bool:
    """Verify reset token and update password."""
    from app.models import PasswordResetToken
    import re
    
    # Password strength validation
    if len(new_password) < 8:
        return False
    if not re.search(r'[A-Z]', new_password):
        return False
    if not re.search(r'[a-z]', new_password):
        return False
    if not re.search(r'[0-9]', new_password):
        return False
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    with Session(engine) as session:
        # Find valid token
        statement = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        )
        reset_token = session.exec(statement).first()
        
        if not reset_token:
            return False
        
        # Get user
        db_user = session.get(User, reset_token.user_id)
        if not db_user:
            return False
            
        # SECURITY FIX: Prevent admin account takeover via email reset
        if db_user.role == "admin":
            return False  # Admins must use manual process or super-admin reset
        
        # Update password
        db_user.hashed_password = pwd_context.hash(new_password)
        session.add(db_user)
        
        # Mark token as used
        reset_token.used = True
        session.add(reset_token)
        
        session.commit()
        return True

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        print(f"DEBUG AUTH: User '{username}' not found.")
        return False
    
    is_valid = verify_password(password, user.hashed_password)
    print(f"DEBUG AUTH: Verification for '{username}'. valid={is_valid}. HashLen={len(user.hashed_password)}")
    if not is_valid:
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # SECURITY: Add unique JTI (JWT ID) to allow individual token revocation
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def revoke_token(token: str):
    """Revoke a token by adding its JTI to the blacklist."""
    from app.models import RevokedToken
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            expires_at = datetime.fromtimestamp(exp)
            
            with Session(engine) as session:
                # Check if already revoked
                existing = session.exec(select(RevokedToken).where(RevokedToken.jti == jti)).first()
                if not existing:
                    revoked = RevokedToken(jti=jti, expires_at=expires_at)
                    session.add(revoked)
                    session.commit()
    except Exception:
        pass # If token is invalid/expired, nothing to revoke

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

async def get_optional_current_user(token: str = Depends(oauth2_scheme_optional)):
    """Return the current user if a valid token is present, otherwise return None."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti: str = payload.get("jti")
        if jti:
            from app.models import RevokedToken
            with Session(engine) as session:
                revoked = session.exec(select(RevokedToken).where(RevokedToken.jti == jti)).first()
                if revoked:
                    return None
        username: str = payload.get("sub")
        if username is None:
            return None
        user = get_user(username)
        if user is None or user.disabled:
            return None
        return user
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # SECURITY: Check revocation blacklist first
    try:
        if not token:
             print("AUTH DEBUG: No token received")
        
        # Decode without verifying signature first to check JTI quickly? 
        # No, safer to verify signature first to prevent DoS on DB with fake tokens.
        # But jose.jwt.decode verifies by default.
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti: str = payload.get("jti")
        
        if jti:
            from app.models import RevokedToken
            with Session(engine) as session:
                revoked = session.exec(select(RevokedToken).where(RevokedToken.jti == jti)).first()
                if revoked:
                    print("AUTH DEBUG: Token revoked")
                    raise credentials_exception
        
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            print("AUTH DEBUG: Username missing in token")
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError as e:
        print(f"AUTH DEBUG: JWT Error: {e}")
        raise credentials_exception
    
    user = get_user(token_data.username)
    if user is None:
        print(f"AUTH DEBUG: User {token_data.username} not found in DB")
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="The user doesn't have enough privileges"
        )
    return current_user

