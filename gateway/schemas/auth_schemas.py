from pydantic import BaseModel
from schemas.base_schemas import RequestHeader




class GenerateUserTokenRequestBody(BaseModel):
    username: str
    password: str


class GenerateUserTokenRequestModel(BaseModel):
    header: RequestHeader
    meta: dict
    body: GenerateUserTokenRequestBody
   

class UserCredentials(BaseModel):
    username: str
    password: str

class UserRegisteration(BaseModel):
    name: str
    email: str
    password: str

class GenerateOtp(BaseModel):
    email: str

class VerifyOtp(BaseModel):
    email: str
    otp: int