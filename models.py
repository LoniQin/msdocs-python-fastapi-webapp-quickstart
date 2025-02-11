from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import datetime
# User model for Pydantic
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Pydantic model for user response
class UserResponse(BaseModel):
    user_id: int
    email: str
    username: str
    access_token: str

class File(BaseModel):
    file_name: str
    mine_type: str 
    content: str

class Message(BaseModel):
    role: str 
    content: str

class InputMessage(BaseModel):
    role: str 
    content: str
    files: List[File]

class Conversation(BaseModel):
    model: str
    messages: List[InputMessage]
    stream: bool
    
class ChatModel(BaseModel):
    id: str
    model: str
    displayName: str
    provider: str
    description: str
    stream: bool

class CommonResponse(BaseModel):
    message: str
    data: Any

class FeedBackModel(BaseModel):
    user_id: int
    contact: str
    title: str
    content: str

class FeedBackResponse(BaseModel):
    id: int
    contact: str
    title: str
    content: str
    created_at: datetime