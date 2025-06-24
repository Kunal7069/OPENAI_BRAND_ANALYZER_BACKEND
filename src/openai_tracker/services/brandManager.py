from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.openai_tracker.models.brand import Brand
from src.openai_tracker.models.brand_question import BrandQuestion
from src.openai_tracker.models.question_repository import QuestionRepository
from src.openai_tracker.schemas.brand import BrandSignup, BrandLogin

class BrandManager:

    @staticmethod
    def signup(data: BrandSignup, db: Session) -> Brand:
        try:
            existing = db.query(Brand).filter(Brand.email == data.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")

            new_brand = Brand(
                email=data.email,
                brand_name=data.brand_name,
                brand_info=data.brand_info,
                password=data.password,
                competitors=data.competitors  
            )
            db.add(new_brand)
            db.commit()
            db.refresh(new_brand)
            return new_brand

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

    @staticmethod
    def login(data: BrandLogin, db: Session) -> Brand:
        try:
            brand = db.query(Brand).filter(Brand.email == data.email).first()
            if not brand or brand.password != data.password:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            return brand
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")