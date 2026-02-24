import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from fastapi.responses import FileResponse
from app.core.logging import log_audit_event
from app.core.config import settings
from app.services.auth_service import get_current_admin_user, User
import pandas as pd
import re
import sqlalchemy.exc
import random
import time

from sqlmodel import Session, select, func
from app.database import engine
from app.models import Question

router = APIRouter()

@router.post("/questions", status_code=status.HTTP_201_CREATED)
def create_question(
    title: str = Form(...),
    difficulty: str = Form(...),
    module_id: str = Form(...),
    tags: str = Form(""),
    topic: str = Form("General"),
    question_py: Optional[UploadFile] = File(None),
    question_text: Optional[str] = Form(None),
    validator_py: Optional[UploadFile] = File(None),
    validator_text: Optional[str] = Form(None),
    data_files: List[UploadFile] = File(None),
    data_file_content: Optional[str] = Form(None),
    data_file_name: Optional[str] = Form(None),
    request: Request = None,
    current_user: User = Depends(get_current_admin_user)
):
    # Retry logic for race condition on ID generation
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with Session(engine) as session:
                # 1. Determine new ID
                statement = select(Question.id)
                existing_ids = session.exec(statement).all()
                
                max_num = 0
                for i in existing_ids:
                    match = re.search(r'\d+', i)
                    if match:
                        num = int(match.group())
                        if num > max_num:
                            max_num = num
                
                new_id_num = max_num + 1
                new_id = f"q{new_id_num}"
                folder_name = f"question_{new_id_num:02d}"
                folder_path = settings.QUESTIONS_DIR / folder_name

                # 2. Check if Directory Exists
                if folder_path.exists():
                     # If existing folder, we can't easily proceed safely without manual intervention
                     # BUT, if we are looping, maybe the next ID will be free?
                     # The ID logic is based on DB max. If DB max is q10, next is q11.
                     # If question_11 folder exists but q11 is NOT in DB, that's the conflict.
                     # In that case, we fail.
                     raise HTTPException(status_code=500, detail=f"Directory {folder_name} already exists but DB record missing.")
                
                os.makedirs(folder_path, exist_ok=True)

                # 3. Save Files
                try:
                    if question_py:
                        question_py.file.seek(0)
                        with open(folder_path / "question.py", "wb") as buffer:
                            shutil.copyfileobj(question_py.file, buffer)
                    elif question_text:
                         with open(folder_path / "question.py", "w", encoding="utf-8") as f:
                             f.write(question_text)
                    
                    if validator_py:
                        validator_py.file.seek(0)
                        with open(folder_path / "validator.py", "wb") as buffer:
                            shutil.copyfileobj(validator_py.file, buffer)
                    elif validator_text:
                         with open(folder_path / "validator.py", "w", encoding="utf-8") as f:
                             f.write(validator_text)
                    
                    if data_files:
                        for file in data_files:
                            if file.filename:
                                file.file.seek(0)
                                # SECURITY: Sanitize filename to prevent path traversal
                                safe_filename = os.path.basename(file.filename)
                                with open(folder_path / safe_filename, "wb") as buffer:
                                    shutil.copyfileobj(file.file, buffer)
                    
                    if data_file_content and data_file_name:
                         # SECURITY: Sanitize filename to prevent path traversal
                         safe_data_file_name = os.path.basename(data_file_name)
                         with open(folder_path / safe_data_file_name, "w", encoding="utf-8") as f:
                             f.write(data_file_content)
                except Exception as e:
                    if folder_path.exists():
                        shutil.rmtree(folder_path)
                    raise HTTPException(status_code=500, detail=f"Failed to save files: {str(e)}")

                # 4. Save to DB
                db_question = Question(
                    id=new_id,
                    folder_name=folder_name,
                    title=title,
                    difficulty=difficulty,
                    module_id=module_id,
                    topic=topic,
                    tags=tags
                )
                session.add(db_question)
                session.commit()
                log_audit_event("create_question", user=current_user.username, request=request, status="success", details={"question_id": new_id})
                # Success!
                return {"message": "Question created successfully", "id": new_id, "folder": folder_name}

        except sqlalchemy.exc.IntegrityError:
            # Race condition detected (likely ID collision on DB insert)
            if folder_path.exists():
                shutil.rmtree(folder_path)
            
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail="Could not generate unique Question ID after retries. Please try again.")
            
            time.sleep(random.uniform(0.1, 0.3)) # Wait a bit before retrying

