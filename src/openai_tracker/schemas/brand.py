from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID

class BrandSignup(BaseModel):
    email: EmailStr
    brand_name: str
    brand_info: Optional[str] = ""
    password: str
    competitors: Optional[List[str]] = []  
    
class BrandParagraph(BaseModel):
    paragraph: str

class BrandLogin(BaseModel):
    email: EmailStr
    password: str

class BrandResponse(BaseModel):
    id: UUID
    email: EmailStr
    brand_name: str
    brand_info: Optional[str]
    competitors: List[str]  

    class Config:
        orm_mode = True