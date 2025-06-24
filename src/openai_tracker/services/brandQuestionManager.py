from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from src.openai_tracker.models.brand_question import BrandQuestion

class BrandQuestionManager:
    def __init__(self):
        pass

    def save_questions(self, brand_id: UUID, questions: List[str], db: Session) -> List[BrandQuestion]:
        try:
            question_objs = [
                BrandQuestion(brand_id=brand_id, question=q)
                for q in questions
            ]
            db.add_all(question_objs)
            db.commit()
            db.refresh(question_objs[0])  # Optional: refresh one to attach to session
            return question_objs
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save questions: {str(e)}")

    def get_questions_by_brand_id(self, brand_id: UUID, db: Session) -> List[str]:
        try:
            results = db.query(BrandQuestion).filter(BrandQuestion.brand_id == brand_id).all()
            return [q.question for q in results]
        except Exception as e:
            raise Exception(f"Failed to fetch questions: {str(e)}")