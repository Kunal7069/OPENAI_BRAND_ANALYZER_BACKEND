from pydantic import BaseModel
from enum import Enum

class DomainEnum(str, Enum):
    fashion = "fashion"
    electronics = "electronics"
    food = "food"

class CategoryEnum(str, Enum):
    brand_identity = "Brand Identity"
    customer_perception = "Customer Perception"
    product_recognition = "Product Recognition"

class QuestionCreate(BaseModel):
    question: str
    domain: DomainEnum
    category: CategoryEnum