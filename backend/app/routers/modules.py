from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.logging import log_audit_event
from typing import List
from ..models import Module
from ..services.auth_service import get_current_active_user, get_current_admin_user, User
from ..core.config import settings
import pandas as pd
import os
from sqlmodel import Session, select
from ..database import engine
from ..models import Module, Question
import shutil

router = APIRouter()



@router.get("", response_model=List[Module])
@router.get("/", response_model=List[Module])
def read_modules(current_user: User = Depends(get_current_active_user)):
    # SECURITY: Removed debug prints that exposed usernames
    try:
        with Session(engine) as session:
            statement = select(Module)
            modules = session.exec(statement).all()
            return modules
    except Exception as e:
        raise e

@router.post("", response_model=Module, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=Module, status_code=status.HTTP_201_CREATED)
def create_module(request: Request, module: Module, current_user: User = Depends(get_current_admin_user)):
    with Session(engine) as session:
        existing = session.get(Module, module.id)
        if existing:
            raise HTTPException(status_code=400, detail="Module ID already exists")
        
        session.add(module)
        session.commit()
        session.refresh(module)
        log_audit_event("create_module", user=current_user.username, request=request, status="success", details={"module_id": module.id})
        return module

@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(request: Request, module_id: str, current_user: User = Depends(get_current_admin_user)):
    with Session(engine) as session:
        module = session.get(Module, module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Cascade delete questions
        statement = select(Question).where(Question.module_id == module_id)
        questions = session.exec(statement).all()
        
        for q in questions:
            # 1. Delete folder
            folder_path = settings.QUESTIONS_DIR / q.folder_name
            if folder_path.exists():
                try:
                    shutil.rmtree(folder_path)
                except Exception as e:
                    print(f"Error deleting folder {folder_path}: {e}")
            
            # 2. Delete from DB
            session.delete(q)
        
        # Finally delete the module
        session.delete(module)
        session.commit()
        log_audit_event("delete_module", user=current_user.username, request=request, status="success", details={"module_id": module_id})
        return None

@router.patch("/{module_id}", response_model=Module)
def update_module(request: Request, module_id: str, module_update: Module, current_user: User = Depends(get_current_admin_user)):
    with Session(engine) as session:
        db_module = session.get(Module, module_id)
        if not db_module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        module_data = module_update.dict(exclude_unset=True)
        # Prevent ID update
        if "id" in module_data:
            del module_data["id"]
            
        for key, value in module_data.items():
            setattr(db_module, key, value)
            
        session.add(db_module)
        session.commit()
        session.refresh(db_module)
        log_audit_event("update_module", user=current_user.username, request=request, status="success", details={"module_id": module_id})
        return db_module
