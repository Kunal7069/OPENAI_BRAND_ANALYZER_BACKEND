from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.openai_tracker.config.database import SessionLocal, Base, engine
from src.openai_tracker.schemas.brand import BrandSignup, BrandLogin, BrandResponse,BrandParagraph
from src.openai_tracker.services.brandManager import BrandManager
from src.openai_tracker.services.brandQuestionGenerator import BrandQuestionGenerator
from src.openai_tracker.services.brandQuestionManager import BrandQuestionManager
from src.openai_tracker.schemas.question_repository import QuestionCreate
from src.openai_tracker.services.questionRepositoryManager import QuestionRepositoryManager
from uuid import UUID
from typing import List
from decimal import Decimal
from pydantic import BaseModel

app = FastAPI()
manager = BrandQuestionManager()

# Create tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Connected to Neon.tech DB!"}


@app.post("/signup", response_model=BrandResponse)
def signup(brand: BrandSignup, db: Session = Depends(get_db)):
    return BrandManager.signup(brand, db)

@app.post("/login", response_model=BrandResponse)
def login(brand: BrandLogin, db: Session = Depends(get_db)):
    return BrandManager.login(brand, db)

@app.post("/generate-questions")
def generate_questions(payload: BrandParagraph):
        generator = BrandQuestionGenerator()
        result = generator.generate_questions(payload.paragraph)
        return result
class QuestionRequest(BaseModel):
    question: str
    

@app.get("/brands/{brand_id}/questions")
def get_questions(brand_id: UUID, db: Session = Depends(get_db)):
    try:
        questions = manager.get_questions_by_brand_id(brand_id, db)
        return {"brand_id": str(brand_id), "questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/brands/{brand_id}/questions")
def save_questions(brand_id: UUID, questions: List[str], db: Session = Depends(get_db)):
    try:
        saved = manager.save_questions(brand_id, questions, db)
        return {"status": "success", "count": len(saved)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/answer-question")
def answer_question(payload: QuestionRequest):
    try:
        generator = BrandQuestionGenerator()
        result = generator.generate_answer(payload.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/brands/{brand_id}/questions/answers")
def get_answers_for_brand_questions(brand_id: UUID, db: Session = Depends(get_db)):
    try:
        questions = manager.get_questions_by_brand_id(brand_id, db)
        if not questions:
            return {
                "brand_id": str(brand_id),
                "answers": [],
                "total_tokens": 0,
                "total_cost": 0.0
            }

        generator = BrandQuestionGenerator()
        all_answers = []
        total_tokens = 0
        total_cost = 0.0
        counter=1
        for q in questions:
            print(counter)
            counter=counter+1
            result = generator.generate_answer(q)

            # Convert Decimal cost to float
            cost = float(result["total_cost"])

            all_answers.append({
                "question": q,
                "answer": result["answer"],
                "tokens_used": result["total_tokens"],
                "cost": round(cost, 6)
            })

            total_tokens += result["total_tokens"]
            total_cost += cost

        return {
            "brand_id": str(brand_id),
            "answers": all_answers,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 6)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-question")
def add_question_to_repository(payload: QuestionCreate, db: Session = Depends(get_db)):
    try:
        saved_question = QuestionRepositoryManager.save_question(
            question_text=payload.question,
            domain=payload.domain,
            category=payload.category,
            db=db
        )
        return {"status": "success", "question_id": str(saved_question.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/question-repository")
def get_question_repository(db: Session = Depends(get_db)):
    try:
        questions = QuestionRepositoryManager.get_all_questions(db)
        return {"questions": [
            {
                "id": str(q.id),
                "question": q.question,
                "domain": q.domain,
                "category": q.category
            } for q in questions
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
