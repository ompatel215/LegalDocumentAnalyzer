from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId
from .document import PyObjectId

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    organization: Optional[str] = None
    role: str = Field(default="user", description="User role (admin, user)")

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    preferences: dict = Field(default_factory=dict)
    document_count: int = 0
    recent_documents: List[PyObjectId] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "organization": "Legal Corp",
                "role": "user",
                "is_active": True,
                "preferences": {
                    "theme": "light",
                    "notification_preferences": {
                        "email": True,
                        "in_app": True
                    }
                }
            }
        }

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    document_count: int
    preferences: dict

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[EmailStr] = None
    preferences: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 