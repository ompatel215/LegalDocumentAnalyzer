from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema: Any) -> Dict[str, Any]:
        return {"type": "string"}

class Entity(BaseModel):
    label: str
    text: str

class Clause(BaseModel):
    type: str
    text: str

class Risk(BaseModel):
    category: str
    severity: str
    context: str

class Statistics(BaseModel):
    word_count: int
    sentence_count: int
    reading_level: float
    reading_time: float

class Sentiment(BaseModel):
    polarity: float
    subjectivity: float

class DocumentAnalysis(BaseModel):
    statistics: Statistics
    summary: str
    entities: Dict[str, List[str]]
    key_clauses: List[Clause]
    risks: List[Risk]
    sentiment: Sentiment

class Document(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    file_type: str
    content_type: str
    size: int
    user_id: PyObjectId
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, processing, completed, failed
    analysis: Optional[DocumentAnalysis] = None
    file_path: str
    tags: List[str] = []
    is_deleted: bool = False

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Contract Agreement",
                "file_type": "pdf",
                "content_type": "application/pdf",
                "size": 1024567,
                "user_id": "507f1f77bcf86cd799439011",
                "status": "pending",
                "file_path": "/uploads/contract.pdf",
                "tags": ["contract", "agreement"]
            }
        }

class DocumentResponse(BaseModel):
    id: str
    title: str
    file_type: str
    size: int
    upload_date: datetime
    last_modified: datetime
    status: str
    analysis: Optional[DocumentAnalysis] = None
    tags: List[str] = []

    class Config:
        populate_by_name = True 