@router.post("/questions/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_upload_questions(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user)
):
    from app.services.question_service import question_service
    
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")
        
    try:
        result = await question_service.process_bulk_zip(file)
        log_audit_event("bulk_upload_questions", user=current_user.username, request=request, status="success", details={"count": result["success"]})
        return result
    except Exception as e:
        log_audit_event("bulk_upload_questions", user=current_user.username, request=request, status="failed", details={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/sample-template")
def get_sample_template(current_user: User = Depends(get_current_admin_user)):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "sample_questions.zip")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample template not found")
    return FileResponse(
        path=file_path,
        filename="sample_questions.zip",
        media_type="application/zip"
    )

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(request: Request, question_id: str, current_user: User = Depends(get_current_admin_user)):
    with Session(engine) as session:
        question = session.get(Question, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
            
        folder_path = settings.QUESTIONS_DIR / question.folder_name
        
        # Remove from DB
        session.delete(question)
        session.commit()
        log_audit_event("delete_question", user=current_user.username, request=request, status="success", details={"question_id": question_id})
        
        # Remove directory
        if folder_path.exists():
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                print(f"Error deleting directory {folder_path}: {e}")
                
        return None


@router.put("/questions/{question_id}")
def update_question(
    question_id: str,
    title: Optional[str] = Form(None),
    difficulty: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    question_py: Optional[UploadFile] = File(None),
    validator_py: Optional[UploadFile] = File(None),
    data_files: List[UploadFile] = File(None),
    request: Request = None,
    current_user: User = Depends(get_current_admin_user)
):
    with Session(engine) as session:
        question = session.get(Question, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Update metadata fields if provided
        if title is not None:
            question.title = title
        if difficulty is not None:
            question.difficulty = difficulty
        if topic is not None:
            question.topic = topic
        if tags is not None:
            question.tags = tags
        
        folder_path = settings.QUESTIONS_DIR / question.folder_name
        
        # Replace files if provided
        try:
            if question_py and question_py.filename:
                with open(folder_path / "question.py", "wb") as buffer:
                    shutil.copyfileobj(question_py.file, buffer)
            
            if validator_py and validator_py.filename:
                with open(folder_path / "validator.py", "wb") as buffer:
                    shutil.copyfileobj(validator_py.file, buffer)
            
            if data_files:
                for file in data_files:
                    if file.filename:
                        # SECURITY: Sanitize filename to prevent path traversal
                        safe_filename = os.path.basename(file.filename)
                        with open(folder_path / safe_filename, "wb") as buffer:
                            shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update files: {str(e)}")
        
        # Reset verification status on any update
        question.is_verified = False
        
        session.add(question)
        session.commit()
        session.refresh(question)
        log_audit_event("update_question", user=current_user.username, request=request, status="success", details={"question_id": question_id})
        
        return {"message": "Question updated successfully", "id": question.id}

from pydantic import BaseModel

class VerifyRequest(BaseModel):
    verified: bool

@router.post("/questions/{question_id}/verify")
def verify_question(
    question_id: str,
    body: VerifyRequest,
    request: Request = None,
    current_user: User = Depends(get_current_admin_user)
):
    with Session(engine) as session:
        question = session.get(Question, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        question.is_verified = body.verified
        session.add(question)
        session.commit()
        log_audit_event("verify_question", user=current_user.username, request=request, status="success", details={"question_id": question_id, "verified": body.verified})
        
        return {"message": f"Question verification status set to {body.verified}", "id": question.id, "is_verified": body.verified}
