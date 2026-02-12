from sqlmodel import Session, select, and_
from ..database import engine
from ..models import UserProgress, User
from typing import Set, Optional
from datetime import datetime, timedelta

class ProgressService:
    def mark_completed(self, username: str, question_id: str, code: str = None):
        username = username.strip()
        question_id = question_id.strip()
        with Session(engine) as session:
            # Check if exists (handle duplicates robustly)
            statement = select(UserProgress).where(
                and_(UserProgress.username == username, UserProgress.question_id == question_id)
            )
            results = session.exec(statement).all()
            
            is_new_completion = False
            if not results:
                # No existing progress for this user/question
                progress = UserProgress(username=username, question_id=question_id, status="completed", user_code=code)
                session.add(progress)
                is_new_completion = True
            else:
                # Check if it was already completed to avoid double counting streak
                was_already_completed = any(p.status == "completed" for p in results)
                if not was_already_completed:
                    is_new_completion = True

                # Update first one to completed, delete others if any (to fix existing duplicates)
                results[0].status = "completed"
                if code: results[0].user_code = code
                results[0].updated_at = datetime.utcnow()
                session.add(results[0])
                
                for p in results[1:]:
                    session.delete(p)
            
            if is_new_completion:
                self._update_streak(session, username)
            session.commit()

    def mark_attempted(self, username: str, question_id: str, code: str = None):
        username = username.strip()
        question_id = question_id.strip()
        with Session(engine) as session:
            statement = select(UserProgress).where(
                and_(UserProgress.username == username, UserProgress.question_id == question_id)
            )
            results = session.exec(statement).all()
            
            if not results:
                progress = UserProgress(username=username, question_id=question_id, status="attempted", user_code=code)
                session.add(progress)
            else:
                # If ANY is completed, preserve it. Just update code if needed.
                is_completed = any(p.status == "completed" for p in results)
                # Use the first one as primary
                primary = results[0]
                if not is_completed:
                    primary.status = "attempted"
                
                # Update code, allowing None (failed attempt) to clear it
                primary.user_code = code
                
                primary.updated_at = datetime.utcnow()
                session.add(primary)
                
                # Cleanup duplicates
                for p in results[1:]:
                    session.delete(p)
            
            session.commit()

    def get_progress(self, username: str) -> dict:
        username = username.strip()
        with Session(engine) as session:
            statement = select(UserProgress).where(UserProgress.username == username)
            results = session.exec(statement).all()
            
            # Use a dict to ensure only one status per question_id
            # Preference: completed > attempted
            status_map = {}
            for p in results:
                qid = p.question_id.strip()
                if qid not in status_map or p.status == "completed":
                    status_map[qid] = p.status
            
            return {
                "completed": {qid for qid, status in status_map.items() if status == "completed"},
                "attempted": {qid for qid, status in status_map.items() if status == "attempted"}
            }

    def get_user_code(self, username: str, question_id: str) -> Optional[str]:
        username = username.strip()
        question_id = question_id.strip()
        with Session(engine) as session:
            statement = select(UserProgress).where(
                and_(UserProgress.username == username, UserProgress.question_id == question_id)
            ).order_by(UserProgress.updated_at.desc())
            progress = session.exec(statement).first()
            return progress.user_code if progress else None

    def _update_streak(self, session: Session, username: str):
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        if not user:
            return

        # Simplified "Solve Streak" logic: Always increment on successful completion
        # This allows users to gain streak points for every question they answer,
        # which is more rewarding for a practice session than a strict "daily" counter.
        now = datetime.utcnow()
        user.current_streak += 1
        user.last_completed_at = now
        session.add(user)

    def refresh_streak(self, username: str):
        """Check if streak should be reset due to inactivity."""
        with Session(engine) as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            if not user or not user.last_completed_at:
                return

            now = datetime.utcnow()
            today = now.date()
            last_date = user.last_completed_at.date()

            if last_date < today - timedelta(days=1):
                # Skipped yesterday, reset streak to 0
                user.current_streak = 0
                session.add(user)
                session.commit()

progress_service = ProgressService()
