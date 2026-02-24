import asyncio
from backend.app.services.execution_service import execution_service
from backend.app.models import ExecutionRequest, User
from sqlmodel import Session, select
from backend.app.database import engine
from backend.app.models import Question
from backend.app.core.config import settings

async def test_execution():
    with Session(engine) as session:
        # Get the failing question
        question = session.exec(select(Question).where(Question.id == "q30")).first()
        if not question:
            print("Question q30 not found")
            return
            
        print(f"Testing Question: {question.title}, Module: {question.module_id}")
        
        # Create a mock user
        user = User(username="test_user", email="test@example.com", hashed_password="pw", role="learner")
        
        # Create execution request
        # NOTE: We need to manually set module_id in the request, mirroring what the frontend does
        req = ExecutionRequest(
            code="import transformers\nprint('Transformers imported successfully')",
            question_id=question.id, 
            module_id=question.module_id 
        )
        
        question_data = {
            "folder_path": str(settings.QUESTIONS_DIR / question.folder_name),
            "image_name": "practice-room-python:latest" # Default, should vary by service logic
        }

        print("--- Running Execution Service ---")
        result = await execution_service.run_code(req, question_data, user)
        print("--- Result ---")
        print(result)

if __name__ == "__main__":
    asyncio.run(test_execution())
