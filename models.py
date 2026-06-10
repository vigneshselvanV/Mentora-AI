from pydantic import BaseModel
from typing import Optional, Any

class SignupRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    question: str

class SaveDataRequest(BaseModel):
    data: dict

class AuthResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user: Optional[dict] = None
    message: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    plan: str
    created_at: str
