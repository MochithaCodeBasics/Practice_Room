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
        with Session(engine) as session:
            question = session.get(Question, question_id)
            if not question:
                return None

            # Create a copy of the data from the DB so we can work with it outside the session
            question_data = question.model_dump(exclude={
                "question_py", "initial_code", "validator_py", "hint", "sample_data"
            })
            folder_name = question.folder_name
            is_verified = question.is_verified

        # Do disk I/O and progress lookup outside the DB session
        folder_path = settings.QUESTIONS_DIR / folder_name
        if not folder_path.exists():
            return None

        q_file = folder_path / "question.py"
        v_file = folder_path / "validator.py"

        q_text = q_file.read_text(encoding="utf-8") if q_file.exists() else ""
        v_text = v_file.read_text(encoding="utf-8") if v_file.exists() else ""

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

        sample_data = self._get_sample_data(folder_path, folder_name) or ""
        data_files = [f for f in os.listdir(folder_path) if f.endswith((".csv", ".txt", ".json", ".pt", ".pth")) and f != "master_question_list.csv"]

        user_progress = progress_service.get_progress(username) if username else {"completed": set(), "attempted": set()}

        # Load saved code if available
        if username:
            saved_code = progress_service.get_user_code(username, question_id)
            if saved_code:
                initial_code = saved_code

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
                if preview_file.suffix == ".csv":
                    # Use CSV module to avoid pandas hanging on lock
                    with open(preview_file, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        rows = []
                        # 5 rows total: 1 header + 4 data rows
                        for _ in range(5): 
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
                        # Limit text preview to 4 lines
                        lines = [f.readline() for _ in range(4)]
                        return "```\n" + "".join(lines) + "\n```"
            except Exception:
                pass
        return None

    async def process_bulk_zip(self, file) -> dict:
        """
        Process a ZIP file containing multiple questions and a metadata Excel file.
        Structure:
        root/
          ├── metadata.xlsx (Manifest)
          ├── q1/
          │    ├── question.py
          │    ├── validator.py
          │    └── data.csv
          └── q2/ ...
        """
        import zipfile
        import shutil
        import tempfile
        from pathlib import Path

        results = {"total": 0, "success": 0, "failed": 0, "errors": []}
        
        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "questions.zip"
            
            # Save the uploaded ZIP
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract ZIP
            try:
                extract_path = temp_path / "extracted"
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            except zipfile.BadZipFile:
                raise ValueError("Invalid ZIP file")

            # Locate Manifest (Excel file)
            # Handle case where ZIP has a single root folder
            excel_files = list(extract_path.rglob("*.xlsx"))
            if not excel_files:
                raise ValueError("No metadata Excel file found in ZIP")
            
            # Pick the first Excel file found as manifest, or prioritize "metadata.xlsx" or "manifest.xlsx"
            manifest_path = next((f for f in excel_files if f.name.lower() in ["metadata.xlsx", "manifest.xlsx", "questions.xlsx"]), excel_files[0])
            
            # The root for relative folder paths is where the manifest is located
            root_path = manifest_path.parent

            try:
                df = pd.read_excel(manifest_path)
                # Normalize columns
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                # Pre-fetch existing IDs
                current_id_num = 0
                with Session(engine) as session:
                    existing_ids = session.exec(select(Question.id)).all()
                    for i in existing_ids:
                        match = re.search(r'\d+', i)
                        if match:
                            num = int(match.group())
                            if num > current_id_num:
                                current_id_num = num

                for index, row in df.iterrows():
                    results["total"] += 1
                    try:
                        current_id_num += 1
                        
                        # Required Fields
                        title = row.get("title")
                        module_id = row.get("module")
                        if pd.isna(title) or pd.isna(module_id):
                             raise ValueError(f"Row {index+2}: Title and Module are required")

                        folder_name_ref = row.get("folder name")
                        if pd.isna(folder_name_ref):
                            raise ValueError(f"Row {index+2}: 'Folder Name' column is required to link content")
                        
                        folder_name_ref = str(folder_name_ref).strip()
                        source_folder = root_path / folder_name_ref
                        
                        if not source_folder.exists() or not source_folder.is_dir():
                            raise ValueError(f"Row {index+2}: Folder '{folder_name_ref}' not found in ZIP")

                        # Generate New ID
                        question_id = f"q{current_id_num}"
                        dest_folder_name = f"question_{current_id_num:02d}"
                        dest_path = settings.QUESTIONS_DIR / dest_folder_name
                        
                        if dest_path.exists():
                             # Collision avoidance
                             current_id_num += 1
                             question_id = f"q{current_id_num}"
                             dest_folder_name = f"question_{current_id_num:02d}"
                             dest_path = settings.QUESTIONS_DIR / dest_folder_name
                        
                        os.makedirs(dest_path, exist_ok=True)
                        
                        # Copy contents recursively (files and subdirectories)
                        files_copied = []
                        
                        # Copy all contents from source_folder to dest_path
                        if dest_path.exists():
                           shutil.rmtree(dest_path)
                        shutil.copytree(source_folder, dest_path)
                        
                        # Capture list of top-level files for verification
                        files_copied = [f.name for f in dest_path.iterdir() if f.is_file()]
                        
                        # Verify essentials
                        if "question.py" not in files_copied:
                            raise ValueError(f"Row {index+2}: question.py missing in folder '{folder_name_ref}'")
                        if "validator.py" not in files_copied:
                             # Auto-generate detailed validator? Or fail?
                             # For ZIP upload, we expect completeness.
                             raise ValueError(f"Row {index+2}: validator.py missing in folder '{folder_name_ref}'")

                        # Required Fields (Difficulty, Topic, Tags)
                        difficulty = row.get("difficulty")
                        if pd.isna(difficulty):
                             raise ValueError(f"Row {index+2}: Difficulty is required")
                        
                        topic = row.get("topic")
                        if pd.isna(topic):
                             raise ValueError(f"Row {index+2}: Topic is required")
                        
                        tags_val = row.get("tags")
                        if pd.isna(tags_val):
                             raise ValueError(f"Row {index+2}: Tags are required")

                        difficulty = str(difficulty).strip()
                        topic = str(topic).strip()
                        tags = str(tags_val).strip()
                        
                        with Session(engine) as session:
                            new_q = Question(
                                id=question_id,
                                title=str(title).strip(),
                                module_id=str(module_id).strip(),
                                difficulty=difficulty,
                                topic=topic,
                                tags=tags,
                                folder_name=dest_folder_name,
                                is_verified=False
                            )
                            session.add(new_q)
                            session.commit()
                        
                        results["success"] += 1

                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Row {index+2}: {str(e)}")
                        # Cleanup destination if created
                        if 'dest_path' in locals() and dest_path.exists() and not any(x.startswith(f"q{current_id_num}") for x in existing_ids):
                             shutil.rmtree(dest_path)

            except Exception as e:
                 # Manifest read error
                 raise ValueError(f"Failed to process manifest: {str(e)}")

        return results

question_service = QuestionService()
