from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str



class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    auth_provider: str
    created_at: Optional[datetime] = None

    class Config:
        # Esto permite que Pydantic entienda que viene de un objeto de SQLAlchemy
        from_attributes = True