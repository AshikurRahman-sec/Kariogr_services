from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

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
    #user_id: str
    hourly_rate: Optional[float]
    availability_status: Optional[str]
    bio: Optional[str]

    class Config:
        orm_mode = True

class UnregisteredUserAddressCreate(BaseModel):
    mobile_id: str
    street_address: Optional[str] = None
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

class UnregisteredUserAddressOut(UnregisteredUserAddressCreate):
    address_id: str

class WorkerZoneOut(BaseModel):
    worker_zone_id: str
    worker_id: str
    division: str
    district: str
    thana: str
    road_number: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    class Config:
        orm_mode = True

# Skill Info
class SkillOut(BaseModel):
    skill_id: str
    skill_name: str
    category: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True

# Request Schema for Filtering Workers
class WorkerFilterRequest(BaseModel):
    skill_id: str
    district: str

# Full Worker Details
class WorkerWithSkillOut(BaseModel):
    user: UserProfileOut
    worker_profile: WorkerProfileOut
    skills: List[SkillOut]
    worker_zone: List[WorkerZoneOut]

    class Config:
        orm_mode = True