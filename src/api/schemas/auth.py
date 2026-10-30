from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignUp(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "CITOYEN"
    district: Optional[str] = "Antananarivo"

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    username: str
    email: EmailStr
    role: str
    district: str
    public_key: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    public_key: str
    role: str
