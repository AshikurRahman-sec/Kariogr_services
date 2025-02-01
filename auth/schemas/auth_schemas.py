from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# UserAuth Schemas
class UserAuthCreate(BaseModel):
    email: EmailStr
    password: str

class UserAuthLogin(BaseModel):
    email: EmailStr
    password: str

class UserAuthOut(BaseModel):
    user_id: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Token Schemas
class TokenCreate(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime

class TokenOut(BaseModel):
    token_id: str
    user_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime

    class Config:
        orm_mode = True

# Firebase Auth Schemas
class FirebaseAuthRequest(BaseModel):
    id_token: str

# Token Schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime

