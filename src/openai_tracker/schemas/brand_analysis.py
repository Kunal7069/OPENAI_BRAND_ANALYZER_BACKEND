from pydantic import BaseModel
from typing import List, Dict

class AnalysisRequest(BaseModel):
    brand: str
    category: str
    competitors: List[str]
    questions_and_responses: List[Dict[str, str]] 