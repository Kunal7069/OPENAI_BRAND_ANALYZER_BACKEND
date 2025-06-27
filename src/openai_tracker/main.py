from fastapi import FastAPI, Depends, HTTPException,WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from src.openai_tracker.config.database import SessionLocal, Base, engine
from src.openai_tracker.schemas.brand import BrandSignup, BrandLogin, BrandResponse,BrandParagraph
from src.openai_tracker.services.brandManager import BrandManager
from src.openai_tracker.services.brandQuestionGenerator import BrandQuestionGenerator
from src.openai_tracker.services.brandQuestionManager import BrandQuestionManager
from src.openai_tracker.schemas.question_repository import QuestionCreate
from src.openai_tracker.services.questionRepositoryManager import QuestionRepositoryManager
from src.openai_tracker.schemas.brand_analysis import AnalysisRequest
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

@app.post("/question-repository")
def add_question_to_repository(payload: QuestionCreate, db: Session = Depends(get_db)):
    try:
        saved_question = QuestionRepositoryManager.save_question(
            question_text=payload.question,
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
                "category": q.category
            } for q in questions
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/question-repository/categories")
def get_unique_categories(db: Session = Depends(get_db)):
    try:
        categories = QuestionRepositoryManager.get_all_unique_categories(db)
        return {"unique_categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    




@app.websocket("/ws/bulk-answer")
async def websocket_bulk_answer(websocket: WebSocket):
    await websocket.accept()
    generator = BrandQuestionGenerator()
    all_results = []

    try:
        # Receive JSON payload with questions
        data = await websocket.receive_json()
        questions: List[str] = data.get("questions", [])

        for idx, question in enumerate(questions, start=1):
            result = generator.generate_answer(question)

            all_results.append({
                "question": question,
                "answer": result["answer"],
                "total_tokens": result["total_tokens"],
                "total_cost": float(round(result["total_cost"], 6))
            })

            # Send only the number of the current question
            await websocket.send_json({
                "type": "progress",
                "question_number": idx
            })

        # Send final response
        await websocket.send_json({
            "type": "complete",
            "results": all_results
        })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Error: {str(e)}"
        })
        
        
@app.post("/generate-analysis")
def generate_analysis_api(payload: AnalysisRequest):
    try:
        generator = BrandQuestionGenerator()

        result = generator.generate_analysis(
            brand=payload.brand,
            category=payload.category,
            competitors=payload.competitors,
            questions_and_responses=payload.questions_and_responses
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# class BulkQuestionRequest(BaseModel):
#     questions: List[str]
    
# @app.post("/bulk-answer")
# def bulk_answer_questions(payload: BulkQuestionRequest):
#     try:
#         generator = BrandQuestionGenerator()
#         results = []

#         for question in payload.questions:
#             answer_data = generator.generate_answer(question)
#             results.append({
#                 "question": question,
#                 "answer": answer_data["answer"],
#                 "total_tokens": answer_data["total_tokens"],
#                 "total_cost": answer_data["total_cost"]
#             })

#         return {"results": results}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/signup", response_model=BrandResponse)
# def signup(brand: BrandSignup, db: Session = Depends(get_db)):
#     return BrandManager.signup(brand, db)

# @app.post("/login", response_model=BrandResponse)
# def login(brand: BrandLogin, db: Session = Depends(get_db)):
#     return BrandManager.login(brand, db)

# @app.post("/generate-questions")
# def generate_questions(payload: BrandParagraph):
#         generator = BrandQuestionGenerator()
#         result = generator.generate_questions(payload.paragraph)
#         return result
# class QuestionRequest(BaseModel):
#     question: str
    
    

# @app.get("/brands/{brand_id}/questions")
# def get_questions(brand_id: UUID, db: Session = Depends(get_db)):
#     try:
#         questions = manager.get_questions_by_brand_id(brand_id, db)
#         return {"brand_id": str(brand_id), "questions": questions}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
    
# @app.post("/brands/{brand_id}/questions")
# def save_questions(brand_id: UUID, questions: List[str], db: Session = Depends(get_db)):
#     try:
#         saved = manager.save_questions(brand_id, questions, db)
#         return {"status": "success", "count": len(saved)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/answer-question")
# def answer_question(payload: QuestionRequest):
#     try:
#         generator = BrandQuestionGenerator()
#         result = generator.generate_answer(payload.question)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    


    
    
# @app.post("/brands/{brand_id}/questions/answers")
# def get_answers_for_brand_questions(brand_id: UUID, db: Session = Depends(get_db)):
#     try:
#         questions = manager.get_questions_by_brand_id(brand_id, db)
#         if not questions:
#             return {
#                 "brand_id": str(brand_id),
#                 "answers": [],
#                 "total_tokens": 0,
#                 "total_cost": 0.0
#             }

#         generator = BrandQuestionGenerator()
#         all_answers = []
#         total_tokens = 0
#         total_cost = 0.0
#         counter=1
#         for q in questions:
#             print(counter)
#             counter=counter+1
#             result = generator.generate_answer(q)

#             # Convert Decimal cost to float
#             cost = float(result["total_cost"])

#             all_answers.append({
#                 "question": q,
#                 "answer": result["answer"],
#                 "tokens_used": result["total_tokens"],
#                 "cost": round(cost, 6)
#             })

#             total_tokens += result["total_tokens"]
#             total_cost += cost

#         return {
#             "brand_id": str(brand_id),
#             "answers": all_answers,
#             "total_tokens": total_tokens,
#             "total_cost": round(total_cost, 6)
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



    
# @app.post("/brands/{brand_id}/batch-questions/answers")
# def get_answers_for_brand_questions(brand_id: UUID, db: Session = Depends(get_db)):
#     try:
#         questions = manager.get_questions_by_brand_id(brand_id, db)
#         if not questions:
#             return {
#                 "brand_id": str(brand_id),
#                 "answers": [],
#                 "total_tokens": 0,
#                 "total_cost": 0.0
#             }

#         generator = BrandQuestionGenerator()
#         result = generator.generate_answers_batch(questions)

#         return {
#             "brand_id": str(brand_id),
#             "answers": result["answers"],
#             "total_tokens": result["total_tokens"],
#             "total_cost": result["total_cost"]
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
