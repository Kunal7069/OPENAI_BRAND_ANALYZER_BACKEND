import uuid
from enum import Enum
from sqlalchemy import Column, String, Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from src.openai_tracker.config.database import Base


class QuestionRepository(Base):
    __tablename__ = "question_repository"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    question = Column(String, nullable=False)
    category = Column(String, nullable=False)
