from pydantic import BaseModel
from datetime import datetime
from typing import List

class MessageBase(BaseModel):
    text: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    sender: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ThreadResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True