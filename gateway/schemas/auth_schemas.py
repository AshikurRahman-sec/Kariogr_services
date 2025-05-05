from pydantic import BaseModel, EmailStr, model_validator
from schemas.base_schemas import RequestHeader, ResponseHeader, ErrorResponse
from datetime import datetime
from typing import Optional


class UserAuth(BaseModel):
    email: str
    password: str

class UserAuthRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: "UserAuth"

class UserAuthResponseBody(BaseModel):
    user_id: str
    email: str
    created_at: str
    updated_at: str

class UserAuthResponse(BaseModel):
    header: ResponseHeader
    meta: dict
    body: UserAuthResponseBody

class TokenOut(BaseModel):
    token_id: str
    user_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime

    class Config:
        orm_mode = True

class UserAuthLogin(BaseModel):
    email: EmailStr
    password: str

class UserAuthLoginRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: UserAuthLogin

class UserAuthLoginResponseBody(BaseModel):
    token_id: str
    user_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime

class UserAuthLoginResponse(BaseModel):
    header: ResponseHeader
    meta: dict
    body: UserAuthLoginResponseBody

class GenerateOtp(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_required(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self

class GenerateOtpRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: GenerateOtp

class GenerateOtpResponse(BaseModel):
    header: ResponseHeader
    meta: dict
    body: dict

class VerifyOtp(BaseModel):
    email: str
    otp: int

class VerifyOtpRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: VerifyOtp

class VerifyOtpResponse(BaseModel):
    header: ResponseHeader
    meta: dict
    body: dict

class FirebaseAuthRequest(BaseModel):
    id_token: str

# Firebase Auth Response Schema
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime

# Gateway Request Schema
class FirebaseAuthGatewayRequest(BaseModel):
    header: RequestHeader
    body: FirebaseAuthRequest

# Gateway Response Schema
class FirebaseAuthGatewayResponse(BaseModel):
    header: ResponseHeader
    meta: dict
    body: TokenResponse

class RefreshTokenBody(BaseModel):
    refresh_token: str

class RefreshTokenRequestBody(BaseModel):
    meta: dict = {}
    header: RequestHeader
    body: RefreshTokenBody