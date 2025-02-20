from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class RequestEmail(BaseModel):
    email: EmailStr

# UserAuth Schemas
class UserAuthCreate(RequestEmail):
    password: str

class UserAuthLogin(RequestEmail):
    password: str

class UserAuthOut(RequestEmail):
    user_id: str
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

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ResetPassword(BaseModel):
    otp: int
    new_password: str


