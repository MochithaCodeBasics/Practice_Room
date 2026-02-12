from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.logging import log_audit_event
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio
from ..models import ExecutionRequest, ExecutionResult, User
from ..services.execution_service import execution_service
from ..services.question_service import question_service
from ..services.auth_service import get_current_active_user
from ..services.progress_service import progress_service
from ..core.config import settings
from ..database import engine
from sqlmodel import Session, select


router = APIRouter()


@router.get("/runs/{run_id}/{filename}")
async def get_artifact(run_id: str, filename: str):
    """
    Serve execution artifacts (images) publicly via Capability URL pattern.
    Security relies on the impossibility of guessing the UUIDv4 run_id.
    """
    # SECURITY: Validate run_id is a valid UUID to prevent scanning
    import uuid
    try:
        uuid.UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    # SECURITY: Validate filename
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Only allow .png files
    if not filename.endswith(".png"):
        raise HTTPException(status_code=400, detail="Only PNG files allowed")
    
    artifact_path = Path("runs") / run_id / filename
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return FileResponse(artifact_path, media_type="image/png")

@router.post("/run", response_model=ExecutionResult)
async def run_code(request: Request, body: ExecutionRequest, current_user: User = Depends(get_current_active_user)):
    # Fetch question details to get data files path
    # We need to extend question_service to give us the raw path or data
    # For now, let's reverse look up or just pass the ID to execution service
    
    # Simple lookup
    q_detail = question_service.get_question(body.question_id)
    if not q_detail:
        return ExecutionResult(stdout="", stderr="Question not found", status="error")
        
    # We need the physical path for the runner to copy files
    # I'll cheat and access private logic or update service. 
    # Let's update service logic in memory or just re-calculate path in execution service?
    # Better: Update execution service to accept the question_id and look it up.
    
    # For this iteration, I'll reconstructed the path logic in the handler or service.
    # Actually, question_service.get_question returns a model, not the path.
    
    # Re-using the path logic from config:
    folder_path = settings.QUESTIONS_DIR / q_detail.folder_name
    

    question_data = {
        "folder_path": str(folder_path),
        "data_files": q_detail.data_files
    }
    
    try:
        log_audit_event("run_code", user=current_user.username, request=request, status="start", details={"question_id": body.question_id})
        result = await execution_service.run_code(body, question_data, current_user)
        log_audit_event("run_code", user=current_user.username, request=request, status="success", details={"question_id": body.question_id, "run_id": result.run_id})
        return result
    except Exception as e:
        import traceback
        return ExecutionResult(stdout="", stderr=f"Server Error Details: {str(e)}\n{traceback.format_exc()}", status="error")

@router.post("/validate", response_model=ExecutionResult)
async def validate_code(request: Request, body: ExecutionRequest, current_user: User = Depends(get_current_active_user)):
    q_detail = question_service.get_question(body.question_id)
    if not q_detail:
         return ExecutionResult(stdout="", stderr="Question not found", status="error")
         
    folder_path = settings.QUESTIONS_DIR / q_detail.folder_name
    
    question_data = {
        "folder_path": str(folder_path),
        "validator_path": str(folder_path / "validator.py"),
        "data_files": q_detail.data_files
    }
    
    try:
        log_audit_event("validate_code", user=current_user.username, request=request, status="start", details={"question_id": body.question_id})
        result = await execution_service.validate_code(body, question_data, current_user)
        log_audit_event("validate_code", user=current_user.username, request=request, status="success", details={"question_id": body.question_id, "run_id": result.run_id})
    except Exception as e:
        import traceback
        return ExecutionResult(stdout="", stderr=f"Server Validation Error: {str(e)}\n{traceback.format_exc()}", status="error")

    # Match frontend logic: check for [PASS] or "Correct!" or emoji success
    is_success = False
    if result.status == "success" and result.stdout:
        lower_stdout = result.stdout.lower()
        if "[pass]" in lower_stdout or "correct!" in lower_stdout or "✅" in result.stdout:
            is_success = True
            
    # CRITICAL: Wrap progress tracking and streak calculation in a separate try-except
    # to avoid 500ing even if database lock or logic error occurs during persistence.
    try:
        if is_success:
            progress_service.mark_completed(current_user.username, body.question_id, body.code)
        else:
            # User requested that code ONLY stays in editor if validation is successful.
            # So we mark as attempted but DON'T save the failed code. 
            # This allows the UI to revert to initial code on refresh.
            progress_service.mark_attempted(current_user.username, body.question_id, code=None)
        
        # Fetch updated streak to return to UI
        with Session(engine) as session:
            # Re-fetch the user to get the latest streak (after mark_completed/mark_attempted)
            db_user = session.get(User, current_user.id)
            if db_user:
                result.current_streak = db_user.current_streak
    except Exception as pe:
        import traceback
        print(f"ERROR during progress/streak update: {pe}")
        traceback.print_exc()
        # We don't fail the request if just the streak update fails, 
        # but we log it. The code execution was successful.
        
    return result
