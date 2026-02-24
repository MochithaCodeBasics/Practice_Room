from sqlmodel import Session, select
from backend.app.database import engine
from backend.app.models import Question

def check_question_module(question_title_snippet):
    with Session(engine) as session:
        statement = select(Question).where(Question.title.contains(question_title_snippet))
        questions = session.exec(statement).all()
        for q in questions:
            print(f"ID: {q.id}, Title: {q.title}, Module: {q.module_id}, Folder: {q.folder_name}")

if __name__ == "__main__":
    check_question_module("Tokenize text")
