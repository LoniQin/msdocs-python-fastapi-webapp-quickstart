from pydantic import BaseModel
from typing import Any, List
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

class Message(BaseModel):
    role: str 
    content: str

class Messages(BaseModel):
    messages: List[Message]


class CommonResponse(BaseModel):
    message: str
    data: Any