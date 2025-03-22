from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler) -> Dict[str, Any]:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        json_schema.update(type="string", format="objectid")
        return json_schema

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            raise ValueError("Invalid ObjectId")
        return str(v)

class DocumentBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(...)
    content: str = Field(...)
    file_path: str = Field(...)
    document_type: str = Field(...)
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    user_id: PyObjectId
    analysis_status: str = Field(default="pending")

class Document(DocumentBase):
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    summary: Optional[str] = None
    key_clauses: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    risk_factors: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    entities: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    key_clauses: Optional[List[dict]] = None
    risk_factors: Optional[List[dict]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 