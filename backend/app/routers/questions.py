from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..services import question_service
from ..models import Question, QuestionDetail, QuestionRead
from ..services.auth_service import get_optional_current_user, User

router = APIRouter()

@router.get("", response_model=List[QuestionRead])
@router.get("/", response_model=List[QuestionRead])
def read_questions(
    difficulty: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user)
):

    try:
        questions = question_service.get_all_questions(
            username=current_user.username if current_user else None,
            difficulty=difficulty,
            status=status,
            user_role=current_user.role if current_user else None
        )

        return questions
    except Exception as e:

        raise e

@router.get("/{question_id}", response_model=QuestionDetail)
def read_question(question_id: str, current_user: Optional[User] = Depends(get_optional_current_user)):

    question = question_service.get_question(
        question_id,
        username=current_user.username if current_user else None,
        user_role=current_user.role if current_user else None
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
