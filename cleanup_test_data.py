import shutil
from pathlib import Path
from backend.app.database import engine
from sqlmodel import Session, select
from backend.app.models import Question
from backend.app.core.config import settings

def cleanup():
    with Session(engine) as session:
        statement = select(Question).where(Question.title == "Test Zip Question")
        questions = session.exec(statement).all()
        for q in questions:
            print(f"Deleting question {q.id}...")
            # Delete folder
            folder_path = settings.QUESTIONS_DIR / q.folder_name
            if folder_path.exists():
                shutil.rmtree(folder_path)
                print(f"Deleted folder {folder_path}")
            
            # Delete from DB
            session.delete(q)
            session.commit()
            print("Deleted from DB")

if __name__ == "__main__":
    cleanup()
