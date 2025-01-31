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

# UserProfile Schemas
class UserProfileUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    date_of_birth: Optional[datetime]
    profile_picture_url: Optional[str]

class UserProfileOut(BaseModel):
    profile_id: str
    user_id: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    date_of_birth: Optional[datetime]
    profile_picture_url: Optional[str]

    class Config:
        orm_mode = True

# WorkerProfile Schemas
class WorkerProfileUpdate(BaseModel):
    hourly_rate: Optional[float]
    availability_status: Optional[str]
    bio: Optional[str]

class WorkerProfileOut(BaseModel):
    worker_id: str
    user_id: str
    hourly_rate: Optional[float]
    availability_status: Optional[str]
    bio: Optional[str]

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
