from pydantic import BaseModel
from enum import Enum


class QuestionCreate(BaseModel):
    question: str
    category: str