from sqlmodel import Session, select
from ..database import engine
from ..models import Question, QuestionDetail, Module, QuestionRead
from ..services.progress_service import progress_service
from ..core.config import settings
import pandas as pd
import csv
import os
from typing import List, Optional
import re

class QuestionService:
    def get_all_questions(
        self, 
        username: Optional[str] = None,
        difficulty: Optional[str] = None,
        status: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> List[QuestionRead]:
        user_progress = progress_service.get_progress(username) if username else {"completed": set(), "attempted": set()}
        completed_ids = user_progress["completed"]
        attempted_ids = user_progress["attempted"]

        with Session(engine) as session:
            statement = select(Question)
            if difficulty:
                statement = statement.where(Question.difficulty == difficulty)
            
            questions = session.exec(statement).all()
            
            result = []
            for q in questions:
                # Filter out unverified questions for non-admins
                # Treat None as False for backward compatibility or explicit check
                verified = getattr(q, "is_verified", False)
                if not verified and user_role != "admin":
                    continue

                is_completed = q.id.strip() in [cid.strip() for cid in completed_ids]
                is_attempted = q.id.strip() in [aid.strip() for aid in attempted_ids]
                
                # Apply status filter
                if status == "completed" and not is_completed:
                    continue
                if status == "attempted" and not (is_attempted and not is_completed):
                    continue
                if status == "todo" and (is_completed or is_attempted):
                    continue
                
                result.append(QuestionRead(
                    **q.model_dump(),
                    is_completed=is_completed,
                    is_attempted=is_attempted
                ))
            return result

    def get_question(self, question_id: str, username: Optional[str] = None, user_role: Optional[str] = None) -> Optional[QuestionDetail]:
        print(f"DEBUG: QuestionService.get_question called for {question_id}")
        with Session(engine) as session:
            print("DEBUG: Session checking DB...")
            question = session.get(Question, question_id)
            if not question:
                print("DEBUG: Question not found in DB")
                return None
            
            # Create a copy of the data from the DB so we can work with it outside the session
            question_data = question.model_dump(exclude={
                "question_py", "initial_code", "validator_py", "hint", "sample_data"
            })
            folder_name = question.folder_name
            is_verified = question.is_verified
        
        print(f"DEBUG: Found question in DB, folder: {folder_name}")

        # Do disk I/O and progress lookup outside the DB session
        folder_path = settings.QUESTIONS_DIR / folder_name
        if not folder_path.exists():
            print(f"DEBUG: Folder does not exist: {folder_path}")
            return None
        
        print(f"DEBUG: Reading files from {folder_path}...")
        # Read files (keep this for now as parsing all python files into DB is complex)
        q_file = folder_path / "question.py"
        v_file = folder_path / "validator.py"
        # s_file removed
        
        q_text = q_file.read_text(encoding="utf-8") if q_file.exists() else ""
        v_text = v_file.read_text(encoding="utf-8") if v_file.exists() else ""
        # solution.py reading removed
        print("DEBUG: Files read successfully.")
        
        print("DEBUG: Extracting metadata manually...", flush=True)
        # Simplified parser to avoid regex hangs on nested quotes
        def extract_str(source, var_name):
            start_marker = f'{var_name} = """'
            start = source.find(start_marker)
            if start == -1: return None
            content_start = start + len(start_marker)
            end = source.find('"""', content_start)
            if end == -1: return None
            return source[content_start:end]

        description = extract_str(q_text, "description") or "Description not found."
        initial_code = extract_str(q_text, "initial_sample_code") or extract_str(q_text, "inital_sample_code") or "# No starting code provided."
        hint = extract_str(q_text, "hint")
        if hint: hint = hint.strip()
        if description: description = description.strip()
        
        print("DEBUG: Getting sample data...", flush=True)
        sample_data = self._get_sample_data(folder_path, folder_name) or ""
        print("DEBUG: Sample data retrieved.", flush=True)
        data_files = [f for f in os.listdir(folder_path) if f.endswith((".csv", ".txt", ".json")) and f != "master_question_list.csv"]

        print("DEBUG: Checking progress...", flush=True)
        user_progress = progress_service.get_progress(username) if username else {"completed": set(), "attempted": set()}
        
        # Load saved code if available
        # SKIP if admin and unverified (User Request: ensure unverified questions show initial code for admins)
        should_load_progress = True
        if user_role == "admin" and not is_verified:
             should_load_progress = False
             
        if username and should_load_progress:
            saved_code = progress_service.get_user_code(username, question_id)
            if saved_code:
                initial_code = saved_code
                
        print("DEBUG: QuestionDetail built. returning...")
        
        return QuestionDetail(
            **question_data,
            question_py=description,
            initial_code=initial_code,
            validator_py=v_text,
            # solution_py removed
            data_files=data_files,
            hint=hint,
            sample_data=sample_data,
            is_completed=question_data["id"].strip() in [cid.strip() for cid in user_progress["completed"]],
            is_attempted=question_data["id"].strip() in [aid.strip() for aid in user_progress["attempted"]]
        )

    def _get_sample_data(self, folder_path, folder_name) -> Optional[str]:
        preview_file = None
        for ext in ["csv", "txt"]:
            for name in ["data", "sales", folder_name]:
                f = folder_path / f"{name}.{ext}"
                if f.exists():
                    preview_file = f
                    break
            if preview_file: break

        if preview_file:
            try:
                print(f"DEBUG: Reading preview file: {preview_file}", flush=True)
                if preview_file.suffix == ".csv":
                    # Use CSV module to avoid pandas hanging on lock
                    with open(preview_file, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        rows = []
                        for _ in range(6): 
                            try:
                                rows.append(next(reader))
                            except StopIteration:
                                break
                    if not rows: return None
                    
                    headers = rows[0]
                    data = rows[1:]
                    
                    md = "| " + " | ".join(headers) + " |\n"
                    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                    for row in data:
                        md += "| " + " | ".join(row) + " |\n"
                    return md
                else:
                    with open(preview_file, "r", encoding="utf-8") as f:
                        lines = [f.readline() for _ in range(5)]
                        return "```\n" + "".join(lines) + "\n```"
            except Exception as e:
                print(f"DEBUG: Sample data error: {e}", flush=True)
                pass
        return None

question_service = QuestionService()
