import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.openai_tracker.config.database import Base

class BrandQuestion(Base):
    __tablename__ = "brand_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    question = Column(String, nullable=False)

    brand = relationship("Brand", back_populates="questions")
