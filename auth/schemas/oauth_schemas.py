import datetime
import pydantic
from typing import Optional


class UserBase(pydantic.BaseModel):
    name: str
    email: str
    class Config:
       from_attributes=True

class UserCreate(UserBase):
    password: str
    class Config:
       from_attributes=True

class User(UserBase):
    id: int
    date_created: datetime.datetime
    class Config:
       from_attributes=True

class AddressBase(pydantic.BaseModel):
    street: str
    landmark: str
    city: str
    country: str
    pincode: str
    latitude: float
    longitude: float
    class Config:
       from_attributes=True

class GenerateUserToken(pydantic.BaseModel):
    username: str
    password: str
    class Config:
       from_attributes=True

class GenerateOtp(pydantic.BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None

    @pydantic.model_validator(mode="after")
    def at_least_one_required(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self
    
class VerifyOtp(pydantic.BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    otp: int

class Payload(pydantic.BaseModel):
    user_id: str

class Profile(pydantic.BaseModel):
    Payload: Payload
    user_data: GenerateUserToken