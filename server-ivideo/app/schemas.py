from pydantic import BaseModel
from typing import Optional, Dict, Any

# 请求和响应模型
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str