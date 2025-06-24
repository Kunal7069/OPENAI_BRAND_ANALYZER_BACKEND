import uuid
from enum import Enum
from sqlalchemy import Column, String, Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from src.openai_tracker.config.database import Base

# Enum for domain
class DomainEnum(str, Enum):
    fashion = "fashion"
    electronics = "electronics"
    food = "food"

# Enum for category
class CategoryEnum(str, Enum):
    brand_identity = "Brand Identity"
    customer_perception = "Customer Perception"
    product_recognition = "Product Recognition"

class QuestionRepository(Base):
    __tablename__ = "question_repository"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    question = Column(String, nullable=False)
    domain = Column(PgEnum(DomainEnum, name="domain_enum"), nullable=False)
    category = Column(PgEnum(CategoryEnum, name="category_enum"), nullable=False)
