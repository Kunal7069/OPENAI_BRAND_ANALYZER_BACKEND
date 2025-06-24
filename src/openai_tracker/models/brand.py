import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from src.openai_tracker.config.database import Base

class Brand(Base):
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    brand_name = Column(String, nullable=False)
    brand_info = Column(String)
    password = Column(String, nullable=False)
    competitors = Column(JSON, default=[])
    
    questions = relationship("BrandQuestion", back_populates="brand", cascade="all, delete-orphan")