from sqlalchemy.orm import Session
from sqlalchemy import distinct
from src.openai_tracker.models.question_repository import QuestionRepository
from uuid import uuid4
from typing import List


class QuestionRepositoryManager:

    @staticmethod
    def save_question(
        question_text: str,
        category: str,
        db: Session
    ) -> QuestionRepository:
        try:
            new_question = QuestionRepository(
                id=uuid4(),
                question=question_text,
                category=category
            )
            db.add(new_question)
            db.commit()
            db.refresh(new_question)
            return new_question
        except Exception as e:
            db.rollback()
            raise Exception(f"Error saving question: {str(e)}")

    @staticmethod
    def get_all_questions(db: Session) -> List[QuestionRepository]:
        try:
            return db.query(QuestionRepository).all()
        except Exception as e:
            raise Exception(f"Error fetching questions: {str(e)}")
        
        
    @staticmethod
    def get_all_unique_categories(db: Session) -> List[str]:
        try:
            results = db.query(distinct(QuestionRepository.category)).all()
            return [row[0] for row in results if row[0] is not None]
        except Exception as e:
            raise Exception(f"Error fetching unique categories: {str(e)}")