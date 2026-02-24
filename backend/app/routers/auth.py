from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.auth_service import (
    Token, authenticate_user, create_access_token, 
    get_current_active_user, get_user, create_user, UserCreate,
    generate_reset_token, verify_and_reset_password
)
from app.services.email_service import email_service
from app.models import User, UserSettingsUpdate
from app.core.config import settings
from pydantic import BaseModel
from app.core.logging import log_audit_event

router = APIRouter()

from app.core.limiter import limiter

class PasswordResetRequest(BaseModel):
    """Step 1: Request password reset - sends email with token."""
    email: str

class PasswordResetVerify(BaseModel):
    """Step 2: Verify token and set new password."""
    token: str
    new_password: str


@router.post("/admin/login", response_model=Token)
@limiter.limit("5/minute")
async def admin_login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Admin-only login endpoint"""
    try:
        user = authenticate_user(form_data.username, form_data.password)
    except Exception as e:
        import traceback
        import logging
        error_logger = logging.getLogger("errors")
        error_logger.error(f"Admin login failed with exception: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login processing error: {str(e)}"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    log_audit_event("admin_login", user=form_data.username, request=request, status="success")
    
    # Only allow admin users
    if user.role != "admin":
        log_audit_event("admin_login", user=form_data.username, request=request, status="failure", details={"reason": "not_admin"})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This login is for administrators only.",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "username": user.username, "current_streak": user.current_streak}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Block admin users from learner login - they must use /admin/login
    if user.role == "admin":
        log_audit_event("login", user=form_data.username, request=request, status="failure", details={"reason": "admin_denied_on_learner_login"})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins must use the admin login portal",
        )
    
    log_audit_event("login", user=form_data.username, request=request, status="success")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "username": user.username, "current_streak": user.current_streak}

@router.get("/me", response_model=User)
@router.get("/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me/settings")
async def update_user_settings(
    settings_in: UserSettingsUpdate, 
    current_user: User = Depends(get_current_active_user)
):
    from app.database import engine
    from sqlmodel import Session
    
    with Session(engine) as session:
        try:
            # Re-fetch user in session to update
            db_user = session.get(User, current_user.id)
            if not db_user:
                 raise HTTPException(status_code=404, detail="User not found")
            
            if settings_in.groq_api_key is not None:
                stripped_key = settings_in.groq_api_key.strip()
                if not stripped_key:
                    db_user.groq_api_key = None
                    db_user.has_groq_api_key = False
                else:
                    db_user.groq_api_key = stripped_key
                    db_user.has_groq_api_key = True
                
            if settings_in.openai_api_key is not None:
                stripped_key = settings_in.openai_api_key.strip()
                if not stripped_key:
                    db_user.openai_api_key = None
                    db_user.has_openai_api_key = False
                else:
                    db_user.openai_api_key = stripped_key
                    db_user.has_openai_api_key = True

            if settings_in.anthropic_api_key is not None:
                stripped_key = settings_in.anthropic_api_key.strip()
                if not stripped_key:
                    db_user.anthropic_api_key = None
                    db_user.has_anthropic_api_key = False
                else:
                    db_user.anthropic_api_key = stripped_key
                    db_user.has_anthropic_api_key = True


            if settings_in.default_llm_provider is not None:
                db_user.default_llm_provider = settings_in.default_llm_provider
                
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return {
                "message": "Settings updated successfully", 
                "has_groq_api_key": db_user.has_groq_api_key,
                "has_openai_api_key": db_user.has_openai_api_key,
                "has_anthropic_api_key": db_user.has_anthropic_api_key,
                "default_llm_provider": db_user.default_llm_provider
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.delete("/me/settings")
async def delete_user_setting(
    field: str,
    current_user: User = Depends(get_current_active_user)
):
    from app.database import engine
    from sqlmodel import Session
    
    with Session(engine) as session:
        try:
            # Re-fetch the user in this session
            db_user = session.get(User, current_user.id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")
                
            # Valid fields to delete
            valid_fields = ["groq_api_key", "openai_api_key", "anthropic_api_key"]
            
            if field not in valid_fields:
                raise HTTPException(status_code=400, detail="Invalid field specified")
                
            setattr(db_user, field, None)
            
            # Update the boolean flag
            flag_name = f"has_{field}"
            setattr(db_user, flag_name, False)
            
            session.add(db_user)
            session.commit()
            return {"message": f"Field {field} deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.post("/logout")
async def logout(request: Request, token: str = Depends(settings.oauth2_scheme)):
    """Logout the user by revoking the current access token."""
    from app.services.auth_service import revoke_token
    revoke_token(token)
    log_audit_event("logout", request=request)
    return {"message": "Successfully logged out"}

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(request: Request, user_in: UserCreate, background_tasks: BackgroundTasks):
    db_user = get_user(user_in.username)
    if db_user:
        # SECURITY FIX: Prevent user enumeration
        # Return generic success masking the existence of the user
        # We return the existing user details to satisfy the response model, 
        # BUT ideally we should return a generic message.
        # Since the frontend redirects to login on success, returning the db_user 
        # (which essentially mocks a successful creation return) is acceptable 
        # as long as we don't leak that it was ALREADY there vs newly created.
        # However, returning the db_user REVEALS their email/data! This is bad.
        
        # Better approach: Create a dummy user object to return
        log_audit_event("signup", user=user_in.username, request=request, status="failure", details={"reason": "user_already_exists"})
        return User(
            username=user_in.username, 
            email=user_in.email, 
            hashed_password="", 
            role="learner"
        )
        
    new_user = create_user(user_in)
    log_audit_event("signup", user=new_user.username, request=request, status="success")
    
    # Send welcome email in background
    background_tasks.add_task(email_service.send_welcome_email, new_user.email, new_user.username)
    
    return new_user

@router.post("/request-password-reset")
@limiter.limit("1/5minute")
async def request_password_reset(request: Request, body: PasswordResetRequest, background_tasks: BackgroundTasks):
    """Step 1: Request password reset. Sends token to email if account exists."""
    # Generate token (returns None if email not found)
    result = generate_reset_token(body.email)
    
    if result:
        username, token = result
        log_audit_event("request_password_reset", user=username, request=request, status="success")
        # Send email with token in background
        background_tasks.add_task(email_service.send_password_reset_email, body.email, username, token)
    else:
        log_audit_event("request_password_reset", request=request, status="failure", details={"email": body.email, "reason": "email_not_found"})
    
    # SECURITY: Always return success to prevent email enumeration
    return {"message": "If an account with that email exists, a password reset link has been sent."}

@router.post("/verify-password-reset")
async def verify_password_reset(request: Request, body: PasswordResetVerify):
    """Step 2: Verify token and set new password."""
    success = verify_and_reset_password(body.token, body.new_password)
    
    if not success:
        log_audit_event("verify_password_reset", request=request, status="failure", details={"reason": "invalid_or_expired_token"})
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token. Please request a new reset link."
        )
    
    log_audit_event("verify_password_reset", request=request, status="success")
    
    return {"message": "Password has been reset successfully. You can now login."}

